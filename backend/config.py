import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass 


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./community_reports.db")
DB_NAME = "community_reports.db" 

ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
BASE_URL = os.getenv("BASE_URL", "http://localhost:8001")


SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    import secrets
    import logging
    logging.warning("CRITICAL SECURITY ALERT: SECRET_KEY is missing from environment!")
    logging.warning("Generating a transient key for this session only. All sessions will be invalidated on restart.")
    SECRET_KEY = secrets.token_hex(32)
    
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

if not GEMINI_API_KEY:
    print("Warning: GEMINI_API_KEY is missing. AI features will not work.")

MIXER_ADDRESSES = [
    "0xd90e2f925da726b50c4ed8d0fb90ad053324f31b", 
    "0x12d66f87a04a9e220743712ce6d9bb1b5616b8fc",
    "0x47ce0c6ed5b0ce3d3a51fdb1c52dc66a7c3c2936",
    "0x910cbd523d972eb0a6f4cae4618ad62622b39dbf",
    "0xa160cdab225685da1d56aa342ad8841c3b53f291", 
    "0x5f6c97c6ad7bdd0ae7e0dd4ca33a4ed3fdabd4d7",
    "0xf4b067dd14e95bab89be928c07cb22e3c94e0daa",
    "0x742d35cc6634c0532925a3b844bc454e4438f44e" 
]

CACHE_DURATION = 10
