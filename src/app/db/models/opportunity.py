"""Opportunity database model."""
import enum
from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, Text, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class OpportunityStage(str, enum.Enum):
    """Opportunity stage enumeration."""
    PROSPECT = "Prospect"
    QUALIFICATION = "Qualification"
    PROPOSAL = "Proposal"
    QUOTE_REQUESTED = "Quote Requested"
    NEGOTIATION = "Negotiation"
    CLOSED_WON = "Closed Won"
    CLOSED_LOST = "Closed Lost"


class Opportunity(Base):
    """Opportunity model for sales pipeline."""
    
    __tablename__ = "opportunities"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    estimated_value = Column(Numeric(15, 2))
    probability = Column(Integer)
    stage = Column(
        SQLEnum(OpportunityStage, native_enum=False, length=50),
        default=OpportunityStage.PROSPECT,
        nullable=False,
        index=True
    )
    expected_close_date = Column(Date)
    created_date = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    quote_request_notes = Column(Text)
    
    # Relationships
    client = relationship("Client", back_populates="opportunities")
    owner = relationship("User", back_populates="opportunities", foreign_keys=[owner_id])
    quotes = relationship("Quote", back_populates="opportunity", cascade="all, delete-orphan")
    activities = relationship("Activity", back_populates="opportunity")
    
    def __repr__(self) -> str:
        return f"<Opportunity(id={self.id}, name='{self.name}', stage='{self.stage.value}')>"
