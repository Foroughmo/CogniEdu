# config.py
import os
from dotenv import load_dotenv

# Force reload of environment variables
load_dotenv(override=True)

DB_CONFIG = {
    'host': os.getenv('DB_HOST', '34.173.214.158'),
    'user': os.getenv('DB_USER', 'UC_CC_J_1'),
    'password': os.getenv('DB_PASSWORD', '$#fUUG-g]Kme4zdb'),
    'database': os.getenv('DB_NAME', 'calendar_app')
}

print("Current DB_CONFIG:", DB_CONFIG)  # Add this line for debugging

CALENDAR_ID = os.getenv('CALENDAR_ID')
SERVICE_ACCOUNT_FILE = os.getenv('SERVICE_ACCOUNT_FILE')
USER_ID = 1  
SYNC_INTERVAL_MINUTES = 1


