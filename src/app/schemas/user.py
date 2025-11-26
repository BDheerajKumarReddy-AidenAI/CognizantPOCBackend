"""User schemas."""
from pydantic import BaseModel, EmailStr
from app.db.models.user import UserRole


class UserCreate(BaseModel):
    """Schema for creating a user."""
    name: str
    email: EmailStr
    role: UserRole


class UserResponse(BaseModel):
    """Schema for user response."""
    id: int
    name: str
    email: str
    role: str

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """Schema for list of users."""
    users: list[UserResponse]
    total: int
