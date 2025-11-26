"""Client schemas."""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr
from app.db.models.client import ClientStatus


class ClientCreate(BaseModel):
    """Schema for creating a client."""
    name: str
    industry: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    status: ClientStatus = ClientStatus.PROSPECT


class ClientUpdate(BaseModel):
    """Schema for updating a client."""
    name: Optional[str] = None
    industry: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    status: Optional[ClientStatus] = None


class ClientResponse(BaseModel):
    """Schema for client response."""
    id: int
    name: str
    industry: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    address: Optional[str]
    status: str
    created_date: datetime

    class Config:
        from_attributes = True


class ClientListResponse(BaseModel):
    """Schema for list of clients."""
    clients: list[ClientResponse]
    total: int
