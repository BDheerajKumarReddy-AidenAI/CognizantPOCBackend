"""Product database model."""
from sqlalchemy import Column, Integer, String, Text, Numeric, Boolean
from app.core.database import Base


class Product(Base):
    """Product model for the product catalog."""
    
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, unique=True, index=True)
    description = Column(Text)
    unit_price = Column(Numeric(15, 2), nullable=False)
    category = Column(String(100), index=True)
    is_active = Column(Boolean, default=True, index=True)
    
    def __repr__(self) -> str:
        return f"<Product(id={self.id}, name='{self.name}', price={self.unit_price})>"
