"""Base Pydantic schemas."""
from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """Base schema with common configuration."""
    
    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        populate_by_name=True
    )


class SuccessResponse(BaseSchema):
    """Standard success response."""
    success: bool = True
    message: str


class ErrorResponse(BaseSchema):
    """Standard error response."""
    success: bool = False
    error: str
    detail: str | None = None
