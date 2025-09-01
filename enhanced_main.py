#!/usr/bin/env python3
"""
Enhanced Main Module with AI-powered account creation and warmup
"""

import random
import schedule
import time
import logging
from datetime import datetime
import sys
import os

# Import enhanced modules
from config import Config
from enhanced_database import EnhancedDatabaseManager
from enhanced_account_manager import EnhancedAccountManager
from scraper import MarketplaceScraper
from messaging import MessagingEngine
from enhanced_warmup import EnhancedAccountWarmup
from utils import Utils

# Setup logging
def setup_logging():
    """Setup logging with fallback options"""
    log_handlers = []
    
    try:
        logs_dir = os.path.join(os.path.dirname(__file__), 'logs')
        os.makedirs(logs_dir, exist_ok=True)
        log_file = os.path.join(logs_dir, 'enhanced_fb_marketplace_bot.log')
        file_handler = logging.FileHandler(log_file)
        log_handlers.append(file_handler)
        print(f"✅ Log file created: {log_file}")
    except:
        print("⚠️ Cannot create log file, using console only")
    
    console_handler = logging.StreamHandler(sys.stdout)
    log_handlers.append(console_handler)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=log_handlers
    )

setup_logging()
logger = logging.getLogger(__name__)

class EnhancedFacebookMarketplaceBot:
    def __init__(self):
        self.config = Config()
        self.db = EnhancedDatabaseManager(self.config)
        self.account_manager = EnhancedAccountManager(self.config, self.db)
        self.scraper = MarketplaceScraper(self.config, self.db)
        self.messaging = MessagingEngine(self.config, self.db)
        self.warmup = EnhancedAccountWarmup(self.config, self.db)
        self.utils = Utils()
        
        # Ensure database has profile picture columns
        self.db.ensure_profile_columns_exist()
        
        logger.info("🤖 Enhanced Facebook Marketplace Bot initialized with AI features")
    
    def create_enhanced_us_based_accounts(self, count=5):
        """Create US-based Facebook accounts with AI-generated profiles"""
        try:
            logger.info(f"🇺🇸 Creating {count} enhanced US-based Facebook accounts with AI profiles...")
            
            accounts = self.account_manager.create_multiple_enhanced_accounts_phone_first_us(count)
            
            if accounts:
                logger.info(f"✅ Successfully created {len(accounts)} enhanced accounts")
                
                # Display summary
                print(f"\n🎉 ENHANCED ACCOUNT CREATION SUMMARY:")
                print(f"=" * 60)
                print(f"✅ Created: {len(accounts)}/{count} accounts")
                print(f"🤖 Features: AI names, birthdays, genders, profile pictures")
                print(f"📱 Method: US phone-first registration")
                
                print(f"\n👥 Created Accounts:")
                for i, acc in enumerate(accounts, 1):
                    print(f"  {i}. {acc['first_name']} {acc['last_name']}")
                    print(f"     📱 {acc['phone']}")
                    print(f"     📧 {acc['email']}")
                    print(f"     🎂 {acc['birth_month']}/{acc['birth_day']}/{acc['birth_year']}")
                    print(f"     ⚧ {acc['gender'].title()}")
                    print(f"     🖼️ Profile Picture: {'✅ Generated' if acc.get('profile_picture_url') else '❌ Failed'}")
                    print()
                
                return accounts
            else:
                logger.error("❌ Failed to create any accounts")
                return []
                
        except Exception as e:
            logger.error(f"💥 Error creating enhanced accounts: {e}")
            return []
    
    def run_enhanced_setup_wizard(self):
        """Enhanced setup wizard with location analysis"""
        try:
            print("\n🤖 ENHANCED FACEBOOK MARKETPLACE BOT SETUP")
            print("=" * 60)
            print("🚀 Features: AI profiles, smart warmup, profile pictures, checkpoint handling")
            print("🎯 NEW: Location consistency analysis to prevent video selfie verification")
            print()
            
            while True:
                print("Choose an option:")
                print("1. 🇺🇸 Create enhanced US phone-first accounts (AI profiles)")
                print("2. 📊 View account status and profile picture info")
                print("3. 🔄 Run enhanced warmup (with profile pictures)")
                print("4. 🖼️ Generate missing profile pictures")
                print("5. 🧪 Test 2FA fix for specific account")
                print("6. 🚨 Test checkpoint handling for specific account")
                print("7. 🔧 View accounts needing manual intervention")
                print("8. 🔍 Analyze account location consistency")  # NEW OPTION
                print("9. 📍 Show proxy location patterns")          # NEW OPTION  
                print("10. 🔧 Fix location inconsistency for existing accounts")  # NEW OPTION
                print("11. 📱 Start full enhanced automation")
                print("12. 🧪 Test AI features")
                print("13. ❌ Exit")
                
                try:
                    choice = input("\nEnter your choice (1-13): ").strip()
                except KeyboardInterrupt:
                    print("\n👋 Goodbye!")
                    return False
                
                if choice == "1":
                    try:
                        count = int(input("How many accounts to create? (1-10): "))
                        if 1 <= count <= 10:
                            self.create_enhanced_us_based_accounts(count)
                        else:
                            print("❌ Please enter a number between 1 and 10")
                    except ValueError:
                        print("❌ Invalid number")
                    
                elif choice == "2":
                    self.show_enhanced_account_status()
                    
                elif choice == "3":
                    self.run_enhanced_account_warmup()
                    
                elif choice == "4":
                    self.generate_missing_profile_pictures()
                    
                elif choice == "5":
                    self.start_enhanced_automation()
                    return True
                    
                elif choice == "6":
                    self.test_ai_features()
                    
                elif choice == "8":  # NEW: Location consistency analysis
                    self.analyze_account_location_consistency()
                                
                elif choice == "9":  # NEW: Proxy location patterns
                    self.show_proxy_location_patterns()
                                
                elif choice == "10":  # NEW: Fix location inconsistency
                    self.fix_location_inconsistency_for_existing_accounts()
                                
                elif choice == "11":
                    self.start_enhanced_automation()
                    return True
                                
                elif choice == "12": 
                    self.test_ai_features()
                                
                elif choice == "13":
                                print("👋 Goodbye!")
                                return False                    
                else:
                    print("❌ Invalid option")
                    
                print("\n" + "="*50)
        
        except Exception as e:
            logger.error(f"💥 Error in enhanced setup wizard: {e}")
            return False

    def analyze_account_location_consistency(self):
        """Analyze which accounts have inconsistent locations - ROOT CAUSE ANALYSIS"""
        try:
            print("\n🔍 LOCATION CONSISTENCY ANALYSIS")
            print("=" * 60)
            print("🎯 THEORY: Changing proxy locations cause video selfie verification")
            print()
            
            # Get all accounts
            accounts = self.db.get_enhanced_active_accounts()
            
            # Load existing location data if available
            location_data = {}
            try:
                import json
                if os.path.exists("account_data/location_history.json"):
                    with open("account_data/location_history.json", 'r') as f:
                        location_data = json.load(f)
            except:
                pass
            
            # Analyze accounts
            high_risk_accounts = []
            medium_risk_accounts = []
            low_risk_accounts = []
            unknown_accounts = []
            
            for account in accounts:
                account_id = str(account['account_id'])
                
                if account_id in location_data:
                    history = location_data[account_id]
                    locations = set()
                    
                    for record in history:
                        location = f"{record.get('city', 'Unknown')}, {record.get('region', 'Unknown')}"
                        locations.add(location)
                    
                    account_analysis = {
                        'account': account,
                        'unique_locations': len(locations),
                        'locations': list(locations),
                        'total_logins': len(history)
                    }
                    
                    if len(locations) >= 3:
                        high_risk_accounts.append(account_analysis)
                    elif len(locations) == 2:
                        medium_risk_accounts.append(account_analysis)
                    elif len(locations) == 1:
                        low_risk_accounts.append(account_analysis)
                else:
                    unknown_accounts.append(account)
            
            # Display results
            print(f"📊 LOCATION ANALYSIS RESULTS:")
            print(f"   🔴 HIGH RISK (3+ locations): {len(high_risk_accounts)} accounts")
            print(f"   🟡 MEDIUM RISK (2 locations): {len(medium_risk_accounts)} accounts")  
            print(f"   🟢 LOW RISK (1 location): {len(low_risk_accounts)} accounts")
            print(f"   ❓ UNKNOWN (no data): {len(unknown_accounts)} accounts")
            print()
            
            # Show high-risk accounts in detail
            if high_risk_accounts:
                print("🔴 HIGH RISK ACCOUNTS (Most likely to get video selfie verification):")
                print("-" * 60)
                for analysis in high_risk_accounts:
                    account = analysis['account']
                    print(f"  Account {account['account_id']} - {account.get('email', 'Unknown')[:30]}")
                    print(f"    📍 Used {analysis['unique_locations']} different locations:")
                    for location in analysis['locations']:
                        print(f"      • {location}")
                    print(f"    📊 Total logins: {analysis['total_logins']}")
                    print(f"    📋 Status: {account.get('status', 'Unknown')}")
                    
                    # Check if this account has video selfie requirement
                    if account.get('status') == 'manual_intervention_required':
                        print(f"    🚨 CONFIRMED: This account hit video selfie verification!")
                    
                    print()
            
            # Show medium-risk accounts
            if medium_risk_accounts:
                print("🟡 MEDIUM RISK ACCOUNTS (Could trigger video selfie):")
                print("-" * 60)
                for analysis in medium_risk_accounts:
                    account = analysis['account']
                    print(f"  Account {account['account_id']} - {account.get('email', 'Unknown')[:30]}")
                    print(f"    📍 Used 2 locations: {', '.join(analysis['locations'])}")
                    print(f"    📋 Status: {account.get('status', 'Unknown')}")
                    print()
            
            # Show recommendations
            print("💡 RECOMMENDATIONS:")
            print("-" * 60)
            
            if high_risk_accounts:
                print("🔴 For HIGH RISK accounts:")
                print("   1. Expect video selfie verification")
                print("   2. Complete verification manually")
                print("   3. After verification, use ONLY ONE consistent location")
                print("   4. These become premium accounts after manual verification")
                print()
            
            if medium_risk_accounts or high_risk_accounts:
                print("🎯 For ALL accounts going forward:")
                print("   1. Implement sticky proxy system (provided above)")
                print("   2. Each account gets ONE consistent location")
                print("   3. Never change locations for an account")
                print("   4. Use account ID to deterministically assign locations")
                print()
            
            print("🔧 IMMEDIATE ACTIONS:")
            print("   1. Implement the StickyProxyManager code provided")
            print("   2. Update get_working_us_proxy_for_warmup() method")
            print("   3. Complete video selfie verification manually for flagged accounts")
            print("   4. Test new accounts with consistent locations")
            print()
            
            return {
                'high_risk': len(high_risk_accounts),
                'medium_risk': len(medium_risk_accounts), 
                'low_risk': len(low_risk_accounts),
                'unknown': len(unknown_accounts)
            }
            
        except Exception as e:
            logger.error(f"💥 Error analyzing location consistency: {e}")
            print(f"❌ Analysis failed: {e}")
            return None

    def show_proxy_location_patterns(self):
        """Show patterns in proxy location usage"""
        try:
            print("\n📍 PROXY LOCATION PATTERNS ANALYSIS")
            print("=" * 60)
            
            # This would analyze your SOAX proxy configuration
            print("🔍 Current SOAX Configuration Analysis:")
            
            soax_configs = [
                {'city': 'phoenix', 'region': 'arizona'},
                {'city': 'losangeles', 'region': 'california'}, 
                {'city': 'newyork', 'region': 'newyork'},
                {'city': 'chicago', 'region': 'illinois'},
                {'city': 'miami', 'region': 'florida'},
                # Add Queen Creek and Scottsdale that appeared in your logs
                {'city': 'queencreek', 'region': 'arizona'},
                {'city': 'scottsdale', 'region': 'arizona'}
            ]
            
            print("🌍 Locations your bot has been using:")
            for config in soax_configs:
                print(f"   • {config['city'].title()}, {config['region'].title()}")
            
            print()
            print("🚨 THE PROBLEM:")
            print("   Your current code randomly selects from these locations")
            print("   Same account gets different cities on different logins")
            print("   Facebook sees this as suspicious → triggers video selfie")
            print()
            
            print("✅ THE SOLUTION:")
            print("   Use StickyProxyManager to assign ONE consistent location per account")
            print("   Account 16 always uses Phoenix, Arizona")
            print("   Account 17 always uses Scottsdale, Arizona")
            print("   Account 18 always uses Tempe, Arizona")
            print("   etc.")
            print()
            
            print("🎯 IMPLEMENTATION:")
            print("   1. Replace your get_working_us_proxy_for_warmup() method")
            print("   2. Each account gets a deterministic city based on account ID")
            print("   3. Same session ID is reused for same account")
            print("   4. Location changes are eliminated")
            print()
            
        except Exception as e:
            logger.error(f"💥 Error showing proxy patterns: {e}")

    def fix_location_inconsistency_for_existing_accounts(self):
        """Fix location inconsistency for accounts that haven't hit video selfie yet - COMPLETE FIXED VERSION"""
        try:
            print("\n🔧 FIXING LOCATION INCONSISTENCY FOR EXISTING ACCOUNTS")
            print("=" * 60)
            
            # STEP 1: Test SOAX configuration first
            print("🧪 Testing SOAX configuration before proceeding...")
            
            # Check SOAX credentials exist
            if not hasattr(self.config, 'SOAX_USERNAME') or not self.config.SOAX_USERNAME:
                print("❌ SOAX_USERNAME not found in config!")
                print("🔧 Please add SOAX_USERNAME to your .env file")
                return
            
            if not hasattr(self.config, 'SOAX_PASSWORD') or not self.config.SOAX_PASSWORD:
                print("❌ SOAX_PASSWORD not found in config!")
                print("🔧 Please add SOAX_PASSWORD to your .env file")
                return
            
            print(f"✅ SOAX credentials found")
            print(f"   Username: {self.config.SOAX_USERNAME[:30]}...")
            print(f"   Endpoint: {getattr(self.config, 'SOAX_ENDPOINT', 'proxy.soax.com:5000')}")
            
            # Initialize sticky proxy manager with fixed version
            from sticky_proxy_manager import StickyProxyManager
            sticky_manager = StickyProxyManager(self.config, self.db)
            
            # Test basic SOAX connectivity
            test_proxy = {
                'type': 'soax',
                'endpoint': getattr(self.config, 'SOAX_ENDPOINT', 'proxy.soax.com:5000'),
                'username': self.config.SOAX_USERNAME,
                'password': self.config.SOAX_PASSWORD
            }
            
            print("🔍 Testing basic SOAX connectivity...")
            if not sticky_manager.test_proxy_connectivity_robust(test_proxy):
                print("❌ SOAX configuration test failed!")
                print("")
                print("🔧 TROUBLESHOOTING STEPS:")
                print("1. Run 'python test_soax.py' to diagnose the specific issue")
                print("2. Check your SOAX dashboard for account status and balance")
                print("3. Verify your package ID is correct in the username")
                print("4. Ensure your IP is whitelisted if required")
                print("5. Contact SOAX support if all else fails")
                print("")
                print("❌ Cannot proceed with location consistency fix until SOAX works")
                return
            
            print("✅ SOAX configuration test passed!")
            
            # STEP 2: Get accounts that can be fixed
            accounts = self.db.get_enhanced_active_accounts()
            
            # Filter accounts that are still usable (not requiring manual intervention)
            fixable_accounts = [
                acc for acc in accounts 
                if acc.get('status') not in ['manual_intervention_required', 'banned', 'disabled']
            ]
            
            if not fixable_accounts:
                print("❌ No fixable accounts found")
                print("📋 All accounts are either banned, disabled, or require manual intervention")
                return
            
            print(f"🔧 Found {len(fixable_accounts)} accounts that can be assigned consistent locations:")
            print()
            
            # Show accounts to be processed
            for acc in fixable_accounts:
                status = acc.get('status', 'unknown')
                email = acc.get('email', 'N/A')[:30]
                phone = acc.get('phone', 'N/A')
                print(f"  👤 Account {acc['account_id']}: {email} ({status})")
            
            print()
            
            # Ask for confirmation
            try:
                confirm = input("🤔 Proceed with assigning sticky proxy locations? (y/N): ").strip().lower()
                if confirm != 'y' and confirm != 'yes':
                    print("❌ Operation cancelled by user")
                    return
            except KeyboardInterrupt:
                print("\n❌ Operation cancelled")
                return
            
            print("\n🚀 Starting location consistency assignment...")
            print("=" * 60)
            
            # STEP 3: Process each account
            successful_assignments = 0
            failed_assignments = 0
            
            for i, account in enumerate(fixable_accounts, 1):
                account_id = account['account_id']
                
                print(f"\n🔧 [{i}/{len(fixable_accounts)}] Processing Account {account_id}...")
                
                try:
                    # Check if account already has a sticky proxy assignment
                    if hasattr(sticky_manager, 'proxy_assignments') and str(account_id) in sticky_manager.proxy_assignments:
                        existing_proxy = sticky_manager.proxy_assignments[str(account_id)]
                        existing_location = f"{existing_proxy.get('verified_city', 'Unknown')}, {existing_proxy.get('verified_region', 'Unknown')}"
                        print(f"   ℹ️ Account already has assignment: {existing_location}")
                        
                        # Test if existing assignment still works
                        print(f"   🧪 Testing existing assignment...")
                        if sticky_manager.test_proxy_connectivity_robust(existing_proxy):
                            print(f"   ✅ Existing assignment is working: {existing_location}")
                            print(f"   🔒 Location consistency maintained")
                            successful_assignments += 1
                            continue
                        else:
                            print(f"   ⚠️ Existing assignment no longer works, creating new one...")
                    
                    # Get/assign new sticky proxy using FIXED method
                    proxy = sticky_manager.get_consistent_proxy_for_account(account_id)
                    
                    if proxy:
                        location = f"{proxy.get('verified_city', 'Unknown')}, {proxy.get('verified_region', 'Unknown')}"
                        config_used = proxy.get('config_used', 'Unknown')
                        session_id = proxy.get('session_id', 'Unknown')
                        
                        print(f"   ✅ NEW Assignment successful!")
                        print(f"   📍 Location: {location}")
                        print(f"   🔗 Session ID: {session_id}")
                        print(f"   🔧 Config: {config_used}")
                        print(f"   🔒 This location is now PERMANENT for Account {account_id}")
                        
                        successful_assignments += 1
                    else:
                        print(f"   ❌ Failed to assign location")
                        print(f"   🔧 This usually indicates:")
                        print(f"      - SOAX account out of balance/traffic")
                        print(f"      - Wrong package ID in configuration")
                        print(f"      - IP whitelisting issues")
                        failed_assignments += 1
                    
                except Exception as e:
                    print(f"   💥 Error processing account {account_id}: {e}")
                    failed_assignments += 1
                
                # Small delay between accounts
                if i < len(fixable_accounts):
                    print(f"   ⏳ Waiting 3 seconds before next account...")
                    time.sleep(3)
            
            # STEP 4: Summary and next steps
            print(f"\n🎯 LOCATION CONSISTENCY FIX SUMMARY:")
            print("=" * 60)
            print(f"✅ Successful assignments: {successful_assignments}/{len(fixable_accounts)}")
            print(f"❌ Failed assignments: {failed_assignments}/{len(fixable_accounts)}")
            
            if successful_assignments > 0:
                print(f"\n🎉 SUCCESS! {successful_assignments} accounts now have consistent locations")
                
                # Show current assignments
                print(f"\n📋 CURRENT LOCATION ASSIGNMENTS:")
                print("-" * 40)
                
                assignments = sticky_manager.proxy_assignments
                for account_id, proxy_data in assignments.items():
                    if any(str(acc['account_id']) == account_id for acc in fixable_accounts):
                        location = f"{proxy_data.get('verified_city', 'Unknown')}, {proxy_data.get('verified_region', 'Unknown')}"
                        print(f"  Account {account_id}: {location}")
            
            if failed_assignments > 0:
                print(f"\n⚠️ WARNING: {failed_assignments} accounts failed assignment")
                print(f"🔧 For failed accounts:")
                print(f"   1. Check SOAX account balance and traffic")
                print(f"   2. Verify package ID in SOAX username")
                print(f"   3. Run 'python test_soax.py' for detailed diagnostics")
                print(f"   4. Contact SOAX support if needed")
            
            print(f"\n🎯 NEXT STEPS:")
            print(f"1. ✅ All processed accounts now have consistent location assignments")
            print(f"2. 🔒 Future logins will ALWAYS use the same location per account")
            print(f"3. 🛡️ This should prevent new video selfie verifications")
            print(f"4. 📱 Continue to manually complete any pending video selfie verifications")
            print(f"5. 🚀 Run warmup to test the new sticky proxy system")
            
            print(f"\n💡 IMPORTANT REMINDERS:")
            print(f"• Each account will now ALWAYS use the same city/region")
            print(f"• Location changes that trigger video selfies should be eliminated")
            print(f"• The system uses deterministic location assignment based on account ID")
            print(f"• Session IDs are reused for consistency")
            print(f"• All location usage is logged for monitoring")
            
        except KeyboardInterrupt:
            print(f"\n❌ Operation interrupted by user")
        except Exception as e:
            logger.error(f"💥 Error fixing location inconsistency: {e}")
            print(f"❌ Fix failed: {e}")
            import traceback
            traceback.print_exc()
    
    def show_current_sticky_proxy_assignments(self):
        """Show all current sticky proxy assignments for debugging - NEW HELPER METHOD"""
        try:
            print("\n📋 CURRENT STICKY PROXY ASSIGNMENTS")
            print("=" * 60)
            
            # Initialize sticky proxy manager if needed
            if not hasattr(self, 'sticky_proxy_manager'):
                from sticky_proxy_manager import StickyProxyManager
                self.sticky_proxy_manager = StickyProxyManager(self.config, self.db)
            
            assignments = self.sticky_proxy_manager.proxy_assignments
            
            if not assignments:
                print("❌ No sticky proxy assignments found")
                print("🔧 Run 'Fix location inconsistency' to create assignments")
                return
            
            print(f"📊 Found {len(assignments)} sticky proxy assignments:")
            print("")
            
            for account_id, proxy_data in assignments.items():
                print(f"👤 Account {account_id}:")
                print(f"   📍 Location: {proxy_data.get('verified_city', 'Unknown')}, {proxy_data.get('verified_region', 'Unknown')}")
                print(f"   🌍 IP: {proxy_data.get('verified_ip', 'Unknown')}")
                print(f"   🔗 Session ID: {proxy_data.get('session_id', 'Unknown')}")
                print(f"   🔧 Config: {proxy_data.get('config_used', 'Unknown')}")
                print(f"   📅 Created: {proxy_data.get('created_at', 'Unknown')[:19]}")
                print(f"   ✅ US Verified: {'Yes' if proxy_data.get('us_verified') else 'No (but working)'}")
                print("")
            
            # Show location distribution
            locations = {}
            for proxy_data in assignments.values():
                location = f"{proxy_data.get('verified_city', 'Unknown')}, {proxy_data.get('verified_region', 'Unknown')}"
                locations[location] = locations.get(location, 0) + 1
            
            print("📊 LOCATION DISTRIBUTION:")
            print("-" * 40)
            for location, count in locations.items():
                print(f"   {location}: {count} account(s)")
            
            print(f"\n✅ All assignments look consistent - good for preventing video selfie verification!")
            
        except Exception as e:
            logger.error(f"💥 Error showing assignments: {e}")
            print(f"❌ Error showing assignments: {e}")

    def test_sticky_proxy_for_account(self, account_id):
        """Test the sticky proxy assignment for a specific account - NEW DIAGNOSTIC METHOD"""
        try:
            print(f"\n🧪 TESTING STICKY PROXY FOR ACCOUNT {account_id}")
            print("=" * 60)
            
            # Initialize sticky proxy manager if needed
            if not hasattr(self, 'sticky_proxy_manager'):
                from sticky_proxy_manager import StickyProxyManager
                self.sticky_proxy_manager = StickyProxyManager(self.config, self.db)
            
            # Get the proxy for this account
            proxy = self.sticky_proxy_manager.get_consistent_proxy_for_account(account_id)
            
            if not proxy:
                print(f"❌ No proxy found for account {account_id}")
                print("🔧 Run 'Fix location inconsistency' to create assignment")
                return False
            
            print(f"📋 PROXY DETAILS:")
            print(f"   📍 Location: {proxy.get('verified_city', 'Unknown')}, {proxy.get('verified_region', 'Unknown')}")
            print(f"   🌍 IP: {proxy.get('verified_ip', 'Unknown')}")
            print(f"   🔗 Session ID: {proxy.get('session_id', 'Unknown')}")
            print(f"   🔧 Config: {proxy.get('config_used', 'Unknown')}")
            
            # Test connectivity
            print(f"\n🔍 Testing connectivity...")
            if self.sticky_proxy_manager.test_proxy_connectivity_robust(proxy):
                print(f"✅ Connectivity test PASSED")
                
                # Test location verification
                print(f"🌍 Testing location verification...")
                location_result = self.sticky_proxy_manager.verify_proxy_location_robust(proxy)
                
                if location_result.get('verified'):
                    print(f"✅ Location verification PASSED")
                    print(f"   🌍 Verified IP: {location_result['ip']}")
                    print(f"   📍 Verified Location: {location_result['city']}, {location_result['region']}")
                    print(f"   🇺🇸 US Status: {'Confirmed' if 'US' in location_result['country'] else 'Non-US'}")
                else:
                    print(f"⚠️ Location verification failed, but proxy is working")
                    print(f"   📍 Using assigned location: {proxy.get('verified_city')}, {proxy.get('verified_region')}")
                
                print(f"\n🎯 OVERALL: Sticky proxy for account {account_id} is working correctly!")
                return True
            else:
                print(f"❌ Connectivity test FAILED")
                print(f"🔧 Possible issues:")
                print(f"   - SOAX account out of balance")
                print(f"   - Wrong proxy configuration")
                print(f"   - Network connectivity issues")
                return False
            
        except Exception as e:
            logger.error(f"💥 Error testing sticky proxy: {e}")
            print(f"❌ Test failed: {e}")
            return False


    def show_enhanced_account_status(self):
        """Show account status with profile picture information"""
        try:
            print("\n📊 ENHANCED ACCOUNT STATUS")
            print("=" * 60)
            
            accounts = self.db.get_enhanced_active_accounts()
            
            if not accounts:
                print("❌ No accounts found")
                return
            
            # Categorize accounts
            no_pic_accounts = []
            pic_ready_accounts = []
            pic_uploaded_accounts = []
            
            for account in accounts:
                profile_status = account.get('profile_status', 'no')
                profile_picture = account.get('profile_picture', '')
                
                if profile_status == 'yes':
                    pic_uploaded_accounts.append(account)
                elif profile_picture and profile_picture.strip():
                    pic_ready_accounts.append(account)
                else:
                    no_pic_accounts.append(account)
            
            print(f"📋 Total Accounts: {len(accounts)}")
            print(f"✅ Profile Pictures Uploaded: {len(pic_uploaded_accounts)}")
            print(f"📷 Ready for Upload: {len(pic_ready_accounts)}")
            print(f"🎨 Need Generation: {len(no_pic_accounts)}")
            print()
            
            # Show detailed status
            if pic_uploaded_accounts:
                print("✅ ACCOUNTS WITH UPLOADED PROFILE PICTURES:")
                for acc in pic_uploaded_accounts:
                    print(f"  👤 Account {acc['account_id']}: {acc.get('email', 'N/A')[:30]}")
                    print(f"     📱 {acc.get('phone', 'N/A')}")
                    print(f"     📊 Status: {acc.get('status', 'N/A')}")
                print()
            
            if pic_ready_accounts:
                print("📷 ACCOUNTS READY FOR PROFILE PICTURE UPLOAD:")
                for acc in pic_ready_accounts:
                    print(f"  👤 Account {acc['account_id']}: {acc.get('email', 'N/A')[:30]}")
                    print(f"     🖼️ Picture: {acc.get('profile_picture', 'N/A')}")
                print()
            
            if no_pic_accounts:
                print("🎨 ACCOUNTS NEEDING PROFILE PICTURE GENERATION:")
                for acc in no_pic_accounts:
                    print(f"  👤 Account {acc['account_id']}: {acc.get('email', 'N/A')[:30]}")
                    print(f"     📊 Status: {acc.get('status', 'N/A')}")
                print()
                
        except Exception as e:
            logger.error(f"💥 Error showing enhanced account status: {e}")
    
    def run_enhanced_account_warmup(self):
        """Run enhanced warmup cycle for all accounts"""
        try:
            logger.info("🚀 Starting enhanced account warmup cycle...")
            
            accounts = self.db.get_enhanced_active_accounts()
            warming_accounts = [
                acc for acc in accounts 
                if acc['status'] in ['created', 'warming']
            ]
            
            if not warming_accounts:
                print("📋 No accounts found that need warmup")
                return
            
            print(f"\n🔄 Starting enhanced warmup for {len(warming_accounts)} accounts...")
            print("🎯 Enhanced features: profile pictures, AI posts, friends, groups, comments")
            print()
            
            successful_warmups = 0
            
            for i, account in enumerate(warming_accounts, 1):
                logger.info(f"🚀 Running enhanced warmup for account {account['account_id']} ({i}/{len(warming_accounts)})")
                
                try:
                    print(f"\n📊 Account {i}/{len(warming_accounts)}: {account.get('email', 'N/A')[:30]}")
                    
                    success = self.warmup.run_enhanced_warmup_cycle_with_facebook_proof(account)
                    
                    if success:
                        successful_warmups += 1
                        logger.info(f"✅ Enhanced warmup successful for {account['email']}")
                        print(f"✅ Enhanced warmup completed successfully")
                    else:
                        logger.error(f"❌ Enhanced warmup failed for {account['email']}")
                        print(f"❌ Enhanced warmup failed")
                        
                except Exception as e:
                    logger.error(f"💥 Error in enhanced warmup for {account['email']}: {e}")
                    print(f"💥 Enhanced warmup error: {e}")
                
                # Delay between accounts
                if i < len(warming_accounts):
                    delay = 120  # 2 minutes between accounts
                    print(f"⏳ Waiting {delay} seconds before next account...")
                    time.sleep(delay)
            
            print(f"\n🎯 ENHANCED WARMUP SUMMARY:")
            print(f"✅ Successful: {successful_warmups}/{len(warming_accounts)}")
            print(f"❌ Failed: {len(warming_accounts) - successful_warmups}/{len(warming_accounts)}")
            
        except Exception as e:
            logger.error(f"💥 Error in enhanced warmup cycle: {e}")
    
    def generate_missing_profile_pictures(self):
        """Generate profile pictures for accounts that don't have them"""
        try:
            print("\n🎨 GENERATING MISSING PROFILE PICTURES")
            print("=" * 60)
            
            profile_info = self.db.get_accounts_needing_profile_pictures()
            needs_generation = profile_info['needs_generation']
            
            if not needs_generation:
                print("✅ All accounts already have profile pictures!")
                return
            
            print(f"🎨 Found {len(needs_generation)} accounts needing profile picture generation")
            
            generated_count = 0
            
            for i, account in enumerate(needs_generation, 1):
                try:
                    account_id = account['account_id']
                    print(f"\n🎨 Generating profile picture {i}/{len(needs_generation)} for account {account_id}")
                    
                    # Generate profile picture
                    image_path = self.warmup.generate_ai_profile_picture(account)
                    
                    if image_path:
                        generated_count += 1
                        print(f"✅ Generated: {image_path}")
                    else:
                        print(f"❌ Failed to generate profile picture")
                    
                    # Small delay between generations
                    if i < len(needs_generation):
                        time.sleep(5)
                        
                except Exception as e:
                    logger.error(f"💥 Error generating profile picture for account {account['account_id']}: {e}")
                    print(f"❌ Error: {e}")
            
            print(f"\n🎯 GENERATION SUMMARY:")
            print(f"✅ Successfully generated: {generated_count}/{len(needs_generation)}")
            print(f"❌ Failed: {len(needs_generation) - generated_count}/{len(needs_generation)}")
            
        except Exception as e:
            logger.error(f"💥 Error generating missing profile pictures: {e}")
    
    def test_ai_features(self):
        """Test AI features like name generation, posts, comments"""
        try:
            print("\n🧪 TESTING AI FEATURES")
            print("=" * 60)
            
            # Test name generation
            print("🤖 Testing AI name generation...")
            first_name, last_name = self.account_manager.generate_ai_names()
            print(f"   Generated name: {first_name} {last_name}")
            
            # Test birthday/gender generation
            print("\n🎂 Testing birthday/gender generation...")
            month, day, year, gender = self.account_manager.generate_ai_birthday_gender()
            print(f"   Generated: {month}/{day}/{year}, Gender: {gender}")
            
            # Test post generation
            print("\n📝 Testing AI post generation...")
            post = self.warmup.generate_ai_post()
            print(f"   Generated post:\n   {post}")
            
            # Test comment generation
            print("\n💬 Testing AI comment generation...")
            sample_post = "Just bought a new car and loving it!"
            comment = self.warmup.generate_ai_comment(sample_post)
            print(f"   Sample post: {sample_post}")
            print(f"   Generated comment: {comment}")
            
            # Test profile picture prompt
            print("\n🖼️ Testing profile picture prompt generation...")
            prompt = self.warmup.generate_profile_picture_prompt("male")
            print(f"   Generated prompt: {prompt}")
            
            print("\n✅ All AI features tested successfully!")
            
        except Exception as e:
            logger.error(f"💥 Error testing AI features: {e}")
            print(f"❌ AI feature test failed: {e}")
    
    def start_enhanced_automation(self):
        """Start the enhanced automation system"""
        try:
            logger.info("🚀 Starting Enhanced Facebook Marketplace Bot automation...")
            
            self.setup_enhanced_schedule()
            self.run_enhanced_health_check()
            
            print("\n🤖 Enhanced Bot is now running with AI features!")
            print("🎯 Features: AI profiles, smart warmup, profile pictures, AI posts/comments")
            print("Press Ctrl+C to stop.\n")
            
            while True:
                schedule.run_pending()
                time.sleep(60)
                
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
            print("\n👋 Enhanced Bot stopped. Goodbye!")
        
        except Exception as e:
            logger.error(f"💥 Critical error in enhanced automation: {e}")
            print(f"\n❌ Critical error: {e}")
    
    def setup_enhanced_schedule(self):
        """Setup enhanced scheduled tasks"""
        try:
            # Enhanced warmup every 4 hours
            schedule.every(4).hours.do(self.run_enhanced_account_warmup)
            
            # Generate missing profile pictures daily
            schedule.every().day.at("06:00").do(self.generate_missing_profile_pictures)
            
            # Original scheduling
            schedule.every().day.at("07:00").do(self.run_daily_scraping)
            schedule.every().day.at("08:00").do(self.run_daily_messaging)
            schedule.every().hour.do(self.run_reply_monitoring)
            schedule.every(6).hours.do(self.run_enhanced_health_check)
            
            logger.info("Enhanced scheduled tasks configured")
            
        except Exception as e:
            logger.error(f"💥 Error setting up enhanced schedule: {e}")
    
    def run_enhanced_health_check(self):
        """Enhanced health check with profile picture status"""
        try:
            logger.info("🏥 Running enhanced health check...")
            
            accounts = self.db.get_enhanced_active_accounts()
            profile_info = self.db.get_accounts_needing_profile_pictures()
            
            total_count = len(accounts)
            active_count = len([acc for acc in accounts if acc['status'] == 'active'])
            warming_count = len([acc for acc in accounts if acc['status'] == 'warming'])
            needs_pic_count = len(profile_info['needs_generation'])
            ready_upload_count = len(profile_info['needs_upload'])
            
            logger.info(f"📊 Enhanced Health Check Results:")
            logger.info(f"   Total accounts: {total_count}")
            logger.info(f"   Active accounts: {active_count}")
            logger.info(f"   Warming accounts: {warming_count}")
            logger.info(f"   Need profile pictures: {needs_pic_count}")
            logger.info(f"   Ready for upload: {ready_upload_count}")
            
            # Alert if many accounts need profile pictures
            if needs_pic_count > 3:
                alert = f"⚠️ ALERT: {needs_pic_count} accounts need profile picture generation!"
                logger.warning(alert)
            
            if ready_upload_count > 5:
                alert = f"⚠️ ALERT: {ready_upload_count} accounts have profile pictures ready for upload!"
                logger.warning(alert)
                
        except Exception as e:
            logger.error(f"💥 Error in enhanced health check: {e}")
    
    # Keep original methods for compatibility
    def run_daily_scraping(self):
        """Original daily scraping method"""
        try:
            logger.info("🔍 Starting daily marketplace scraping...")
            
            # Get active accounts for scraping
            accounts = self.db.get_enhanced_active_accounts()
            active_accounts = [acc for acc in accounts if acc['status'] == 'active']
            
            if not active_accounts:
                logger.info("📋 No active accounts available for scraping")
                return
            
            logger.info(f"🔍 Starting scraping with {len(active_accounts)} active accounts")
            
            for account in active_accounts[:3]:  # Limit to 3 accounts for scraping
                try:
                    logger.info(f"🔍 Running scraper with account {account['account_id']}")
                    
                    # Use the scraper with this account
                    leads_found = self.scraper.scrape_marketplace_leads(account)
                    
                    if leads_found and len(leads_found) > 0:
                        logger.info(f"✅ Found {len(leads_found)} new leads with account {account['account_id']}")
                    else:
                        logger.info(f"📋 No new leads found with account {account['account_id']}")
                    
                    # Delay between accounts
                    time.sleep(300)  # 5 minutes between accounts
                    
                except Exception as e:
                    logger.error(f"💥 Error scraping with account {account['account_id']}: {e}")
                    continue
            
            logger.info("✅ Daily scraping cycle completed")
            
        except Exception as e:
            logger.error(f"💥 Error in daily scraping: {e}")
    
    def run_daily_messaging(self):
        """Original daily messaging method with enhanced features"""
        try:
            logger.info("📨 Starting daily messaging...")
            
            # Get active accounts
            accounts = self.db.get_enhanced_active_accounts()
            active_accounts = [acc for acc in accounts if acc['status'] == 'active']
            
            if not active_accounts:
                logger.info("📋 No active accounts available for messaging")
                return
            
            # Get unmessaged leads
            leads = self.db.get_unmessaged_leads()
            
            if not leads:
                logger.info("📋 No unmessaged leads found")
                return
            
            logger.info(f"📨 Starting messaging: {len(active_accounts)} accounts, {len(leads)} leads")
            
            messages_sent = 0
            max_messages = 50  # Daily limit
            
            for account in active_accounts:
                if messages_sent >= max_messages:
                    break
                
                account_id = account['account_id']
                account_leads = leads[:5]  # Max 5 leads per account
                
                for lead in account_leads:
                    if messages_sent >= max_messages:
                        break
                    
                    try:
                        logger.info(f"📨 Sending message for lead {lead['lead_id']} with account {account_id}")
                        
                        # Send message using messaging engine
                        success = self.messaging.send_message_to_lead(account, lead)
                        
                        if success:
                            messages_sent += 1
                            logger.info(f"✅ Message sent successfully ({messages_sent}/{max_messages})")
                            
                            # Update lead status
                            self.db.mark_lead_messaged(lead['lead_id'], account_id)
                        else:
                            logger.warning(f"⚠️ Failed to send message for lead {lead['lead_id']}")
                        
                        # Delay between messages
                        time.sleep(random.randint(180, 300))  # 3-5 minutes
                        
                    except Exception as e:
                        logger.error(f"💥 Error sending message for lead {lead['lead_id']}: {e}")
                        continue
            
            logger.info(f"✅ Daily messaging completed: {messages_sent} messages sent")
            
        except Exception as e:
            logger.error(f"💥 Error in daily messaging: {e}")
    
    def run_reply_monitoring(self):
        """Enhanced reply monitoring method"""
        try:
            logger.info("👀 Monitoring replies...")
            
            # Get accounts that have sent messages
            accounts = self.db.get_enhanced_active_accounts()
            messaging_accounts = [acc for acc in accounts if acc['status'] == 'active']
            
            if not messaging_accounts:
                logger.info("📋 No messaging accounts to monitor")
                return
            
            new_replies_found = 0
            
            for account in messaging_accounts[:2]:  # Monitor 2 accounts per cycle
                try:
                    account_id = account['account_id']
                    logger.info(f"👀 Monitoring replies for account {account_id}")
                    
                    # Check for new replies
                    new_replies = self.messaging.check_for_new_replies(account)
                    
                    if new_replies:
                        new_replies_found += len(new_replies)
                        logger.info(f"📬 Found {len(new_replies)} new replies for account {account_id}")
                        
                        # Process each reply
                        for reply in new_replies:
                            try:
                                # Generate and send follow-up using AI
                                followup_sent = self.messaging.send_ai_followup(account, reply)
                                
                                if followup_sent:
                                    logger.info(f"✅ AI follow-up sent for reply {reply['message_id']}")
                                else:
                                    logger.warning(f"⚠️ Failed to send AI follow-up for reply {reply['message_id']}")
                                
                                # Small delay between follow-ups
                                time.sleep(random.randint(60, 120))
                                
                            except Exception as e:
                                logger.error(f"💥 Error processing reply {reply['message_id']}: {e}")
                                continue
                    else:
                        logger.info(f"📭 No new replies found for account {account_id}")
                    
                    # Delay between accounts
                    time.sleep(60)
                    
                except Exception as e:
                    logger.error(f"💥 Error monitoring account {account['account_id']}: {e}")
                    continue
            
            if new_replies_found > 0:
                logger.info(f"✅ Reply monitoring completed: {new_replies_found} new replies processed")
            else:
                logger.info("✅ Reply monitoring completed: No new replies")
            
        except Exception as e:
            logger.error(f"💥 Error in reply monitoring: {e}")
    
    def get_unmessaged_leads(self):
        """Get leads that haven't been messaged yet"""
        try:
            worksheet = self.db.get_worksheet("leads")
            records = worksheet.get_all_records()
            
            unmessaged = [lead for lead in records if lead.get('status', '') != 'messaged']
            return unmessaged[:20]  # Return max 20 leads
            
        except Exception as e:
            logger.error(f"💥 Error getting unmessaged leads: {e}")
            return []
    
    def mark_lead_messaged(self, lead_id, account_id):
        """Mark a lead as messaged"""
        try:
            worksheet = self.db.get_worksheet("leads")
            records = worksheet.get_all_records()
            
            for i, record in enumerate(records, start=2):
                if str(record['lead_id']) == str(lead_id):
                    worksheet.update_cell(i, 12, 'messaged')  # Status column
                    worksheet.update_cell(i, 13, account_id)   # Account that messaged
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"💥 Error marking lead as messaged: {e}")
            return False


def main():
    """Enhanced main entry point"""
    try:
        bot = EnhancedFacebookMarketplaceBot()
        
        if len(sys.argv) > 1 and sys.argv[1] == "--setup":
            bot.run_enhanced_setup_wizard()
        else:
            accounts = bot.db.get_enhanced_active_accounts()
            
            if not accounts:
                print("🤖 No accounts found. Running enhanced setup wizard...")
                bot.run_enhanced_setup_wizard()
            else:
                print(f"Found {len(accounts)} existing accounts.")
                print("Choose an option:")
                print("1. 🚀 Start enhanced automation")
                print("2. ⚙️ Run setup wizard")
                
                choice = input("Enter choice (1-2): ").strip()
                
                if choice == "1":
                    bot.start_enhanced_automation()
                elif choice == "2":
                    bot.run_enhanced_setup_wizard()
                else:
                    print("❌ Invalid choice")
                    
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        logger.error(f"💥 Critical error in main: {e}")
        print(f"❌ Critical error: {e}")

if __name__ == "__main__":
    main()