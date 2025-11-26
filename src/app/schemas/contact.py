"""Contact schemas."""
from typing import Optional
from pydantic import BaseModel, EmailStr


class ContactCreate(BaseModel):
    """Schema for creating a contact."""
    client_id: int
    first_name: str
    last_name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    job_title: Optional[str] = None
    is_primary: bool = False


class ContactUpdate(BaseModel):
    """Schema for updating a contact."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    job_title: Optional[str] = None
    is_primary: Optional[bool] = None


class ContactResponse(BaseModel):
    """Schema for contact response."""
    id: int
    client_id: int
    first_name: str
    last_name: str
    email: Optional[str]
    phone: Optional[str]
    job_title: Optional[str]
    is_primary: bool

    class Config:
        from_attributes = True


class ContactListResponse(BaseModel):
    """Schema for list of contacts."""
    contacts: list[ContactResponse]
    total: int
