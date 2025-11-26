"""Client API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db
from app.services.client import ClientService
from app.schemas.client import ClientCreate, ClientUpdate, ClientResponse, ClientListResponse

router = APIRouter()


@router.post("/", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def create_client(
    data: ClientCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new client."""
    service = ClientService(db)
    client = await service.create(data)
    await db.commit()
    return client


@router.get("/", response_model=ClientListResponse)
async def list_clients(db: AsyncSession = Depends(get_db)):
    """List all clients."""
    service = ClientService(db)
    clients = await service.list()
    return {"clients": clients, "total": len(clients)}


@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a client by ID."""
    service = ClientService(db)
    client = await service.get_by_id(client_id)
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    return client


@router.put("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: int,
    data: ClientUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a client."""
    service = ClientService(db)
    client = await service.update(client_id, data)
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    await db.commit()
    return client


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(
    client_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a client."""
    service = ClientService(db)
    deleted = await service.delete(client_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    await db.commit()
