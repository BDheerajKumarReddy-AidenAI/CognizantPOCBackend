"""Opportunity schemas."""
from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel, Field
from app.db.models.opportunity import OpportunityStage


class OpportunityCreate(BaseModel):
    """Schema for creating an opportunity."""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    estimated_value: Optional[float] = None
    probability: Optional[int] = Field(None, ge=0, le=100)
    expected_close_date: Optional[date] = None
    client_id: int


class OpportunityUpdate(BaseModel):
    """Schema for updating an opportunity."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    estimated_value: Optional[float] = None
    probability: Optional[int] = Field(None, ge=0, le=100)
    expected_close_date: Optional[date] = None
    stage: Optional[OpportunityStage] = None
    quote_request_notes: Optional[str] = None


class QuoteRequest(BaseModel):
    """Schema for requesting a quote (Sales only)."""
    product_ids: list[int] = Field(..., min_length=1)
    quantities: list[int] = Field(..., min_length=1)
    contract_months: int = Field(12, ge=12, le=36)
    notes: Optional[str] = None


class OpportunityResponse(BaseModel):
    """Schema for opportunity response."""
    id: int
    name: str
    description: Optional[str]
    client_id: int
    owner_id: int
    estimated_value: Optional[float]
    probability: Optional[int]
    stage: str
    expected_close_date: Optional[date]
    created_date: datetime
    quote_request_notes: Optional[str]

    class Config:
        from_attributes = True


class OpportunityDetailResponse(BaseModel):
    """Schema for detailed opportunity response with relationships."""
    id: int
    name: str
    description: Optional[str]
    client_id: int
    client_name: str
    owner_id: int
    owner_name: str
    estimated_value: Optional[float]
    probability: Optional[int]
    stage: str
    expected_close_date: Optional[date]
    created_date: datetime
    quote_request_notes: Optional[str]
    quotes_count: int

    class Config:
        from_attributes = True


class OpportunityListResponse(BaseModel):
    """Schema for list of opportunities."""
    opportunities: list[OpportunityResponse]
    total: int
