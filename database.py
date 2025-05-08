import os
from supabase import create_client, Client
import httpx
from dotenv import load_dotenv
from pathlib import Path
from streamlit import st

# Load environment variables from .env file
os.environ.clear()
load_dotenv()

# === Config ===
SUPABASE_URL = os.getenv("SUPABASE_URL", st.secrets.get("SUPABASE_URL"))
SUPABASE_KEY = os.getenv("SUPABASE_KEY", st.secrets.get("SUPABASE_KEY"))


client = httpx.Client(timeout=10.0)  # 10 seconds timeout
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
