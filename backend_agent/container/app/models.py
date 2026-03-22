from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum


class LifeEvent(str, Enum):
    JOB_LOSS = "job_loss"
    MEDICAL_EMERGENCY = "medical_emergency"
    DIVORCE = "divorce"
    NEW_CHILD = "new_child"
    RELOCATION = "relocation"
    OTHER = "other"


class Bill(BaseModel):
    name: str
    amount: float
    due_date: str
    category: str


class Debt(BaseModel):
    name: str
    balance: float
    interest_rate: float
    minimum_payment: float
    type: str


class SpendingEntry(BaseModel):
    date: str
    amount: float
    category: str
    description: Optional[str] = None


class FinancialContext(BaseModel):
    monthly_income: float
    checking_balance: float
    savings_balance: float = 0.0
    bills: List[Bill] = []
    debts: List[Debt] = []
    spending_history: List[SpendingEntry] = []
    credit_score: Optional[int] = None
    life_events: List[LifeEvent] = []
    extra: Optional[Dict[str, Any]] = None


class Message(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    messages: List[Message]
    context: Optional[FinancialContext] = None
