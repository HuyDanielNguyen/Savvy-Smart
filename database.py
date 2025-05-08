import os
from supabase import create_client, Client
import httpx
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# === Config ===
SUPABASE_URL = "https://qyzkaoglhbrziptrnqqb.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_KEY")  # Get API key from environment variable

client = httpx.Client(timeout=10.0)  # 10 seconds timeout
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
