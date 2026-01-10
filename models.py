from sqlalchemy import Column, Integer, String, Float, DateTime
from database import Base
import enum
from datetime import datetime

class TransactionType(str, enum.Enum):
    CREDIT = "CREDIT"
    DEBIT = "DEBIT"

class PaymentMode(str, enum.Enum):
    CASH = "CASH"
    CHEQUE = "CHEQUE"
    BANK = "BANK"

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    transaction_type = Column(String, nullable=False)
    name_or_purpose = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    towards = Column(String, nullable=True)
    payment_mode = Column(String, nullable=False)
    bank_name = Column(String, nullable=True)
    cheque_no = Column(String, nullable=True)
    reference_no = Column(String, nullable=False)
    transaction_date = Column(DateTime, default=datetime.now, nullable=False)
    place = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False, index=True)
