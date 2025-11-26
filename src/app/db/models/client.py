"""Client database model."""
import enum
from sqlalchemy import Column, Integer, String, Text, Enum as SQLEnum, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class ClientStatus(str, enum.Enum):
    """Client status enumeration."""
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    PROSPECT = "Prospect"


class Client(Base):
    """Client model representing customer organizations."""
    
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    industry = Column(String(100))
    email = Column(String(255))
    phone = Column(String(50))
    address = Column(Text)
    status = Column(
        SQLEnum(ClientStatus, native_enum=False, length=50),
        default=ClientStatus.PROSPECT,
        nullable=False,
        index=True
    )
    created_date = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    contacts = relationship("Contact", back_populates="client", cascade="all, delete-orphan")
    opportunities = relationship("Opportunity", back_populates="client")
    
    def __repr__(self) -> str:
        return f"<Client(id={self.id}, name='{self.name}', status='{self.status.value}')>"
