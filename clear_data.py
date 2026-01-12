import os
import sys
from supabase_utils import get_supabase_client

def get_record_count():
    """Returns the current number of transaction records from Supabase."""
    supabase = get_supabase_client()
    if not supabase:
        return 0
    try:
        response = supabase.table("transactions").select("id", count="exact").execute()
        return response.count if response.count is not None else 0
    except Exception as e:
        print(f"Error counting records: {e}")
        return 0

def clear_database():
    """
    Clears all records from the 'transactions' table in Supabase.
    """
    supabase = get_supabase_client()
    if not supabase:
        print("Error: Could not connect to Supabase.")
        return

    try:
        print("Connecting to Supabase and clearing transaction data...")
        # Delete all records. In Supabase/PostgREST, we filter by something always true to delete all
        # or use a RPC if available. A common way is to filter for id is not null.
        response = supabase.table("transactions").delete().neq("id", -1).execute()
        
        print("\nSUCCESS: All transaction records have been erased from Supabase.")
    except Exception as e:
        print(f"\nERROR while clearing transaction data: {e}")

if __name__ == "__main__":
    print("=" * 50)
    print("      SUPABASE DATABASE CLEANUP UTILITY")
    print("=" * 50)
    
    count = get_record_count()
    if count == 0:
        print("The database is already empty. No records to clear.")
        sys.exit(0)
        
    print(f"!!! WARNING: This will permanently erase {count} records from SUPABASE !!!")
    print("This action cannot be undone.")
    print("-" * 50)
    
    confirm = input(f"Are you absolutely sure you want to delete these {count} records? (yes/no): ")
    if confirm.lower() == 'yes':
        clear_database()
    else:
        print("\nOperation cancelled. No data was deleted.")


