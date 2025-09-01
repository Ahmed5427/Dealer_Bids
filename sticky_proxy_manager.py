#!/usr/bin/env python3
"""
FIXED Sticky Proxy Manager with better error handling and city name mapping
"""

from asyncio.log import logger
import json
import os
import hashlib
import requests
import time
from datetime import datetime

class StickyProxyManager:
    """Manage consistent proxy locations per account to prevent video selfie verification - FIXED VERSION"""
    
    def __init__(self, config, db):
        self.config = config
        self.db = db
        self.proxy_assignments_file = "account_data/proxy_assignments.json"
        self.location_history_file = "account_data/location_history.json"
        
        # Ensure directories exist
        os.makedirs("account_data", exist_ok=True)
        
        # Load existing assignments
        self.proxy_assignments = self.load_proxy_assignments()
        self.location_history = self.load_location_history()
        
        # FIXED: Better city mapping that works with SOAX
        self.reliable_cities = [
            {'city': 'phoenix', 'region': 'arizona'},
            {'city': 'scottsdale', 'region': 'arizona'}, 
            {'city': 'tempe', 'region': 'arizona'},
            {'city': 'mesa', 'region': 'arizona'},
            {'city': 'losangeles', 'region': 'california'},  # FIXED: Use losangeles not sanfrancisco
            {'city': 'sandiego', 'region': 'california'},
            {'city': 'miami', 'region': 'florida'},
            {'city': 'orlando', 'region': 'florida'},
            {'city': 'chicago', 'region': 'illinois'},
            {'city': 'newyork', 'region': 'newyork'}  # FIXED: Use newyork format
        ]
    
    def load_proxy_assignments(self):
        """Load existing proxy assignments"""
        try:
            if os.path.exists(self.proxy_assignments_file):
                with open(self.proxy_assignments_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Error loading proxy assignments: {e}")
            return {}
    
    def save_proxy_assignments(self):
        """Save proxy assignments"""
        try:
            with open(self.proxy_assignments_file, 'w') as f:
                json.dump(self.proxy_assignments, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving proxy assignments: {e}")
    
    def load_location_history(self):
        """Load location history"""
        try:
            if os.path.exists(self.location_history_file):
                with open(self.location_history_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Error loading location history: {e}")
            return {}
    
    def save_location_history(self):
        """Save location history"""
        try:
            with open(self.location_history_file, 'w') as f:
                json.dump(self.location_history, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving location history: {e}")
    
    def get_consistent_proxy_for_account(self, account_id):
        """Get a consistent proxy for a specific account - FIXED VERSION"""
        try:
            account_key = str(account_id)
            
            # Check if account already has a proxy assignment
            if account_key in self.proxy_assignments:
                assigned_proxy = self.proxy_assignments[account_key]
                logger.info(f"🎯 Using EXISTING sticky proxy for account {account_id}:")
                logger.info(f"   📍 Location: {assigned_proxy.get('verified_city', 'Unknown')}, {assigned_proxy.get('verified_region', 'Unknown')}")
                logger.info(f"   🔗 Session ID: {assigned_proxy.get('session_id', 'Unknown')}")
                
                # Test if existing proxy still works
                if self.test_proxy_connectivity_robust(assigned_proxy):
                    logger.info("✅ Existing sticky proxy is still working")
                    # Log location usage
                    self.log_location_usage(account_id, assigned_proxy)
                    return assigned_proxy
                else:
                    logger.warning(f"⚠️ Existing sticky proxy for account {account_id} no longer working - creating new one")
            
            # Need to assign new proxy - use STICKY approach with FIXED city selection
            new_proxy = self.create_sticky_proxy_for_account_fixed(account_id)
            
            if new_proxy:
                # Save assignment
                self.proxy_assignments[account_key] = new_proxy
                self.save_proxy_assignments()
                
                # Log initial location
                self.log_location_usage(account_id, new_proxy)
                
                logger.info(f"✅ NEW STICKY proxy assigned to account {account_id}:")
                logger.info(f"   📍 Location: {new_proxy.get('verified_city', 'Unknown')}, {new_proxy.get('verified_region', 'Unknown')}")
                logger.info(f"   🔒 This location will be CONSISTENT for this account")
                
                return new_proxy
            
            logger.error(f"❌ Could not create sticky proxy for account {account_id}")
            return None
            
        except Exception as e:
            logger.error(f"💥 Error getting consistent proxy: {e}")
            return None
    
    def create_sticky_proxy_for_account_fixed(self, account_id):
        """Create a sticky proxy session for an account - FIXED VERSION"""
        try:
            # Validate SOAX credentials first
            if not self.validate_soax_credentials():
                logger.error("❌ SOAX credentials validation failed")
                return None
            
            # Create a consistent session ID based on account ID
            account_hash = hashlib.md5(str(account_id).encode()).hexdigest()[:8]
            session_id = f"sticky_{account_hash}_{account_id}"
            
            # Choose a consistent city for this account using FIXED reliable cities
            city_index = int(account_id) % len(self.reliable_cities)
            selected_location = self.reliable_cities[city_index]
            
            logger.info(f"🎯 Creating FIXED sticky proxy for account {account_id}:")
            logger.info(f"   📍 Selected Location: {selected_location['city'].title()}, {selected_location['region'].title()}")
            logger.info(f"   🔗 Session ID: {session_id}")
            
            # Try multiple proxy configurations until one works
            proxy_configs = [
                # Config 1: Full SOAX format
                {
                    'username': f"package-309866-country-us-region-{selected_location['region']}-city-{selected_location['city']}-sessionid-{session_id}",
                    'description': 'Full SOAX format'
                },
                # Config 2: Generic US format as fallback  
                {
                    'username': f"package-309866-country-us-sessionid-{session_id}",
                    'description': 'Generic US format'
                },
                # Config 3: Original config username as fallback
                {
                    'username': self.config.SOAX_USERNAME,
                    'description': 'Original config username'
                }
            ]
            
            for config in proxy_configs:
                try:
                    logger.info(f"🔧 Trying {config['description']}: {config['username'][:50]}...")
                    
                    proxy = {
                        'type': 'soax',
                        'endpoint': getattr(self.config, 'SOAX_ENDPOINT', 'proxy.soax.com:5000'),
                        'username': config['username'],
                        'password': self.config.SOAX_PASSWORD,
                        'geo_country': 'United States',
                        'geo_region': selected_location['region'].title(),
                        'geo_city': selected_location['city'].title(),
                        'session_id': session_id,
                        'account_id': account_id,
                        'is_sticky': True,
                        'created_at': datetime.now().isoformat(),
                        'config_used': config['description']
                    }
                    
                    # Test connectivity with this configuration
                    if self.test_proxy_connectivity_robust(proxy):
                        logger.info(f"✅ {config['description']} connectivity successful!")
                        
                        # Try to get location verification
                        verification = self.verify_proxy_location_robust(proxy)
                        if verification.get('verified'):
                            proxy.update({
                                'verified_ip': verification['ip'],
                                'verified_country': verification['country'],
                                'verified_region': verification.get('region', selected_location['region'].title()),
                                'verified_city': verification.get('city', selected_location['city'].title()),
                                'us_verified': True,
                                'verification_service': verification.get('service', 'ip-api')
                            })
                            logger.info(f"✅ Location verified: {verification['city']}, {verification['region']}")
                        else:
                            # Even if verification fails, keep the assigned location for consistency
                            proxy.update({
                                'verified_ip': 'Unknown',
                                'verified_country': 'US (Assigned)',
                                'verified_region': selected_location['region'].title(),
                                'verified_city': selected_location['city'].title(),
                                'us_verified': False,
                                'note': 'Working proxy but location verification failed'
                            })
                            logger.info(f"⚠️ Location verification failed but proxy works - using assigned location")
                        
                        return proxy
                    else:
                        logger.warning(f"⚠️ {config['description']} connectivity failed")
                        continue
                        
                except Exception as e:
                    logger.error(f"❌ Error with {config['description']}: {e}")
                    continue
            
            logger.error(f"❌ All proxy configurations failed for account {account_id}")
            return None
                
        except Exception as e:
            logger.error(f"💥 Error creating sticky proxy: {e}")
            return None
    
    def validate_soax_credentials(self):
        """Validate SOAX credentials are properly configured"""
        try:
            if not hasattr(self.config, 'SOAX_USERNAME') or not self.config.SOAX_USERNAME:
                logger.error("❌ SOAX_USERNAME not configured")
                return False
            
            if not hasattr(self.config, 'SOAX_PASSWORD') or not self.config.SOAX_PASSWORD:
                logger.error("❌ SOAX_PASSWORD not configured")
                return False
            
            endpoint = getattr(self.config, 'SOAX_ENDPOINT', 'proxy.soax.com:5000')
            logger.info(f"✅ SOAX credentials validated - endpoint: {endpoint}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error validating SOAX credentials: {e}")
            return False
    
    def test_proxy_connectivity_robust(self, proxy, timeout=15):
        """Test if proxy is working with multiple fallbacks - ROBUST VERSION"""
        try:
            if not proxy or not proxy.get('username') or not proxy.get('password'):
                logger.error("❌ Invalid proxy configuration")
                return False
            
            proxy_url = f"http://{proxy['username']}:{proxy['password']}@{proxy['endpoint']}"
            proxy_config = {
                'http': proxy_url,
                'https': proxy_url
            }
            
            # Test with multiple services for better reliability
            test_services = [
                {'url': 'http://httpbin.org/ip', 'timeout': 10, 'name': 'HTTPBin'},
                {'url': 'http://icanhazip.com', 'timeout': 8, 'name': 'ICanHazIP'},
                {'url': 'https://api.ipify.org', 'timeout': 12, 'name': 'IPify'},
                {'url': 'http://checkip.amazonaws.com', 'timeout': 10, 'name': 'AWS CheckIP'}
            ]
            
            successful_tests = 0
            
            for service in test_services:
                try:
                    logger.info(f"🔧 Testing {service['name']}: {service['url']}")
                    
                    response = requests.get(
                        service['url'],
                        proxies=proxy_config,
                        timeout=service['timeout'],
                        headers={
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                            'Accept': 'text/plain, application/json, */*'
                        }
                    )
                    
                    if response.status_code == 200 and len(response.text.strip()) > 5:
                        logger.info(f"✅ {service['name']}: Success ({response.text.strip()[:20]})")
                        successful_tests += 1
                        
                        # If we get 2+ successful tests, consider it working
                        if successful_tests >= 2:
                            logger.info(f"✅ Proxy connectivity confirmed ({successful_tests}/{len(test_services)} services)")
                            return True
                    else:
                        logger.warning(f"⚠️ {service['name']}: Invalid response (status: {response.status_code})")
                        
                except requests.exceptions.Timeout:
                    logger.warning(f"⏰ {service['name']}: Timeout after {service['timeout']}s")
                except Exception as e:
                    logger.warning(f"⚠️ {service['name']}: {str(e)[:100]}")
                
                # Small delay between tests
                time.sleep(1)
            
            if successful_tests > 0:
                logger.info(f"⚠️ Partial connectivity ({successful_tests}/{len(test_services)}) - may still work")
                return successful_tests >= 1  # Accept if at least 1 service works
            else:
                logger.error(f"❌ All connectivity tests failed (0/{len(test_services)})")
                return False
            
        except Exception as e:
            logger.error(f"💥 Connectivity test error: {e}")
            return False
    
    def verify_proxy_location_robust(self, proxy):
        """Verify proxy location with multiple services - ROBUST VERSION"""
        try:
            if not proxy or not proxy.get('username') or not proxy.get('password'):
                return {'verified': False, 'error': 'Invalid proxy'}
            
            proxy_url = f"http://{proxy['username']}:{proxy['password']}@{proxy['endpoint']}"
            proxy_config = {
                'http': proxy_url,
                'https': proxy_url
            }
            
            # Multiple location services for better reliability
            location_services = [
                {
                    'url': 'http://ip-api.com/json/',
                    'timeout': 10,
                    'name': 'IP-API',
                    'parser': lambda data: {
                        'ip': data.get('query'),
                        'country': data.get('country'),
                        'region': data.get('regionName'),
                        'city': data.get('city')
                    }
                },
                {
                    'url': 'https://ipapi.co/json/',
                    'timeout': 12,
                    'name': 'IPapi.co',
                    'parser': lambda data: {
                        'ip': data.get('ip'),
                        'country': data.get('country_name'),
                        'region': data.get('region'),
                        'city': data.get('city')
                    }
                },
                {
                    'url': 'https://freegeoip.app/json/',
                    'timeout': 10,
                    'name': 'FreeGeoIP',
                    'parser': lambda data: {
                        'ip': data.get('ip'),
                        'country': data.get('country_name'),
                        'region': data.get('region_name'),
                        'city': data.get('city')
                    }
                }
            ]
            
            for service in location_services:
                try:
                    logger.info(f"🌍 Testing location with {service['name']}...")
                    
                    response = requests.get(
                        service['url'],
                        proxies=proxy_config,
                        timeout=service['timeout'],
                        headers={
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                            'Accept': 'application/json'
                        }
                    )
                    
                    if response.status_code == 200:
                        try:
                            data = response.json()
                            parsed = service['parser'](data)
                            
                            ip = parsed.get('ip', 'Unknown')
                            country = parsed.get('country', 'Unknown')
                            region = parsed.get('region', 'Unknown')
                            city = parsed.get('city', 'Unknown')
                            
                            logger.info(f"🌍 {service['name']} result:")
                            logger.info(f"   IP: {ip}")
                            logger.info(f"   Country: {country}")
                            logger.info(f"   Region: {region}")
                            logger.info(f"   City: {city}")
                            
                            # Check if it's US-based
                            us_indicators = ['US', 'USA', 'UNITED STATES', 'AMERICA']
                            if any(indicator in str(country).upper() for indicator in us_indicators):
                                logger.info(f"✅ {service['name']}: Verified as US-based!")
                                return {
                                    'verified': True,
                                    'ip': ip,
                                    'country': country,
                                    'region': region,
                                    'city': city,
                                    'service': service['name']
                                }
                            else:
                                logger.warning(f"⚠️ {service['name']}: Not US-based (country: {country})")
                                
                        except (ValueError, KeyError) as e:
                            logger.warning(f"⚠️ {service['name']}: JSON parsing error: {e}")
                            continue
                    else:
                        logger.warning(f"⚠️ {service['name']}: HTTP {response.status_code}")
                        
                except requests.exceptions.Timeout:
                    logger.warning(f"⏰ {service['name']}: Timeout")
                except Exception as e:
                    logger.warning(f"⚠️ {service['name']}: {str(e)[:100]}")
                
                # Small delay between services
                time.sleep(2)
            
            logger.error("❌ Could not verify location with any service")
            return {'verified': False, 'error': 'All location services failed'}
            
        except Exception as e:
            logger.error(f"💥 Error verifying proxy location: {e}")
            return {'verified': False, 'error': str(e)}
    
    def log_location_usage(self, account_id, proxy):
        """Log when and where account is used"""
        try:
            account_key = str(account_id)
            
            if account_key not in self.location_history:
                self.location_history[account_key] = []
            
            usage_record = {
                'timestamp': datetime.now().isoformat(),
                'city': proxy.get('verified_city', 'Unknown'),
                'region': proxy.get('verified_region', 'Unknown'),
                'ip': proxy.get('verified_ip', 'Unknown'),
                'session_id': proxy.get('session_id', 'Unknown'),
                'config_used': proxy.get('config_used', 'Unknown')
            }
            
            self.location_history[account_key].append(usage_record)
            
            # Keep only last 50 records per account
            if len(self.location_history[account_key]) > 50:
                self.location_history[account_key] = self.location_history[account_key][-50:]
            
            self.save_location_history()
            
            # Check for concerning location changes
            self.check_location_consistency(account_id)
            
        except Exception as e:
            logger.error(f"💥 Error logging location usage: {e}")
    
    def check_location_consistency(self, account_id):
        """Check if account has been used from consistent locations"""
        try:
            account_key = str(account_id)
            
            if account_key not in self.location_history:
                return
            
            history = self.location_history[account_key]
            
            if len(history) < 2:
                return
            
            # Check last 5 logins for consistency
            recent_history = history[-5:]
            locations = set()
            
            for record in recent_history:
                location = f"{record['city']}, {record['region']}"
                locations.add(location)
            
            if len(locations) > 1:
                logger.warning(f"⚠️ LOCATION INCONSISTENCY DETECTED for account {account_id}:")
                logger.warning(f"   📍 Recent locations: {', '.join(locations)}")
                logger.warning(f"   🚨 This could trigger video selfie verification!")
                
                # Log all recent locations for debugging
                for record in recent_history:
                    logger.warning(f"   🕐 {record['timestamp'][:19]}: {record['city']}, {record['region']}")
            else:
                logger.info(f"✅ Location consistency maintained for account {account_id}: {list(locations)[0]}")
                
        except Exception as e:
            logger.error(f"💥 Error checking location consistency: {e}")
    
    def get_account_location_report(self, account_id):
        """Get detailed location report for an account"""
        try:
            account_key = str(account_id)
            
            if account_key not in self.location_history:
                return {"error": "No location history found"}
            
            history = self.location_history[account_key]
            locations = {}
            
            for record in history:
                location = f"{record['city']}, {record['region']}"
                if location not in locations:
                    locations[location] = []
                locations[location].append(record['timestamp'])
            
            return {
                'account_id': account_id,
                'total_logins': len(history),
                'unique_locations': len(locations),
                'locations': locations,
                'consistency_risk': 'HIGH' if len(locations) > 2 else 'LOW' if len(locations) == 1 else 'MEDIUM'
            }
            
        except Exception as e:
            logger.error(f"💥 Error generating location report: {e}")
            return {"error": str(e)}
    
    # Keep existing test_proxy_connectivity for backward compatibility
    def test_proxy_connectivity(self, proxy, timeout=10):
        """Legacy method - calls robust version"""
        return self.test_proxy_connectivity_robust(proxy, timeout)
    
    def verify_proxy_location(self, proxy):
        """Legacy method - calls robust version"""
        return self.verify_proxy_location_robust(proxy)