import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Google Sheets
    GOOGLE_SHEETS_CREDS = "credentials.json"
    SPREADSHEET_NAME = "FB_Marketplace_Bot_Data"
    
    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Email Services
    PROTONMAIL_USERNAME = os.getenv("PROTONMAIL_USERNAME")
    PROTONMAIL_PASSWORD = os.getenv("PROTONMAIL_PASSWORD")
    
    # SMS Services - SMSPinVerify
    SMSPINVERIFY_API_KEY = os.getenv("SMSPINVERIFY_API_KEY")
    
    # Legacy 5SIM (keep for backup)
    FIVESIM_API_KEY = os.getenv("FIVESIM_API_KEY")
    
    # Proxy Services - SOAX
    SOAX_USERNAME = os.getenv("SOAX_USERNAME")
    SOAX_PASSWORD = os.getenv("SOAX_PASSWORD")
    SOAX_ENDPOINT = os.getenv("SOAX_ENDPOINT", "residential-proxy.soax.com:9000")
    
    # Proxy Services - BrightData
    BRIGHTDATA_USERNAME = os.getenv("BRIGHTDATA_USERNAME") 
    BRIGHTDATA_PASSWORD = os.getenv("BRIGHTDATA_PASSWORD")
    BRIGHTDATA_ENDPOINT = os.getenv("BRIGHTDATA_ENDPOINT", "brd-customer-hl_12345678-zone-residential:22225")
    
    # Proxy Services - PacketStream
    PACKETSTREAM_USERNAME = os.getenv("PACKETSTREAM_USERNAME")
    PACKETSTREAM_PASSWORD = os.getenv("PACKETSTREAM_PASSWORD")
    PACKETSTREAM_ENDPOINT = os.getenv("PACKETSTREAM_ENDPOINT", "4g.packetstream.io:31112")
    
    # Legacy Proxy Services (backup)
    PROXY_USERNAME = os.getenv("PROXY_USERNAME")
    PROXY_PASSWORD = os.getenv("PROXY_PASSWORD")
    PROXY_ENDPOINT = os.getenv("PROXY_ENDPOINT")
    
    # Anti-Detection Settings
    MULTILOGIN_API_KEY = os.getenv("MULTILOGIN_API_KEY")
    GOLOGIN_API_KEY = os.getenv("GOLOGIN_API_KEY")
    
    # Bot Settings
    MAX_MESSAGES_PER_DAY = 25
    MESSAGE_DELAY_MIN = 2
    MESSAGE_DELAY_MAX = 4
    
    # Account Creation Settings
    ACCOUNTS_PER_PROXY = 1  # How many accounts per proxy
    PROXY_ROTATION_HOURS = 24  # How often to rotate proxies
    FINGERPRINT_REUSE_DAYS = 0  # Never reuse fingerprints
    
    # Target Settings
    TARGET_CITIES = ["Phoenix", "Chandler", "Scottsdale", "Tempe"]
    PRICE_RANGE = {"min": 3000, "max": 25000}
    TARGET_YEARS = list(range(2010, 2025))
    
    # Geolocation Settings (Phoenix area)
    DEFAULT_LOCATION = {
        'latitude': 33.4484,
        'longitude': -112.0740,
        'accuracy': 100
    }
    
    # Rate Limiting
    SMS_REQUESTS_PER_MINUTE = 5
    PROXY_TEST_TIMEOUT = 10
    ACCOUNT_CREATION_DELAY_MIN = 15
    ACCOUNT_CREATION_DELAY_MAX = 25