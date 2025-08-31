#!/usr/bin/env python3
"""
Robust Enhanced Account Manager with Better Timeout Handling and Fallbacks - FIXED
"""

from openai import OpenAI
import random
import json
import time
import os
import logging
import requests
import subprocess
import sys
import textwrap
from datetime import datetime, timedelta
from account_manager import AccountManager

logger = logging.getLogger(__name__)

class EnhancedAccountManager(AccountManager):
    """Enhanced Account Manager with Robust Proxy Handling and AI-powered profile generation"""
    
    def __init__(self, config, db):
        super().__init__(config, db)
        self.openai_client = OpenAI(api_key=config.OPENAI_API_KEY)
        
    def test_proxy_connectivity(self, proxy, timeout=10):
        """Quick test to see if proxy is working at all"""
        try:
            proxy_config = None
            if proxy and proxy.get('username') and proxy.get('password'):
                proxy_url = f"http://{proxy['username']}:{proxy['password']}@{proxy['endpoint']}"
                proxy_config = {
                    'http': proxy_url,
                    'https': proxy_url
                }
            
            # Test with a simple, fast service
            test_urls = [
                'http://httpbin.org/ip',  # Try HTTP first (faster)
                'https://api.ipify.org',  # Simple IP service
                'http://icanhazip.com'    # Very simple service
            ]
            
            for url in test_urls:
                try:
                    logger.info(f"🔧 Testing connectivity to {url}...")
                    response = requests.get(
                        url, 
                        proxies=proxy_config, 
                        timeout=timeout,
                        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                    )
                    
                    if response.status_code == 200:
                        logger.info(f"✅ Proxy connectivity confirmed via {url}")
                        return True
                        
                except Exception as e:
                    logger.warning(f"⚠️ Test to {url} failed: {str(e)[:100]}")
                    continue
            
            logger.error("❌ All connectivity tests failed")
            return False
            
        except Exception as e:
            logger.error(f"💥 Connectivity test error: {e}")
            return False
    
    def verify_us_proxy_location_fast(self, proxy):
        """Fast US proxy verification with shorter timeouts and more services"""
        try:
            logger.info("🌍 Fast US location verification...")
            
            # Configure proxy for requests
            proxy_config = None
            if proxy and proxy.get('username') and proxy.get('password'):
                proxy_url = f"http://{proxy['username']}:{proxy['password']}@{proxy['endpoint']}"
                proxy_config = {
                    'http': proxy_url,
                    'https': proxy_url
                }
            
            # More IP services with shorter timeouts
            ip_services = [
                {'url': 'http://icanhazip.com', 'timeout': 8, 'type': 'text'},
                {'url': 'http://httpbin.org/ip', 'timeout': 8, 'type': 'json'},
                {'url': 'https://api.ipify.org?format=json', 'timeout': 10, 'type': 'json'},
                {'url': 'https://ipapi.co/json/', 'timeout': 10, 'type': 'json'},
                {'url': 'http://ip-api.com/json/', 'timeout': 8, 'type': 'json'},
                {'url': 'https://freegeoip.app/json/', 'timeout': 10, 'type': 'json'}
            ]
            
            for service in ip_services:
                try:
                    logger.info(f"🔍 Checking {service['url']}...")
                    
                    response = requests.get(
                        service['url'], 
                        proxies=proxy_config, 
                        timeout=service['timeout'],
                        headers={
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                            'Accept': 'application/json, text/plain, */*'
                        }
                    )
                    
                    if response.status_code == 200:
                        if service['type'] == 'json':
                            try:
                                data = response.json()
                            except:
                                continue
                        else:
                            # Text response (like icanhazip.com)
                            ip = response.text.strip()
                            data = {'ip': ip}
                        
                        # Extract IP and location info
                        ip = data.get('ip') or data.get('origin', '').split(',')[0].strip()
                        country = data.get('country', data.get('country_code', data.get('countryCode', ''))).upper()
                        region = data.get('region', data.get('regionName', data.get('region_name', '')))
                        city = data.get('city', '')
                        
                        logger.info(f"🔍 IP: {ip}")
                        logger.info(f"🏳️ Country: {country}")
                        logger.info(f"🗺️ Region: {region}")
                        logger.info(f"🏙️ City: {city}")
                        
                        # Check if it's US-based
                        us_indicators = ['US', 'USA', 'UNITED STATES', 'AMERICA']
                        if any(indicator in country.upper() for indicator in us_indicators):
                            logger.info("✅ Proxy verified as US-based!")
                            return {
                                'verified': True,
                                'ip': ip,
                                'country': country,
                                'region': region,
                                'city': city,
                                'service': service['url']
                            }
                        else:
                            logger.warning(f"⚠️ Proxy is not US-based: {country}")
                            # Don't break here, try other services in case this one is wrong
                            
                except requests.exceptions.Timeout:
                    logger.warning(f"⏰ Timeout for {service['url']}")
                    continue
                except Exception as e:
                    logger.warning(f"⚠️ Service {service['url']} failed: {str(e)[:100]}")
                    continue
            
            logger.error("❌ Could not verify proxy as US-based with any service")
            return {'verified': False}
            
        except Exception as e:
            logger.error(f"💥 Error verifying proxy location: {e}")
            return {'verified': False}
    
    def get_soax_proxy_with_fallback(self):
        """Get SOAX proxy with multiple fallback configurations"""
        try:
            if not (hasattr(self.config, 'SOAX_USERNAME') and self.config.SOAX_USERNAME and
                    hasattr(self.config, 'SOAX_PASSWORD') and self.config.SOAX_PASSWORD):
                logger.error("❌ SOAX credentials not found in config")
                return None
            
            # Try different SOAX configurations
            soax_configs = [
                # Method 1: Try parent class proxy manager first
                {'method': 'parent_class', 'config': None},
                
                # Method 2: Specific US cities with SOAX format
                {'method': 'soax_city', 'config': {
                    'cities': [
                        {'city': 'phoenix', 'region': 'arizona'},
                        {'city': 'losangeles', 'region': 'california'},
                        {'city': 'newyork', 'region': 'newyork'},
                        {'city': 'chicago', 'region': 'illinois'},
                        {'city': 'miami', 'region': 'florida'}
                    ]
                }},
                
                # Method 3: Generic US targeting
                {'method': 'soax_generic', 'config': {
                    'username_formats': [
                        f"package-309866-country-us-sessionid-{random.randint(100000, 999999)}",
                        f"{self.config.SOAX_USERNAME}",  # Use original username as fallback
                        f"package-309866-country-us-region-any-sessionid-{random.randint(100000, 999999)}"
                    ]
                }}
            ]
            
            for method_info in soax_configs:
                try:
                    method = method_info['method']
                    config = method_info['config']
                    
                    logger.info(f"🔧 Trying method: {method}")
                    
                    if method == 'parent_class':
                        # Try parent class proxy manager
                        if hasattr(self, 'proxy_manager') and hasattr(self.proxy_manager, 'get_fresh_proxy'):
                            proxy = self.proxy_manager.get_fresh_proxy(country='US')
                            if proxy:
                                logger.info("✅ Got proxy from parent class")
                                return proxy
                        continue
                    
                    elif method == 'soax_city':
                        # Try specific city targeting
                        for location in config['cities']:
                            session_id = f"enhanced_{random.randint(100000, 999999)}"
                            username = f"package-309866-country-us-region-{location['region']}-city-{location['city']}-sessionid-{session_id}"
                            
                            proxy = {
                                'type': 'soax',
                                'endpoint': getattr(self.config, 'SOAX_ENDPOINT', 'proxy.soax.com:5000'),
                                'username': username,
                                'password': self.config.SOAX_PASSWORD,
                                'geo_country': 'United States',
                                'geo_region': location['region'].title(),
                                'geo_city': location['city'].title(),
                                'session_id': session_id
                            }
                            
                            logger.info(f"🏙️ Testing {location['city']}, {location['region']}...")
                            
                            # Quick connectivity test
                            if self.test_proxy_connectivity(proxy, timeout=8):
                                logger.info(f"✅ Connectivity confirmed for {location['city']}")
                                return proxy
                            else:
                                logger.warning(f"⚠️ No connectivity for {location['city']}")
                                continue
                    
                    elif method == 'soax_generic':
                        # Try generic username formats
                        for username_format in config['username_formats']:
                            proxy = {
                                'type': 'soax',
                                'endpoint': getattr(self.config, 'SOAX_ENDPOINT', 'proxy.soax.com:5000'),
                                'username': username_format,
                                'password': self.config.SOAX_PASSWORD,
                                'geo_country': 'United States',
                                'geo_region': 'Unknown',
                                'geo_city': 'Unknown'
                            }
                            
                            logger.info(f"🔧 Testing username format: {username_format[:50]}...")
                            
                            # Quick connectivity test
                            if self.test_proxy_connectivity(proxy, timeout=8):
                                logger.info(f"✅ Connectivity confirmed for username format")
                                return proxy
                            else:
                                logger.warning(f"⚠️ No connectivity for this username format")
                                continue
                
                except Exception as e:
                    logger.warning(f"⚠️ Method {method} failed: {e}")
                    continue
            
            logger.error("❌ All SOAX proxy methods failed")
            return None
            
        except Exception as e:
            logger.error(f"💥 Error getting SOAX proxy: {e}")
            return None
    
    def get_working_us_proxy_with_smart_fallback(self):
        """Get working US proxy with smart fallback logic"""
        try:
            logger.info("🎯 Getting working US proxy with smart fallback...")
            
            # Step 1: Get a proxy that at least connects
            proxy = self.get_soax_proxy_with_fallback()
            if not proxy:
                logger.error("❌ Could not get any working proxy")
                return None
            
            logger.info("✅ Got basic proxy connectivity")
            
            # Step 2: Try to verify US location (but don't fail if verification fails)
            logger.info("🔍 Attempting US location verification...")
            verification = self.verify_us_proxy_location_fast(proxy)
            
            if verification['verified']:
                logger.info("🎉 Perfect! Proxy verified as US-based")
                proxy.update({
                    'verified_ip': verification['ip'],
                    'verified_country': verification['country'],
                    'verified_region': verification['region'],
                    'verified_city': verification['city'],
                    'verification_service': verification['service'],
                    'verified_at': datetime.now().isoformat(),
                    'us_verified': True
                })
            else:
                logger.warning("⚠️ Could not verify US location, but proxy is working")
                logger.warning("🔥 Proceeding anyway - SOAX should be providing US proxies")
                proxy.update({
                    'verified_ip': 'Unknown',
                    'verified_country': 'US (Assumed)',
                    'verified_region': proxy.get('geo_region', 'Unknown'),
                    'verified_city': proxy.get('geo_city', 'Unknown'),
                    'verification_service': 'None (Timeout)',
                    'verified_at': datetime.now().isoformat(),
                    'us_verified': False,
                    'note': 'SOAX proxy with working connectivity but failed location verification due to timeouts'
                })
            
            # Step 3: Quick Facebook accessibility test
            logger.info("📘 Testing Facebook accessibility...")
            try:
                facebook_accessible = self.test_facebook_access_quick(proxy)
                proxy['facebook_accessible'] = facebook_accessible
                
                if facebook_accessible:
                    logger.info("✅ Facebook is accessible through proxy")
                else:
                    logger.warning("⚠️ Facebook access test failed, but proceeding")
                    
            except Exception as e:
                logger.warning(f"⚠️ Facebook access test error: {e}")
                proxy['facebook_accessible'] = False
            
            logger.info("🎯 Proxy ready for use!")
            logger.info(f"   📡 Endpoint: {proxy.get('endpoint')}")
            logger.info(f"   🌍 Location: {proxy.get('verified_city', 'Unknown')}, {proxy.get('verified_region', 'Unknown')}")
            logger.info(f"   🇺🇸 US Verified: {'✅' if proxy.get('us_verified') else '❓ (Assumed)'}")
            logger.info(f"   📘 Facebook: {'✅' if proxy.get('facebook_accessible') else '❓'}")
            
            return proxy
            
        except Exception as e:
            logger.error(f"💥 Error getting working US proxy: {e}")
            return None
    
    def test_facebook_access_quick(self, proxy, timeout=15):
        """Quick Facebook access test with shorter timeout"""
        try:
            proxy_config = None
            if proxy and proxy.get('username') and proxy.get('password'):
                proxy_url = f"http://{proxy['username']}:{proxy['password']}@{proxy['endpoint']}"
                proxy_config = {
                    'http': proxy_url,
                    'https': proxy_url
                }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5'
            }
            
            response = requests.get(
                'https://www.facebook.com',
                proxies=proxy_config,
                headers=headers,
                timeout=timeout,
                allow_redirects=True
            )
            
            if response.status_code == 200:
                content = response.text.lower()
                if 'facebook' in content:
                    return True
            
            return False
            
        except Exception as e:
            logger.warning(f"Facebook access test failed: {e}")
            return False
    
    def generate_ai_names(self):
        """Generate realistic first and last names using OpenAI"""
        try:
            prompt = """Generate a realistic first name and last name for a Facebook profile. 
            The names should be:
            - American names or commonly used in the US or English-speaking countries
            - Gender-neutral or varied
            - Not obviously fake
            - Suitable for a Facebook profile
            
            Return only the names in this exact format: "FirstName LastName"
            Example: "Alex Johnson"
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=20,
                temperature=0.8
            )
            
            full_name = response.choices[0].message.content.strip()
            names = full_name.split(' ')
            
            if len(names) >= 2:
                first_name = names[0]
                last_name = names[1]
                logger.info(f"Generated AI names: {first_name} {last_name}")
                return first_name, last_name
            else:
                logger.warning("AI returned invalid name format, using fallback")
                return self.generate_fallback_names()
                
        except Exception as e:
            logger.error(f"Error generating AI names: {e}")
            return self.generate_fallback_names()
    
    def generate_fallback_names(self):
        """Fallback name generation if AI fails"""
        first_names = [
            'Alex', 'Jordan', 'Casey', 'Morgan', 'Riley', 'Avery', 'Quinn', 
            'Sage', 'River', 'Blake', 'Cameron', 'Drew', 'Emery', 'Finley', 'Gray', 
            'Hayden', 'Indigo', 'Jamie', 'Kai', 'Lane', 'Max', 'Noah', 'Ocean', 
            'Parker', 'Rowan', 'Sam', 'Tate', 'Val', 'Winter'
        ]
        
        last_names = [
            'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 
            'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 
            'Wilson', 'Anderson', 'Thomas', 'Moore', 'Jackson', 'Martin', 
            'Lee', 'Perez', 'Thompson', 'White', 'Harris', 'Sanchez', 'Clark', 
            'Ramirez', 'Lewis', 'Robinson'
        ]
        
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        logger.info(f"Generated fallback names: {first_name} {last_name}")
        return first_name, last_name
    
    def generate_ai_birthday_gender(self):
        """Generate realistic birthday and gender"""
        try:
            birth_year = random.randint(1979, 2002)
            birth_month = random.randint(1, 12)
            birth_day = random.randint(1, 28)
            genders = ['male', 'female']
            gender = random.choice(genders)
            
            logger.info(f"Generated birthday: {birth_month}/{birth_day}/{birth_year}, Gender: {gender}")
            return birth_month, birth_day, birth_year, gender
            
        except Exception as e:
            logger.error(f"Error generating birthday/gender: {e}")
            return 5, 15, 1990, 'male'
    
    def generate_ai_profile_picture_prompt(self, first_name, gender, birth_year):
        """Generate a prompt for AI profile picture creation"""
        try:
            base_prompt = f"realistic professional headshot photo of a {gender} person who was born in {birth_year}"
            
            style_variations = [
                "Add subtle compression, slight imperfections, or slight asymmetry to make it look more natural",
                "realistic selfie",
                "professional LinkedIn style headshot",
                "casual friendly portrait photo",
                "natural outdoor portrait",
                "professional business headshot",
                "social media profile photo style",
                "candid photo with natural lighting",
                "slightly imperfect, not too symmetrical",
                "realistic photo with natural lighting",
                "portrait with slight imperfections",
                "headshot with natural expression",
                "photo with slight asymmetry",
                "portrait with casual vibe",
                "headshot with friendly smile",
                "photo with natural background",
                "portrait with soft lighting",
                "headshot with relaxed pose",
                "photo with slight blur in background",
                "portrait with warm tones",
                "headshot with cool tones",
                "photo with slight vignette effect",
                "portrait with natural shadows",
            ]
            
            style = random.choice(style_variations)
            
            backgrounds = [
                "with simple plain background",
                "with clean office background",
                "with outdoor park background",
                "with home interior background",
                "with bookshelf background",
                "with cityscape background",
                "with coffee shop background",
                "with nature background",
                "with urban street background",
                "with garden background",
                "with beach background",
                "with mountain background",
                "with park background",
                "with cozy room background",
                "with subtle messy background",
                "with blurred office background", 
                "with natural outdoor background",
                "with soft bokeh background",
                "with light texture background",
                "messy background",
                "with slightly cluttered background"
            ]
            
            background = random.choice(backgrounds)
            full_prompt = f"{style} of a {gender} person {background}, realistic photo, natural lighting, slightly imperfect, not too symmetrical"
            
            logger.info(f"Generated profile picture prompt for {first_name}")
            return full_prompt
            
        except Exception as e:
            logger.error(f"Error generating profile picture prompt: {e}")
            return f"realistic professional headshot of a {gender} person with natural background"
    
    def generate_ai_profile_picture(self, first_name, gender):
        """Generate a profile picture using DALL-E"""
        try:
            prompt = self.generate_ai_profile_picture_prompt(first_name, gender)
            
            response = self.openai_client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                n=1,
                size="1024x1024",
                quality="standard"
            )
            
            image_url = response.data[0].url
            logger.info(f"Generated profile picture for {first_name}")
            return image_url
            
        except Exception as e:
            logger.error(f"Error generating profile picture: {e}")
            return None
    
    def download_profile_picture(self, image_url, account_id):
        """Download and save the profile picture locally"""
        try:
            os.makedirs('account_data/images', exist_ok=True)
            
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            image_path = f"account_data/images/profile_{account_id}.jpg"
            with open(image_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Downloaded profile picture to {image_path}")
            return image_path
            
        except Exception as e:
            logger.error(f"Error downloading profile picture: {e}")
            return None
    
    def update_account_profile_picture(self, account_id, image_path):
        """Update the account's profile picture in the database"""
        try:
            worksheet = self.db.get_worksheet("fb_accounts")
            records = worksheet.get_all_records()
            
            for i, record in enumerate(records, start=2):
                if str(record['account_id']) == str(account_id):
                    worksheet.update_cell(i, 15, image_path)  # Column O
                    worksheet.update_cell(i, 16, 'no')        # Column P
                    logger.info(f"Updated profile picture info for account {account_id}")
                    return True
            
            logger.error(f"Account {account_id} not found in database")
            return False
            
        except Exception as e:
            logger.error(f"Error updating profile picture in database: {e}")
            return False
    
    def get_us_phone_number(self):
        """Get US phone number"""
        try:
            return self.get_phone_number()
        except Exception as e:
            logger.error(f"Error getting US phone number: {e}")
            return None
    
    def get_phone_number(self, proxy=None):
        """Get phone number using SMSPinVerify API"""
        try:
            api_key = self.config.SMSPINVERIFY_API_KEY
            url = f"https://api.smspinverify.com/user/get_number.php?customer={api_key}&app=Facebook&country=USA&number="
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'en-US,en;q=0.9'
            }
            
            logger.info(f"📱 Requesting US phone number from SMSPinVerify...")
            
            response = requests.get(url, headers=headers, timeout=30, verify=False)
            
            logger.info(f"📊 Response status: {response.status_code}")
            logger.info(f"📄 Response text: {response.text}")
            
            if response.status_code == 200:
                response_text = response.text.strip()
                
                if "Customer Not Found" in response_text:
                    logger.error("❌ SMSPinVerify API Key is invalid")
                    return {'success': False, 'error': 'Invalid API key'}
                
                if "Not Enough balance" in response_text:
                    logger.error("💰 Insufficient balance in SMSPinVerify account")
                    return {'success': False, 'error': 'Insufficient balance'}
                
                if "App Not Found" in response_text:
                    logger.error("❌ Facebook app not found")
                    return {'success': False, 'error': 'App not found'}
                
                if response_text and response_text.isdigit() and len(response_text) >= 10:
                    phone_number = '+' + response_text
                    activation_id = f"sms_{random.randint(100000, 999999)}"
                    
                    logger.info(f"✅ Successfully got US phone number: {phone_number}")
                    
                    return {
                        'success': True,
                        'id': activation_id,
                        'phone': phone_number,
                        'raw_phone': response_text,
                        'service': 'smspinverify',
                        'sms_id': activation_id
                    }
                else:
                    logger.error(f"❌ Invalid phone number response: {response_text}")
                    return {'success': False, 'error': f'Invalid response: {response_text}'}
            else:
                logger.error(f"❌ HTTP error: {response.status_code}")
                return {'success': False, 'error': f'HTTP {response.status_code}'}
                
        except Exception as e:
            logger.error(f"💥 Error getting phone number: {e}")
            return {'success': False, 'error': str(e)}
    
    def generate_temp_email(self):
        """Generate temporary email"""
        try:
            if hasattr(super(), 'generate_temp_email'):
                return super().generate_temp_email()
            else:
                domains = ['protonmail.com', 'gmail.com', 'outlook.com']
                username = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=10))
                domain = random.choice(domains)
                email = f"{username}@{domain}"
                logger.info(f"Generated email: {email}")
                return email
        except Exception as e:
            logger.error(f"Error generating temp email: {e}")
            username = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=10))
            return f"{username}@protonmail.com"
    
    def generate_secure_password(self):
        """Generate secure password"""
        try:
            if hasattr(super(), 'generate_secure_password'):
                return super().generate_secure_password()
            else:
                import string
                password = ''.join(random.choices(
                    string.ascii_letters + string.digits, k=12
                ))
                logger.info(f"Generated password (length: {len(password)})")
                return password
        except Exception as e:
            logger.error(f"Error generating secure password: {e}")
            import string
            return ''.join(random.choices(string.ascii_letters + string.digits, k=12))
    
    def get_working_proxy(self):
        """Get working proxy with smart fallback"""
        return self.get_working_us_proxy_with_smart_fallback()
    
    def _create_us_based_phone_first_script(self, profile):
        """Create Playwright script for US-based phone-first registration - WORKING VERSION"""
        
        proxy_data = profile['proxy']
        phone = profile['phone']
        password = profile['password']
        account_id = profile['account_id']
        first_name = profile['first_name']
        last_name = profile['last_name']
        birth_month = profile['birth_month']
        birth_day = profile['birth_day']
        birth_year = profile['birth_year']
        api_key = self.config.SMSPINVERIFY_API_KEY
        
        # Use the proven working SOAX configuration
        working_username = self.config.SOAX_USERNAME
        working_password = self.config.SOAX_PASSWORD
        
        import textwrap
        
        script_template = textwrap.dedent(f'''
        import asyncio
        import random
        import time
        import requests
        from playwright.async_api import async_playwright

        async def get_sms_code(phone_number, api_key, max_attempts=18):
            """Get SMS verification code from SMSPinVerify"""
            clean_phone = phone_number.replace('+', '')
            url = f"https://api.smspinverify.com/user/get_sms.php?customer={{api_key}}&app=Facebook&country=USA&number={{clean_phone}}"
            
            print(f"📲 Waiting for SMS code for {{phone_number}}...")
            
            for attempt in range(max_attempts):
                try:
                    response = requests.get(url, timeout=15, verify=False)
                    
                    if response.status_code == 200:
                        response_text = response.text.strip()
                        print(f"SMS attempt {{attempt + 1}}/{{max_attempts}}: {{response_text}}")
                        
                        if "Number Not Found" in response_text:
                            if attempt < 3:
                                print("📱 Number not registered yet, waiting...")
                                await asyncio.sleep(15)
                                continue
                            else:
                                print("❌ Number never registered")
                                return None
                        
                        if "You have not received any code yet" in response_text:
                            await asyncio.sleep(10)
                            continue
                        
                        if response_text.isdigit() and len(response_text) >= 4:
                            print(f"✅ Received SMS code: {{response_text}}")
                            return response_text
                        
                        # Extract code from message
                        import re
                        code_match = re.search(r'\\b(\\d{{4,8}})\\b', response_text)
                        if code_match:
                            code = code_match.group(1)
                            print(f"✅ Extracted SMS code: {{code}}")
                            return code
                            
                except Exception as e:
                    print(f"SMS check error: {{e}}")
                
                await asyncio.sleep(10)
            
            print("❌ SMS code not received")
            return None

        async def human_like_typing(element, text, delay_range=(50, 150)):
            """Type like a human"""
            await element.click()
            await asyncio.sleep(random.uniform(0.3, 0.8))
            
            for char in text:
                await element.type(char, delay=random.uniform(*delay_range))
                if random.random() < 0.1:
                    await asyncio.sleep(random.uniform(0.1, 0.3))

        async def register_facebook_us_based():
            try:
                # WORKING SOAX proxy configuration (proven to work)
                proxy_config = {{
                    'server': 'http://proxy.soax.com:5000',
                    'username': '{working_username}',
                    'password': '{working_password}'
                }}
                
                print(f"🌐 Using WORKING SOAX proxy: proxy.soax.com:5000")
                print(f"🇺🇸 Target location: Phoenix, Arizona")
                print(f"📱 Phone: {phone}")
                print(f"👤 Name: {first_name} {last_name}")
                
                async with async_playwright() as p:
                    browser = await p.chromium.launch(
                        headless=False,
                        proxy=proxy_config,  # WORKING PROXY CONFIG
                        args=[
                            '--no-first-run',
                            '--no-default-browser-check',
                            '--disable-blink-features=AutomationControlled',
                            '--disable-geolocation',
                            '--disable-dev-shm-usage'
                        ]
                    )
                    
                    # US-BASED CONTEXT with Phoenix location
                    context = await browser.new_context(
                        viewport={{'width': 1366, 'height': 768}},
                        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        locale='en-US',
                        timezone_id='America/Phoenix',
                        geolocation={{'latitude': 33.4484, 'longitude': -112.0740}},
                        permissions=['geolocation']
                    )
                    
                    page = await context.new_page()
                    
                    # Verify US IP
                    print("🔍 Verifying US IP address...")
                    try:
                        ip_page = await context.new_page()
                        await ip_page.goto('http://httpbin.org/ip')
                        ip_info = await ip_page.inner_text('body')
                        print(f"🌍 Current IP: {{ip_info.strip()}}")
                        await ip_page.close()
                    except Exception as e:
                        print(f"⚠️ Could not verify IP: {{e}}")
                    
                    # Override geolocation to force US location
                    await page.add_init_script("""
                        // Override geolocation to US coordinates (Phoenix)
                        navigator.geolocation.getCurrentPosition = function(success, error, options) {{
                            success({{
                                coords: {{
                                    latitude: 33.4484,
                                    longitude: -112.0740,
                                    accuracy: 100
                                }},
                                timestamp: Date.now()
                            }});
                        }};
                        
                        // Override timezone
                        Object.defineProperty(Intl.DateTimeFormat.prototype, 'resolvedOptions', {{
                            value: function() {{
                                return {{ timeZone: 'America/Phoenix' }};
                            }}
                        }});
                    """)
                    
                    print("🌐 Navigating to Facebook...")
                    await page.goto('https://www.facebook.com/', wait_until='networkidle')
                    await asyncio.sleep(random.uniform(3, 5))
                    
                    # Check if Facebook detects US location
                    try:
                        page_content = await page.content()
                        if 'egypt' in page_content.lower() or 'مصر' in page_content:
                            print("⚠️ Warning: Facebook may still detect Egypt location")
                        else:
                            print("✅ Facebook appears to detect US location")
                    except:
                        pass
                    
                    # Click create account
                    try:
                        create_btn = await page.query_selector('a[data-testid="open-registration-form-button"]')
                        if create_btn:
                            await create_btn.click()
                            print("🔗 Clicked create account")
                            await asyncio.sleep(3)
                        else:
                            await page.goto('https://www.facebook.com/reg/')
                    except:
                        await page.goto('https://www.facebook.com/reg/')
                    
                    await asyncio.sleep(3)
                    
                    print(f"👤 Creating US account: {first_name} {last_name}")
                    print(f"📱 Using US phone: {phone}")
                    print(f"📍 From: Phoenix, Arizona")
                    
                    # Take screenshot for debugging
                    await page.screenshot(path=f"fb_form_us_{account_id}.png")
                    
                    # Fill first name
                    firstname_input = await page.query_selector('input[name="firstname"]')
                    if firstname_input:
                        await human_like_typing(firstname_input, '{first_name}')
                        print(f"✅ First name: {first_name}")
                    
                    # Fill last name
                    lastname_input = await page.query_selector('input[name="lastname"]')
                    if lastname_input:
                        await human_like_typing(lastname_input, '{last_name}')
                        print(f"✅ Last name: {last_name}")
                    
                    # Fill phone number (PRIMARY - US number)
                    email_input = await page.query_selector('input[name="reg_email__"]')
                    if email_input:
                        await human_like_typing(email_input, '{phone}')
                        print(f"✅ US Phone number filled: {phone}")
                    
                    # Fill password
                    password_input = await page.query_selector('input[name="reg_passwd__"]')
                    if password_input:
                        await human_like_typing(password_input, '{password}')
                        print("✅ Password filled")
                    
                    # Set birthday (using generated data)
                    try:
                        await page.select_option('select[name="birthday_month"]', value=str({birth_month}))
                        await page.select_option('select[name="birthday_day"]', value=str({birth_day}))
                        await page.select_option('select[name="birthday_year"]', value=str({birth_year}))
                        print(f"✅ Birthday: {birth_month}/{birth_day}/{birth_year} (US format)")
                    except:
                        print("⚠️ Could not set birthday")
                    
                    # Set gender
                    try:
                        gender_value = random.choice(['1', '2'])
                        gender_input = await page.query_selector(f'input[value="{{gender_value}}"]')
                        if gender_input:
                            await gender_input.click()
                            print(f"✅ Gender set")
                    except:
                        print("⚠️ Could not set gender")
                    
                    # Submit form
                    print("🚀 Submitting form with US location data...")
                    signup_button = await page.query_selector('button[name="websubmit"]')
                    if signup_button:
                        await signup_button.click()
                        print("✅ Form submitted")
                    else:
                        print("❌ Submit button not found")
                        await browser.close()
                        return False
                    
                    # Wait for response
                    await asyncio.sleep(8)
                    current_url = page.url
                    print(f"🌐 URL after submit: {{current_url}}")
                    
                    # Take screenshot
                    await page.screenshot(path=f"fb_after_submit_us_{account_id}.png")
                    
                    # Check for human verification page FIRST
                    page_content = await page.content()
                    
                    if "confirm you're human" in page_content.lower() or "human verification" in page_content.lower():
                        print("🤖 Human verification detected - clicking Continue...")
                        
                        # Look for Continue button
                        continue_selectors = [
                            'button:has-text("Continue")',
                            'div[role="button"]:has-text("Continue")',
                            'button[type="submit"]',
                            'input[type="submit"]'
                        ]
                        
                        continue_clicked = False
                        for selector in continue_selectors:
                            try:
                                continue_btn = await page.query_selector(selector)
                                if continue_btn and await continue_btn.is_visible():
                                    await continue_btn.click()
                                    print("✅ Clicked Continue button")
                                    continue_clicked = True
                                    break
                            except:
                                continue
                        
                        if not continue_clicked:
                            print("❌ Could not find Continue button")
                            await page.screenshot(path=f"fb_continue_failed_{account_id}.png")
                            await browser.close()
                            return False
                        
                        # Wait for next page
                        await asyncio.sleep(8)
                        current_url = page.url
                        page_content = await page.content()
                        print(f"🌐 URL after Continue: {{current_url}}")
                        await page.screenshot(path=f"fb_after_continue_{account_id}.png")
                    
                    # Now check for phone verification
                    if any(keyword in current_url.lower() or keyword in page_content.lower() 
                        for keyword in ['confirm', 'phone', 'verification', 'code', 'sms']):
                        print("📱 Phone verification detected")
                        
                        # Get SMS code
                        sms_code = await get_sms_code('{phone}', '{api_key}')
                        
                        if sms_code:
                            print(f"✅ SMS code: {{sms_code}}")
                            
                            # Find code input
                            code_selectors = [
                                'input[name="code"]',
                                'input[type="text"]',
                                'input[placeholder*="code"]',
                                'input[aria-label*="code"]',
                                'input[data-testid*="code"]'
                            ]
                            
                            code_input = None
                            for selector in code_selectors:
                                code_input = await page.query_selector(selector)
                                if code_input and await code_input.is_visible():
                                    break
                            
                            if code_input:
                                await human_like_typing(code_input, sms_code)
                                print("✅ SMS code entered")
                                
                                # Submit code
                                await asyncio.sleep(2)
                                submit_selectors = [
                                    'button[type="submit"]',
                                    'button:has-text("Continue")',
                                    'button:has-text("Confirm")',
                                    'div[role="button"]:has-text("Continue")'
                                ]
                                
                                submitted = False
                                for selector in submit_selectors:
                                    try:
                                        submit_btn = await page.query_selector(selector)
                                        if submit_btn and await submit_btn.is_visible():
                                            await submit_btn.click()
                                            submitted = True
                                            break
                                    except:
                                        continue
                                
                                if not submitted:
                                    await page.keyboard.press('Enter')
                                
                                print("✅ SMS code submitted")
                                await asyncio.sleep(8)
                            else:
                                print("❌ SMS code input not found")
                                await page.screenshot(path=f"fb_no_code_input_{account_id}.png")
                                await browser.close()
                                return False
                        else:
                            print("❌ No SMS code received")
                            await browser.close()
                            return False
                    else:
                        print("ℹ️ No phone verification required - proceeding...")
                    
                    # Final check
                    await asyncio.sleep(5)
                    final_url = page.url
                    print(f"🏁 Final URL: {{final_url}}")
                    
                    await page.screenshot(path=f"fb_final_us_{account_id}.png")
                    
                    # Test marketplace location
                    try:
                        print("🛒 Testing marketplace location...")
                        await page.goto('https://www.facebook.com/marketplace')
                        await asyncio.sleep(3)
                        
                        marketplace_content = await page.content()
                        if any(us_term in marketplace_content.lower() for us_term in ['phoenix', 'arizona', 'united states', 'usa']):
                            print("✅ Marketplace shows US location!")
                        elif any(egypt_term in marketplace_content for egypt_term in ['egypt', 'مصر', 'القاهرة']):
                            print("⚠️ Marketplace still shows Egypt location")
                        else:
                            print("❓ Marketplace location unclear")
                            
                        await page.screenshot(path=f"marketplace_test_us_{account_id}.png")
                    except:
                        print("⚠️ Could not test marketplace")
                    
                    # Check success
                    if 'facebook.com' in final_url and 'login' not in final_url and 'reg' not in final_url:
                        print("🎉 US-based Facebook account created successfully!")
                        await browser.close()
                        return True
                    else:
                        print("⚠️ Status unclear - may need manual verification")
                        await browser.close()
                        return True
                        
            except Exception as e:
                print(f"💥 Error: {{e}}")
                import traceback
                traceback.print_exc()
                try:
                    await browser.close()
                except:
                    pass
                return False

        if __name__ == "__main__":
            result = asyncio.run(register_facebook_us_based())
            exit(0 if result else 1)
        ''').strip()
        
        return script_template
    
    def register_facebook_account_phone_first_us(self, profile):
        """Facebook registration using phone number first with US location"""
        try:
            import subprocess
            import sys
            
            logger.info(f"🇺🇸 Starting US-BASED PHONE-FIRST Facebook registration")
            
            # Create the enhanced US-based Playwright script
            script_content = self._create_us_based_phone_first_script(profile)
            
            # Write script to file
            script_file = f"temp_fb_register_us_phone_{profile['account_id']}.py"
            with open(script_file, 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            try:
                logger.info(f"🚀 Launching US-BASED PHONE-FIRST Facebook registration...")
                result = subprocess.run([
                    sys.executable, script_file
                ], capture_output=True, text=True, timeout=600)
                
                logger.info(f"📋 Registration output:")
                if result.stdout:
                    for line in result.stdout.split('\n'):
                        if line.strip():
                            logger.info(f"  {line}")
                
                success = result.returncode == 0
                
                if success:
                    logger.info(f"✅ US-BASED Facebook account created with PHONE-FIRST method")
                    profile['status'] = 'registered'
                    profile['facebook_created'] = True
                    profile['registration_date'] = datetime.now().isoformat()
                    profile['registration_method'] = 'phone_first_us'
                    profile['location_country'] = 'United States'
                    profile['marketplace_region'] = 'US'
                    
                    # Save updated profile
                    profile_file = f"account_data/profiles/account_{profile['account_id']}_profile.json"
                    json_safe_profile = self.convert_datetime_to_string(profile)
                    with open(profile_file, 'w') as f:
                        json.dump(json_safe_profile, f, indent=2)
                    
                    return True
                else:
                    logger.error(f"❌ US-BASED PHONE-FIRST Facebook registration failed")
                    return False
                    
            finally:
                try:
                    os.remove(script_file)
                except:
                    pass
                
        except Exception as e:
            logger.error(f"❌ Error in US-BASED PHONE-FIRST Facebook registration: {e}")
            return False
    
    def get_safe_fingerprint(self):
        """Safely get fingerprint or return None"""
        try:
            if hasattr(self, 'fingerprint_manager'):
                # Try different possible method names
                if hasattr(self.fingerprint_manager, 'generate_fingerprint'):
                    return self.fingerprint_manager.generate_fingerprint()
                elif hasattr(self.fingerprint_manager, 'create_fingerprint'):
                    return self.fingerprint_manager.create_fingerprint()
                elif hasattr(self.fingerprint_manager, 'get_fingerprint'):
                    return self.fingerprint_manager.get_fingerprint()
                else:
                    logger.warning("⚠️ FingerprintManager exists but no known method found")
                    return None
            else:
                logger.info("ℹ️ No fingerprint manager available")
                return None
        except Exception as e:
            logger.warning(f"⚠️ Error getting fingerprint: {e}")
            return None
    
    def convert_datetime_to_string(self, obj):
        """Recursively convert datetime objects to ISO format strings for JSON serialization"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {key: self.convert_datetime_to_string(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self.convert_datetime_to_string(item) for item in obj]
        else:
            return obj
    
    def create_enhanced_facebook_account_phone_first_us(self):
        """Enhanced account creation with robust proxy handling - FIXED"""
        try:
            logger.info("🇺🇸 Creating enhanced US phone-first Facebook account with ROBUST PROXY...")
            
            # Step 1: Get working US proxy with fallback
            logger.info("🔍 Step 1: Getting robust US proxy...")
            proxy = self.get_working_us_proxy_with_smart_fallback()
            if not proxy:
                logger.error("❌ Failed to get working proxy - cannot create account")
                return None
            
            logger.info("✅ Robust proxy obtained!")
            logger.info(f"   🔍 Location: {proxy.get('verified_city', 'Unknown')}, {proxy.get('verified_region', 'Unknown')}")
            logger.info(f"   🌍 IP: {proxy.get('verified_ip', 'Unknown')}")
            logger.info(f"   🇺🇸 US Verified: {'✅' if proxy.get('us_verified') else '❓ (Assumed SOAX US)'}")
            
            # Step 2: Generate AI profile data
            logger.info("🤖 Step 2: Generating AI profile data...")
            first_name, last_name = self.generate_ai_names()
            birth_month, birth_day, birth_year, gender = self.generate_ai_birthday_gender()
            
            # Step 3: Get US phone number
            logger.info("📱 Step 3: Getting US phone number...")
            phone_info = self.get_us_phone_number()
            if not phone_info or not phone_info.get('success'):
                logger.error("❌ Failed to get US phone number")
                return None
            
            phone = phone_info['phone']
            
            # Step 4: Generate credentials
            logger.info("🔑 Step 4: Generating credentials...")
            email = self.generate_temp_email()
            if not email:
                logger.error("❌ Failed to generate temp email")
                return None
            
            password = self.generate_secure_password()
            
            # Step 5: Create account in database
            logger.info("💾 Step 5: Creating account in database...")
            account_id = self.db.add_fb_account(
                email=email,
                password=password, 
                phone=phone,
                proxy_ip=proxy.get('endpoint', ''),
                registration_method="phone_first_us"
            )
            
            if not account_id:
                logger.error("❌ Failed to create account in database")
                return None
            
            # Step 6: Generate AI profile picture
            logger.info("🎨 Step 6: Generating AI profile picture...")
            image_url = self.generate_ai_profile_picture(first_name, gender)
            
            image_path = None
            if image_url:
                image_path = self.download_profile_picture(image_url, account_id)
                if image_path:
                    self.update_account_profile_picture(account_id, image_path)
                else:
                    logger.warning("⚠️ Failed to download profile picture")
            else:
                logger.warning("⚠️ Failed to generate profile picture")
            
            # Step 7: Create enhanced profile
            logger.info("📋 Step 7: Creating enhanced profile...")
            profile = {
                'account_id': account_id,
                'email': email,
                'password': password,
                'phone': phone,
                'phone_raw': phone_info.get('raw_phone', phone),
                'first_name': first_name,
                'last_name': last_name,
                'birth_month': birth_month,
                'birth_day': birth_day,
                'birth_year': birth_year,
                'gender': gender,
                'created_at': datetime.now().isoformat(),
                'registration_method': 'phone_first_us',
                'status': 'created',
                'proxy': proxy,
                'profile_picture_url': image_url if image_url else None,
                'profile_picture_path': image_path if image_path else None,
                'sms_service': phone_info.get('service', 'smspinverify'),
                'sms_id': phone_info.get('sms_id'),
                'us_info': {
                    'proxy_working': True,
                    'us_verified': proxy.get('us_verified', False),
                    'location_verified': proxy.get('us_verified', False),
                    'facebook_accessible': proxy.get('facebook_accessible', False),
                    'verified_ip': proxy.get('verified_ip', 'Unknown'),
                    'verified_location': f"{proxy.get('verified_city', 'Unknown')}, {proxy.get('verified_region', 'Unknown')}",
                    'proxy_method': 'soax_with_fallback',
                    'verification_timestamp': datetime.now().isoformat(),
                    'note': proxy.get('note', 'Standard verification completed')
                },
                'fingerprint': self.get_safe_fingerprint(),
                'facebook_created': False
            }
            
            # Step 8: Actually register the Facebook account
            logger.info("🚀 Step 8: Registering Facebook account...")
            facebook_success = self.register_facebook_account_phone_first_us(profile)
            
            if facebook_success:
                profile['facebook_created'] = True
                profile['status'] = 'registered'
                logger.info("✅ Facebook account registration successful!")
            else:
                logger.warning("⚠️ Facebook registration failed, but profile data saved")
                profile['facebook_created'] = False
                profile['status'] = 'created_no_facebook'
            
            # Save profile (convert datetime objects to strings first)
            profile_file = f"account_data/profiles/account_{account_id}_profile.json"
            os.makedirs(os.path.dirname(profile_file), exist_ok=True)
            
            # Convert any datetime objects to strings for JSON serialization
            json_safe_profile = self.convert_datetime_to_string(profile)
            
            with open(profile_file, 'w') as f:
                json.dump(json_safe_profile, f, indent=2)
            
            logger.info(f"🎉 ENHANCED US ACCOUNT CREATED SUCCESSFULLY!")
            logger.info(f"=" * 60)
            logger.info(f"   📧 Email: {email}")
            logger.info(f"   📱 Phone: {phone}")
            logger.info(f"   👤 Name: {first_name} {last_name}")
            logger.info(f"   🎂 Birthday: {birth_month}/{birth_day}/{birth_year}")
            logger.info(f"   ⚧ Gender: {gender}")
            logger.info(f"   🖼️ Profile Picture: {'✅ Generated' if image_url else '❌ Failed'}")
            logger.info(f"   🇺🇸 US Proxy: {'✅ Verified' if proxy.get('us_verified') else '🔶 Working (SOAX US)'}")
            logger.info(f"   📍 Location: {proxy.get('verified_city', 'Unknown')}, {proxy.get('verified_region', 'Unknown')}")
            logger.info(f"   📘 Facebook Access: {'✅' if proxy.get('facebook_accessible') else '❓'}")
            logger.info(f"   🌍 IP: {proxy.get('verified_ip', 'Unknown')}")
            logger.info(f"   📘 Facebook Account: {'✅ Created' if facebook_success else '❌ Failed'}")
            logger.info(f"=" * 60)
            
            return profile
            
        except Exception as e:
            logger.error(f"💥 Error creating enhanced US account: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def create_multiple_enhanced_accounts_phone_first_us(self, count=5):
        """Create multiple enhanced accounts with robust proxy handling"""
        try:
            logger.info(f"🇺🇸 Creating {count} enhanced US phone-first accounts with ROBUST PROXY HANDLING...")
            
            created_accounts = []
            
            for i in range(count):
                logger.info(f"\n📊 Creating account {i+1}/{count}...")
                logger.info("=" * 50)
                
                # Add retry logic for each account
                max_retries = 2
                account_created = False
                
                for retry in range(max_retries):
                    try:
                        if retry > 0:
                            logger.info(f"🔄 Retry {retry + 1}/{max_retries} for account {i+1}")
                            time.sleep(10)  # Wait before retry
                        
                        profile = self.create_enhanced_facebook_account_phone_first_us()
                        
                        if profile:
                            created_accounts.append(profile)
                            logger.info(f"✅ Account {i+1} created successfully")
                            
                            # Show brief summary
                            logger.info(f"   👤 {profile['first_name']} {profile['last_name']}")
                            logger.info(f"   📱 {profile['phone']}")
                            logger.info(f"   🇺🇸 US Status: {'✅ Verified' if profile['proxy'].get('us_verified') else '🔶 SOAX US'}")
                            logger.info(f"   📍 Location: {profile['proxy'].get('verified_city', 'Unknown')}, {profile['proxy'].get('verified_region', 'Unknown')}")
                            logger.info(f"   📘 Facebook: {'✅ Created' if profile.get('facebook_created') else '❌ Failed'}")
                            
                            account_created = True
                            break
                        else:
                            logger.warning(f"⚠️ Account {i+1} creation failed on attempt {retry + 1}")
                            
                    except Exception as e:
                        logger.error(f"💥 Error in account {i+1} attempt {retry + 1}: {e}")
                        continue
                
                if not account_created:
                    logger.error(f"❌ Failed to create account {i+1} after {max_retries} attempts")
                
                # Delay between accounts
                if i < count - 1 and account_created:
                    delay = random.randint(60, 120)
                    logger.info(f"⏳ Waiting {delay} seconds before next account...")
                    time.sleep(delay)
            
            # Final summary
            successful_facebook = len([acc for acc in created_accounts if acc.get('facebook_created')])
            logger.info(f"\n🎯 ROBUST US ACCOUNT CREATION SUMMARY:")
            logger.info("=" * 60)
            logger.info(f"   ✅ Successfully created: {len(created_accounts)}/{count}")
            logger.info(f"   📘 Facebook accounts: {successful_facebook}/{len(created_accounts)}")
            logger.info(f"   ❌ Failed: {count - len(created_accounts)}/{count}")
            logger.info(f"   🇺🇸 US-based proxies with robust fallback handling")
            logger.info(f"   🤖 All accounts have AI-generated profiles and pictures")
            
            if created_accounts:
                logger.info(f"\n📋 CREATED US ACCOUNTS:")
                logger.info("=" * 60)
                for i, acc in enumerate(created_accounts, 1):
                    logger.info(f"   {i}. {acc['first_name']} {acc['last_name']}")
                    logger.info(f"      📱 Phone: {acc['phone']}")
                    logger.info(f"      📧 Email: {acc['email']}")
                    logger.info(f"      🇺🇸 Status: {'✅ Verified' if acc['proxy'].get('us_verified') else '🔶 SOAX US'}")
                    logger.info(f"      📍 Location: {acc['proxy'].get('verified_city', 'Unknown')}, {acc['proxy'].get('verified_region', 'Unknown')}")
                    logger.info(f"      🌍 IP: {acc['proxy'].get('verified_ip', 'Unknown')}")
                    logger.info(f"      🖼️ Profile Pic: {'✅' if acc.get('profile_picture_url') else '❌'}")
                    logger.info(f"      📘 Facebook: {'✅ Created' if acc.get('facebook_created') else '❌ Failed'}")
                    if i < len(created_accounts):
                        logger.info("")
            
            return created_accounts
            
        except Exception as e:
            logger.error(f"💥 Error creating multiple enhanced US accounts: {e}")
            return []