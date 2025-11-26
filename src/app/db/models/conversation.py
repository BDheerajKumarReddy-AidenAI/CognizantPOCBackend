"""Conversation database model."""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Conversation(Base):
    """Conversation model for tracking chat history."""
    
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    thread_id = Column(String(255), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    message_type = Column(String(50), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    
    def __repr__(self) -> str:
        return f"<Conversation(id={self.id}, type='{self.message_type}')>"
