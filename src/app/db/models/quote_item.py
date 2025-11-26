"""Quote item database model."""
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class QuoteItem(Base):
    """Quote item model for line items in quotes."""
    
    __tablename__ = "quote_items"
    
    id = Column(Integer, primary_key=True, index=True)
    quote_id = Column(Integer, ForeignKey("quotes.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    item_description = Column(String(500), nullable=False)
    quantity = Column(Numeric(15, 2), nullable=False)
    unit_price = Column(Numeric(15, 2), nullable=False)
    discount_percent = Column(Numeric(5, 2), default=0)
    line_total = Column(Numeric(15, 2), nullable=False)
    
    # Relationships
    quote = relationship("Quote", back_populates="items")
    product = relationship("Product")
    
    def __repr__(self) -> str:
        return f"<QuoteItem(id={self.id}, description='{self.item_description}', total={self.line_total})>"
