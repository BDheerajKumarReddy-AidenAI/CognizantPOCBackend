"""Opportunity API endpoints."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db, get_current_user
from app.db.models.user import User
from app.db.models.opportunity import OpportunityStage
from app.services.opportunity import OpportunityService
from app.schemas.opportunity import (
    OpportunityCreate,
    OpportunityUpdate,
    OpportunityResponse,
    OpportunityDetailResponse,
    OpportunityListResponse,
    QuoteRequest
)

router = APIRouter()


@router.post("/", response_model=OpportunityResponse, status_code=status.HTTP_201_CREATED)
async def create_opportunity(
    data: OpportunityCreate,
    user_id: int = Query(..., description="Current user ID"),
    db: AsyncSession = Depends(get_db)
):
    """Create a new opportunity (Sales only)."""
    user = await get_current_user(user_id, db)
    service = OpportunityService(db, user.id, user.role)
    
    opportunity = await service.create(data)
    await db.commit()
    return opportunity


@router.get("/", response_model=OpportunityListResponse)
async def list_opportunities(
    stage: Optional[str] = Query(None, description="Filter by stage"),
    user_id: int = Query(..., description="Current user ID"),
    db: AsyncSession = Depends(get_db)
):
    """List opportunities (filtered by role)."""
    user = await get_current_user(user_id, db)
    service = OpportunityService(db, user.id, user.role)
    
    stage_enum = None
    if stage:
        try:
            stage_enum = OpportunityStage(stage)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid stage: {stage}"
            )
    
    opportunities = await service.list(stage_enum)
    return {"opportunities": opportunities, "total": len(opportunities)}


@router.get("/{opportunity_id}", response_model=OpportunityDetailResponse)
async def get_opportunity(
    opportunity_id: int,
    user_id: int = Query(..., description="Current user ID"),
    db: AsyncSession = Depends(get_db)
):
    """Get an opportunity by ID."""
    user = await get_current_user(user_id, db)
    service = OpportunityService(db, user.id, user.role)
    
    opportunity = await service.get_by_id(opportunity_id)
    
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found or access denied"
        )
    
    return {
        "id": opportunity.id,
        "name": opportunity.name,
        "description": opportunity.description,
        "client_id": opportunity.client_id,
        "client_name": opportunity.client.name if opportunity.client else "N/A",
        "owner_id": opportunity.owner_id,
        "owner_name": opportunity.owner.name,
        "estimated_value": float(opportunity.estimated_value) if opportunity.estimated_value else None,
        "probability": opportunity.probability,
        "stage": opportunity.stage.value,
        "expected_close_date": opportunity.expected_close_date,
        "created_date": opportunity.created_date,
        "quote_request_notes": opportunity.quote_request_notes,
        "quotes_count": len(opportunity.quotes)
    }


@router.put("/{opportunity_id}", response_model=OpportunityResponse)
async def update_opportunity(
    opportunity_id: int,
    data: OpportunityUpdate,
    user_id: int = Query(..., description="Current user ID"),
    db: AsyncSession = Depends(get_db)
):
    """Update an opportunity (Sales only, own opportunities)."""
    user = await get_current_user(user_id, db)
    service = OpportunityService(db, user.id, user.role)
    
    opportunity = await service.update(opportunity_id, data)
    
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found or access denied"
        )
    
    await db.commit()
    return opportunity


@router.delete("/{opportunity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_opportunity(
    opportunity_id: int,
    user_id: int = Query(..., description="Current user ID"),
    db: AsyncSession = Depends(get_db)
):
    """Delete an opportunity (Sales only, own opportunities)."""
    user = await get_current_user(user_id, db)
    service = OpportunityService(db, user.id, user.role)
    
    deleted = await service.delete(opportunity_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found or access denied"
        )
    
    await db.commit()
