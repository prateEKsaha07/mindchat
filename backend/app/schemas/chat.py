from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class MessageResponse(BaseModel):
    id: str
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True

class ConversationResponse(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ChatRequest(BaseModel):
    message: str
    conversation_id : Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    message_id: str