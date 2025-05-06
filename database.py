from supabase import create_client, Client
import httpx
import uuid

# === Config ===
SUPABASE_URL = "https://qyzkaoglhbrziptrnqqb.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InF5emthb2dsaGJyemlwdHJucXFiIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NjQxNDYxMCwiZXhwIjoyMDYxOTkwNjEwfQ.bEbC4b6Tb1d4TgngpXpTHilPH2BVppLV-Y7dJRINvUE"
client = httpx.Client(timeout=10.0)  # 10 giây timeout
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def generate_uuid():
    return str(uuid.uuid4())

def get_user_by_id(user_id):
    return supabase.table("users").select("*").eq("id", user_id).single().execute().data

def insert_transaction(transaction_data):
    return supabase.table("transactions").insert(transaction_data).execute()

def fetch_transactions(user_id):
    return supabase.table("transactions").select("*").eq("user_id", user_id).execute().data

def delete_transaction(transaction_id):
    return supabase.table("transactions").delete().eq("id", transaction_id).execute()
