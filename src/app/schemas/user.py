"""User schemas."""
from app.schemas.base import BaseSchema
from app.db.models.user import UserRole


class UserResponse(BaseSchema):
    """Schema for user response."""
    id: int
    name: str
    role: UserRole


class UserListResponse(BaseSchema):
    """Schema for list of users."""
    users: list[UserResponse]
    total: int
