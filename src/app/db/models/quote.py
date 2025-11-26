"""Quote database model."""
import enum
from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, Text, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class QuoteStatus(str, enum.Enum):
    """Quote status enumeration."""
    DRAFT = "Draft"
    PENDING_REVIEW = "Pending Review"
    APPROVED = "Approved"
    SENT = "Sent"
    ACCEPTED = "Accepted"
    REJECTED = "Rejected"
    EXPIRED = "Expired"


class Quote(Base):
    """Quote model for pricing proposals."""
    
    __tablename__ = "quotes"
    
    id = Column(Integer, primary_key=True, index=True)
    opportunity_id = Column(Integer, ForeignKey("opportunities.id"), nullable=False, index=True)
    quote_number = Column(String(50), unique=True, nullable=False, index=True)
    quote_date = Column(Date, nullable=False)
    valid_until = Column(Date)
    subtotal = Column(Numeric(15, 2), default=0)
    tax_amount = Column(Numeric(15, 2), default=0)
    discount_amount = Column(Numeric(15, 2), default=0)
    total_amount = Column(Numeric(15, 2), default=0)
    status = Column(
        SQLEnum(QuoteStatus, native_enum=False, length=50),
        default=QuoteStatus.DRAFT,
        nullable=False,
        index=True
    )
    notes = Column(Text)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_date = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    opportunity = relationship("Opportunity", back_populates="quotes")
    creator = relationship("User", back_populates="quotes_created", foreign_keys=[created_by_id])
    items = relationship("QuoteItem", back_populates="quote", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        status_val = self.status.value if hasattr(self.status, 'value') else str(self.status)
        return f"<Quote(id={self.id}, number='{self.quote_number}', status='{status_val}')>"
