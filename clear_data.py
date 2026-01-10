import os
import sys
from sqlalchemy import text
from database import SessionLocal
import models

def clear_database():
    """
    Clears all records from the 'transactions' table and resets the ID sequence.
    This does NOT delete the database file, only the data within it.
    """
    db = SessionLocal()
    try:
        print("Connecting to database and clearing transaction data...")
        # Delete all records from transactions table
        db.query(models.Transaction).delete()
        
        # Reset the autoincrement ID counter for SQLite if it exists
        try:
            db.execute(text("DELETE FROM sqlite_sequence WHERE name='transactions'"))
        except Exception:
            # Table might not exist yet if no data was ever inserted
            pass
        
        db.commit()
        print("\nSUCCESS: All transaction records have been erased.")
        print("The database structure remains intact.")
    except Exception as e:
        db.rollback()
        print(f"\nERROR while clearing transaction data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 50)
    print("           DATABASE CLEANUP UTILITY")
    print("=" * 50)
    print("!!! WARNING: This will permanently erase all transaction records !!!")
    print("This action cannot be undone.")
    print("-" * 50)
    
    confirm = input("Are you absolutely sure you want to proceed? (yes/no): ")
    if confirm.lower() == 'yes':
        clear_database()
    else:
        print("\nOperation cancelled. No data was deleted.")
