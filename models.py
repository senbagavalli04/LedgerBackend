import enum

class TransactionType(str, enum.Enum):
    CREDIT = "CREDIT"
    DEBIT = "DEBIT"

class PaymentMode(str, enum.Enum):
    CASH = "CASH"
    CHEQUE = "CHEQUE"
    BANK = "BANK"
