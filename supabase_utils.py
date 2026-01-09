import os
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

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

def upload_database_backup():
    client = get_supabase_client()
    if not client:
        return
        
    bucket_name = os.getenv("SUPABASE_BUCKET", "backups")
    db_path = "ledger.db"
    
    if not os.path.exists(db_path):
        print("ledger.db not found for backup")
        return
        
    try:
        # Check if bucket exists, if not create it (this might fail if the key doesn't have permissions)
        # For simplicity, we assume the bucket 'backups' is already created in Supabase Dashboard
        
        with open(db_path, 'rb') as f:
            file_data = f.read()
            
            # Archive name with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            blob_name = f"ledger_{timestamp}.db"
            
            # Upload historical backup
            client.storage.from_(bucket_name).upload(
                path=blob_name,
                file=file_data,
                file_options={"cache-control": "3600", "upsert": "true"}
            )
            
            # Update 'latest.db'
            client.storage.from_(bucket_name).upload(
                path="latest.db",
                file=file_data,
                file_options={"cache-control": "3600", "upsert": "true"}
            )
            
        print(f"Successfully backed up database to Supabase: {blob_name}")
    except Exception as e:
        print(f"Error during Supabase database backup: {e}")
