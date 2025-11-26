"""Product API endpoints."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db
from app.services.product import ProductService
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse, ProductListResponse

router = APIRouter()


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    data: ProductCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new product."""
    service = ProductService(db)
    product = await service.create(data)
    await db.commit()
    return product


@router.get("/", response_model=ProductListResponse)
async def list_products(
    active_only: bool = Query(True, description="Filter active products only"),
    db: AsyncSession = Depends(get_db)
):
    """List all products."""
    service = ProductService(db)
    products = await service.list(active_only=active_only)
    return {"products": products, "total": len(products)}


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a product by ID."""
    service = ProductService(db)
    product = await service.get_by_id(product_id)
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return product


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    data: ProductUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a product."""
    service = ProductService(db)
    product = await service.update(product_id, data)
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    await db.commit()
    return product
