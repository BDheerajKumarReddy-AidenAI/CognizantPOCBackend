"""Quote API endpoints."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db, get_current_user
from app.db.models.user import User
from app.services.quote import QuoteService
from app.schemas.quote import (
    QuoteCreate,
    QuoteUpdate,
    QuoteResponse,
    QuoteDetailResponse,
    QuoteListResponse
)

router = APIRouter()


@router.post("/", response_model=QuoteDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_quote(
    data: QuoteCreate,
    contract_months: int = Query(12, ge=12, le=36, description="Contract term in months"),
    user_id: int = Query(..., description="Current user ID"),
    db: AsyncSession = Depends(get_db)
):
    """Create a new quote (Pricing role only)."""
    user = await get_current_user(user_id, db)
    service = QuoteService(db, user.id, user.role)
    
    quote = await service.create(data, contract_months)
    await db.commit()
    
    return {
        "id": quote.id,
        "opportunity_id": quote.opportunity_id,
        "opportunity_name": quote.opportunity.name,
        "quote_number": quote.quote_number,
        "quote_date": quote.quote_date,
        "valid_until": quote.valid_until,
        "subtotal": float(quote.subtotal),
        "tax_amount": float(quote.tax_amount),
        "discount_amount": float(quote.discount_amount),
        "total_amount": float(quote.total_amount),
        "status": quote.status.value,
        "notes": quote.notes,
        "created_by_id": quote.created_by_id,
        "created_by_name": quote.creator.name,
        "created_date": quote.created_date,
        "items": [
            {
                "id": item.id,
                "product_id": item.product_id,
                "item_description": item.item_description,
                "quantity": float(item.quantity),
                "unit_price": float(item.unit_price),
                "discount_percent": float(item.discount_percent),
                "line_total": float(item.line_total)
            }
            for item in quote.items
        ]
    }


@router.get("/opportunity/{opportunity_id}", response_model=QuoteListResponse)
async def list_quotes_by_opportunity(
    opportunity_id: int,
    user_id: int = Query(..., description="Current user ID"),
    db: AsyncSession = Depends(get_db)
):
    """List all quotes for an opportunity."""
    user = await get_current_user(user_id, db)
    service = QuoteService(db, user.id, user.role)
    
    quotes = await service.list_by_opportunity(opportunity_id)
    return {"quotes": quotes, "total": len(quotes)}


@router.get("/{quote_id}", response_model=QuoteDetailResponse)
async def get_quote(
    quote_id: int,
    user_id: int = Query(..., description="Current user ID"),
    db: AsyncSession = Depends(get_db)
):
    """Get a quote by ID."""
    user = await get_current_user(user_id, db)
    service = QuoteService(db, user.id, user.role)
    
    quote = await service.get_by_id(quote_id)
    
    if not quote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quote not found or access denied"
        )
    
    return {
        "id": quote.id,
        "opportunity_id": quote.opportunity_id,
        "opportunity_name": quote.opportunity.name,
        "quote_number": quote.quote_number,
        "quote_date": quote.quote_date,
        "valid_until": quote.valid_until,
        "subtotal": float(quote.subtotal),
        "tax_amount": float(quote.tax_amount),
        "discount_amount": float(quote.discount_amount),
        "total_amount": float(quote.total_amount),
        "status": quote.status.value,
        "notes": quote.notes,
        "created_by_id": quote.created_by_id,
        "created_by_name": quote.creator.name,
        "created_date": quote.created_date,
        "items": [
            {
                "id": item.id,
                "product_id": item.product_id,
                "item_description": item.item_description,
                "quantity": float(item.quantity),
                "unit_price": float(item.unit_price),
                "discount_percent": float(item.discount_percent),
                "line_total": float(item.line_total)
            }
            for item in quote.items
        ]
    }


@router.put("/{quote_id}", response_model=QuoteResponse)
async def update_quote(
    quote_id: int,
    data: QuoteUpdate,
    user_id: int = Query(..., description="Current user ID"),
    db: AsyncSession = Depends(get_db)
):
    """Update a quote (Pricing role can update any, Sales only their own)."""
    user = await get_current_user(user_id, db)
    service = QuoteService(db, user.id, user.role)
    
    quote = await service.update(quote_id, data)
    
    if not quote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quote not found or access denied"
        )
    
    await db.commit()
    return quote
