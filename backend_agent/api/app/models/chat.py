from pydantic import BaseModel
from typing import List, Optional
from app.models.financial import FinancialContext


class Message(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    messages: List[Message]
    context: Optional[FinancialContext] = None
