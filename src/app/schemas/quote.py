"""Quote schemas."""
from typing import Optional
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, Field
from app.db.models.quote import QuoteStatus


class QuoteItemCreate(BaseModel):
    """Schema for creating a quote item."""
    product_id: Optional[int] = None
    item_description: str = Field(..., min_length=1)
    quantity: Decimal = Field(..., gt=0)
    unit_price: Decimal = Field(..., gt=0)
    discount_percent: Decimal = Field(0, ge=0, le=100)


class QuoteItemResponse(BaseModel):
    """Schema for quote item response."""
    id: int
    product_id: Optional[int]
    item_description: str
    quantity: float
    unit_price: float
    discount_percent: float
    line_total: float

    class Config:
        from_attributes = True


class QuoteCreate(BaseModel):
    """Schema for creating a quote."""
    opportunity_id: int
    quote_date: date
    valid_until: Optional[date] = None
    notes: Optional[str] = None
    items: list[QuoteItemCreate] = Field(..., min_length=1)


class QuoteUpdate(BaseModel):
    """Schema for updating a quote."""
    tax_amount: Optional[Decimal] = Field(None, ge=0)
    discount_amount: Optional[Decimal] = Field(None, ge=0)
    status: Optional[QuoteStatus] = None
    notes: Optional[str] = None


class QuoteResponse(BaseModel):
    """Schema for quote response."""
    id: int
    opportunity_id: int
    quote_number: str
    quote_date: date
    valid_until: Optional[date]
    subtotal: float
    tax_amount: float
    discount_amount: float
    total_amount: float
    status: str
    notes: Optional[str]
    created_by_id: int
    created_date: datetime

    class Config:
        from_attributes = True


class QuoteDetailResponse(BaseModel):
    """Schema for detailed quote response with items."""
    id: int
    opportunity_id: int
    opportunity_name: str
    quote_number: str
    quote_date: date
    valid_until: Optional[date]
    subtotal: float
    tax_amount: float
    discount_amount: float
    total_amount: float
    status: str
    notes: Optional[str]
    created_by_id: int
    created_by_name: str
    created_date: datetime
    items: list[QuoteItemResponse]

    class Config:
        from_attributes = True


class QuoteListResponse(BaseModel):
    """Schema for list of quotes."""
    quotes: list[QuoteResponse]
    total: int
