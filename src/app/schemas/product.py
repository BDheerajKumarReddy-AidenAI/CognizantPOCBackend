"""Product schemas."""
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    """Schema for creating a product."""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    unit_price: Decimal = Field(..., gt=0)
    category: Optional[str] = None
    is_active: bool = True


class ProductUpdate(BaseModel):
    """Schema for updating a product."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    unit_price: Optional[Decimal] = Field(None, gt=0)
    category: Optional[str] = None
    is_active: Optional[bool] = None


class ProductResponse(BaseModel):
    """Schema for product response."""
    id: int
    name: str
    description: Optional[str]
    unit_price: float
    category: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    """Schema for list of products."""
    products: list[ProductResponse]
    total: int
