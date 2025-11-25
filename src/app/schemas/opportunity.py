"""Opportunity schemas."""
from typing import Optional
from pydantic import Field
from app.schemas.base import BaseSchema


# Import enums directly - they don't cause circular issues
from app.db.models.opportunity import Location, Stage


class OpportunityBase(BaseSchema):
    """Base opportunity schema."""
    name: str = Field(..., min_length=1, max_length=255, alias="oppurtunity_name")
    location: Location = Location.USA
    contract_months: Optional[int] = Field(None, ge=1, le=120)
    user_count: Optional[int] = Field(None, alias="users_count", ge=1)


class OpportunityCreate(OpportunityBase):
    """Schema for creating opportunities."""
    client_id: Optional[int] = None
    product_ids: Optional[list[int]] = None


class OpportunityUpdate(BaseSchema):
    """Schema for updating opportunities."""
    name: Optional[str] = Field(None, min_length=1, max_length=255, alias="oppurtunity_name")
    location: Optional[Location] = None
    stage: Optional[Stage] = None
    contract_months: Optional[int] = Field(None, ge=1, le=120)
    user_count: Optional[int] = Field(None, alias="users_count", ge=1)
    client_id: Optional[int] = None
    product_ids: Optional[list[int]] = None


class OpportunityResponse(OpportunityBase):
    """Schema for opportunity responses."""
    id: int = Field(..., alias="opp_id")
    stage: Stage
    quote_amount: float
    sales_person: Optional[str] = None
    creator_id: int
    client_id: Optional[int] = None
    
    model_config = BaseSchema.model_config | {"populate_by_name": True}


class OpportunityListResponse(BaseSchema):
    """Schema for list of opportunities."""
    opportunities: list[OpportunityResponse]
    total: int
