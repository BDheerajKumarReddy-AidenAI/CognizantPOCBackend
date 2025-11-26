"""Client service."""
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.db.models.client import Client
from app.schemas.client import ClientCreate, ClientUpdate
from app.services.base import BaseService
from app.core.logging import get_logger

logger = get_logger(__name__)


class ClientService(BaseService[Client]):
    """Service for client operations."""
    
    async def create(self, data: ClientCreate) -> Client:
        """Create a new client."""
        try:
            logger.info(f"✨ Creating client: {data.name}")
            
            client = Client(
                name=data.name,
                industry=data.industry,
                email=data.email,
                phone=data.phone,
                address=data.address,
                status=data.status
            )
            
            self.db.add(client)
            await self.db.flush()
            await self.db.refresh(client)
            
            logger.info(f"✅ Created client ID: {client.id}")
            return client
        except Exception as e:
            await self.db.rollback()
            logger.error(f"❌ Error creating client: {e}")
            raise
    
    async def get_by_id(self, client_id: int) -> Optional[Client]:
        """Get client by ID with eager loading."""
        try:
            stmt = (
                select(Client)
                .where(Client.id == client_id)
                .options(
                    selectinload(Client.contacts),
                    selectinload(Client.opportunities)
                )
            )
            result = await self.db.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"❌ Error getting client: {e}")
            raise
    
    async def list(self) -> list[Client]:
        """List all clients."""
        try:
            stmt = select(Client).order_by(Client.name)
            result = await self.db.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"❌ Error listing clients: {e}")
            raise
    
    async def update(self, client_id: int, data: ClientUpdate) -> Optional[Client]:
        """Update a client."""
        try:
            client = await self.get_by_id(client_id)
            if not client:
                return None
            
            logger.info(f"📝 Updating client ID: {client_id}")
            
            update_data = data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                if value is not None and hasattr(client, field):
                    setattr(client, field, value)
            
            await self.db.flush()
            await self.db.refresh(client)
            
            logger.info(f"✅ Updated client ID: {client_id}")
            return client
        except Exception as e:
            await self.db.rollback()
            logger.error(f"❌ Error updating client: {e}")
            raise
    
    async def delete(self, client_id: int) -> bool:
        """Delete a client."""
        try:
            client = await self.get_by_id(client_id)
            if not client:
                return False
            
            logger.info(f"🗑️ Deleting client ID: {client_id}")
            await self.db.delete(client)
            await self.db.flush()
            
            return True
        except Exception as e:
            await self.db.rollback()
            logger.error(f"❌ Error deleting client: {e}")
            raise
