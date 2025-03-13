import os
from dotenv import load_dotenv

load_dotenv()

MASTER_CLIENT_ID = os.getenv("MASTER_CLIENT_ID")
MASTER_CLIENT_SECRET = os.getenv("MASTER_CLIENT_SECRET")
MASTER_ADMIN_USERNAME = os.getenv("MASTER_ADMIN_USERNAME")
MASTER_ADMIN_PASSWORD = os.getenv("MASTER_ADMIN_PASSWORD")
