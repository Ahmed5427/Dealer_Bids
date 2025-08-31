#!/usr/bin/env python3
"""
Enhanced Warmup Module with improved navigation and error handling
"""

from openai import OpenAI
import random
import time
import json
import os
import logging
import requests
from playwright.sync_api import sync_playwright
from datetime import datetime
from warmup import AccountWarmup
from sticky_proxy_manager import StickyProxyManager

logger = logging.getLogger(__name__)

class EnhancedAccountWarmup(AccountWarmup):
    """Enhanced Account Warmup with AI features and improved navigation"""
    
    def __init__(self, config, db):
        super().__init__(config, db)
        self.openai_client = OpenAI(api_key=config.OPENAI_API_KEY)
        
        # Facebook groups to join
        self.target_groups = [
            "https://www.facebook.com/share/g/1RhMgJAQE4/",
            "https://www.facebook.com/share/g/1KFUDKqPZK/", 
            "https://www.facebook.com/share/g/1BAe6c4nKt/",
            "https://www.facebook.com/share/g/16TDteWaXw/",
            "https://www.facebook.com/share/g/1ADd6ehECW/",
            "https://www.facebook.com/share/g/19XEB7EpTx/",
            "https://www.facebook.com/share/g/1MoqmuDKa1/"
        ]
    
    def check_profile_picture_status(self, account):
        """Check if account needs profile picture upload"""
        try:
            account_id = account['account_id']
            profile_status = account.get('profile_status', 'no')
            profile_picture = account.get('profile_picture', '')
            
            logger.info(f"🖼️ Checking profile picture status for account {account_id}")
            logger.info(f"   📊 Profile status: {profile_status}")
            logger.info(f"   🖼️ Profile picture: {profile_picture}")
            
            if profile_status == 'yes':
                logger.info("✅ Account already has profile picture uploaded")
                return 'uploaded'
            
            elif profile_status == 'no':
                if profile_picture and profile_picture.strip():
                    logger.info("📷 Profile picture exists but not uploaded yet")
                    return 'needs_upload'
                else:
                    logger.info("🎨 No profile picture found, needs generation")
                    return 'needs_generation'
            
            else:
                logger.info("❓ Profile status unknown, checking for picture")
                return 'needs_generation'
                
        except Exception as e:
            logger.error(f"❌ Error checking profile picture status: {e}")
            return 'needs_generation'
    
    def generate_ai_profile_picture(self, account):
        """Generate profile picture using OpenAI DALL-E"""
        try:
            # Load account profile for name and gender info
            profile = self.load_account_profile(account['account_id'])
            if not profile:
                logger.error("❌ Could not load account profile")
                return None
            
            first_name = profile.get('first_name', 'Person')
            gender = profile.get('gender', 'person')
            
            # Generate realistic prompt based on screenshot instructions
            prompt = self.generate_profile_picture_prompt(gender)
            
            logger.info(f"🎨 Generating profile picture for {first_name} ({gender})")
            logger.info(f"   🎯 Prompt: {prompt}")
            
            response = self.openai_client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                n=1,
                size="1024x1024",
                quality="standard"
            )
            
            image_url = response.data[0].url
            
            # Download and save locally
            image_path = self.download_and_save_image(image_url, account['account_id'])
            
            if image_path:
                # Update database
                self.update_profile_picture_database(account['account_id'], image_path)
                logger.info(f"✅ Profile picture generated and saved: {image_path}")
                return image_path
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error generating AI profile picture: {e}")
            return None
    
    def generate_profile_picture_prompt(self, gender):
        """Generate DALL-E prompt following screenshot instructions"""
        base_prompts = [
            f"realistic professional headshot photo of a {gender} person",
            f"natural portrait photo of a {gender} person", 
            f"casual profile photo of a {gender} person",
            f"friendly headshot of a {gender} person"
        ]
        
        backgrounds = [
            "with messy background",
            "with cluttered office background",
            "with blurred natural background", 
            "with imperfect lighting",
            "with slightly busy background"
        ]
        
        styles = [
            "realistic photo",
            "natural lighting", 
            "not too perfect",
            "slightly asymmetrical",
            "authentic feel",
            "real person photo"
        ]
        
        base = random.choice(base_prompts)
        background = random.choice(backgrounds)
        style = ", ".join(random.sample(styles, 2))
        
        return f"{base} {background}, {style}"
    
    def download_and_save_image(self, image_url, account_id):
        """Download image from URL and save locally"""
        try:
            os.makedirs('account_data/images', exist_ok=True)
            
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            image_path = f"account_data/images/profile_{account_id}.jpg"
            with open(image_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"📥 Downloaded image to {image_path}")
            return image_path
            
        except Exception as e:
            logger.error(f"❌ Error downloading image: {e}")
            return None
    
    def update_profile_picture_database(self, account_id, image_path):
        """Update profile picture info in Google Sheets"""
        try:
            worksheet = self.db.get_worksheet("fb_accounts")
            records = worksheet.get_all_records()
            
            for i, record in enumerate(records, start=2):
                if str(record['account_id']) == str(account_id):
                    # Update column O (profile_picture) and keep P as 'no' until uploaded
                    worksheet.update_cell(i, 15, image_path)  # Column O
                    worksheet.update_cell(i, 16, 'no')        # Column P
                    logger.info(f"📊 Updated database with profile picture path")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error updating database: {e}")
            return False
    
    def setup_browser_with_facebook_proof_proxy(self, proxy):
        """Setup browser with FACEBOOK-PROOF proxy configuration"""
        try:
            from playwright.sync_api import sync_playwright
            
            if hasattr(self, 'playwright'):
                try:
                    self.playwright.stop()
                except:
                    pass
            
            logger.info("✅ Setting up FACEBOOK-PROOF browser with advanced anti-detection...")
            
            self.playwright = sync_playwright().start()
            
            # Enhanced proxy configuration with DNS forcing
            proxy_config = None
            if proxy and proxy.get('username'):
                proxy_config = {
                    'server': f"http://{proxy['endpoint']}",
                    'username': proxy['username'],
                    'password': proxy['password']
                }
                logger.info(f"🛡️ Using FACEBOOK-PROOF proxy: {proxy['endpoint']}")
            else:
                logger.error("❌ No valid proxy configuration - aborted")
                return False
            
            try:
                # Launch browser with FACEBOOK-PROOF settings
                self.browser = self.playwright.chromium.launch(
                    headless=False,
                    args=[
                        '--no-sandbox',
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                        '--disable-web-security',
                        '--disable-features=VizDisplayCompositor',
                        # FACEBOOK-PROOF: Disable WebRTC to prevent IP leaks
                        '--disable-webrtc',
                        '--disable-webrtc-multiple-routes',
                        '--disable-webrtc-hw-decoding',
                        '--disable-webrtc-hw-encoding',
                        '--disable-webrtc-encryption',
                        # DNS and geolocation
                        '--disable-geolocation',
                        '--disable-background-timer-throttling',
                        '--disable-renderer-backgrounding',
                        '--disable-backgrounding-occluded-windows'
                    ],
                    proxy=proxy_config,
                    timeout=60000
                )
                
                # FACEBOOK-PROOF context with comprehensive US fingerprinting
                context_options = {
                    'viewport': {'width': 1366, 'height': 768},
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'locale': 'en-US',
                    'timezone_id': 'America/Phoenix',  # Force US timezone
                    'geolocation': {'latitude': 33.4484, 'longitude': -112.0740},
                    'permissions': ['geolocation'],
                    # FACEBOOK-PROOF: Override color scheme and reduce motion
                    'color_scheme': 'light',
                    'reduced_motion': 'no-preference'
                }
                
                self.context = self.browser.new_context(**context_options)
                
                # Set timeouts
                self.context.set_default_timeout(60000)
                self.context.set_default_navigation_timeout(120000)
                
                self.page = self.context.new_page()
                
                # CRITICAL: Add FACEBOOK-PROOF JavaScript overrides
                facebook_proof_script = """
                    // FACEBOOK-PROOF: Override all location detection methods
                    
                    // 1. Force geolocation to Phoenix, AZ
                    Object.defineProperty(navigator, 'geolocation', {
                        value: {
                            getCurrentPosition: function(success, error, options) {
                                success({
                                    coords: {
                                        latitude: 33.4484,
                                        longitude: -112.0740,
                                        accuracy: 100,
                                        altitude: null,
                                        altitudeAccuracy: null,
                                        heading: null,
                                        speed: null
                                    },
                                    timestamp: Date.now()
                                });
                            },
                            watchPosition: function(success, error, options) {
                                return this.getCurrentPosition(success, error, options);
                            },
                            clearWatch: function(id) {}
                        },
                        writable: false,
                        configurable: false
                    });
                    
                    // 2. Override timezone detection
                    Object.defineProperty(Intl.DateTimeFormat.prototype, 'resolvedOptions', {
                        value: function() {
                            return {
                                locale: 'en-US',
                                timeZone: 'America/Phoenix',
                                calendar: 'gregory',
                                numberingSystem: 'latn'
                            };
                        },
                        writable: false
                    });
                    
                    // 3. Force timezone offset for Phoenix (-7 hours from UTC)
                    Date.prototype.getTimezoneOffset = function() {
                        return 420; // Phoenix timezone offset (7 * 60 minutes)
                    };
                    
                    // 4. Block WebRTC to prevent IP leaks
                    if (window.RTCPeerConnection) {
                        window.RTCPeerConnection = undefined;
                    }
                    if (window.webkitRTCPeerConnection) {
                        window.webkitRTCPeerConnection = undefined;
                    }
                    if (window.mozRTCPeerConnection) {
                        window.mozRTCPeerConnection = undefined;
                    }
                    
                    // 5. Override language detection
                    Object.defineProperty(navigator, 'language', { value: 'en-US', writable: false });
                    Object.defineProperty(navigator, 'languages', { value: ['en-US', 'en'], writable: false });
                    
                    console.log('🛡️ FACEBOOK-PROOF protection activated - Phoenix, AZ identity locked');
                """

                # Then use:
                self.page.add_init_script(facebook_proof_script)
                
                # FACEBOOK-PROOF: Additional DNS and connection verification
                logger.info("🔍 Running FACEBOOK-PROOF verification tests...")
                
                # Test 1: Verify basic connectivity through proxy
                try:
                    self.page.goto('http://httpbin.org/ip', timeout=30000)
                    ip_content = self.page.content()
                    logger.info(f"🔍 Proxy IP test result: {ip_content[:200]}")
                except Exception as e:
                    logger.warning(f"⚠️ Proxy IP test failed: {e}")
                
                # Test 2: JavaScript-based location verification
                try:
                    self.page.goto('data:text/html,<html><body><script>document.body.innerHTML="TZ: " + Intl.DateTimeFormat().resolvedOptions().timeZone + "<br>Offset: " + new Date().getTimezoneOffset() + "<br>Lang: " + navigator.language;</script></body></html>')
                    time.sleep(2)
                    js_content = self.page.content()
                    logger.info(f"🔍 JavaScript location test: {js_content}")
                except Exception as e:
                    logger.warning(f"⚠️ JavaScript location test failed: {e}")
                
                # CRITICAL: FACEBOOK-PROOF verification
                logger.info("🔍 Running FACEBOOK-PROOF Facebook verification...")
                if not self.verify_facebook_proof_protection():
                    logger.error("❌ FACEBOOK-PROOF protection failed - warmup aborted")
                    self.cleanup_browser()
                    return False
                
                logger.info(f"✅ FACEBOOK-PROOF browser setup successful")
                return True
                
            except Exception as e:
                logger.error(f"❌ FACEBOOK-PROOF browser setup failed: {e}")
                try:
                    if hasattr(self, 'browser'):
                        self.browser.close()
                except:
                    pass
                return False
            
        except Exception as e:
            logger.error(f"❌ Error setting up FACEBOOK-PROOF browser: {e}")
            return False

    def verify_facebook_proof_protection(self):
        """Verify FACEBOOK-PROOF protection is working - FIXED DETECTION"""
        try:
            logger.info("🛡️ Testing FACEBOOK-PROOF protection against Facebook detection...")
            
            # Test Facebook accessibility with protection
            self.page.goto('https://www.facebook.com', timeout=30000)
            time.sleep(5)
            
            # Check if page loaded
            current_url = self.page.url
            if 'facebook.com' not in current_url:
                logger.error("❌ Failed to reach Facebook through FACEBOOK-PROOF proxy")
                return False
            
            # Quick marketplace test with FACEBOOK-PROOF protection
            logger.info("🔍 Testing Facebook marketplace with FACEBOOK-PROOF protection...")
            self.page.goto('https://www.facebook.com/marketplace', timeout=30000)
            time.sleep(5)
            
            page_content = self.page.content().lower()
            
            # FIXED: Better location indicators
            us_cities = [
                'phoenix', 'scottsdale', 'tempe', 'mesa', 'chandler',  # Arizona
                'San Francisco', 'los angeles', 'san diego', 'oakland', 'sacramento',  # California  
                'new york', 'brooklyn', 'manhattan', 'queens', 'bronx',  # New York
                'chicago', 'milwaukee', 'detroit', 'cleveland',  # Midwest
                'miami', 'orlando', 'tampa', 'jacksonville',  # Florida
                'houston', 'dallas', 'austin', 'san antonio',  # Texas
                'seattle', 'portland', 'denver', 'atlanta', 'boston'  # Other major US cities
            ]
            
            us_indicators = [
                'united states', 'usa', 'america',
                'miles', ' mi ', 'mi away', 'miles away',
                '$', 'usd', 'dollars'
            ]
            
            egypt_cities = [
                'cairo', 'alexandria', 'giza', 'shubra el-kheima', 'port said',
                'suez', 'luxor', 'mansoura', 'el mahalla el kubra', 'tanta',
                'asyut', 'ismailia', 'fayyum', 'zagazig', 'aswan',
                'damietta', 'minya', 'beni suef', 'qena', 'sohag'
            ]
            
            egypt_indicators = [
                'egypt', 'مصر', 'القاهرة', 'الإسكندرية', 'الجيزة',
                'km ', ' كم', 'kilometers', 'كيلو',
                'egp', 'جنيه', 'ج.م', 'pound', 'egyptian',
                'عربي', 'العربية'
            ]
            
            # Count US indicators
            us_city_score = sum(1 for city in us_cities if city in page_content)
            us_general_score = sum(1 for indicator in us_indicators if indicator in page_content)
            us_total_score = us_city_score + us_general_score
            
            # Count Egypt indicators  
            egypt_city_score = sum(1 for city in egypt_cities if city in page_content)
            egypt_general_score = sum(1 for indicator in egypt_indicators if indicator in page_content)
            egypt_total_score = egypt_city_score + egypt_general_score
            
            # Additional checks for distance units (very reliable indicator)
            has_miles = any(indicator in page_content for indicator in ['miles', ' mi ', 'mi away'])
            has_km = any(indicator in page_content for indicator in [' km ', 'kilometers', ' كم'])
            
            logger.info(f"🔍 DETAILED Location Analysis:")
            logger.info(f"   🇺🇸 US Cities: {us_city_score}, US General: {us_general_score}, Total: {us_total_score}")
            logger.info(f"   🇪🇬 Egypt Cities: {egypt_city_score}, Egypt General: {egypt_general_score}, Total: {egypt_total_score}")
            logger.info(f"   📏 Distance Units: Miles={has_miles}, Kilometers={has_km}")
            
            # Take screenshot for debugging
            try:
                screenshot_path = f"facebook_proof_test_{int(time.time())}.png"
                self.page.screenshot(path=screenshot_path)
                logger.info(f"📸 FACEBOOK-PROOF test screenshot saved: {screenshot_path}")
            except Exception as e:
                logger.warning(f"📸 Screenshot failed: {e}")
            
            # DECISION LOGIC - Improved
            if has_miles and not has_km:
                logger.info("✅ FACEBOOK-PROOF SUCCESS: Distance in miles (US format)")
                return True
            elif has_km and not has_miles:
                logger.error("❌ FACEBOOK-PROOF FAILED: Distance in kilometers (Egypt format)")
                return False
            elif us_total_score > egypt_total_score and us_total_score > 0:
                logger.info(f"✅ FACEBOOK-PROOF SUCCESS: Higher US score ({us_total_score} vs {egypt_total_score})")
                return True
            elif egypt_total_score > us_total_score and egypt_total_score > 0:
                logger.error(f"❌ FACEBOOK-PROOF FAILED: Higher Egypt score ({egypt_total_score} vs {us_total_score})")
                # Log sample content for debugging
                content_sample = page_content[:500] if len(page_content) > 500 else page_content
                logger.error(f"📄 Content sample: {content_sample}")
                return False
            else:
                logger.warning(f"⚠️ FACEBOOK-PROOF UNCLEAR: Inconclusive scores (US:{us_total_score}, Egypt:{egypt_total_score})")
                logger.info("✅ Assuming success since Facebook is accessible")
                return True
            
        except Exception as e:
            logger.error(f"❌ FACEBOOK-PROOF verification failed: {e}")
            return False

    def final_location_check_after_login(self):
        """Final location verification after login - NEW IMPROVED VERSION"""
        try:
            logger.info("📍 Running IMPROVED final location check...")
            
            self.page.goto('https://www.facebook.com/marketplace', timeout=60000)
            time.sleep(5)
            
            page_content = self.page.content().lower()
            
            # NEW: Comprehensive US city detection
            us_cities = [
                'phoenix', 'scottsdale', 'tempe', 'mesa', 'chandler', 'queen creek',  # Arizona
                'san francisco', 'los angeles', 'san diego', 'oakland', 'sacramento', 'fresno',  # California  
                'new york', 'brooklyn', 'manhattan', 'queens', 'bronx', 'buffalo',  # New York
                'chicago', 'milwaukee', 'detroit', 'cleveland', 'columbus',  # Midwest
                'miami', 'orlando', 'tampa', 'jacksonville', 'fort lauderdale',  # Florida
                'houston', 'dallas', 'austin', 'san antonio', 'fort worth',  # Texas
                'seattle', 'portland', 'denver', 'atlanta', 'boston', 'philadelphia',  # Other major US cities
                'las vegas', 'nashville', 'charlotte', 'indianapolis', 'kansas city'
            ]
            
            us_indicators = [
                'united states', 'usa', 'america', 'american',
                'miles', ' mi ', 'mi away', 'miles away', ' miles',
                '$', 'usd', 'dollars', 'dollar'
            ]
            
            # Egypt detection (comprehensive)
            egypt_cities = [
                'cairo', 'alexandria', 'giza', 'shubra el-kheima', 'port said',
                'suez', 'luxor', 'mansoura', 'tanta', 'asyut', 'ismailia',
                'fayyum', 'zagazig', 'aswan', 'damietta', 'minya', 'beni suef',
                'qena', 'sohag', 'القاهرة', 'الإسكندرية', 'الجيزة', 'بني سويف'
            ]
            
            egypt_indicators = [
                'egypt', 'مصر', 'القاهرة', 'الإسكندرية', 'الجيزة', 'egyptian',
                'km ', ' كم', 'kilometers', 'كيلومتر', 'كيلو متر',
                'egp', 'جنيه', 'ج.م', 'pound', 'جنيها',
                'عربي', 'العربية', 'arabic'
            ]
            
            # Count all indicators
            us_city_count = sum(1 for city in us_cities if city in page_content)
            us_general_count = sum(1 for indicator in us_indicators if indicator in page_content)
            us_total_score = us_city_count + us_general_count
            
            egypt_city_count = sum(1 for city in egypt_cities if city in page_content)
            egypt_general_count = sum(1 for indicator in egypt_indicators if indicator in page_content)
            egypt_total_score = egypt_city_count + egypt_general_count
            
            # Check distance units (most reliable indicator)
            has_miles = any(indicator in page_content for indicator in ['miles', ' mi ', 'mi away', ' miles'])
            has_km_only = any(indicator in page_content for indicator in [' km ', 'kilometers', ' كم']) and not has_miles
            
            logger.info(f"📊 IMPROVED Final Location Analysis:")
            logger.info(f"   🇺🇸 US Cities found: {us_city_count}, US Indicators: {us_general_count}, Total: {us_total_score}")
            logger.info(f"   🇪🇬 Egypt Cities found: {egypt_city_count}, Egypt Indicators: {egypt_general_count}, Total: {egypt_total_score}")
            logger.info(f"   📏 Distance Format: Miles={has_miles}, KM-only={has_km_only}")
            
            # Take screenshot for verification
            try:
                screenshot_name = f"final_location_improved_{int(time.time())}.png"
                self.page.screenshot(path=screenshot_name)
                logger.info(f"📸 Final location screenshot: {screenshot_name}")
            except Exception as e:
                logger.warning(f"📸 Screenshot failed: {e}")
            
            # IMPROVED DECISION LOGIC with priority system
            
            # Priority 1: Distance units (most reliable)
            if has_miles and not has_km_only:
                logger.info("✅ LOCATION: US confirmed by miles format")
                return 'us'
            elif has_km_only and not has_miles:
                logger.warning("⚠️ LOCATION: Egypt indicated by km-only format")
                return 'egypt'
            
            # Priority 2: City detection
            if us_city_count > 0 and egypt_city_count == 0:
                logger.info(f"✅ LOCATION: US confirmed by cities ({us_city_count} US cities found)")
                return 'us'
            elif egypt_city_count > 0 and us_city_count == 0:
                logger.warning(f"⚠️ LOCATION: Egypt indicated by cities ({egypt_city_count} Egypt cities found)")
                return 'egypt'
            
            # Priority 3: Overall score comparison
            if us_total_score > egypt_total_score and us_total_score >= 3:
                logger.info(f"✅ LOCATION: US wins by score ({us_total_score} vs {egypt_total_score})")
                return 'us'
            elif egypt_total_score > us_total_score and egypt_total_score >= 3:
                logger.warning(f"⚠️ LOCATION: Egypt wins by score ({egypt_total_score} vs {us_total_score})")
                return 'egypt'
            
            # Priority 4: If unclear, assume success since login worked
            logger.info("❓ LOCATION: Unclear from analysis, assuming US since login succeeded")
            return 'unclear'
            
        except Exception as e:
            logger.error(f"❌ Error in improved final location check: {e}")
            return 'error'

    def run_enhanced_warmup_cycle_with_facebook_proof(self, account):
        """Enhanced warmup with FACEBOOK-PROOF browser protection - FIXED DETECTION"""
        try:
            account_id = account['account_id']
            current_phase = account.get('warmup_phase', 'phase_1')
            
            logger.info(f"🚀 Starting FACEBOOK-PROOF enhanced warmup for account {account_id}")
            logger.info("🛡️ FACEBOOK-PROOF MODE: Advanced anti-detection enabled")
            
            # Determine login credential
            login_credential = self.determine_login_credential(account)
            password = account['password']
            
            # Get working proxy (same robust method)
            proxy_info = self.get_working_us_proxy_for_warmup()
            if not proxy_info:
                logger.error(f"❌ No working proxy available for account {account_id}")
                return False
            
            # Setup FACEBOOK-PROOF browser
            if not self.setup_browser_with_facebook_proof_proxy(proxy_info):
                logger.error(f"❌ FACEBOOK-PROOF browser setup failed for account {account_id}")
                return False
            
            # Login with FACEBOOK-PROOF protection
            twofa_secret = account.get('twofa_secret')
            if not self.login_facebook_robust(login_credential, password, twofa_secret):
                logger.error(f"❌ Login failed for account {account_id}")
                self.cleanup_browser()
                return False
            
            logger.info(f"✅ FACEBOOK-PROOF login successful for account {account_id}")
            
            # FIXED: Use NEW improved location detection after login
            logger.info("🔍 Final FACEBOOK-PROOF location verification after login...")
            location_result = self.final_location_check_after_login()
            
            if location_result == 'us':
                logger.info("✅ FACEBOOK-PROOF SUCCESS: Account shows US location after login!")
            elif location_result == 'egypt':
                logger.warning("⚠️ Account shows Egypt location after login (account history)")
                logger.warning("🔄 This is common for accounts originally registered in Egypt")
                logger.info("✅ Continuing warmup anyway - proxy and login are working fine")
            elif location_result == 'unclear':
                logger.info("❓ Location unclear after login, but continuing warmup")
            else:  # location_result == 'error'
                logger.warning("⚠️ Could not verify location after login, but continuing")
            
            # IMPORTANT: Continue with warmup activities regardless of location
            logger.info("🚀 Starting enhanced warmup activities...")
            
            # Run enhanced warmup activities
            success = self.enhanced_warmup_cycle(account)
            
            # Cleanup browser
            self.cleanup_browser()
            
            if success:
                self.db.update_account_status(account_id, "warming", "FACEBOOK-PROOF enhanced warmup completed successfully")
                logger.info(f"✅ FACEBOOK-PROOF enhanced warmup successful for account {account_id}")
                logger.info("🎯 Account is now warmed up and ready for use!")
            else:
                self.db.update_account_status(account_id, "warmup_failed", "FACEBOOK-PROOF enhanced warmup activities failed")
                logger.error(f"❌ FACEBOOK-PROOF enhanced warmup activities failed for account {account_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error in FACEBOOK-PROOF enhanced warmup: {e}")
            self.cleanup_browser()
            return False

    def setup_browser_with_mandatory_proxy(self, proxy):
        """Setup browser with MANDATORY proxy - no fallback to direct connection"""
        try:
            from playwright.sync_api import sync_playwright
            
            if hasattr(self, 'playwright'):
                try:
                    self.playwright.stop()
                except:
                    pass
            
            # First, verify proxy is actually working
            logger.info("🔍 Testing proxy connectivity before browser setup...")
            if not self.test_proxy_connectivity_detailed(proxy):
                logger.error("❌ Proxy connectivity test failed - warmup aborted")
                return False
            
            logger.info("✅ Proxy connectivity confirmed - setting up browser...")
            
            self.playwright = sync_playwright().start()
            
            # Only try with proxy - NO fallback to direct connection
            proxy_config = None
            if proxy and proxy.get('username'):
                proxy_config = {
                    'server': f"http://{proxy['endpoint']}",
                    'username': proxy['username'],
                    'password': proxy['password']
                }
                logger.info(f"🌐 Using MANDATORY proxy: {proxy['endpoint']}")
            else:
                logger.error("❌ No valid proxy configuration - warmup aborted")
                return False
            
            try:
                # Launch browser with proxy (no fallback)
                self.browser = self.playwright.chromium.launch(
                    headless=False,
                    args=[
                        '--no-sandbox',
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage'
                    ],
                    proxy=proxy_config,
                    timeout=60000  # 1 minute timeout
                )
                
                # Create context with US settings
                context_options = {
                    'viewport': {'width': 1366, 'height': 768},
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'locale': 'en-US',
                    'timezone_id': 'America/Phoenix',
                    'geolocation': {'latitude': 33.4484, 'longitude': -112.0740},
                    'permissions': ['geolocation']
                }
                
                self.context = self.browser.new_context(**context_options)
                
                # Set reasonable timeouts
                self.context.set_default_timeout(60000)  # 1 minute
                self.context.set_default_navigation_timeout(120000)  # 2 minutes
                
                self.page = self.context.new_page()
                
                # CRITICAL: Verify proxy is working with actual Facebook access
                logger.info("🔍 Verifying proxy works with Facebook...")
                if not self.verify_proxy_with_facebook():
                    logger.error("❌ Proxy failed Facebook verification - warmup aborted")
                    self.cleanup_browser()
                    return False
                
                logger.info(f"✅ Browser setup successful with MANDATORY proxy")
                return True
                
            except Exception as e:
                logger.error(f"❌ Browser setup with proxy failed: {e}")
                logger.error("❌ No fallback - warmup process aborted")
                try:
                    if hasattr(self, 'browser'):
                        self.browser.close()
                except:
                    pass
                return False
            
        except Exception as e:
            logger.error(f"❌ Error setting up browser with mandatory proxy: {e}")
            return False

    def test_proxy_connectivity_detailed(self, proxy):
        """Detailed proxy connectivity test before warmup"""
        try:
            logger.info("🧪 Running detailed proxy connectivity test...")
            
            if not proxy or not proxy.get('username'):
                logger.error("❌ No proxy configuration provided")
                return False
            
            proxy_url = f"http://{proxy['username']}:{proxy['password']}@{proxy['endpoint']}"
            proxy_config = {
                'http': proxy_url,
                'https': proxy_url
            }
            
            # Test multiple services
            test_services = [
                {'url': 'http://httpbin.org/ip', 'name': 'HTTPBin', 'timeout': 10},
                {'url': 'http://icanhazip.com', 'name': 'ICanHazIP', 'timeout': 8},
                {'url': 'https://api.ipify.org', 'name': 'IPify', 'timeout': 10}
            ]
            
            successful_tests = 0
            
            for service in test_services:
                try:
                    logger.info(f"🔍 Testing {service['name']}: {service['url']}")
                    
                    response = requests.get(
                        service['url'], 
                        proxies=proxy_config, 
                        timeout=service['timeout'],
                        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                    )
                    
                    if response.status_code == 200:
                        logger.info(f"✅ {service['name']} test passed")
                        successful_tests += 1
                    else:
                        logger.warning(f"⚠️ {service['name']} returned status {response.status_code}")
                        
                except Exception as e:
                    logger.warning(f"❌ {service['name']} test failed: {str(e)[:100]}")
                    continue
            
            if successful_tests >= 1:
                logger.info(f"✅ Proxy connectivity confirmed ({successful_tests}/{len(test_services)} tests passed)")
                return True
            else:
                logger.error(f"❌ Proxy connectivity failed (0/{len(test_services)} tests passed)")
                return False
                
        except Exception as e:
            logger.error(f"❌ Proxy connectivity test error: {e}")
            return False
        
    def verify_proxy_with_facebook(self):
        """Verify proxy actually works with Facebook"""
        try:
            logger.info("📘 Testing proxy with Facebook access...")
            
            # Test Facebook accessibility
            self.page.goto('https://www.facebook.com', timeout=30000)
            time.sleep(3)
            
            # Check if page loaded
            current_url = self.page.url
            if 'facebook.com' not in current_url:
                logger.error("❌ Failed to reach Facebook through proxy")
                return False
            
            # Quick marketplace test to verify location
            try:
                self.page.goto('https://www.facebook.com/marketplace', timeout=30000)
                time.sleep(3)
                
                page_content = self.page.content()
                
                # Check for US indicators
                us_indicators = ['phoenix', 'arizona', 'united states', 'usa', 'miles', 'mi ']
                egypt_indicators = ['egypt', 'مصر', 'القاهرة', 'بني سويف', 'km ']
                
                us_detected = any(indicator in page_content.lower() for indicator in us_indicators)
                egypt_detected = any(indicator in page_content.lower() for indicator in egypt_indicators)
                
                if us_detected and not egypt_detected:
                    logger.info("✅ Proxy verified: Facebook shows US location")
                    return True
                elif egypt_detected:
                    logger.error("❌ Proxy failed: Facebook shows Egypt location")
                    return False
                else:
                    logger.warning("⚠️ Location unclear, but Facebook accessible")
                    return True  # Allow to proceed if Facebook is accessible
                    
            except Exception as e:
                logger.warning(f"⚠️ Marketplace test failed: {e}")
                # If marketplace test fails but Facebook is accessible, proceed
                return True
            
        except Exception as e:
            logger.error(f"❌ Facebook verification failed: {e}")
            return False    
    
    def navigate_to_facebook_robust(self, max_retries=5):
        """Navigate to Facebook with robust retry logic"""
        facebook_urls = [
            'https://www.facebook.com',
            'https://m.facebook.com',
            'https://facebook.com',
            'https://www.facebook.com/login'
        ]
        
        for attempt in range(max_retries):
            for url in facebook_urls:
                try:
                    logger.info(f"🌐 Attempt {attempt + 1}/{max_retries}: Navigating to {url}")
                    
                    # Try with different wait strategies
                    wait_strategies = ['domcontentloaded', 'networkidle', 'load']
                    
                    for wait_strategy in wait_strategies:
                        try:
                            logger.info(f"   📡 Using wait strategy: {wait_strategy}")
                            
                            # Navigate with timeout
                            self.page.goto(url, wait_until=wait_strategy, timeout=45000)  # 45 seconds
                            
                            # Wait for page to stabilize
                            time.sleep(random.uniform(3, 5))
                            
                            # Check if page loaded successfully
                            current_url = self.page.url
                            page_title = self.page.title()
                            
                            logger.info(f"📄 Page loaded - URL: {current_url}")
                            logger.info(f"📄 Title: {page_title}")
                            
                            # Verify it's actually Facebook
                            if ('facebook' in current_url.lower() and 
                                ('facebook' in page_title.lower() or 'log in' in page_title.lower() or len(page_title) > 0)):
                                logger.info(f"✅ Successfully navigated to Facebook!")
                                return True
                            else:
                                logger.warning(f"⚠️ Page might not be Facebook, but continuing...")
                                return True  # Sometimes Facebook loads without obvious indicators
                                
                        except Exception as wait_error:
                            logger.warning(f"⚠️ Wait strategy {wait_strategy} failed: {str(wait_error)[:100]}")
                            continue
                            
                except Exception as url_error:
                    logger.warning(f"⚠️ URL {url} failed: {str(url_error)[:100]}")
                    continue
            
            # Wait before retry
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 10
                logger.info(f"⏳ Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
        
        logger.error(f"❌ Failed to navigate to Facebook after {max_retries} attempts")
        return False
    
    def handle_facebook_checkpoint(self, account):
        """Handle Facebook checkpoint/security verification - WITH CHAINED CHECKPOINT SUPPORT"""
        try:
            max_checkpoint_attempts = 5  # Handle up to 5 chained checkpoints
            attempt = 0
            
            while attempt < max_checkpoint_attempts:
                attempt += 1
                logger.info(f"🚨 Facebook checkpoint detected - attempt {attempt}/{max_checkpoint_attempts}")
                
                # Take screenshot for debugging
                current_time = int(time.time())
                self.page.screenshot(path=f"checkpoint_attempt_{attempt}_{current_time}.png")
                logger.info(f"📸 Checkpoint screenshot: checkpoint_attempt_{attempt}_{current_time}.png")
                
                # Wait for page to fully load
                time.sleep(random.uniform(3, 5))
                
                # Get page content to analyze what type of checkpoint this is
                page_content = self.page.content()
                current_url = self.page.url
                
                logger.info(f"🔍 Checkpoint URL (attempt {attempt}): {current_url}")
                
                # Check if we're still on a checkpoint page
                if not any(indicator in current_url.lower() for indicator in ['checkpoint', 'verify', 'security']):
                    logger.info("✅ No longer on checkpoint page - verification complete")
                    return True
                
                logger.info(f"🔍 Analyzing checkpoint type (attempt {attempt})...")
                
                # DEBUG: Log key content
                try:
                    page_text = self.page.inner_text('body') if self.page.query_selector('body') else page_content
                    key_phrases = []
                    
                    # Look for different checkpoint indicators
                    checkpoint_phrases = [
                        'confirm you\'re human', 'help us confirm it\'s you', 
                        'protecting your account', 'solve this puzzle', 'start puzzle',
                        'account integrity', 'community standards', 'verification',
                        'security check', 'suspicious activity'
                    ]
                    
                    for phrase in checkpoint_phrases:
                        if phrase in page_text.lower():
                            key_phrases.append(phrase)
                            
                    logger.info(f"🔍 Key phrases detected (attempt {attempt}): {', '.join(key_phrases)}")
                except:
                    pass
                
                # Identify checkpoint type
                checkpoint_type = self.identify_checkpoint_type(page_content)
                logger.info(f"🎯 Checkpoint type (attempt {attempt}): {checkpoint_type}")
                
                # Handle the specific checkpoint type
                checkpoint_handled = False
                
                if checkpoint_type == "puzzle_verification":
                    checkpoint_handled = self.handle_puzzle_verification_checkpoint()
                elif checkpoint_type == "human_verification":
                    checkpoint_handled = self.handle_human_verification_checkpoint()
                elif checkpoint_type == "phone_verification":
                    checkpoint_handled = self.handle_phone_verification_checkpoint()
                elif checkpoint_type == "identity_verification":
                    checkpoint_handled = self.handle_identity_verification_checkpoint()
                elif checkpoint_type == "suspicious_activity":
                    checkpoint_handled = self.handle_suspicious_activity_checkpoint()
                elif checkpoint_type == "device_verification":
                    checkpoint_handled = self.handle_device_verification_checkpoint()
                elif checkpoint_type == "photo_verification":
                    checkpoint_handled = self.handle_photo_verification_checkpoint()
                elif checkpoint_type == "security_questions":
                    checkpoint_handled = self.handle_security_questions_checkpoint()
                elif checkpoint_type == "two_factor":
                    checkpoint_handled = self.handle_2fa_authentication(account.get('twofa_secret'))
                else:
                    checkpoint_handled = self.handle_generic_checkpoint()
                
                if checkpoint_handled:
                    logger.info(f"✅ Checkpoint {attempt} handled successfully")
                    
                    # Wait and check if there are more checkpoints
                    time.sleep(5)
                    new_url = self.page.url
                    logger.info(f"🔍 URL after checkpoint {attempt}: {new_url}")
                    
                    # If still on checkpoint page, continue to next checkpoint
                    if any(indicator in new_url.lower() for indicator in ['checkpoint', 'verify', 'security']):
                        logger.info(f"⏭️ Still on checkpoint page - checking for next checkpoint (attempt {attempt + 1})")
                        continue
                    else:
                        logger.info(f"✅ All checkpoints completed after {attempt} attempts")
                        return True
                else:
                    logger.error(f"❌ Checkpoint {attempt} handling failed")
                    
                    # Try generic handling as fallback
                    if checkpoint_type != "generic":
                        logger.info(f"🔄 Trying generic handling for checkpoint {attempt}")
                        if self.handle_generic_checkpoint():
                            logger.info(f"✅ Generic handling worked for checkpoint {attempt}")
                            continue
                    
                    # If this checkpoint failed and we have more attempts, try skipping
                    if attempt < max_checkpoint_attempts:
                        logger.info(f"⏭️ Attempting to skip checkpoint {attempt}")
                        if self.try_skip_checkpoint():
                            logger.info(f"⏭️ Successfully skipped checkpoint {attempt}")
                            continue
                    
                    logger.error(f"❌ Could not handle checkpoint {attempt}")
                    return False
            
            logger.error(f"❌ Exceeded maximum checkpoint attempts ({max_checkpoint_attempts})")
            return False
            
        except Exception as e:
            logger.error(f"💥 Error handling chained checkpoints: {e}")
            return False


    def identify_checkpoint_type(self, page_content):
        """Identify the type of Facebook checkpoint - WITH PUZZLE DETECTION"""
        try:
            content_lower = page_content.lower()
            
            # PRIORITY 1: Puzzle/CAPTCHA verification indicators
            if any(indicator in content_lower for indicator in [
                'solve this puzzle', 'start puzzle', 'complete the puzzle',
                'protecting your account', 'help us confirm it\'s you',
                'puzzle so we know you are a real person', 'arkose', 'captcha'
            ]):
                return "puzzle_verification"
            
            # PRIORITY 2: Human verification indicators (simple continue)
            elif any(indicator in content_lower for indicator in [
                'confirm you\'re human', 'confirm youre human', 'human verification',
                'to use your account', 'account integrity', 'community standards',
                'precaution based on our community standards'
            ]):
                return "human_verification"
            
            # PRIORITY 3: Phone verification indicators  
            elif any(indicator in content_lower for indicator in [
                'confirm your phone', 'phone number', 'text message', 
                'enter your phone', 'mobile number', 'sms code'
            ]):
                return "phone_verification"
            
            # Rest of the existing logic...
            elif any(indicator in content_lower for indicator in [
                'verify your identity', 'confirm your identity', 'identity verification',
                'government id', 'photo id', 'upload id'
            ]):
                return "identity_verification"
            
            elif any(indicator in content_lower for indicator in [
                'suspicious activity', 'unusual activity', 'security check',
                'verify it was you', 'recent login', 'unrecognized login'
            ]):
                return "suspicious_activity"
            
            elif any(indicator in content_lower for indicator in [
                'new device', 'unrecognized device', 'device verification',
                'browser verification', 'save browser', 'remember browser'
            ]):
                return "device_verification"
            
            elif any(indicator in content_lower for indicator in [
                'upload a photo', 'photo verification', 'face verification',
                'selfie', 'camera'
            ]):
                return "photo_verification"
            
            elif any(indicator in content_lower for indicator in [
                'security question', 'answer question', 'verify information'
            ]):
                return "security_questions"
            
            elif any(indicator in content_lower for indicator in [
                'two-factor authentication', 'authentication app', 'login code from',
                'enter the 6-digit code', 'authentication code from your app'
            ]):
                return "two_factor"
            
            else:
                return "generic"
                
        except Exception as e:
            logger.error(f"💥 Error identifying checkpoint type: {e}")
            return "generic"

    def handle_puzzle_verification_checkpoint(self):
        """Handle puzzle/CAPTCHA verification checkpoint - NEW HANDLER"""
        try:
            logger.info("🧩 Handling puzzle verification checkpoint...")
            
            # Take screenshot
            self.page.screenshot(path=f"puzzle_checkpoint_{int(time.time())}.png")
            
            # This type of checkpoint usually requires solving a CAPTCHA/puzzle
            # Look for skip options first before attempting to solve
            
            logger.info("🔍 Looking for skip options for puzzle verification...")
            skip_selectors = [
                'div[role="button"]:has-text("Skip")',
                'div[role="button"]:has-text("Not now")',
                'div[role="button"]:has-text("Later")',
                'a:has-text("Skip")',
                'a:has-text("Not now")',
                'div[role="button"]:has-text("I\'ll do this later")',
                'div[role="button"]:has-text("Continue without")'
            ]
            
            for selector in skip_selectors:
                try:
                    button = self.page.query_selector(selector)
                    if button and button.is_visible():
                        logger.info(f"⏭️ Found skip button for puzzle: {selector}")
                        button.click()
                        time.sleep(5)
                        
                        if self.check_checkpoint_completion():
                            logger.info("✅ Successfully skipped puzzle verification")
                            return True
                except:
                    continue
            
            # Look for audio alternative (sometimes easier to handle)
            logger.info("🔊 Looking for audio alternative...")
            audio_selectors = [
                '[aria-label="Audio"]',
                'button:has-text("Audio")',
                'div[role="button"]:has-text("Audio")',
                '.audio-button',
                '[data-testid="audio-button"]'
            ]
            
            for selector in audio_selectors:
                try:
                    button = self.page.query_selector(selector)
                    if button and button.is_visible():
                        logger.info(f"🔊 Found audio button: {selector}")
                        # For now, just note that audio is available but don't click
                        # (Audio CAPTCHAs are complex to solve programmatically)
                        break
                except:
                    continue
            
            # Look for "Start Puzzle" button and click it to see what happens
            logger.info("🧩 Looking for Start Puzzle button...")
            start_puzzle_selectors = [
                'div[role="button"]:has-text("Start Puzzle")',
                'button:has-text("Start Puzzle")',
                'div[role="button"]:has-text("Start")',
                '[aria-label="Start Puzzle"]'
            ]
            
            puzzle_started = False
            for selector in start_puzzle_selectors:
                try:
                    button = self.page.query_selector(selector)
                    if button and button.is_visible():
                        logger.info(f"🧩 Found Start Puzzle button: {selector}")
                        button.click()
                        puzzle_started = True
                        time.sleep(3)
                        break
                except:
                    continue
            
            if puzzle_started:
                logger.info("🧩 Puzzle started - looking for completion options...")
                
                # Wait a moment for puzzle to load
                time.sleep(5)
                
                # Take screenshot of the puzzle
                self.page.screenshot(path=f"puzzle_loaded_{int(time.time())}.png")
                
                # Look for any way to complete or skip the puzzle
                # Sometimes puzzles have "I can't solve this" or similar options
                completion_selectors = [
                    'div[role="button"]:has-text("I can\'t solve this")',
                    'div[role="button"]:has-text("Try different challenge")',
                    'div[role="button"]:has-text("Get new challenge")',
                    'div[role="button"]:has-text("Skip")',
                    'a:has-text("I can\'t solve this")',
                    'button:has-text("Continue")',
                    'div[role="button"]:has-text("Continue")'
                ]
                
                for selector in completion_selectors:
                    try:
                        button = self.page.query_selector(selector)
                        if button and button.is_visible():
                            logger.info(f"🔄 Found puzzle completion option: {selector}")
                            button.click()
                            time.sleep(5)
                            
                            if self.check_checkpoint_completion():
                                logger.info("✅ Puzzle verification completed")
                                return True
                    except:
                        continue
            
            # If puzzle can't be solved/skipped, this may require manual intervention
            logger.warning("⚠️ Puzzle verification detected - may require manual intervention")
            logger.warning("🧩 Automated puzzle solving is not implemented")
            
            # Try to continue anyway in case the page changes
            time.sleep(10)  # Wait longer in case puzzle auto-completes or times out
            
            if self.check_checkpoint_completion():
                logger.info("✅ Puzzle checkpoint completed (possibly timed out or auto-resolved)")
                return True
            
            logger.error("❌ Could not complete puzzle verification automatically")
            return False
            
        except Exception as e:
            logger.error(f"💥 Error in puzzle verification: {e}")
            return False

    def handle_phone_verification_checkpoint(self):
        """Handle phone verification checkpoint"""
        try:
            logger.info("📱 Handling phone verification checkpoint...")
            
            # Look for phone input field
            phone_selectors = [
                'input[name="phone_number"]',
                'input[type="tel"]',
                'input[placeholder*="phone"]',
                'input[placeholder*="number"]'
            ]
            
            phone_input = None
            for selector in phone_selectors:
                phone_input = self.page.query_selector(selector)
                if phone_input and phone_input.is_visible():
                    logger.info(f"📱 Found phone input: {selector}")
                    break
            
            if phone_input:
                # If we have the account's phone number, use it
                # This would need to be passed from the account data
                logger.info("📱 Phone verification required - would need account phone number")
                
                # Look for "Skip" or "Not now" options
                skip_buttons = [
                    'div[role="button"]:has-text("Skip")',
                    'div[role="button"]:has-text("Not now")',
                    'a:has-text("Skip")',
                    'div[role="button"]:has-text("Continue without")'
                ]
                
                for selector in skip_buttons:
                    button = self.page.query_selector(selector)
                    if button and button.is_visible():
                        logger.info("⏭️ Skipping phone verification")
                        button.click()
                        time.sleep(5)
                        return self.check_checkpoint_completion()
            
            return False
            
        except Exception as e:
            logger.error(f"💥 Error in phone verification: {e}")
            return False

    def handle_suspicious_activity_checkpoint(self):
        """Handle suspicious activity checkpoint"""
        try:
            logger.info("🔍 Handling suspicious activity checkpoint...")
            
            # Look for "This was me" or "Yes, this was me" buttons
            confirm_buttons = [
                'div[role="button"]:has-text("This was me")',
                'div[role="button"]:has-text("Yes")',
                'button:has-text("This was me")',
                'button:has-text("Yes, this was me")',
                'div[role="button"]:has-text("Continue")',
                'input[type="submit"]'
            ]
            
            for selector in confirm_buttons:
                try:
                    button = self.page.query_selector(selector)
                    if button and button.is_visible():
                        logger.info(f"✅ Confirming activity: {selector}")
                        button.click()
                        time.sleep(5)
                        return self.check_checkpoint_completion()
                except:
                    continue
            
            # If no confirm button found, try to skip
            return self.try_skip_checkpoint()
            
        except Exception as e:
            logger.error(f"💥 Error in suspicious activity handling: {e}")
            return False

    def handle_device_verification_checkpoint(self):
        """Handle device verification checkpoint"""
        try:
            logger.info("💻 Handling device verification checkpoint...")
            
            # Look for "Save Device" or "Remember Device" options
            save_device_buttons = [
                'div[role="button"]:has-text("Save Device")',
                'div[role="button"]:has-text("Remember")',
                'button:has-text("Save Browser")',
                'div[role="button"]:has-text("Yes")',
                'div[role="button"]:has-text("Continue")'
            ]
            
            for selector in save_device_buttons:
                try:
                    button = self.page.query_selector(selector)
                    if button and button.is_visible():
                        logger.info(f"💾 Saving device: {selector}")
                        button.click()
                        time.sleep(5)
                        return self.check_checkpoint_completion()
                except:
                    continue
            
            # Try "Don't Save" options
            dont_save_buttons = [
                'div[role="button"]:has-text("Don\'t Save")',
                'div[role="button"]:has-text("Not Now")',
                'button:has-text("Don\'t Save")'
            ]
            
            for selector in dont_save_buttons:
                try:
                    button = self.page.query_selector(selector)
                    if button and button.is_visible():
                        logger.info(f"⏭️ Not saving device: {selector}")
                        button.click()
                        time.sleep(5)
                        return self.check_checkpoint_completion()
                except:
                    continue
            
            return self.try_skip_checkpoint()
            
        except Exception as e:
            logger.error(f"💥 Error in device verification: {e}")
            return False

    def handle_identity_verification_checkpoint(self):
        """Handle identity verification checkpoint"""
        try:
            logger.info("🆔 Handling identity verification checkpoint...")
            
            # This type usually requires document upload, which we can't automate
            # Look for skip options
            logger.warning("⚠️ Identity verification detected - this usually requires manual intervention")
            
            return self.try_skip_checkpoint()
            
        except Exception as e:
            logger.error(f"💥 Error in identity verification: {e}")
            return False

    def handle_photo_verification_checkpoint(self):
        """Handle photo verification checkpoint"""
        try:
            logger.info("📷 Handling photo verification checkpoint...")
            
            # This usually requires uploading a selfie, which we can't automate
            logger.warning("⚠️ Photo verification detected - this usually requires manual intervention")
            
            return self.try_skip_checkpoint()
            
        except Exception as e:
            logger.error(f"💥 Error in photo verification: {e}")
            return False

    def handle_security_questions_checkpoint(self):
        """Handle security questions checkpoint"""
        try:
            logger.info("❓ Handling security questions checkpoint...")
            
            # Security questions would need account-specific information
            logger.warning("⚠️ Security questions detected - this usually requires manual intervention")
            
            return self.try_skip_checkpoint()
            
        except Exception as e:
            logger.error(f"💥 Error in security questions: {e}")
            return False

    def handle_generic_checkpoint(self):
        """Handle generic checkpoint with common patterns - IMPROVED VERSION"""
        try:
            logger.info("🔄 Handling generic checkpoint...")
            
            # Take screenshot
            self.page.screenshot(path=f"generic_checkpoint_{int(time.time())}.png")
            
            # Try common checkpoint completion buttons in order of likelihood
            common_buttons = [
                # Most common Facebook checkpoint buttons
                'div[role="button"]:has-text("Continue")',
                'button:has-text("Continue")',
                
                # Alternative continue buttons
                'div[role="button"]:has-text("Submit")',
                'div[role="button"]:has-text("Confirm")',
                'div[role="button"]:has-text("Next")',
                
                # Standard form buttons
                'button:has-text("Submit")',
                'button:has-text("Next")',
                'button[type="submit"]',
                'input[type="submit"]',
                
                # Generic buttons
                'div[role="button"][tabindex="0"]',
                'button[tabindex="0"]'
            ]
            
            for selector in common_buttons:
                try:
                    button = self.page.query_selector(selector)
                    if button and button.is_visible():
                        # Additional check - make sure it's not a back/cancel button
                        button_text = button.inner_text().lower()
                        aria_label = (button.get_attribute('aria-label') or '').lower()
                        
                        # Skip buttons that are clearly not what we want
                        if any(skip_word in button_text or skip_word in aria_label 
                            for skip_word in ['back', 'cancel', 'close', 'skip']):
                            continue
                        
                        logger.info(f"🔄 Clicking generic button: {selector} (text: '{button_text}')")
                        button.click()
                        time.sleep(random.uniform(3, 5))
                        
                        if self.check_checkpoint_completion():
                            logger.info("✅ Generic checkpoint completed successfully")
                            return True
                        else:
                            # Wait a bit more and check again
                            time.sleep(5)
                            if self.check_checkpoint_completion():
                                logger.info("✅ Generic checkpoint completed after wait")
                                return True
                except Exception as e:
                    logger.warning(f"⚠️ Error with button {selector}: {e}")
                    continue
            
            # If no buttons worked, try pressing Enter
            logger.info("⌨️ Trying Enter key as fallback...")
            try:
                self.page.keyboard.press('Enter')
                time.sleep(5)
                if self.check_checkpoint_completion():
                    logger.info("✅ Checkpoint completed with Enter key")
                    return True
            except:
                pass
            
            # Final attempt: try to skip
            return self.try_skip_checkpoint()
            
        except Exception as e:
            logger.error(f"💥 Error in generic checkpoint handling: {e}")
            return False

    def try_skip_checkpoint(self):
        """Try to skip the current checkpoint - IMPROVED VERSION"""
        try:
            logger.info("⏭️ Attempting to skip checkpoint...")
            
            # Take screenshot before skip attempt
            self.page.screenshot(path=f"before_skip_attempt_{int(time.time())}.png")
            
            skip_selectors = [
                # Most common skip options
                'div[role="button"]:has-text("Skip")',
                'div[role="button"]:has-text("Not now")',
                'div[role="button"]:has-text("Later")',
                'div[role="button"]:has-text("Skip for now")',
                
                # Alternative skip options
                'a:has-text("Skip")',
                'a:has-text("Not now")',
                'div[role="button"]:has-text("Continue without")',
                'div[role="button"]:has-text("I\'ll do this later")',
                
                # Sometimes "Back" can help escape checkpoints
                'div[role="button"]:has-text("Back")',
                '[aria-label="Back"]',
                
                # Look for any "Continue" that might bypass the checkpoint
                'div[role="button"]:has-text("Continue")',
                'button:has-text("Continue")'
            ]
            
            for selector in skip_selectors:
                try:
                    button = self.page.query_selector(selector)
                    if button and button.is_visible():
                        # Get button text to log what we're clicking
                        button_text = button.inner_text() if button.inner_text() else 'Unknown'
                        logger.info(f"⏭️ Found skip option: {selector} (text: '{button_text}')")
                        
                        button.click()
                        time.sleep(5)
                        
                        # Check if skip was successful
                        current_url = self.page.url
                        if not any(indicator in current_url.lower() for indicator in ['checkpoint', 'verify', 'security']):
                            logger.info("✅ Successfully skipped checkpoint")
                            return True
                        else:
                            logger.info(f"⏳ Skip attempt with '{button_text}' - still on checkpoint page")
                except Exception as e:
                    logger.warning(f"⚠️ Error with skip option {selector}: {e}")
                    continue
            
            logger.warning("⚠️ No working skip options found")
            return False
            
        except Exception as e:
            logger.error(f"💥 Error trying to skip checkpoint: {e}")
            return False

    def check_checkpoint_completion(self):
        """Check if checkpoint was completed successfully - IMPROVED FOR CHAINED CHECKPOINTS"""
        try:
            time.sleep(3)  # Wait for page to update
            
            current_url = self.page.url
            logger.info(f"🔍 Checking completion - URL: {current_url}")
            
            # Check if we're no longer on ANY checkpoint page
            checkpoint_indicators = ['checkpoint', 'verify', 'security', 'confirm']
            
            if not any(indicator in current_url.lower() for indicator in checkpoint_indicators):
                logger.info("✅ No longer on any checkpoint page - all checkpoints completed")
                return True
            
            # Check for Facebook main page indicators
            success_indicators = [
                '[aria-label="Account"]',
                '[data-testid="nav_account_switcher"]',
                '[aria-label="Facebook"]'
            ]
            
            for indicator in success_indicators:
                if self.page.query_selector(indicator):
                    logger.info(f"✅ Found Facebook main page indicator: {indicator}")
                    return True
            
            # If still on checkpoint page, check if it's a different checkpoint
            # This helps us detect chained checkpoints
            page_content = self.page.content().lower()
            
            # Different checkpoint types that might be chained
            checkpoint_types = {
                'human_verification': ['confirm you\'re human', 'account integrity'],
                'puzzle_verification': ['solve this puzzle', 'start puzzle', 'protecting your account'],
                'phone_verification': ['confirm your phone', 'phone number'],
                'device_verification': ['save device', 'remember browser']
            }
            
            current_checkpoint_type = None
            for checkpoint_type, indicators in checkpoint_types.items():
                if any(indicator in page_content for indicator in indicators):
                    current_checkpoint_type = checkpoint_type
                    break
            
            if current_checkpoint_type:
                logger.info(f"⏭️ Still on checkpoint page - detected: {current_checkpoint_type}")
                return False  # Not completed, but we know what type it is
            
            logger.info("⏳ Still on checkpoint page - type unclear")
            return False
            
        except Exception as e:
            logger.error(f"💥 Error checking checkpoint completion: {e}")
            return False
        
    def handle_human_verification_checkpoint(self):
        """Handle 'confirm you're human' checkpoint - NEW HANDLER"""
        try:
            logger.info("🤖 Handling 'confirm you're human' checkpoint...")
            
            # Take screenshot for debugging
            self.page.screenshot(path=f"human_verification_{int(time.time())}.png")
            
            # This type typically just needs clicking "Continue"
            continue_selectors = [
                # Most common selectors for Continue button
                'div[role="button"]:has-text("Continue")',
                'button:has-text("Continue")',
                '[aria-label="Continue"]',
                
                # Alternative selectors
                'div[role="button"]:has-text("Submit")',
                'button:has-text("Submit")',
                'div[role="button"]:has-text("Confirm")',
                'button:has-text("Confirm")',
                
                # Generic submit buttons
                'button[type="submit"]',
                'input[type="submit"]',
                
                # Look for any blue button (Facebook's primary button color)
                'div[role="button"][style*="background"]',
                'button[style*="background"]'
            ]
            
            for selector in continue_selectors:
                try:
                    button = self.page.query_selector(selector)
                    if button and button.is_visible():
                        logger.info(f"✅ Found Continue button: {selector}")
                        button.click()
                        logger.info("🤖 Clicked Continue button for human verification")
                        time.sleep(random.uniform(3, 5))
                        
                        # Check if checkpoint was completed
                        if self.check_checkpoint_completion():
                            logger.info("✅ Human verification completed successfully")
                            return True
                        else:
                            logger.info("⏳ Waiting longer for human verification to process...")
                            time.sleep(5)
                            if self.check_checkpoint_completion():
                                logger.info("✅ Human verification completed after wait")
                                return True
                except Exception as e:
                    logger.warning(f"⚠️ Error clicking button {selector}: {e}")
                    continue
            
            # If no specific button found, try generic approach
            logger.info("🔍 No specific Continue button found, trying generic approach...")
            return self.handle_generic_checkpoint()
            
        except Exception as e:
            logger.error(f"💥 Error in human verification: {e}")
            return False

    def login_facebook_robust(self, login_credential, password, twofa_secret=None):
        """Enhanced login with comprehensive chained checkpoint handling"""
        try:
            # Ensure all credentials are strings
            login_credential = str(login_credential).strip()
            password = str(password).strip()
            
            logger.info(f"🔑 Attempting login for: {login_credential}")
            logger.info(f"🔑 Password length: {len(password)} characters")
            logger.info(f"🔑 2FA Secret available: {'✅' if twofa_secret else '❌'}")
            
            # Navigate to Facebook with robust method
            if not self.navigate_to_facebook_robust():
                logger.error("❌ Failed to navigate to Facebook")
                return False
            
            # Wait for page to be ready
            time.sleep(random.uniform(5, 8))
            
            # Handle cookie consent if present
            try:
                cookie_buttons = [
                    'button[data-cookiebanner="accept_only_essential_button"]',
                    'button:has-text("Allow essential and optional cookies")',
                    'button:has-text("Accept All Cookies")',
                    'div[role="button"]:has-text("Accept")'
                ]
                
                for selector in cookie_buttons:
                    cookie_button = self.page.query_selector(selector)
                    if cookie_button and cookie_button.is_visible():
                        cookie_button.click()
                        time.sleep(2)
                        logger.info("✅ Accepted cookies")
                        break
            except:
                pass
            
            # Check if already logged in
            if self.page.query_selector('[aria-label="Account"]') or self.page.query_selector('[data-testid="nav_account_switcher"]'):
                logger.info("Already logged in")
                return True
            
            # Fill login form
            logger.info("🔍 Looking for login form...")
            
            # Find and fill email/phone input
            email_selectors = [
                'input[name="email"]',
                'input[type="email"]',
                'input[data-testid="royal_email"]',
                'input[placeholder*="Email"]',
                'input[placeholder*="Phone"]',
                'input[autocomplete="username"]'
            ]
            
            email_input = None
            for selector in email_selectors:
                email_input = self.page.query_selector(selector)
                if email_input and email_input.is_visible():
                    logger.info(f"✅ Found email/phone input: {selector}")
                    break
            
            if not email_input:
                logger.error("❌ Could not find email/phone input field")
                self.page.screenshot(path="no_email_input.png")
                return False
            
            try:
                email_input.click()
                time.sleep(0.5)
                email_input.fill("")
                time.sleep(0.5)
                email_input.fill(login_credential)
                time.sleep(random.uniform(1, 2))
                logger.info(f"✅ Filled login credential")
            except Exception as e:
                logger.error(f"❌ Error filling credential: {e}")
                return False
            
            # Find and fill password input
            password_selectors = [
                'input[name="pass"]',
                'input[type="password"]',
                'input[data-testid="royal_pass"]',
                'input[placeholder*="Password"]',
                'input[autocomplete="current-password"]'
            ]
            
            password_input = None
            for selector in password_selectors:
                password_input = self.page.query_selector(selector)
                if password_input and password_input.is_visible():
                    logger.info(f"✅ Found password input: {selector}")
                    break
            
            if not password_input:
                logger.error("❌ Could not find password input field")
                self.page.screenshot(path="no_password_input.png")
                return False
            
            try:
                password_input.click()
                time.sleep(0.5)
                password_input.fill("")
                time.sleep(0.5)
                password_input.fill(password)
                time.sleep(random.uniform(1, 2))
                logger.info("✅ Filled password")
            except Exception as e:
                logger.error(f"❌ Error filling password: {e}")
                return False
            
            # Take screenshot before login
            try:
                self.page.screenshot(path="before_login_attempt.png")
                logger.info("📸 Screenshot saved: before_login_attempt.png")
            except:
                pass
            
            # Click login button
            login_selectors = [
                'button[name="login"]',
                'button[type="submit"]',
                'div[role="button"]:has-text("Log in")',
                'button:has-text("Log In")',
                'input[type="submit"]'
            ]
            
            login_clicked = False
            for selector in login_selectors:
                try:
                    button = self.page.query_selector(selector)
                    if button and button.is_visible():
                        button.click()
                        login_clicked = True
                        logger.info(f"✅ Clicked login button: {selector}")
                        break
                except:
                    continue
            
            if not login_clicked:
                logger.error("❌ Could not find or click login button")
                self.page.screenshot(path="no_login_button.png")
                return False
            
            # Wait for login to process
            logger.info("⏳ Waiting for login to process...")
            time.sleep(random.uniform(8, 12))
            
            # Take screenshot after login
            try:
                self.page.screenshot(path="after_login_attempt.png")
                logger.info("📸 Screenshot saved: after_login_attempt.png")
            except:
                pass
            
            # Check current state and handle all checkpoints
            current_url = self.page.url
            logger.info(f"🔍 Current URL after login: {current_url}")
            
            # IMPROVED: Handle checkpoints (including chained ones) with comprehensive handling
            if 'checkpoint' in current_url:
                logger.info("🚨 Checkpoint detected - using comprehensive chained checkpoint handling")
                
                # Pass account data for checkpoint handling
                account_data = {
                    'email': login_credential,
                    'twofa_secret': twofa_secret
                }
                
                # Handle ALL chained checkpoints
                if self.handle_facebook_checkpoint(account_data):
                    logger.info("✅ All checkpoints handled successfully")
                    # Continue with final verification below
                else:
                    logger.error("❌ Checkpoint handling failed")
                    return False
            
            # Handle standalone 2FA if present (not in checkpoint flow)
            elif ('two-factor' in current_url or 'two_step_verification' in current_url or
                self.page.query_selector('input[name="approvals_code"]')):
                logger.info("🔍 Standalone 2FA required")
                
                if self.handle_2fa_authentication(twofa_secret):
                    logger.info("✅ 2FA handled successfully")
                else:
                    logger.error("❌ 2FA handling failed")
                    return False
            
            # Handle save browser prompt
            try:
                save_buttons = [
                    'button:has-text("Save Browser")',
                    'button:has-text("Don\'t Save")',
                    'button:has-text("Not Now")',
                    'div[role="button"]:has-text("Not Now")'
                ]
                
                for selector in save_buttons:
                    button = self.page.query_selector(selector)
                    if button and button.is_visible():
                        button.click()
                        logger.info("Handled save browser prompt")
                        time.sleep(2)
                        break
            except:
                pass
            
            # FINAL VERIFICATION - Make sure we're actually logged in and past ALL checkpoints
            logger.info("🔍 Performing final login verification...")
            time.sleep(5)  # Give more time for all redirects to complete
            
            # Try to navigate to main Facebook to ensure we're fully logged in
            try:
                logger.info("🏠 Testing navigation to main Facebook...")
                self.page.goto('https://www.facebook.com', timeout=30000)
                time.sleep(5)
            except Exception as e:
                logger.warning(f"⚠️ Error navigating to main Facebook: {e}")
            
            final_url = self.page.url
            logger.info(f"🔍 Final URL after all processing: {final_url}")
            
            # CHECK FOR TRUE SUCCESS - Must not be on any security/verification pages
            login_successful = False
            
            # Method 1: Check we're NOT on any security pages
            security_indicators = ['checkpoint', 'verify', 'security', 'two_step_verification', 'login', 'recover']
            on_security_page = any(indicator in final_url.lower() for indicator in security_indicators)
            
            if not on_security_page:
                logger.info("✅ Not on any security/checkpoint pages")
                login_successful = True
            
            # Method 2: Check for positive success indicators
            success_indicators = [
                '[aria-label="Account"]',
                '[data-testid="nav_account_switcher"]',
                '[aria-label="Your profile"]',
                'div[role="banner"]',
                '[aria-label="Facebook"]'
            ]
            
            success_elements_found = 0
            for indicator in success_indicators:
                if self.page.query_selector(indicator):
                    success_elements_found += 1
                    logger.info(f"✅ Found success element: {indicator}")
            
            if success_elements_found >= 1:
                login_successful = True
            
            # Method 3: Check URL patterns for success
            success_url_patterns = [
                '?sk=welcome',
                '?sk=h_chr', 
                '/home',
                'facebook.com/?',
                'facebook.com/#',
                'facebook.com/checkpoint/1501092823525282/?next=https%3A%2F%2Fwww.facebook.com%2F%3Fsk%3Dwelcome%26lsrc%3Dlb'
            ]
            
            # SPECIAL CASE: If we're on the specific checkpoint URL with success params, that might be success
            if 'facebook.com' in final_url:
                # Check if we can access basic Facebook functionality
                try:
                    # Look for basic Facebook elements that indicate we're logged in
                    basic_elements = [
                        'div[role="main"]',
                        'nav',
                        '[data-testid="facebook"]',
                        'div[role="banner"]'
                    ]
                    
                    basic_elements_found = 0
                    for element in basic_elements:
                        if self.page.query_selector(element):
                            basic_elements_found += 1
                    
                    if basic_elements_found >= 2:
                        logger.info("✅ Found basic Facebook elements - likely logged in")
                        login_successful = True
                except:
                    pass
            
            # Final decision
            if login_successful:
                logger.info(f"✅ Login verification SUCCESSFUL: {login_credential}")
                logger.info(f"   Final URL: {final_url}")
                logger.info(f"   Success elements found: {success_elements_found}")
                logger.info(f"   On security page: {on_security_page}")
                return True
            else:
                logger.error(f"❌ Login verification FAILED: {login_credential}")
                logger.error(f"   Final URL: {final_url}")
                logger.error(f"   Success elements found: {success_elements_found}")
                logger.error(f"   Still on security page: {on_security_page}")
                
                # Take final failure screenshot
                self.page.screenshot(path=f"login_verification_failed_{int(time.time())}.png")
                return False
                
        except Exception as e:
            logger.error(f"💥 Error during enhanced login: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def handle_2fa_authentication(self, twofa_secret):
        """Handle 2FA authentication with fallback options"""
        try:
            logger.info("🔍 Handling 2FA authentication...")
            
            # Take screenshot for debugging
            try:
                self.page.screenshot(path=f"2fa_page_{int(time.time())}.png")
                logger.info("📸 2FA page screenshot saved")
            except:
                pass
            
            # Method 1: Use provided 2FA secret if available
            if twofa_secret:
                logger.info("🔑 Using provided 2FA secret")
                code = self.get_2fa_code(twofa_secret)
                if code and self.enter_2fa_code(code):
                    return True
            
            # Method 2: Look for alternative verification methods
            logger.info("🔍 Looking for alternative 2FA methods...")
            
            # Check for "Try another way" or "Use different method" options
            alternative_methods = [
                'div[role="button"]:has-text("Try another way")',
                'div[role="button"]:has-text("Use a different method")',
                'a:has-text("Try another way")',
                'a:has-text("Use a different method")',
                '[aria-label="Try another way"]',
                'div[role="button"]:has-text("Get help")'
            ]
            
            for selector in alternative_methods:
                try:
                    button = self.page.query_selector(selector)
                    if button and button.is_visible():
                        logger.info(f"🔄 Found alternative method: {selector}")
                        button.click()
                        time.sleep(3)
                        
                        # After clicking, look for other options
                        if self.handle_alternative_2fa_methods():
                            return True
                except:
                    continue
            
            # Method 3: Look for "Skip" or "Not now" options
            logger.info("🔍 Looking for skip options...")
            skip_selectors = [
                'div[role="button"]:has-text("Skip")',
                'div[role="button"]:has-text("Not now")',
                'div[role="button"]:has-text("Skip for now")',
                'a:has-text("Skip")',
                'a:has-text("Not now")',
                '[aria-label="Skip"]',
                'div[role="button"]:has-text("Continue without")'
            ]
            
            for selector in skip_selectors:
                try:
                    button = self.page.query_selector(selector)
                    if button and button.is_visible():
                        logger.info(f"⏭️ Found skip option: {selector}")
                        button.click()
                        time.sleep(5)
                        
                        # Check if we're past the 2FA page
                        current_url = self.page.url
                        if '2fa' not in current_url.lower() and 'two' not in current_url.lower():
                            logger.info("✅ Successfully skipped 2FA")
                            return True
                except:
                    continue
            
            # Method 4: Try to request SMS code to the phone number
            logger.info("📱 Looking for SMS verification option...")
            if self.try_sms_verification():
                return True
            
            # Method 5: Look for backup options or recovery
            logger.info("🔄 Looking for backup verification methods...")
            backup_selectors = [
                'div[role="button"]:has-text("Use backup codes")',
                'div[role="button"]:has-text("Use recovery")',
                'a:has-text("Use backup codes")',
                'div[role="button"]:has-text("Get codes via SMS")',
                'div[role="button"]:has-text("Text me a login code")'
            ]
            
            for selector in backup_selectors:
                try:
                    button = self.page.query_selector(selector)
                    if button and button.is_visible():
                        logger.info(f"🔄 Found backup method: {selector}")
                        button.click()
                        time.sleep(3)
                        
                        if self.handle_sms_code_verification():
                            return True
                except:
                    continue
            
            logger.error("❌ All 2FA methods exhausted - cannot proceed")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error in 2FA handling: {e}")
    
    def handle_alternative_2fa_methods(self):
        """Handle alternative 2FA verification methods"""
        try:
            time.sleep(3)  # Wait for page to load
            
            # Look for SMS option
            sms_selectors = [
                'div[role="button"]:has-text("Text")',
                'div[role="button"]:has-text("SMS")',
                'div[role="button"]:has-text("Send SMS")',
                'div[role="button"]:has-text("Text me")',
                'label:has-text("Text") input[type="radio"]'
            ]
            
            for selector in sms_selectors:
                try:
                    element = self.page.query_selector(selector)
                    if element and element.is_visible():
                        logger.info("📱 Found SMS verification option")
                        element.click()
                        time.sleep(2)
                        
                        # Look for continue/send button
                        continue_buttons = [
                            'div[role="button"]:has-text("Continue")',
                            'div[role="button"]:has-text("Send")',
                            'button:has-text("Continue")',
                            'button:has-text("Send")'
                        ]
                        
                        for continue_selector in continue_buttons:
                            try:
                                continue_btn = self.page.query_selector(continue_selector)
                                if continue_btn and continue_btn.is_visible():
                                    continue_btn.click()
                                    logger.info("📱 Requested SMS verification code")
                                    time.sleep(3)
                                    return self.handle_sms_code_verification()
                            except:
                                continue
                except:
                    continue
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error handling alternative 2FA methods: {e}")
            return False

    def try_sms_verification(self):
        """Try to use SMS verification"""
        try:
            # Look for SMS-related buttons on the current page
            sms_buttons = [
                'div[role="button"]:has-text("Get codes via SMS")',
                'div[role="button"]:has-text("Text me a login code")',
                'div[role="button"]:has-text("Send code via SMS")',
                'a:has-text("Get codes via SMS")',
                'div[role="button"]:has-text("Text me")'
            ]
            
            for selector in sms_buttons:
                try:
                    button = self.page.query_selector(selector)
                    if button and button.is_visible():
                        logger.info(f"📱 Found SMS option: {selector}")
                        button.click()
                        time.sleep(5)
                        
                        return self.handle_sms_code_verification()
                except:
                    continue
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error trying SMS verification: {e}")
            return False

    def handle_sms_code_verification(self):
        """Handle SMS code verification"""
        try:
            logger.info("📱 Waiting for SMS verification code...")
            
            # Wait longer for SMS to arrive
            time.sleep(10)
            
            # Look for code input field
            code_selectors = [
                'input[name="approvals_code"]',
                'input[aria-label*="code"]',
                'input[placeholder*="code"]',
                'input[type="text"]',
                'input[autocomplete="one-time-code"]'
            ]
            
            code_input = None
            for selector in code_selectors:
                try:
                    input_elem = self.page.query_selector(selector)
                    if input_elem and input_elem.is_visible():
                        code_input = input_elem
                        logger.info(f"📱 Found SMS code input: {selector}")
                        break
                except:
                    continue
            
            if not code_input:
                logger.error("❌ Could not find SMS code input field")
                return False
            
            # Try to get SMS code (this would need to be integrated with your SMS service)
            logger.info("📱 SMS code input found - would need SMS service integration")
            logger.warning("⚠️ SMS verification requires SMS service integration - skipping for now")
            
            # For now, try to skip or continue without the code
            skip_selectors = [
                'div[role="button"]:has-text("Skip")',
                'div[role="button"]:has-text("Not now")',
                'a:has-text("Skip")'
            ]
            
            for selector in skip_selectors:
                try:
                    button = self.page.query_selector(selector)
                    if button and button.is_visible():
                        logger.info("⏭️ Skipping SMS verification")
                        button.click()
                        time.sleep(5)
                        return True
                except:
                    continue
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error in SMS code verification: {e}")
            return False

    def enter_2fa_code(self, code):
        """Enter 2FA code and submit"""
        try:
            logger.info(f"🔑 Entering 2FA code: {code}")
            
            # Find 2FA input
            twofa_selectors = [
                'input[name="approvals_code"]',
                'input[aria-label*="code"]',
                'input[placeholder*="code"]',
                'input[type="text"]',
                'input[autocomplete="one-time-code"]'
            ]
            
            twofa_input = None
            for selector in twofa_selectors:
                try:
                    input_elem = self.page.query_selector(selector)
                    if input_elem and input_elem.is_visible():
                        twofa_input = input_elem
                        logger.info(f"✅ Found 2FA input: {selector}")
                        break
                except:
                    continue
            
            if not twofa_input:
                logger.error("❌ Could not find 2FA input field")
                return False
            
            # Enter code
            twofa_input.fill(code)
            time.sleep(1)
            
            # Submit
            submit_selectors = [
                'button[type="submit"]',
                'div[role="button"]:has-text("Continue")',
                'div[role="button"]:has-text("Submit")',
                'button:has-text("Continue")',
                'button:has-text("Submit")'
            ]
            
            for selector in submit_selectors:
                try:
                    button = self.page.query_selector(selector)
                    if button and button.is_visible():
                        button.click()
                        logger.info("✅ Submitted 2FA code")
                        time.sleep(8)
                        
                        # Check if successful
                        current_url = self.page.url
                        if ('two-factor' not in current_url and 'two_step_verification' not in current_url and 
                            'checkpoint' not in current_url):
                            logger.info("✅ 2FA authentication successful")
                            return True
                        break
                except:
                    continue
            
            logger.error("❌ 2FA code submission failed")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error entering 2FA code: {e}")
            return False

    def get_2fa_code(self, secret_key):
        """Generate 2FA code"""
        try:
            if secret_key.startswith('http') and 'token=' in secret_key:
                secret_key = secret_key.split('token=')[1].split('&')[0]
            
            import pyotp
            totp = pyotp.TOTP(secret_key)
            code = totp.now()
            logger.info(f"Generated 2FA code: {code}")
            return code
        except Exception as e:
            logger.error(f"Error generating 2FA code: {e}")
            return None
    
    def generate_ai_post(self):
        """Generate AI post about cars (5 lines)"""
        try:
            prompt = """Generate a casual Facebook post about cars. Requirements:
            - Exactly 5 lines long
            - Sound like a regular person, not a car dealer
            - Include 1-2 relevant emojis
            - Topics can include: car maintenance tips, driving experiences, car shows, classic cars, new models, road trips, etc.
            - Keep it engaging and authentic
            - No hashtags or promotional language
            
            Example format:
            Just finished washing my car and wow what a difference! 🚗
            Nothing beats that fresh clean feeling after a good wash and wax.
            Took me about 2 hours but totally worth it.
            Anyone else obsessed with keeping their ride spotless?
            Ready for another road trip adventure! ✨"""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.8
            )
            
            post = response.choices[0].message.content.strip()
            logger.info("✅ Generated AI post about cars")
            return post
            
        except Exception as e:
            logger.error(f"❌ Error generating AI post: {e}")
            # Fallback posts
            fallback_posts = [
                "Just saw the most beautiful classic Mustang at the gas station today! 🚗\nThe owner let me take a closer look at the engine.\nYou can tell this car has been loved and maintained perfectly.\nMakes me appreciate good craftsmanship even more.\nClassic cars just have that special something! ✨",
                
                "Finally got my oil changed after putting it off for weeks! 🔧\nNothing like taking care of your car properly.\nThe mechanic said everything looks great under the hood.\nRegular maintenance really does make all the difference.\nFeeling good about my reliable ride! 🚙"
            ]
            return random.choice(fallback_posts)
    
    def generate_ai_comment(self, post_text):
        """Generate AI comment for a Facebook post"""
        try:
            prompt = f"""Generate a casual, friendly comment for this Facebook post: "{post_text}"

            Requirements:
            - Sound like a regular person commenting
            - Keep it under 20 words
            - Include 1-2 relevant emojis
            - Be positive and engaging
            - Match the tone of the post
            - Don't be overly enthusiastic
            
            Just return the comment text, nothing else."""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=30,
                temperature=0.8
            )
            
            comment = response.choices[0].message.content.strip()
            logger.info("✅ Generated AI comment")
            return comment
            
        except Exception as e:
            logger.error(f"❌ Error generating AI comment: {e}")
            # Fallback comments
            fallback_comments = [
                "Nice! 👍", "Love this! 😊", "So cool! 🔥", "Awesome! ✨", 
                "Great post! 👍", "This is great! 💯", "Love it! ❤️", "So true! 😄"
            ]
            return random.choice(fallback_comments)
    
    def load_account_profile(self, account_id):
        """Load account profile from JSON file"""
        try:
            profile_file = f"account_data/profiles/account_{account_id}_profile.json"
            if os.path.exists(profile_file):
                with open(profile_file, 'r') as f:
                    return json.load(f)
            return None
        except Exception as e:
            logger.error(f"❌ Error loading account profile: {e}")
            return None
    
    def cleanup_browser(self):
        """Clean up browser resources"""
        try:
            if hasattr(self, 'page') and self.page:
                self.page.close()
            if hasattr(self, 'context') and self.context:
                self.context.close()
            if hasattr(self, 'browser') and self.browser:
                self.browser.close()
            if hasattr(self, 'playwright') and self.playwright:
                self.playwright.stop()
            logger.info("🧹 Browser cleanup completed")
        except Exception as e:
            logger.warning(f"⚠️ Error during browser cleanup: {e}")
    
    def run_enhanced_warmup_cycle_with_mandatory_proxy(self, account):
        """Main entry point for enhanced warmup with MANDATORY proxy"""
        try:
            account_id = account['account_id']
            current_phase = account.get('warmup_phase', 'phase_1')
            
            logger.info(f"🚀 Starting enhanced warmup for account {account_id} (Phase: {current_phase})")
            logger.info("⚠️ MANDATORY PROXY MODE: Will fail if proxy doesn't work")
            
            # Determine login credential
            login_credential = self.determine_login_credential(account)
            password = account['password']
            
            # Get MANDATORY proxy info
            proxy_info = self.get_account_proxy_mandatory(account)
            if not proxy_info:
                logger.error(f"❌ No working proxy available for account {account_id} - warmup aborted")
                return False
            
            # Setup browser with MANDATORY proxy (no fallback)
            if not self.setup_browser_with_mandatory_proxy(proxy_info):
                logger.error(f"❌ Browser setup with mandatory proxy failed for account {account_id}")
                return False
            
            # Login to Facebook with robust method
            twofa_secret = account.get('twofa_secret')
            if not self.login_facebook_robust(login_credential, password, twofa_secret):
                logger.error(f"❌ Login failed for account {account_id}")
                self.cleanup_browser()
                return False
            
            logger.info(f"✅ Login successful for account {account_id}")
            
            # Verify we're still using US location after login
            logger.info("🔍 Verifying US location after login...")
            try:
                self.page.goto('https://www.facebook.com/marketplace', timeout=30000)
                time.sleep(3)
                page_content = self.page.content()
                
                if any(indicator in page_content.lower() for indicator in ['egypt', 'مصر', 'km ']):
                    logger.error("❌ Account shows Egypt location after login - warmup aborted")
                    self.cleanup_browser()
                    return False
                else:
                    logger.info("✅ Account maintains US location after login")
            except:
                logger.warning("⚠️ Could not verify location, proceeding...")
            
            # Run enhanced warmup activities
            success = self.enhanced_warmup_cycle(account)
            
            # Cleanup browser
            self.cleanup_browser()
            
            if success:
                # Update account status
                self.db.update_account_status(account_id, "warming", "Enhanced warmup completed successfully with US proxy")
                logger.info(f"✅ Enhanced warmup successful for account {account_id}")
            else:
                self.db.update_account_status(account_id, "warmup_failed", "Enhanced warmup failed")
                logger.error(f"❌ Enhanced warmup failed for account {account_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error in enhanced warmup cycle: {e}")
            # Make sure to cleanup browser on error
            self.cleanup_browser()
            return False
   
    def get_working_us_proxy_for_warmup(self):
        """Get working US proxy for warmup using SAME methods as account manager"""
        try:
            logger.info("🎯 Getting working US proxy for warmup (using account manager methods)...")
            
            # Use the enhanced account manager's proven proxy methods
            # First try to get a basic working proxy
            proxy = self.get_soax_proxy_with_fallback_warmup()
            if not proxy:
                logger.error("❌ Could not get any working proxy using fallback methods")
                return None
            
            logger.info("✅ Got basic proxy connectivity for warmup")
            
            # Try to verify US location (but don't fail if verification fails)
            logger.info("🔍 Attempting US location verification for warmup...")
            verification = self.verify_us_proxy_location_fast_warmup(proxy)
            
            if verification['verified']:
                logger.info("🎉 Perfect! Warmup proxy verified as US-based")
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
                logger.warning("⚠️ Could not verify US location for warmup, but proxy is working")
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
            
            logger.info("🎯 Warmup proxy ready for use!")
            logger.info(f"   📡 Endpoint: {proxy.get('endpoint')}")
            logger.info(f"   🌍 Location: {proxy.get('verified_city', 'Unknown')}, {proxy.get('verified_region', 'Unknown')}")
            logger.info(f"   🇺🇸 US Verified: {'✅' if proxy.get('us_verified') else '❓ (Assumed)'}")
            
            return proxy
            
        except Exception as e:
            logger.error(f"💥 Error getting working US proxy for warmup: {e}")
            return None
        
    def get_soax_proxy_with_fallback_warmup(self):
        """Get SOAX proxy with multiple fallback configurations - WARMUP VERSION"""
        try:
            if not (hasattr(self.config, 'SOAX_USERNAME') and self.config.SOAX_USERNAME and
                    hasattr(self.config, 'SOAX_PASSWORD') and self.config.SOAX_PASSWORD):
                logger.error("❌ SOAX credentials not found in config")
                return None
            
            # Try different SOAX configurations (same as account manager)
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
                    
                    logger.info(f"🔧 Warmup trying method: {method}")
                    
                    if method == 'parent_class':
                        # Try parent class proxy manager
                        if hasattr(self, 'proxy_manager') and hasattr(self.proxy_manager, 'get_fresh_proxy'):
                            proxy = self.proxy_manager.get_fresh_proxy(country='US')
                            if proxy:
                                logger.info("✅ Got warmup proxy from parent class")
                                return proxy
                        continue
                    
                    elif method == 'soax_city':
                        # Try specific city targeting
                        for location in config['cities']:
                            session_id = f"warmup_{random.randint(100000, 999999)}"
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
                            
                            logger.info(f"🏙️ Warmup testing {location['city']}, {location['region']}...")
                            
                            # Quick connectivity test
                            if self.test_proxy_connectivity_warmup(proxy, timeout=8):
                                logger.info(f"✅ Warmup connectivity confirmed for {location['city']}")
                                return proxy
                            else:
                                logger.warning(f"⚠️ No warmup connectivity for {location['city']}")
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
                            
                            logger.info(f"🔧 Warmup testing username format: {username_format[:50]}...")
                            
                            # Quick connectivity test
                            if self.test_proxy_connectivity_warmup(proxy, timeout=8):
                                logger.info(f"✅ Warmup connectivity confirmed for username format")
                                return proxy
                            else:
                                logger.warning(f"⚠️ No warmup connectivity for this username format")
                                continue
                
                except Exception as e:
                    logger.warning(f"⚠️ Warmup method {method} failed: {e}")
                    continue
            
            logger.error("❌ All SOAX proxy methods failed for warmup")
            return None
            
        except Exception as e:
            logger.error(f"💥 Error getting SOAX proxy for warmup: {e}")
            return None    

    def test_proxy_connectivity_warmup(self, proxy, timeout=10):
        """Quick test to see if proxy is working at all - WARMUP VERSION"""
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
                    logger.info(f"🔧 Warmup testing connectivity to {url}...")
                    response = requests.get(
                        url, 
                        proxies=proxy_config, 
                        timeout=timeout,
                        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                    )
                    
                    if response.status_code == 200:
                        logger.info(f"✅ Warmup proxy connectivity confirmed via {url}")
                        return True
                        
                except Exception as e:
                    logger.warning(f"⚠️ Warmup test to {url} failed: {str(e)[:100]}")
                    continue
            
            logger.error("❌ All warmup connectivity tests failed")
            return False
            
        except Exception as e:
            logger.error(f"💥 Warmup connectivity test error: {e}")
            return False

    def verify_us_proxy_location_fast_warmup(self, proxy):
        """Fast US proxy verification with shorter timeouts - WARMUP VERSION"""
        try:
            logger.info("🌍 Fast US location verification for warmup...")
            
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
                    logger.info(f"🔍 Warmup checking {service['url']}...")
                    
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
                        
                        logger.info(f"🔍 Warmup IP: {ip}")
                        logger.info(f"🏳️ Warmup Country: {country}")
                        logger.info(f"🗺️ Warmup Region: {region}")
                        logger.info(f"🏙️ Warmup City: {city}")
                        
                        # Check if it's US-based
                        us_indicators = ['US', 'USA', 'UNITED STATES', 'AMERICA']
                        if any(indicator in country.upper() for indicator in us_indicators):
                            logger.info("✅ Warmup proxy verified as US-based!")
                            return {
                                'verified': True,
                                'ip': ip,
                                'country': country,
                                'region': region,
                                'city': city,
                                'service': service['url']
                            }
                        else:
                            logger.warning(f"⚠️ Warmup proxy is not US-based: {country}")
                            # Don't break here, try other services in case this one is wrong
                            
                except requests.exceptions.Timeout:
                    logger.warning(f"⏰ Warmup timeout for {service['url']}")
                    continue
                except Exception as e:
                    logger.warning(f"⚠️ Warmup service {service['url']} failed: {str(e)[:100]}")
                    continue
            
            logger.error("❌ Could not verify warmup proxy as US-based with any service")
            return {'verified': False}
            
        except Exception as e:
            logger.error(f"💥 Error verifying warmup proxy location: {e}")
            return {'verified': False}

    def setup_browser_with_robust_proxy(self, proxy):
        """Setup browser with ROBUST proxy (same as account manager) - no fallback"""
        try:
            from playwright.sync_api import sync_playwright
            
            if hasattr(self, 'playwright'):
                try:
                    self.playwright.stop()
                except:
                    pass
            
            logger.info("✅ Proxy connectivity confirmed for warmup - setting up browser...")
            
            self.playwright = sync_playwright().start()
            
            # Use the working proxy (no fallback to direct connection)
            proxy_config = None
            if proxy and proxy.get('username'):
                proxy_config = {
                    'server': f"http://{proxy['endpoint']}",
                    'username': proxy['username'],
                    'password': proxy['password']
                }
                logger.info(f"🌐 Using ROBUST proxy for warmup: {proxy['endpoint']}")
            else:
                logger.error("❌ No valid proxy configuration for warmup - aborted")
                return False
            
            try:
                # Launch browser with proxy (no fallback)
                self.browser = self.playwright.chromium.launch(
                    headless=False,
                    args=[
                        '--no-sandbox',
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage'
                    ],
                    proxy=proxy_config,
                    timeout=60000  # 1 minute timeout
                )
                
                # Create context with US settings
                context_options = {
                    'viewport': {'width': 1366, 'height': 768},
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'locale': 'en-US',
                    'timezone_id': 'America/Phoenix',
                    'geolocation': {'latitude': 33.4484, 'longitude': -112.0740},
                    'permissions': ['geolocation']
                }
                
                self.context = self.browser.new_context(**context_options)
                
                # Set reasonable timeouts
                self.context.set_default_timeout(60000)  # 1 minute
                self.context.set_default_navigation_timeout(120000)  # 2 minutes
                
                self.page = self.context.new_page()
                
                # CRITICAL: Verify proxy is working with actual Facebook access
                logger.info("🔍 Verifying robust proxy works with Facebook...")
                if not self.verify_proxy_with_facebook_warmup():
                    logger.error("❌ Robust proxy failed Facebook verification - warmup aborted")
                    self.cleanup_browser()
                    return False
                
                logger.info(f"✅ Browser setup successful with ROBUST proxy for warmup")
                return True
                
            except Exception as e:
                logger.error(f"❌ Browser setup with robust proxy failed: {e}")
                logger.error("❌ No fallback - warmup process aborted")
                try:
                    if hasattr(self, 'browser'):
                        self.browser.close()
                except:
                    pass
                return False
            
        except Exception as e:
            logger.error(f"❌ Error setting up browser with robust proxy: {e}")
            return False

    def verify_proxy_with_facebook_warmup(self):
        """Verify proxy actually works with Facebook for warmup"""
        try:
            logger.info("📘 Testing robust proxy with Facebook access...")
            
            # Test Facebook accessibility
            self.page.goto('https://www.facebook.com', timeout=30000)
            time.sleep(3)
            
            # Check if page loaded
            current_url = self.page.url
            if 'facebook.com' not in current_url:
                logger.error("❌ Failed to reach Facebook through robust proxy")
                return False
            
            # Quick marketplace test to verify location
            try:
                self.page.goto('https://www.facebook.com/marketplace', timeout=30000)
                time.sleep(3)
                
                page_content = self.page.content()
                
                # Check for US indicators
                us_indicators = ['phoenix', 'arizona', 'united states', 'usa', 'miles', 'mi ']
                egypt_indicators = ['egypt', 'مصر', 'القاهرة', 'بني سويف', 'km ']
                
                us_detected = any(indicator in page_content.lower() for indicator in us_indicators)
                egypt_detected = any(indicator in page_content.lower() for indicator in egypt_indicators)
                
                if us_detected and not egypt_detected:
                    logger.info("✅ Robust proxy verified: Facebook shows US location for warmup")
                    return True
                elif egypt_detected:
                    logger.error("❌ Robust proxy failed: Facebook shows Egypt location")
                    return False
                else:
                    logger.warning("⚠️ Location unclear for warmup, but Facebook accessible")
                    return True  # Allow to proceed if Facebook is accessible
                    
            except Exception as e:
                logger.warning(f"⚠️ Marketplace test failed for warmup: {e}")
                # If marketplace test fails but Facebook is accessible, proceed
                return True
            
        except Exception as e:
            logger.error(f"❌ Facebook verification failed for warmup: {e}")
            return False

    def run_enhanced_warmup_cycle_with_robust_proxy(self, account):
        """Main entry point for enhanced warmup with ROBUST proxy (like account manager)"""
        try:
            account_id = account['account_id']
            current_phase = account.get('warmup_phase', 'phase_1')
            
            logger.info(f"🚀 Starting enhanced warmup for account {account_id} (Phase: {current_phase})")
            logger.info("🎯 ROBUST PROXY MODE: Using same methods as account manager")
            
            # Determine login credential
            login_credential = self.determine_login_credential(account)
            password = account['password']
            
            # Get ROBUST working proxy using same methods as account manager
            proxy_info = self.get_working_us_proxy_for_warmup()
            if not proxy_info:
                logger.error(f"❌ No working proxy available for account {account_id} - warmup aborted")
                return False
            
            # Setup browser with ROBUST proxy (no fallback)
            if not self.setup_browser_with_robust_proxy(proxy_info):
                logger.error(f"❌ Browser setup with robust proxy failed for account {account_id}")
                return False
            
            # Login to Facebook with robust method
            twofa_secret = account.get('twofa_secret')
            if not self.login_facebook_robust(login_credential, password, twofa_secret):
                logger.error(f"❌ Login failed for account {account_id}")
                self.cleanup_browser()
                return False
            
            logger.info(f"✅ Login successful for account {account_id}")
            
            # Verify we're still using US location after login
            logger.info("🔍 Verifying US location after login...")
            try:
                self.page.goto('https://www.facebook.com/marketplace', timeout=30000)
                time.sleep(3)
                page_content = self.page.content()
                
                if any(indicator in page_content.lower() for indicator in ['egypt', 'مصر', 'km ']):
                    logger.error("❌ Account shows Egypt location after login - warmup aborted")
                    self.cleanup_browser()
                    return False
                else:
                    logger.info("✅ Account maintains US location after login")
            except:
                logger.warning("⚠️ Could not verify location, proceeding...")
            
            # Run enhanced warmup activities
            success = self.enhanced_warmup_cycle(account)
            
            # Cleanup browser
            self.cleanup_browser()
            
            if success:
                # Update account status
                self.db.update_account_status(account_id, "warming", "Enhanced warmup completed successfully with robust US proxy")
                logger.info(f"✅ Enhanced warmup successful for account {account_id}")
            else:
                self.db.update_account_status(account_id, "warmup_failed", "Enhanced warmup failed")
                logger.error(f"❌ Enhanced warmup failed for account {account_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error in enhanced warmup cycle: {e}")
            # Make sure to cleanup browser on error
            self.cleanup_browser()
            return False

    def enhanced_warmup_cycle(self, account):
        """Run enhanced warmup cycle with all new features"""
        try:
            account_id = account['account_id']
            logger.info(f"🚀 Starting enhanced warmup activities for account {account_id}")
            
            # Step 1: Check and handle profile picture
            logger.info("🖼️ Step 1: Profile picture management")
            pic_status = self.check_profile_picture_status(account)
            
            if pic_status == 'needs_generation':
                logger.info("🎨 Generating new profile picture...")
                image_path = self.generate_ai_profile_picture(account)
                if image_path:
                    # Update account record with new image path
                    account['profile_picture'] = image_path
                    pic_status = 'needs_upload'
            
            if pic_status == 'needs_upload':
                logger.info("📤 Uploading profile picture...")
                image_path = account.get('profile_picture', '')
                if image_path and self.upload_profile_picture_to_facebook(image_path):
                    self.mark_profile_picture_uploaded(account_id)
                    logger.info("✅ Profile picture uploaded successfully")
                else:
                    logger.warning("⚠️ Profile picture upload failed")
            
            time.sleep(random.uniform(3, 6))
            
            # Step 2: Create car post
            logger.info("📝 Step 2: Creating AI car post...")
            if self.create_car_post():
                logger.info("✅ Car post created successfully")
            else:
                logger.warning("⚠️ Car post creation failed")
            
            time.sleep(random.uniform(5, 10))
            
            # Step 3: Add friends
            logger.info("👥 Step 3: Adding friends...")
            friends_added = self.add_friends()
            logger.info(f"✅ Added {friends_added} friends")
            
            time.sleep(random.uniform(5, 10))
            
            # Step 4: Join groups
            logger.info("🔗 Step 4: Joining target groups...")
            groups_joined = self.join_target_groups()
            logger.info(f"✅ Joined {groups_joined} groups")
            
            time.sleep(random.uniform(5, 10))
            
            # Step 5: Return to home and scroll/like
            logger.info("📱 Step 5: Scrolling and liking posts...")
            posts_liked = self.scroll_and_like_posts_enhanced()
            logger.info(f"✅ Liked {posts_liked} posts")
            
            time.sleep(random.uniform(3, 8))
            
            # Step 6: Comment on posts with AI
            logger.info("💬 Step 6: AI commenting on posts...")
            comments_added = self.comment_on_posts_with_ai()
            logger.info(f"✅ Added {comments_added} AI comments")
            
            # Log activity summary
            activity_summary = {
                'profile_picture': pic_status,
                'car_post': 'created',
                'friends_added': friends_added,
                'groups_joined': groups_joined,
                'posts_liked': posts_liked,
                'comments_added': comments_added,
                'completed_at': datetime.now().isoformat()
            }
            
            self.db.log_account_activity(
                account_id, 
                "enhanced_warmup_completed", 
                True, 
                json.dumps(activity_summary)
            )
            
            logger.info(f"🎉 Enhanced warmup completed for account {account_id}")
            logger.info(f"📊 Summary: {friends_added} friends, {groups_joined} groups, {posts_liked} likes, {comments_added} comments")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error in enhanced warmup cycle: {e}")
            self.db.log_account_activity(account_id, "enhanced_warmup_failed", False, str(e))
            return False
    
    def upload_profile_picture_to_facebook(self, image_path):
        """Upload profile picture to Facebook"""
        try:
            logger.info(f"📤 Uploading profile picture to Facebook: {image_path}")
            
            if not os.path.exists(image_path):
                logger.error(f"❌ Image file not found: {image_path}")
                return False
            
            # Navigate to profile
            self.page.goto('https://www.facebook.com/me', timeout=60000)
            time.sleep(random.uniform(3, 5))
            
            # Look for profile picture area or camera icon
            profile_pic_selectors = [
                '[data-testid="profile-photo-change-button"]',
                '[aria-label="Add a profile picture"]',
                '[aria-label="Update profile picture"]',
                'div[role="button"]:has-text("Add profile picture")',
                'svg[aria-label="Camera"]'
            ]
            
            clicked = False
            for selector in profile_pic_selectors:
                try:
                    element = self.page.query_selector(selector)
                    if element and element.is_visible():
                        element.click()
                        logger.info(f"📸 Clicked profile picture button: {selector}")
                        clicked = True
                        break
                except:
                    continue
            
            if not clicked:
                logger.warning("⚠️ Could not find profile picture upload button")
                return False
            
            time.sleep(random.uniform(2, 3))
            
            # Handle file upload
            try:
                # Look for file input or upload button
                upload_selectors = [
                    'input[type="file"]',
                    '[aria-label="Upload photo"]',
                    'div[role="button"]:has-text("Upload")'
                ]
                
                for selector in upload_selectors:
                    file_input = self.page.query_selector(selector)
                    if file_input:
                        file_input.set_input_files(image_path)
                        logger.info("📁 File uploaded successfully")
                        time.sleep(random.uniform(3, 5))
                        
                        # Look for save/confirm button
                        save_selectors = [
                            'div[role="button"]:has-text("Save")',
                            'div[role="button"]:has-text("Set as profile picture")',
                            '[aria-label="Save"]'
                        ]
                        
                        for save_selector in save_selectors:
                            save_btn = self.page.query_selector(save_selector)
                            if save_btn and save_btn.is_visible():
                                save_btn.click()
                                logger.info("💾 Clicked save button")
                                time.sleep(random.uniform(2, 4))
                                return True
                        
                        # If no explicit save button, upload might be automatic
                        logger.info("✅ Profile picture upload completed")
                        return True
                
                logger.error("❌ Could not find file upload input")
                return False
                
            except Exception as e:
                logger.error(f"❌ Error during file upload: {e}")
                return False
            
        except Exception as e:
            logger.error(f"❌ Error uploading profile picture: {e}")
            return False
    
    def mark_profile_picture_uploaded(self, account_id):
        """Mark profile picture as uploaded in database"""
        try:
            worksheet = self.db.get_worksheet("fb_accounts")
            records = worksheet.get_all_records()
            
            for i, record in enumerate(records, start=2):
                if str(record['account_id']) == str(account_id):
                    worksheet.update_cell(i, 16, 'yes')  # Column P
                    logger.info(f"✅ Marked profile picture as uploaded for account {account_id}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error marking profile picture as uploaded: {e}")
            return False
    
    def create_car_post(self):
        """Create and post AI-generated car content - FIXED for contenteditable elements"""
        try:
            logger.info("📝 Creating AI-generated car post with IMPROVED Facebook interface handling...")
            
            # Generate post content
            post_content = self.generate_ai_post()
            
            # Navigate to home page
            self.page.goto('https://www.facebook.com', timeout=60000)
            time.sleep(random.uniform(3, 5))
            
            # Handle any overlay dialogs
            try:
                overlay_selectors = [
                    'div[role="dialog"] button:has-text("Not Now")',
                    'div[role="dialog"] button[aria-label="Close"]',
                    'div[role="dialog"] div[role="button"]:has-text("Not Now")',
                    '[aria-label="Close"]'
                ]
                
                for selector in overlay_selectors:
                    overlay_button = self.page.query_selector(selector)
                    if overlay_button and overlay_button.is_visible():
                        overlay_button.click()
                        time.sleep(1)
                        logger.info("✅ Closed overlay dialog")
                        break
            except:
                pass
            
            # Take screenshot to see current interface
            try:
                self.page.screenshot(path=f"facebook_interface_before_post_{int(time.time())}.png")
                logger.info("📸 Screenshot of current Facebook interface saved")
            except:
                pass
            
            # Look for post creation interface
            post_selectors = [
                '[aria-label*="What\'s on your mind"]',
                '[placeholder*="What\'s on your mind"]',
                'div[role="button"][aria-label*="What\'s on your mind"]',
                '[aria-label="Create a post"]',
                'div[role="textbox"][contenteditable="true"]'
            ]
            
            post_element = None
            for selector in post_selectors:
                try:
                    element = self.page.query_selector(selector)
                    if element and element.is_visible():
                        post_element = element
                        logger.info(f"✅ Found post creation element: {selector}")
                        break
                except:
                    continue
            
            if not post_element:
                logger.error("❌ Could not find post creation element")
                return False
            
            # Click the post creation element
            try:
                post_element.scroll_into_view_if_needed()
                time.sleep(1)
                post_element.click()
                time.sleep(random.uniform(2, 4))
                logger.info("✅ Clicked post creation element")
            except Exception as e:
                logger.error(f"❌ Error clicking post creation element: {e}")
                return False
            
            # Wait for composer to load
            logger.info("⏳ Waiting for post composer to load...")
            time.sleep(3)
            
            # Look for the expanded text input with improved selectors
            expanded_selectors = [
                'div[role="textbox"][contenteditable="true"]',
                'div[contenteditable="true"][role="textbox"]',
                'div[aria-label*="What\'s on your mind"]',
                '[data-testid="status-attachment-mentions-input"] div[contenteditable="true"]',
                'div[contenteditable="true"]'  # Most generic
            ]
            
            text_input = None
            for selector in expanded_selectors:
                try:
                    element = self.page.query_selector(selector)
                    if element and element.is_visible():
                        # Check if element is actually editable
                        is_contenteditable = element.get_attribute('contenteditable')
                        if is_contenteditable == 'true':
                            text_input = element
                            logger.info(f"✅ Found contenteditable text input: {selector}")
                            break
                except:
                    continue
            
            if not text_input:
                # Use original element as fallback
                text_input = post_element
                logger.info("⚠️ Using original post element as fallback")
            
            # IMPROVED: Handle contenteditable elements properly
            try:
                # Focus the element first
                text_input.scroll_into_view_if_needed()
                text_input.focus()
                time.sleep(1)
                
                logger.info(f"📝 Typing post content: {post_content[:50]}...")
                
                # Method 1: Try using keyboard input instead of fill()
                # This works better for contenteditable divs
                try:
                    # Clear any existing content
                    self.page.keyboard.press('Control+a')
                    time.sleep(0.5)
                    self.page.keyboard.press('Delete')
                    time.sleep(0.5)
                    
                    # Type the content character by character
                    for char in post_content:
                        self.page.keyboard.type(char, delay=random.randint(20, 50))
                        if char == ' ' and random.random() < 0.1:  # Occasional pause at spaces
                            time.sleep(random.uniform(0.1, 0.3))
                    
                    logger.info("✅ Post content entered using keyboard typing")
                    
                except Exception as keyboard_error:
                    logger.warning(f"⚠️ Keyboard typing failed: {keyboard_error}")
                    
                    # Method 2: Try JavaScript injection as fallback
                    try:
                        logger.info("🔄 Trying JavaScript text injection...")
                        
                        # Use JavaScript to set the content
                        script = f"""
                        (element) => {{
                            element.focus();
                            element.innerHTML = `{post_content.replace('`', '\\`').replace('${', '\\${')}`;
                            
                            // Trigger input events to make Facebook recognize the content
                            element.dispatchEvent(new Event('input', {{ bubbles: true }}));
                            element.dispatchEvent(new Event('change', {{ bubbles: true }}));
                            
                            return element.innerHTML;
                        }}
                        """
                        
                        result = text_input.evaluate(script)
                        logger.info("✅ Post content entered using JavaScript injection")
                        
                    except Exception as js_error:
                        logger.error(f"❌ JavaScript injection failed: {js_error}")
                        
                        # Method 3: Try simple click and type
                        try:
                            logger.info("🔄 Trying simple click and type...")
                            text_input.click()
                            time.sleep(1)
                            
                            # Just type without clearing first
                            self.page.keyboard.type(post_content, delay=random.randint(30, 80))
                            logger.info("✅ Post content entered using simple typing")
                            
                        except Exception as simple_error:
                            logger.error(f"❌ All text input methods failed: {simple_error}")
                            return False
                
                time.sleep(random.uniform(2, 3))
                
            except Exception as e:
                logger.error(f"❌ Error entering post content: {e}")
                return False
            
            # Take screenshot after typing
            try:
                self.page.screenshot(path=f"facebook_after_typing_{int(time.time())}.png")
                logger.info("📸 Screenshot after typing content saved")
            except:
                pass
            
            # Look for post button with extensive selectors
            logger.info("🔍 Looking for Post button...")
            
            post_button_selectors = [
                'div[role="button"][aria-label="Post"]',
                'div[role="button"]:has-text("Post")',
                'button:has-text("Post")',
                '[aria-label="Post"]',
                'div[role="button"]:has-text("Share")',
                '[aria-label="Share"]',
                'button:has-text("Share")',
                '[data-testid="react-composer-post-button"]',
                'button[type="submit"]',
                'input[type="submit"]'
            ]
            
            post_button = None
            for selector in post_button_selectors:
                try:
                    button = self.page.query_selector(selector)
                    if button and button.is_visible():
                        # Verify it's likely a post button
                        button_text = button.inner_text().lower() if button.inner_text() else ''
                        aria_label = (button.get_attribute('aria-label') or '').lower()
                        
                        if ('post' in button_text or 'share' in button_text or 
                            'post' in aria_label or 'share' in aria_label):
                            post_button = button
                            logger.info(f"✅ Found post button: {selector} (text: '{button_text}', aria: '{aria_label}')")
                            break
                except:
                    continue
            
            if not post_button:
                # Try to find any button that might work
                logger.info("🔍 Looking for any viable button...")
                all_buttons = self.page.query_selector_all('div[role="button"], button')
                
                for button in all_buttons:
                    try:
                        if button.is_visible():
                            button_text = button.inner_text().lower() if button.inner_text() else ''
                            aria_label = (button.get_attribute('aria-label') or '').lower()
                            
                            # Look for buttons that might be post buttons
                            if (('post' in button_text or 'share' in button_text) and
                                not any(skip in button_text for skip in ['skip', 'cancel', 'back'])):
                                post_button = button
                                logger.info(f"🎯 Found potential post button: text='{button_text}', aria='{aria_label}'")
                                break
                    except:
                        continue
            
            if not post_button:
                logger.error("❌ Could not find post button")
                return False
            
            # Click the post button
            try:
                post_button.scroll_into_view_if_needed()
                time.sleep(1)
                post_button.click()
                logger.info("✅ Clicked post button - post should be published")
                time.sleep(random.uniform(3, 5))
                
                # Take final screenshot
                self.page.screenshot(path=f"facebook_after_post_{int(time.time())}.png")
                logger.info("📸 Screenshot after posting saved")
                
                return True
                
            except Exception as e:
                logger.error(f"❌ Error clicking post button: {e}")
                return False
            
        except Exception as e:
            logger.error(f"❌ Error creating car post: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def add_friends(self, target_count=None):
        """Add 6-12 friends as specified"""
        try:
            if target_count is None:
                target_count = random.randint(6, 12)
            
            logger.info(f"👥 Adding {target_count} friends...")
            
            # Navigate to people you may know
            self.page.goto('https://www.facebook.com/friends/suggestions', timeout=60000)
            time.sleep(random.uniform(4, 6))
            
            friends_added = 0
            attempts = 0
            max_attempts = target_count * 3
            
            while friends_added < target_count and attempts < max_attempts:
                try:
                    # Look for "Add Friend" buttons
                    add_friend_buttons = self.page.query_selector_all(
                        'div[role="button"]:has-text("Add friend"), '
                        '[aria-label="Add friend"], '
                        'div[role="button"][aria-label="Add friend"]'
                    )
                    
                    if not add_friend_buttons:
                        logger.info("🔄 Scrolling to find more friend suggestions...")
                        self.page.evaluate("window.scrollBy(0, 800)")
                        time.sleep(random.uniform(2, 4))
                        attempts += 1
                        continue
                    
                    # Click on a random available button
                    available_buttons = [btn for btn in add_friend_buttons if btn.is_visible()]
                    if available_buttons:
                        button = random.choice(available_buttons)
                        button.click()
                        friends_added += 1
                        logger.info(f"👤 Added friend {friends_added}/{target_count}")
                        
                        # Random delay between friend requests
                        time.sleep(random.uniform(3, 8))
                    
                    attempts += 1
                    
                except Exception as e:
                    logger.warning(f"⚠️ Error adding friend: {e}")
                    attempts += 1
                    continue
            
            logger.info(f"✅ Successfully added {friends_added} friends")
            return friends_added
            
        except Exception as e:
            logger.error(f"❌ Error adding friends: {e}")
            return 0
    
    def join_target_groups(self):
        """Join the specified Facebook groups"""
        try:
            logger.info("🔗 Joining target Facebook groups...")
            
            joined_count = 0
            
            for i, group_url in enumerate(self.target_groups, 1):
                try:
                    logger.info(f"🔗 Joining group {i}/{len(self.target_groups)}: {group_url}")
                    
                    # Navigate to group
                    self.page.goto(group_url, timeout=60000)
                    time.sleep(random.uniform(4, 6))
                    
                    # Look for join button
                    join_selectors = [
                        'div[role="button"]:has-text("Join")',
                        '[aria-label="Join group"]',
                        'div[role="button"][aria-label="Join group"]',
                        'div[role="button"]:has-text("Join group")'
                    ]
                    
                    joined = False
                    for selector in join_selectors:
                        try:
                            button = self.page.query_selector(selector)
                            if button and button.is_visible():
                                button.click()
                                logger.info(f"✅ Joined group {i}")
                                joined_count += 1
                                joined = True
                                time.sleep(random.uniform(3, 6))
                                break
                        except:
                            continue
                    
                    if not joined:
                        logger.warning(f"⚠️ Could not join group {i} - might already be a member or private")
                    
                    # Delay between groups
                    if i < len(self.target_groups):
                        time.sleep(random.uniform(5, 10))
                        
                except Exception as e:
                    logger.warning(f"⚠️ Error joining group {i}: {e}")
                    continue
            
            logger.info(f"✅ Successfully joined {joined_count}/{len(self.target_groups)} groups")
            return joined_count
            
        except Exception as e:
            logger.error(f"❌ Error joining groups: {e}")
            return 0
    
    def scroll_and_like_posts_enhanced(self):
        """Enhanced post liking with more natural behavior"""
        try:
            logger.info("📱 Starting enhanced post scrolling and liking...")
            
            # Go to home page
            self.page.goto('https://www.facebook.com', timeout=60000)
            time.sleep(random.uniform(4, 6))
            
            posts_liked = 0
            posts_seen = 0
            max_likes = random.randint(5, 12)
            scroll_count = 0
            max_scrolls = 20
            
            while posts_liked < max_likes and scroll_count < max_scrolls:
                try:
                    # Find like buttons
                    like_selectors = [
                        '[aria-label="Like"]',
                        'div[role="button"][aria-label="Like"]',
                        '[data-testid="fb-ufi-likelink"]'
                    ]
                    
                    like_buttons = []
                    for selector in like_selectors:
                        buttons = self.page.query_selector_all(selector)
                        like_buttons.extend(buttons)
                    
                    # Filter for visible buttons not already liked
                    available_buttons = []
                    for button in like_buttons:
                        try:
                            if button.is_visible():
                                # Check if already liked
                                aria_label = button.get_attribute('aria-label') or ''
                                if 'like' in aria_label.lower() and 'unlike' not in aria_label.lower():
                                    available_buttons.append(button)
                        except:
                            continue
                    
                    # Like some posts (not all)
                    if available_buttons:
                        posts_seen += len(available_buttons)
                        
                        # Like with some probability
                        to_like = random.sample(
                            available_buttons, 
                            min(len(available_buttons), random.randint(1, 3))
                        )
                        
                        for button in to_like:
                            if posts_liked >= max_likes:
                                break
                            try:
                                button.click()
                                posts_liked += 1
                                logger.info(f"👍 Liked post {posts_liked}/{max_likes}")
                                time.sleep(random.uniform(1, 3))
                            except:
                                continue
                    
                    # Scroll down
                    scroll_amount = random.randint(400, 800)
                    self.page.evaluate(f"window.scrollBy(0, {scroll_amount})")
                    time.sleep(random.uniform(2, 4))
                    scroll_count += 1
                    
                except Exception as e:
                    logger.warning(f"⚠️ Error in scrolling/liking: {e}")
                    scroll_count += 1
                    continue
            
            logger.info(f"✅ Liked {posts_liked} posts, saw {posts_seen} posts total")
            return posts_liked
            
        except Exception as e:
            logger.error(f"❌ Error in enhanced scrolling/liking: {e}")
            return 0
    
    def comment_on_posts_with_ai(self, target_comments=None):
        """Comment on posts with AI-generated comments"""
        try:
            if target_comments is None:
                target_comments = random.randint(2, 5)
            
            logger.info(f"💬 Adding {target_comments} AI comments...")
            
            # Go to home page
            self.page.goto('https://www.facebook.com', timeout=60000)
            time.sleep(random.uniform(4, 6))
            
            comments_added = 0
            scroll_count = 0
            max_scrolls = 15
            
            while comments_added < target_comments and scroll_count < max_scrolls:
                try:
                    # Find posts to comment on
                    comment_buttons = self.page.query_selector_all(
                        '[aria-label="Comment"], '
                        'div[role="button"][aria-label="Comment"], '
                        '[data-testid="UFI2CommentsCount/root"]'
                    )
                    
                    if comment_buttons:
                        # Pick a random post to comment on
                        button = random.choice([btn for btn in comment_buttons if btn.is_visible()])
                        
                        # Get post text for context
                        try:
                            # Find the post container
                            post_container = button.evaluate_handle(
                                'button => button.closest(\'[role="article"]\') || button.closest(\'[data-testid="story-subtitle"]\').parentElement'
                            ).as_element()
                            
                            post_text = post_container.inner_text()[:200] if post_container else "Great post!"
                        except:
                            post_text = "Great post!"
                        
                        # Generate AI comment
                        ai_comment = self.generate_ai_comment(post_text)
                        
                        # Click comment button
                        button.click()
                        time.sleep(random.uniform(1, 2))
                        
                        # Find comment input
                        comment_inputs = self.page.query_selector_all(
                            '[placeholder*="comment"], '
                            '[aria-label*="comment"], '
                            'div[contenteditable="true"][role="textbox"]'
                        )
                        
                        comment_input = None
                        for input_elem in comment_inputs:
                            if input_elem.is_visible():
                                comment_input = input_elem
                                break
                        
                        if comment_input:
                            # Type comment with human-like delays
                            comment_input.click()
                            time.sleep(random.uniform(0.5, 1))
                            
                            for char in ai_comment:
                                self.page.keyboard.type(char)
                                if char == ' ':
                                    time.sleep(random.uniform(0.1, 0.2))
                                else:
                                    time.sleep(random.uniform(0.05, 0.1))
                            
                            # Press Enter to post comment
                            self.page.keyboard.press('Enter')
                            comments_added += 1
                            logger.info(f"💬 Posted AI comment {comments_added}/{target_comments}: {ai_comment}")
                            
                            time.sleep(random.uniform(3, 6))
                    
                    # Scroll to find more posts
                    self.page.evaluate("window.scrollBy(0, 600)")
                    time.sleep(random.uniform(2, 4))
                    scroll_count += 1
                    
                except Exception as e:
                    logger.warning(f"⚠️ Error commenting on post: {e}")
                    scroll_count += 1
                    continue
            
            logger.info(f"✅ Successfully added {comments_added} AI comments")
            return comments_added
            
        except Exception as e:
            logger.error(f"❌ Error in AI commenting: {e}")
            return 0
    
    def get_account_proxy_mandatory(self, account):
        """Get proxy configuration - MANDATORY for warmup"""
        try:
            logger.info("🔍 Getting MANDATORY proxy for warmup...")
            
            # Check if proxy should be disabled (NOT allowed for warmup)
            if hasattr(self.config, 'DISABLE_PROXY') and self.config.DISABLE_PROXY:
                logger.error("❌ Proxy is disabled in config - warmup requires proxy")
                return None
            
            # Get enhanced proxy from account creation
            if 'proxy' in account and account['proxy']:
                proxy_data = account['proxy']
                if proxy_data.get('username') and proxy_data.get('password'):
                    proxy = {
                        'type': proxy_data.get('type', 'soax'),
                        'endpoint': proxy_data.get('endpoint'),
                        'username': proxy_data['username'],
                        'password': proxy_data['password']
                    }
                    logger.info(f"📋 Using account proxy: {proxy['endpoint']}")
                    return proxy
            
            # Fallback to config proxy if credentials exist
            if (hasattr(self.config, 'SOAX_USERNAME') and self.config.SOAX_USERNAME and 
                hasattr(self.config, 'SOAX_PASSWORD') and self.config.SOAX_PASSWORD):
                proxy = {
                    'type': 'soax',
                    'endpoint': getattr(self.config, 'SOAX_ENDPOINT', 'proxy.soax.com:5000'),
                    'username': self.config.SOAX_USERNAME,
                    'password': self.config.SOAX_PASSWORD
                }
                logger.info(f"⚙️ Using config proxy: {proxy['endpoint']}")
                return proxy
            else:
                logger.error("❌ No proxy credentials found - warmup requires proxy")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error getting mandatory proxy: {e}")
            return None
    
    def determine_login_credential(self, account):
        """Determine whether to use email or phone for login"""
        try:
            registration_method = account.get('registration_method', '')
            phone = account.get('phone', '')
            email = account.get('email', '')
            
            if 'phone_first' in registration_method and phone:
                # Format phone number properly
                phone_str = str(phone).strip()
                if not phone_str.startswith('+'):
                    formatted_phone = f"+{phone_str}"
                else:
                    formatted_phone = phone_str
                
                logger.info(f"📱 Using phone for login: {formatted_phone}")
                return formatted_phone
            else:
                logger.info(f"📧 Using email for login: {email}")
                return email
                
        except Exception as e:
            logger.error(f"❌ Error determining login credential: {e}")
            return account.get('email', '')