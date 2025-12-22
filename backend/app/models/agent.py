from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class AgentRequest(BaseModel):
    session_id: str
    message: str = Field(..., min_length=1, max_length=500)

class Message(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime

class AgentResponse(BaseModel):
    session_id: str
    message: str
    tables: Optional[List[dict]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    thought_process: Optional[str] = None  # For debugging

class SessionCreate(BaseModel):
    store_url: str = Field(..., pattern=r'^https?://[\w\-]+(\.[\w\-]+)+[/#?]?.*$')
