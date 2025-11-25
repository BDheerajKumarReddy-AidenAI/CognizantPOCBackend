"""Opportunity database model."""
import enum
from sqlalchemy import Column, Integer, String, Enum, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Location(enum.Enum):
    """Location enumeration."""
    USA = "USA"
    UK = "UK"
    INDIA = "India"


class Stage(enum.Enum):
    """Opportunity stage enumeration."""
    LEAD = "Lead"
    QUALIFIED = "Qualified"
    PROPOSAL = "Proposal"
    NEGOTIATION = "Negotiation"
    WON = "Won"
    LOST = "Lost"


class Opportunity(Base):
    """Opportunity model for sales pipeline management."""
    
    __tablename__ = "opportunities"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    location = Column(Enum(Location), nullable=False)
    stage = Column(Enum(Stage), nullable=False, default=Stage.LEAD, index=True)
    quote_amount = Column(Float, nullable=False, default=0.0)
    contract_months = Column(Integer)
    user_count = Column(Integer)
    sales_person = Column(String, nullable=True)
    
    # Foreign Keys
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True, index=True)
    
    # Relationships - use string references and lazy import of secondary table
    creator_user = relationship("User", back_populates="opportunities")
    client = relationship("Client", back_populates="opportunities")
    products = relationship(
        "Product",
        secondary="opportunity_product",  # Use string reference
        back_populates="opportunities"
    )
    
    def __repr__(self) -> str:
        return f"<Opportunity(id={self.id}, name='{self.name}', stage='{self.stage.value}')>"
