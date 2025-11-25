"""Conversation database model for agent chat history."""
from typing import TYPE_CHECKING
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.sql import func
from app.core.database import Base

if TYPE_CHECKING:
    from app.db.models.user import User


class Conversation(Base):
    """
    Conversation model for storing agent chat history.
    Each message is stored separately with thread_id for grouping.
    """
    
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    thread_id = Column(String, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    message_type = Column(String, nullable=False)  # 'human' or 'ai'
    message = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships - use string reference
    user: "Mapped[User]" = relationship("User", back_populates="conversations")
    
    def __repr__(self) -> str:
        return f"<Conversation(id={self.id}, thread_id='{self.thread_id}', type='{self.message_type}')>"
