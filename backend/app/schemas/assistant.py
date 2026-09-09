from pydantic import BaseModel
from uuid import UUID
from typing import Optional

class ChatMessage(BaseModel):
    role: str
    content: str

class AssistantRequest(BaseModel):
    query: str
    case_id: Optional[UUID] = None
    history: list[ChatMessage] = []

class AssistantResponse(BaseModel):
    answer: str
    sources: list[str] = []
