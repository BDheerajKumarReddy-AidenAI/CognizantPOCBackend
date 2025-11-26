"""Activity schemas."""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from app.db.models.activity import ActivityType


class ActivityCreate(BaseModel):
    """Schema for creating an activity."""
    opportunity_id: Optional[int] = None
    client_id: Optional[int] = None
    activity_type: ActivityType
    subject: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None


class ActivityResponse(BaseModel):
    """Schema for activity response."""
    id: int
    opportunity_id: Optional[int]
    client_id: Optional[int]
    activity_type: str
    subject: str
    description: Optional[str]
    activity_date: datetime
    created_by_id: int

    class Config:
        from_attributes = True


class ActivityListResponse(BaseModel):
    """Schema for list of activities."""
    activities: list[ActivityResponse]
    total: int
