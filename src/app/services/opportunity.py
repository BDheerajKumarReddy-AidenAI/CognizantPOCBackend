"""Opportunity service with business logic."""
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.db.models.opportunity import Opportunity, OpportunityStage
from app.db.models.user import User, UserRole
from app.db.models.client import Client
from app.schemas.opportunity import OpportunityCreate, OpportunityUpdate
from app.services.base import BaseService
from app.core.logging import get_logger

logger = get_logger(__name__)


class OpportunityService(BaseService[Opportunity]):
    """Service for opportunity business logic."""
    
    def __init__(self, db: AsyncSession, user_id: int, user_role: UserRole):
        super().__init__(db)
        self.user_id = user_id
        self.user_role = user_role
    
    async def create(self, data: OpportunityCreate) -> Opportunity:
        """Create a new opportunity (Sales only)."""
        try:
            if self.user_role != UserRole.SALES:
                raise PermissionError("Only Sales users can create opportunities")
            
            logger.info(f"✨ Creating opportunity: {data.name}")
            
            opportunity = Opportunity(
                name=data.name,
                description=data.description,
                estimated_value=data.estimated_value,
                probability=data.probability,
                expected_close_date=data.expected_close_date,
                client_id=data.client_id,
                owner_id=self.user_id,
                stage=OpportunityStage.PROSPECT
            )
            
            self.db.add(opportunity)
            await self.db.flush()
            await self.db.refresh(opportunity, ["client", "owner"])
            
            logger.info(f"✅ Created opportunity ID: {opportunity.id}")
            return opportunity
        except Exception as e:
            await self.db.rollback()
            logger.error(f"❌ Error creating opportunity: {e}")
            raise
    
    async def get_by_id(self, opp_id: int) -> Optional[Opportunity]:
        """
        Get opportunity by ID with eager loading.
        Sales: Only their own opportunities
        Pricing: All opportunities
        """
        try:
            stmt = (
                select(Opportunity)
                .where(Opportunity.id == opp_id)
                .options(
                    selectinload(Opportunity.client),
                    selectinload(Opportunity.owner),
                    selectinload(Opportunity.quotes)
                )
            )
            
            # Sales can only see their own opportunities
            if self.user_role == UserRole.SALES:
                stmt = stmt.where(Opportunity.owner_id == self.user_id)
            
            result = await self.db.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"❌ Error getting opportunity: {e}")
            raise
    
    async def list(self, stage: Optional[OpportunityStage] = None) -> list[Opportunity]:
        """
        List opportunities with eager loading.
        Sales: Only their own
        Pricing: All opportunities
        """
        try:
            stmt = (
                select(Opportunity)
                .options(
                    selectinload(Opportunity.client),
                    selectinload(Opportunity.owner),
                    selectinload(Opportunity.quotes)
                )
            )
            
            # Filter by role
            if self.user_role == UserRole.SALES:
                stmt = stmt.where(Opportunity.owner_id == self.user_id)
            
            # Filter by stage if provided
            if stage:
                stmt = stmt.where(Opportunity.stage == stage)
            
            stmt = stmt.order_by(Opportunity.created_date.desc())
            
            result = await self.db.execute(stmt)
            opportunities = list(result.scalars().all())
            
            logger.info(f"Found {len(opportunities)} opportunities")
            return opportunities
            
        except Exception as e:
            logger.error(f"❌ Error listing opportunities: {e}")
            raise
    
    async def update(self, opp_id: int, data: OpportunityUpdate) -> Optional[Opportunity]:
        """
        Update an opportunity.
        Sales: Only their own opportunities
        Pricing: Cannot update opportunities
        """
        try:
            if self.user_role == UserRole.PRICING:
                raise PermissionError("Pricing users cannot update opportunities")
            
            opportunity = await self.get_by_id(opp_id)
            if not opportunity:
                return None
            
            logger.info(f"📝 Updating opportunity ID: {opp_id}")
            
            # Update fields
            update_data = data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                if value is not None and hasattr(opportunity, field):
                    setattr(opportunity, field, value)
            
            await self.db.flush()
            await self.db.refresh(opportunity, ["client", "owner"])
            
            logger.info(f"✅ Updated opportunity ID: {opp_id}")
            return opportunity
        except Exception as e:
            await self.db.rollback()
            logger.error(f"❌ Error updating opportunity: {e}")
            raise
    
    async def delete(self, opp_id: int) -> bool:
        """Delete an opportunity (Sales only, their own)."""
        try:
            if self.user_role != UserRole.SALES:
                raise PermissionError("Only Sales users can delete opportunities")
            
            opportunity = await self.get_by_id(opp_id)
            if not opportunity:
                return False
            
            logger.info(f"🗑️ Deleting opportunity ID: {opp_id}")
            await self.db.delete(opportunity)
            await self.db.flush()
            
            return True
        except Exception as e:
            await self.db.rollback()
            logger.error(f"❌ Error deleting opportunity: {e}")
            raise
