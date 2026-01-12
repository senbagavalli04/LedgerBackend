import os
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime

# Get the path to the .env file in the same directory as this script
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
load_dotenv(dotenv_path=env_path)


# Global variable to track initialization
_supabase_client: Client = None

def get_supabase_client():
    global _supabase_client
    if _supabase_client:
        return _supabase_client
    
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        print("SUPABASE_URL or SUPABASE_KEY not set in .env")
        return None
        
    try:
        _supabase_client = create_client(url, key)
        return _supabase_client
    except Exception as e:
        print(f"Error initializing Supabase: {e}")
        return None

