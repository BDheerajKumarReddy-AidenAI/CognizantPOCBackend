"""User database model."""
import enum
from sqlalchemy import Column, Integer, String, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.core.database import Base


class UserRole(str, enum.Enum):
    """User role enumeration."""
    SALES = "Sales"
    PRICING = "Pricing"


class User(Base):
    """User model representing sales and pricing team members."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    role = Column(
        SQLEnum(UserRole, native_enum=False, length=50),
        nullable=False,
        index=True
    )
    
    # Relationships
    opportunities = relationship("Opportunity", back_populates="owner", foreign_keys="Opportunity.owner_id")
    quotes_created = relationship("Quote", back_populates="creator")
    activities = relationship("Activity", back_populates="creator")
    conversations = relationship("Conversation", back_populates="user")
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, name='{self.name}', role='{self.role.value}')>"
