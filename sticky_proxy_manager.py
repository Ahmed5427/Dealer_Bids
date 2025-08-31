from asyncio.log import logger
import json
import os
import hashlib
from datetime import datetime

class StickyProxyManager:
    """Manage consistent proxy locations per account to prevent video selfie verification"""
    
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
    
    def load_proxy_assignments(self):
        """Load existing proxy assignments"""
        try:
            if os.path.exists(self.proxy_assignments_file):
                with open(self.proxy_assignments_file, 'r') as f:
                    return json.load(f)
            return {}
        except:
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
        except:
            return {}
    
    def save_location_history(self):
        """Save location history"""
        try:
            with open(self.location_history_file, 'w') as f:
                json.dump(self.location_history, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving location history: {e}")
    
    def get_consistent_proxy_for_account(self, account_id):
        """Get a consistent proxy for a specific account - CRITICAL FOR AVOIDING VIDEO SELFIE"""
        try:
            account_key = str(account_id)
            
            # Check if account already has a proxy assignment
            if account_key in self.proxy_assignments:
                assigned_proxy = self.proxy_assignments[account_key]
                logger.info(f"🎯 Using CONSISTENT proxy for account {account_id}:")
                logger.info(f"   📍 Location: {assigned_proxy.get('verified_city', 'Unknown')}, {assigned_proxy.get('verified_region', 'Unknown')}")
                logger.info(f"   🔗 Session ID: {assigned_proxy.get('session_id', 'Unknown')}")
                
                # Verify proxy is still working
                if self.test_proxy_connectivity(assigned_proxy):
                    # Log location usage
                    self.log_location_usage(account_id, assigned_proxy)
                    return assigned_proxy
                else:
                    logger.warning(f"⚠️ Assigned proxy for account {account_id} no longer working - finding replacement")
            
            # Need to assign new proxy - use STICKY approach
            new_proxy = self.create_sticky_proxy_for_account(account_id)
            
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
    
    def create_sticky_proxy_for_account(self, account_id):
        """Create a sticky proxy session for an account"""
        try:
            # Create a consistent session ID based on account ID
            # This ensures the same account always gets the same session
            account_hash = hashlib.md5(str(account_id).encode()).hexdigest()[:8]
            session_id = f"sticky_{account_hash}_{account_id}"
            
            # Choose a consistent city for this account
            # Use account ID to deterministically select city
            us_cities = [
                {'city': 'phoenix', 'region': 'arizona'},
                {'city': 'scottsdale', 'region': 'arizona'},
                {'city': 'tempe', 'region': 'arizona'},
                {'city': 'mesa', 'region': 'arizona'},
                {'city': 'glendale', 'region': 'arizona'},
                # Add more cities but limit to avoid too much variation
                {'city': 'losangeles', 'region': 'california'},
                {'city': 'sandiego', 'region': 'california'},
                {'city': 'sanfrancisco', 'region': 'california'},
                {'city': 'miami', 'region': 'florida'},
                {'city': 'orlando', 'region': 'florida'}
            ]
            
            # Use account ID to consistently pick the same city
            city_index = int(account_id) % len(us_cities)
            selected_location = us_cities[city_index]
            
            # Create SOAX proxy with consistent location
            username = f"package-309866-country-us-region-{selected_location['region']}-city-{selected_location['city']}-sessionid-{session_id}"
            
            proxy = {
                'type': 'soax',
                'endpoint': getattr(self.config, 'SOAX_ENDPOINT', 'proxy.soax.com:5000'),
                'username': username,
                'password': self.config.SOAX_PASSWORD,
                'geo_country': 'United States',
                'geo_region': selected_location['region'].title(),
                'geo_city': selected_location['city'].title(),
                'session_id': session_id,
                'account_id': account_id,
                'is_sticky': True,
                'created_at': datetime.now().isoformat()
            }
            
            logger.info(f"🎯 Creating STICKY proxy for account {account_id}:")
            logger.info(f"   📍 Consistent Location: {selected_location['city'].title()}, {selected_location['region'].title()}")
            logger.info(f"   🔗 Session ID: {session_id}")
            
            # Test connectivity
            if self.test_proxy_connectivity(proxy):
                # Try to get location verification
                verification = self.verify_proxy_location(proxy)
                if verification.get('verified'):
                    proxy.update({
                        'verified_ip': verification['ip'],
                        'verified_country': verification['country'],
                        'verified_region': verification['region'],
                        'verified_city': verification['city'],
                        'us_verified': True
                    })
                else:
                    # Even if verification fails, keep the assigned location for consistency
                    proxy.update({
                        'verified_ip': 'Unknown',
                        'verified_country': 'US (Assigned)',
                        'verified_region': selected_location['region'].title(),
                        'verified_city': selected_location['city'].title(),
                        'us_verified': False
                    })
                
                return proxy
            else:
                logger.error(f"❌ Sticky proxy connectivity test failed for account {account_id}")
                return None
                
        except Exception as e:
            logger.error(f"💥 Error creating sticky proxy: {e}")
            return None
    
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
                'session_id': proxy.get('session_id', 'Unknown')
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
    
    def test_proxy_connectivity(self, proxy, timeout=10):
        """Test if proxy is working"""
        try:
            import requests
            
            proxy_config = None
            if proxy and proxy.get('username') and proxy.get('password'):
                proxy_url = f"http://{proxy['username']}:{proxy['password']}@{proxy['endpoint']}"
                proxy_config = {
                    'http': proxy_url,
                    'https': proxy_url
                }
            
            response = requests.get(
                'http://httpbin.org/ip',
                proxies=proxy_config,
                timeout=timeout,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            )
            
            return response.status_code == 200
            
        except:
            return False
    
    def verify_proxy_location(self, proxy):
        """Verify proxy location"""
        try:
            import requests
            
            proxy_config = None
            if proxy and proxy.get('username') and proxy.get('password'):
                proxy_url = f"http://{proxy['username']}:{proxy['password']}@{proxy['endpoint']}"
                proxy_config = {
                    'http': proxy_url,
                    'https': proxy_url
                }
            
            response = requests.get(
                'http://ip-api.com/json/',
                proxies=proxy_config,
                timeout=10,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'verified': True,
                    'ip': data.get('query', 'Unknown'),
                    'country': data.get('country', 'Unknown'),
                    'region': data.get('regionName', 'Unknown'),
                    'city': data.get('city', 'Unknown')
                }
            
            return {'verified': False}
            
        except:
            return {'verified': False}

# Update your enhanced_warmup.py to use sticky proxies
def get_working_us_proxy_for_warmup(self, account=None):
    """Get working US proxy with STICKY location for account"""
    try:
        logger.info("🎯 Getting STICKY working US proxy for warmup...")
        
        # Initialize sticky proxy manager if not exists
        if not hasattr(self, 'sticky_proxy_manager'):
            self.sticky_proxy_manager = StickyProxyManager(self.config, self.db)
        
        account_id = account.get('account_id') if account else None
        
        if account_id:
            # Get consistent proxy for this specific account
            proxy = self.sticky_proxy_manager.get_consistent_proxy_for_account(account_id)
            
            if proxy:
                logger.info(f"✅ STICKY proxy obtained for account {account_id}:")
                logger.info(f"   📍 Consistent Location: {proxy.get('verified_city', 'Unknown')}, {proxy.get('verified_region', 'Unknown')}")
                logger.info(f"   🔒 Same location will be used for all future sessions")
                return proxy
        
        # Fallback to original method if account_id not provided
        logger.warning("⚠️ No account ID provided - using non-sticky proxy (NOT RECOMMENDED)")
        return self.get_soax_proxy_with_fallback_warmup()
        
    except Exception as e:
        logger.error(f"💥 Error getting sticky proxy for warmup: {e}")
        return None

# Update the main warmup method to pass account info
def run_enhanced_warmup_cycle_with_facebook_proof(self, account):
    """Enhanced warmup with STICKY proxy support"""
    try:
        account_id = account['account_id']
        
        logger.info(f"🚀 Starting warmup for account {account_id} with STICKY PROXY")
        logger.info("🎯 CRITICAL: Using consistent location to prevent video selfie verification")
        
        # Get STICKY proxy for this specific account
        proxy_info = self.get_working_us_proxy_for_warmup(account)  # Pass account object
        
        if not proxy_info:
            logger.error(f"❌ No sticky proxy available for account {account_id}")
            return False
        
        # Rest of your existing warmup code...
        # The key difference is now each account will ALWAYS use the same location
        
        # Continue with existing warmup process
        login_credential = self.determine_login_credential(account)
        password = account['password']
        twofa_secret = account.get('twofa_secret')
        
        if not self.setup_browser_with_facebook_proof_proxy(proxy_info):
            logger.error(f"❌ Browser setup failed for account {account_id}")
            return False
        
        login_success = self.login_facebook_robust(login_credential, password, twofa_secret)
        
        if login_success:
            logger.info(f"✅ STICKY PROXY LOGIN SUCCESS for account {account_id}")
            logger.info("🎯 Consistent location maintained - reduced checkpoint risk")
            
            # Continue with warmup activities...
            success = self.enhanced_warmup_cycle(account)
            self.cleanup_browser()
            return success
        else:
            logger.error(f"❌ Login failed for account {account_id} despite sticky proxy")
            self.cleanup_browser()
            return False
            
    except Exception as e:
        logger.error(f"💥 Error in sticky proxy warmup: {e}")
        self.cleanup_browser()
        return False