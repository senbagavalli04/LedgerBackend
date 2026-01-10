import sqlite3
import os

db_path = 'ledger.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check current columns
    cursor.execute("PRAGMA table_info(transactions)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'towards' not in columns:
        print("Adding 'towards' column...")
        cursor.execute("ALTER TABLE transactions ADD COLUMN towards VARCHAR")
    
    if 'cheque_no' not in columns:
        print("Adding 'cheque_no' column...")
        cursor.execute("ALTER TABLE transactions ADD COLUMN cheque_no VARCHAR")
        
    if 'bank_name' not in columns:
        print("Adding 'bank_name' column...")
        cursor.execute("ALTER TABLE transactions ADD COLUMN bank_name VARCHAR")
        
    if 'transaction_date' not in columns:
        print("Adding 'transaction_date' column...")
        cursor.execute("ALTER TABLE transactions ADD COLUMN transaction_date DATETIME")
        # Populate with created_at for existing rows
        cursor.execute("UPDATE transactions SET transaction_date = created_at")
        
    if 'place' not in columns:
        print("Adding 'place' column...")
        cursor.execute("ALTER TABLE transactions ADD COLUMN place VARCHAR")
        
    conn.commit()
    conn.close()
    print("Schema update complete.")
else:
    print("Database file not found")
