from pydantic import BaseModel, field_validator, Field
from datetime import datetime
from typing import Optional
import re
from models import TransactionType, PaymentMode

class CreditCreate(BaseModel):
    name_or_purpose: str
    amount: float = Field(gt=0)
    towards: str
    payment_mode: PaymentMode
    bank_name: Optional[str] = None
    cheque_no: Optional[str] = None
    reference_no: str
    transaction_date: datetime
    place: Optional[str] = None

    @field_validator('place')
    @classmethod
    def validate_place(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if v and not re.match(r'^[a-zA-Z ]+$', v):
            raise ValueError('Place must contain only letters and spaces')
        return v

    @field_validator('cheque_no', 'reference_no')
    @classmethod
    def validate_reference_str(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if v and not re.match(r'^[a-zA-Z0-9\- ]+$', v):
            raise ValueError('Must contain only letters, digits, spaces or hyphens')
        return v

class DebitCreate(BaseModel):
    name_or_purpose: str
    amount: float = Field(gt=0)
    payment_mode: PaymentMode
    bank_name: Optional[str] = None
    cheque_no: Optional[str] = None
    reference_no: str
    transaction_date: datetime

    @field_validator('cheque_no', 'reference_no')
    @classmethod
    def validate_reference_str(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if v and not re.match(r'^[a-zA-Z0-9\- ]+$', v):
            raise ValueError('Must contain only letters, digits, spaces or hyphens')
        return v

class TransactionResponse(BaseModel):
    id: int
    transaction_type: TransactionType
    name_or_purpose: str
    amount: float
    towards: Optional[str] = None
    payment_mode: PaymentMode
    bank_name: Optional[str] = None
    cheque_no: Optional[str] = None
    reference_no: str
    transaction_date: datetime
    place: Optional[str] = None
    running_balance: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True

class BalanceSummary(BaseModel):
    total_credit: float
    total_debit: float
    balance: float
