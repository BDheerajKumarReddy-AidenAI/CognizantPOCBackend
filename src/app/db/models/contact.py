"""Contact database model."""
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Contact(Base):
    """Contact model representing individuals within client organizations."""
    
    __tablename__ = "contacts"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255))
    phone = Column(String(50))
    job_title = Column(String(100))
    is_primary = Column(Boolean, default=False)
    
    # Relationships
    client = relationship("Client", back_populates="contacts")
    
    def __repr__(self) -> str:
        return f"<Contact(id={self.id}, name='{self.first_name} {self.last_name}')>"
