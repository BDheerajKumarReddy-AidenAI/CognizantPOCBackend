"""Conversation schemas."""
from datetime import datetime
from typing import Literal
from app.schemas.base import BaseSchema


class ConversationThreadResponse(BaseSchema):
    """Schema for conversation thread summary."""
    thread_id: str
    first_message: str
    created_at: datetime


class ConversationMessageResponse(BaseSchema):
    """Schema for a single conversation message."""
    id: int
    message_type: Literal["human", "ai"]
    message: str
    created_at: datetime


class ConversationMessagesResponse(BaseSchema):
    """Schema for all messages in a conversation thread."""
    thread_id: str
    user_id: int
    messages: list[ConversationMessageResponse]
    total_messages: int
