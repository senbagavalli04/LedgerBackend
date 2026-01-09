from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import engine, get_db
import models, schemas
from models import TransactionType
from typing import List, Optional
from datetime import datetime
from supabase_utils import upload_database_backup
from apscheduler.schedulers.background import BackgroundScheduler

# Initialize scheduler as None
scheduler = None

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.on_event("startup")
def start_scheduler():
    # Schedule daily backup at the end of the day (23:59)
    global scheduler
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=upload_database_backup, trigger="cron", hour=23, minute=59)
    scheduler.start()
    print("APScheduler started: Daily backup scheduled for 23:59")

@app.on_event("shutdown")
def stop_scheduler():
    if scheduler:
        scheduler.shutdown()

# CORS configuration
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:5173",

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
    return {"Hello": "World"}

@app.post("/api/credit", response_model=schemas.TransactionResponse)
def create_credit(credit: schemas.CreditCreate, db: Session = Depends(get_db)):
    try:
        db_txn = models.Transaction(
            transaction_type=TransactionType.CREDIT,
            name_or_purpose=credit.name_or_purpose,
            amount=credit.amount,
            towards=credit.towards,
            payment_mode=credit.payment_mode,
            bank_name=credit.bank_name,
            cheque_no=credit.cheque_no,
            reference_no=credit.reference_no
        )
        db.add(db_txn)
        db.commit()
        db.refresh(db_txn)
        return db_txn
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/debit", response_model=schemas.TransactionResponse)
def create_debit(debit: schemas.DebitCreate, db: Session = Depends(get_db)):
    try:
        db_txn = models.Transaction(
            transaction_type=TransactionType.DEBIT,
            name_or_purpose=debit.name_or_purpose,
            amount=debit.amount,
            payment_mode=debit.payment_mode,
            bank_name=debit.bank_name,
            cheque_no=debit.cheque_no,
            reference_no=debit.reference_no
        )
        db.add(db_txn)
        db.commit()
        db.refresh(db_txn)
        return db_txn
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/transactions")
def get_transactions(
    date: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    transaction_type: Optional[str] = None,
    payment_mode: Optional[str] = None,
    db: Session = Depends(get_db)
):
    # Fetch ALL transactions sorted by creation date to calculate correct balance
    all_transactions = db.query(models.Transaction).order_by(models.Transaction.created_at.asc()).all()
    
    results = []
    current_balance = 0.0
    
    for txn in all_transactions:
        if txn.transaction_type == TransactionType.CREDIT:
            current_balance += txn.amount
        else:
            current_balance -= txn.amount
            
        # Add running balance to the object (we'll manually construct the response)
        txn_data = {
            "id": txn.id,
            "transaction_type": txn.transaction_type,
            "name_or_purpose": txn.name_or_purpose,
            "amount": txn.amount,
            "towards": txn.towards,
            "payment_mode": txn.payment_mode,
            "bank_name": txn.bank_name,
            "cheque_no": txn.cheque_no,
            "reference_no": txn.reference_no,
            "running_balance": current_balance,
            "created_at": txn.created_at
        }
        results.append(txn_data)

    # Now apply filters to the calculated results
    filtered_results = results
    
    if date:
        try:
            target_date = datetime.strptime(date, "%Y-%m-%d").date()
            filtered_results = [t for t in filtered_results if t["created_at"].date() == target_date]
        except ValueError:
            pass

    if start_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            filtered_results = [t for t in filtered_results if t["created_at"] >= start]
        except ValueError:
            pass
            
    if end_date:
        try:
            end = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
            filtered_results = [t for t in filtered_results if t["created_at"] <= end]
        except ValueError:
            pass
            
    if transaction_type and transaction_type != "ALL":
        filtered_results = [t for t in filtered_results if t["transaction_type"] == transaction_type]
        
    if payment_mode and payment_mode != "ALL":
        filtered_results = [t for t in filtered_results if t["payment_mode"] == payment_mode]
        
    # Return reversed order for history display (newest first)
    return sorted(filtered_results, key=lambda x: x["created_at"], reverse=True)

@app.get("/api/balance", response_model=schemas.BalanceSummary)
def get_balance(db: Session = Depends(get_db)):
    total_credit = db.query(func.sum(models.Transaction.amount)).filter(
        models.Transaction.transaction_type == TransactionType.CREDIT
    ).scalar() or 0.0
    
    total_debit = db.query(func.sum(models.Transaction.amount)).filter(
        models.Transaction.transaction_type == TransactionType.DEBIT
    ).scalar() or 0.0
    
    return schemas.BalanceSummary(
        total_credit=total_credit,
        total_debit=total_debit,
        balance=total_credit - total_debit
    )

@app.post("/api/backup")
def manual_backup(background_tasks: BackgroundTasks):
    background_tasks.add_task(upload_database_backup)
    return {"message": "Backup task started in background"}
