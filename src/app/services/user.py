"""User service."""
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.user import User
from app.schemas.user import UserCreate
from app.services.base import BaseService
from app.core.logging import get_logger

logger = get_logger(__name__)


class UserService(BaseService[User]):
    """Service for user operations."""
    
    async def create(self, data: UserCreate) -> User:
        """Create a new user."""
        try:
            logger.info(f"✨ Creating user: {data.email}")
            
            user = User(
                name=data.name,
                email=data.email,
                role=data.role
            )
            
            self.db.add(user)
            await self.db.flush()
            await self.db.refresh(user)
            
            logger.info(f"✅ Created user ID: {user.id}")
            return user
        except Exception as e:
            await self.db.rollback()
            logger.error(f"❌ Error creating user: {e}")
            raise
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        try:
            stmt = select(User).where(User.id == user_id)
            result = await self.db.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"❌ Error getting user: {e}")
            raise
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        try:
            stmt = select(User).where(User.email == email)
            result = await self.db.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"❌ Error getting user by email: {e}")
            raise
    
    async def list(self) -> list[User]:
        """List all users."""
        try:
            stmt = select(User).order_by(User.name)
            result = await self.db.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"❌ Error listing users: {e}")
            raise
