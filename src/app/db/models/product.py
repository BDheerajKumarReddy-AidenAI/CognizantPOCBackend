"""Product database model."""
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from app.core.database import Base


class Product(Base):
    """Product model representing sellable items."""
    
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True, index=True)
    price = Column(Float, nullable=False)
    
    # Relationships - use string reference for secondary table
    opportunities = relationship(
        "Opportunity",
        secondary="opportunity_product",  # Use string reference
        back_populates="products"
    )
    
    def __repr__(self) -> str:
        return f"<Product(id={self.id}, name='{self.name}', price={self.price})>"
