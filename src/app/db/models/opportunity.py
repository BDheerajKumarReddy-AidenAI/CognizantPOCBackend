"""Opportunity database model."""
import enum
from typing import TYPE_CHECKING
from sqlalchemy import Column, Integer, String, Enum as SQLEnum, Float, ForeignKey
from sqlalchemy.orm import relationship, Mapped
from app.core.database import Base

if TYPE_CHECKING:
    from app.db.models.user import User
    from app.db.models.client import Client
    from app.db.models.product import Product


class Location(str, enum.Enum):
    """Location enumeration."""
    USA = "USA"
    UK = "UK"
    INDIA = "India"


class Stage(str, enum.Enum):
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
    location = Column(SQLEnum(Location, native_enum=False, length=50), nullable=False)
    stage = Column(SQLEnum(Stage, native_enum=False, length=50), nullable=False, default=Stage.LEAD, index=True)
    quote_amount = Column(Float, nullable=False, default=0.0)
    contract_months = Column(Integer)
    user_count = Column(Integer)
    sales_person = Column(String, nullable=True)
    
    # Foreign Keys
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True, index=True)
    
    # Relationships
    creator_user: "Mapped[User]" = relationship("User", back_populates="opportunities")
    client: "Mapped[Client]" = relationship("Client", back_populates="opportunities")
    products: "Mapped[list[Product]]" = relationship(
        "Product",
        secondary="opportunity_product",
        back_populates="opportunities"
    )
    
    def __repr__(self) -> str:
        return f"<Opportunity(id={self.id}, name='{self.name}', stage='{self.stage.value}')>"
