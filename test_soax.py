#!/usr/bin/env python3
"""
SOAX Configuration Diagnostic Script
Run this to test your SOAX proxy setup before using the sticky proxy system
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

def test_soax_configuration():
    """Test SOAX proxy configuration with detailed diagnostics"""
    
    print("🔧 SOAX CONFIGURATION DIAGNOSTIC")
    print("=" * 60)
    
    # Check 1: Environment variables
    print("\n1. 📋 Checking environment variables...")
    
    soax_username = os.getenv("SOAX_USERNAME")
    soax_password = os.getenv("SOAX_PASSWORD") 
    soax_endpoint = os.getenv("SOAX_ENDPOINT", "proxy.soax.com:5000")
    
    if not soax_username:
        print("❌ SOAX_USERNAME not found in environment")
        return False
    else:
        print(f"✅ SOAX_USERNAME: {soax_username[:20]}...")
    
    if not soax_password:
        print("❌ SOAX_PASSWORD not found in environment")
        return False
    else:
        print(f"✅ SOAX_PASSWORD: {'*' * len(soax_password)}")
    
    print(f"✅ SOAX_ENDPOINT: {soax_endpoint}")
    
    # Check 2: Test different username formats
    print("\n2. 🧪 Testing different SOAX username formats...")
    
    test_usernames = [
        # Format 1: Full city specification
        f"package-309866-country-us-region-arizona-city-phoenix-sessionid-test123",
        # Format 2: Generic US targeting
        f"package-309866-country-us-sessionid-test456",
        # Format 3: Your original username (whatever it is)
        soax_username
    ]
    
    for i, username in enumerate(test_usernames, 1):
        print(f"\n   Format {i}: {username[:50]}...")
        
        proxy_config = {
            'http': f'http://{username}:{soax_password}@{soax_endpoint}',
            'https': f'http://{username}:{soax_password}@{soax_endpoint}'
        }
        
        success = test_proxy_connectivity(proxy_config, f"Format {i}")
        
        if success:
            print(f"   ✅ Format {i} WORKS!")
            print(f"   🎯 Use this format: {username}")
            return True
        else:
            print(f"   ❌ Format {i} failed")
    
    print("\n❌ All username formats failed!")
    print("\n🔧 TROUBLESHOOTING STEPS:")
    print("1. Verify your SOAX account is active and has balance")
    print("2. Check if your SOAX package number is correct (309866)")
    print("3. Try logging into SOAX dashboard to verify credentials")
    print("4. Contact SOAX support if all formats fail")
    
    return False

def test_proxy_connectivity(proxy_config, format_name):
    """Test proxy connectivity with multiple services"""
    
    test_services = [
        {'url': 'http://httpbin.org/ip', 'timeout': 10},
        {'url': 'http://icanhazip.com', 'timeout': 8},
        {'url': 'https://api.ipify.org', 'timeout': 10},
        {'url': 'http://checkip.amazonaws.com', 'timeout': 8}
    ]
    
    successful_tests = 0
    
    for service in test_services:
        try:
            response = requests.get(
                service['url'],
                proxies=proxy_config,
                timeout=service['timeout'],
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            )
            
            if response.status_code == 200:
                ip_result = response.text.strip()
                print(f"     ✅ {service['url']}: {ip_result}")
                successful_tests += 1
            else:
                print(f"     ❌ {service['url']}: HTTP {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"     ⏰ {service['url']}: Timeout")
        except Exception as e:
            print(f"     ❌ {service['url']}: {str(e)[:50]}")
    
    return successful_tests >= 2  # Consider success if 2+ services work

def test_location_detection(username, password, endpoint):
    """Test location detection with working proxy"""
    
    print(f"\n3. 🌍 Testing location detection...")
    
    proxy_config = {
        'http': f'http://{username}:{password}@{endpoint}',
        'https': f'http://{username}:{password}@{endpoint}'
    }
    
    location_services = [
        {
            'url': 'http://ip-api.com/json/',
            'name': 'IP-API',
            'parser': lambda data: f"{data.get('city', 'Unknown')}, {data.get('regionName', 'Unknown')}, {data.get('country', 'Unknown')}"
        },
        {
            'url': 'https://ipapi.co/json/',
            'name': 'IPapi.co', 
            'parser': lambda data: f"{data.get('city', 'Unknown')}, {data.get('region', 'Unknown')}, {data.get('country_name', 'Unknown')}"
        }
    ]
    
    for service in location_services:
        try:
            response = requests.get(
                service['url'],
                proxies=proxy_config,
                timeout=12,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            )
            
            if response.status_code == 200:
                data = response.json()
                location = service['parser'](data)
                print(f"   ✅ {service['name']}: {location}")
                
                # Check if US-based
                if 'United States' in location or 'USA' in location:
                    print(f"   🇺🇸 Confirmed US location")
                else:
                    print(f"   ⚠️ Non-US location detected")
            else:
                print(f"   ❌ {service['name']}: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ {service['name']}: {str(e)[:50]}")

if __name__ == "__main__":
    try:
        success = test_soax_configuration()
        
        if success:
            print("\n🎉 SOAX CONFIGURATION TEST PASSED!")
            print("✅ Your SOAX proxy should work with the sticky proxy system")
        else:
            print("\n❌ SOAX CONFIGURATION TEST FAILED!")
            print("🔧 Please fix the issues above before using sticky proxies")
            
    except KeyboardInterrupt:
        print("\n👋 Test interrupted")
    except Exception as e:
        print(f"\n💥 Test error: {e}")