"""Activity database model."""
import enum
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class ActivityType(str, enum.Enum):
    """Activity type enumeration."""
    CALL = "Call"
    EMAIL = "Email"
    MEETING = "Meeting"
    TASK = "Task"
    NOTE = "Note"


class Activity(Base):
    """Activity model for tracking interactions."""
    
    __tablename__ = "activities"
    
    id = Column(Integer, primary_key=True, index=True)
    opportunity_id = Column(Integer, ForeignKey("opportunities.id"), nullable=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True, index=True)
    activity_type = Column(
        SQLEnum(ActivityType, native_enum=False, length=50),
        nullable=False
    )
    subject = Column(String(200), nullable=False)
    description = Column(Text)
    activity_date = Column(DateTime(timezone=True), server_default=func.now())
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    opportunity = relationship("Opportunity", back_populates="activities")
    creator = relationship("User", back_populates="activities")
    
    def __repr__(self) -> str:
        return f"<Activity(id={self.id}, type='{self.activity_type.value}', subject='{self.subject}')>"
