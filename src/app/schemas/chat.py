"""Chat/Agent schemas."""
from typing import Optional
from pydantic import Field
from app.schemas.base import BaseSchema


class ChatRequest(BaseSchema):
    """Schema for chat requests."""
    message: str = Field(..., min_length=1)
    session_id: Optional[str] = Field(None, alias="thread_id")
    user_id: int = Field(..., description="User ID for conversation tracking")


class ChatStreamEvent(BaseSchema):
    """Schema for streaming chat events."""
    current_stage: Optional[str] = None
    final_message: Optional[str] = None
    error: Optional[str] = None
    session_id: str = Field(..., alias="thread_id")
