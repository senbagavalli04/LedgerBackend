from fastapi import FastAPI, HTTPException, BackgroundTasks
from typing import List, Optional
from datetime import datetime
import schemas
from models import TransactionType
from supabase_utils import get_supabase_client

app = FastAPI()

# CORS configuration
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "online", "database": "supabase"}

@app.post("/api/credit", response_model=schemas.TransactionResponse)
def create_credit(credit: schemas.CreditCreate):
    try:
        supabase = get_supabase_client()
        if not supabase:
            raise HTTPException(status_code=500, detail="Supabase client not initialized")

        data = {
            "transaction_type": TransactionType.CREDIT,
            "name_or_purpose": credit.name_or_purpose,
            "amount": credit.amount,
            "towards": credit.towards,
            "payment_mode": credit.payment_mode,
            "bank_name": credit.bank_name,
            "cheque_no": credit.cheque_no,
            "reference_no": credit.reference_no,
            "transaction_date": credit.transaction_date.isoformat(),
            "place": credit.place,
            "created_at": datetime.now().isoformat()
        }
        
        response = supabase.table("transactions").insert(data).execute()
        
        if not response.data:
            raise HTTPException(status_code=400, detail="Failed to insert credit entry")
            
        return response.data[0]
    except Exception as e:
        print(f"Error creating credit: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/debit", response_model=schemas.TransactionResponse)
def create_debit(debit: schemas.DebitCreate):
    try:
        supabase = get_supabase_client()
        if not supabase:
            raise HTTPException(status_code=500, detail="Supabase client not initialized")

        data = {
            "transaction_type": TransactionType.DEBIT,
            "name_or_purpose": debit.name_or_purpose,
            "amount": debit.amount,
            "payment_mode": debit.payment_mode,
            "bank_name": debit.bank_name,
            "cheque_no": debit.cheque_no,
            "reference_no": debit.reference_no,
            "transaction_date": debit.transaction_date.isoformat(),
            "created_at": datetime.now().isoformat()
        }
        
        response = supabase.table("transactions").insert(data).execute()
        
        if not response.data:
            raise HTTPException(status_code=400, detail="Failed to insert debit entry")
            
        return response.data[0]
    except Exception as e:
        print(f"Error creating debit: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/transactions")
def get_transactions(
    date: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    transaction_type: Optional[str] = None,
    payment_mode: Optional[str] = None
):
    try:
        supabase = get_supabase_client()
        if not supabase:
            raise HTTPException(status_code=500, detail="Supabase client not initialized")

        # Fetch ALL to calculate running balance (as was done in the SQLite version)
        # We sort by created_at ascending for balance calculation
        query = supabase.table("transactions").select("*").order("created_at", desc=False)
        response = query.execute()
        
        all_txns = response.data
        results = []
        current_balance = 0.0
        
        for txn in all_txns:
            if txn["transaction_type"] == TransactionType.CREDIT:
                current_balance += txn["amount"]
            else:
                current_balance -= txn["amount"]
            
            txn["running_balance"] = current_balance
            results.append(txn)

        # Apply filters in Python to mimic the previous logic
        filtered_results = results
        
        if date:
            filtered_results = [t for t in filtered_results if t["created_at"].startswith(date)]

        if start_date:
            filtered_results = [t for t in filtered_results if t["created_at"] >= start_date]
            
        if end_date:
            # Append max time to end_date for inclusive filtering
            end_val = f"{end_date}T23:59:59"
            filtered_results = [t for t in filtered_results if t["created_at"] <= end_val]
            
        if transaction_type and transaction_type != "ALL":
            filtered_results = [t for t in filtered_results if t["transaction_type"] == transaction_type]
            
        if payment_mode and payment_mode != "ALL":
            filtered_results = [t for t in filtered_results if t["payment_mode"] == payment_mode]
            
        # Return newest first for UI
        return sorted(filtered_results, key=lambda x: x["created_at"], reverse=True)
    except Exception as e:
        print(f"Error fetching transactions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/balance", response_model=schemas.BalanceSummary)
def get_balance():
    try:
        supabase = get_supabase_client()
        if not supabase:
            raise HTTPException(status_code=500, detail="Supabase client not initialized")

        response = supabase.table("transactions").select("amount, transaction_type").execute()
        txns = response.data
        
        total_credit = sum(t["amount"] for t in txns if t["transaction_type"] == TransactionType.CREDIT)
        total_debit = sum(t["amount"] for t in txns if t["transaction_type"] == TransactionType.DEBIT)
        
        return schemas.BalanceSummary(
            total_credit=total_credit,
            total_debit=total_debit,
            balance=total_credit - total_debit
        )
    except Exception as e:
        print(f"Error calculating balance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/backup")
def manual_backup():
    return {"message": "Database is now managed by Supabase Cloud. Automatic backups are enabled in Supabase Dashboard."}

@app.delete("/api/clear")
def clear_all_transactions():
    try:
        supabase = get_supabase_client()
        if not supabase:
            raise HTTPException(status_code=500, detail="Supabase client not initialized")
        
        # Delete all records where id is not negative (all records)
        response = supabase.table("transactions").delete().neq("id", -1).execute()
        
        return {"message": "All transactions cleared successfully"}
    except Exception as e:
        print(f"Error clearing transactions: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/api/transactions/{transaction_id}")
def delete_transaction(transaction_id: int):
    try:
        supabase = get_supabase_client()
        if not supabase:
            raise HTTPException(status_code=500, detail="Supabase client not initialized")
        
        # Check if exists first (optional but good for debugging)
        response = supabase.table("transactions").delete().eq("id", transaction_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Transaction not found or already deleted")
            
        return {"message": "Transaction deleted successfully"}
    except Exception as e:
        print(f"Error deleting transaction: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/api/transactions/{transaction_id}", response_model=schemas.TransactionResponse)
def update_transaction(transaction_id: int, transaction: schemas.TransactionUpdate):
    try:
        supabase = get_supabase_client()
        if not supabase:
            raise HTTPException(status_code=500, detail="Supabase client not initialized")
        
        data = transaction.model_dump(exclude_unset=True)
        
        # Handle datetime
        if "transaction_date" in data and data["transaction_date"]:
            data["transaction_date"] = data["transaction_date"].isoformat()
            
        response = supabase.table("transactions").update(data).eq("id", transaction_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Transaction not found")
            
        return response.data[0]
    except Exception as e:
        print(f"Error updating transaction: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

