"""Client database model."""
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base


class Client(Base):
    """Client model representing customers."""
    
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True, index=True)
    
    # Relationships
    opportunities = relationship("Opportunity", back_populates="client")
    
    def __repr__(self) -> str:
        return f"<Client(id={self.id}, name='{self.name}')>"
