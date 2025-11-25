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
    name = Column(String, nullable=False, index=True)
    role = Column(SQLEnum(UserRole, native_enum=False, length=50), nullable=False)
    
    # Relationships
    opportunities = relationship("Opportunity", back_populates="creator_user")
    conversations = relationship("Conversation", back_populates="user")
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, name='{self.name}', role='{self.role.value}')>"
