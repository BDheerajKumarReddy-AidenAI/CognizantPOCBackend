"""Opportunity API routes."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.opportunity import (
    OpportunityCreate,
    OpportunityUpdate,
    OpportunityResponse,
    OpportunityListResponse
)
from app.services.opportunity import OpportunityService
from app.db.session import get_db
from app.db.models.opportunity import Stage

router = APIRouter(prefix="/opportunities", tags=["Opportunities"])


@router.post("/", response_model=OpportunityResponse, status_code=201)
async def create_opportunity(
    data: OpportunityCreate,
    user_id: int = Query(..., description="Creator user ID"),
    db: AsyncSession = Depends(get_db)
):
    """Create a new opportunity."""
    service = OpportunityService(db, user_id)
    opportunity = await service.create(data)
    return opportunity


@router.get("/", response_model=OpportunityListResponse)
async def list_opportunities(
    stage: Optional[Stage] = None,
    user_id: int = Query(..., description="User ID"),
    db: AsyncSession = Depends(get_db)
):
    """List all opportunities, optionally filtered by stage."""
    service = OpportunityService(db, user_id)
    opportunities = await service.list(stage)
    return {"opportunities": opportunities, "total": len(opportunities)}


@router.get("/{opp_id}", response_model=OpportunityResponse)
async def get_opportunity(
    opp_id: int,
    user_id: int = Query(..., description="User ID"),
    db: AsyncSession = Depends(get_db)
):
    """Get opportunity by ID."""
    service = OpportunityService(db, user_id)
    opportunity = await service.get_by_id(opp_id)
    
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    
    return opportunity


@router.put("/{opp_id}", response_model=OpportunityResponse)
async def update_opportunity(
    opp_id: int,
    data: OpportunityUpdate,
    user_id: int = Query(..., description="User ID"),
    db: AsyncSession = Depends(get_db)
):
    """Update an opportunity."""
    service = OpportunityService(db, user_id)
    opportunity = await service.update(opp_id, data)
    
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    
    return opportunity


@router.delete("/{opp_id}", status_code=204)
async def delete_opportunity(
    opp_id: int,
    user_id: int = Query(..., description="User ID"),
    db: AsyncSession = Depends(get_db)
):
    """Delete an opportunity."""
    service = OpportunityService(db, user_id)
    success = await service.delete(opp_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Opportunity not found")
