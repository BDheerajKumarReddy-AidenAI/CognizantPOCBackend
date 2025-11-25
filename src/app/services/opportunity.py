"""Opportunity service with business logic."""
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.db.models.opportunity import Opportunity, Stage
from app.db.models.product import Product
from app.schemas.opportunity import OpportunityCreate, OpportunityUpdate
from app.services.base import BaseService
from app.core.logging import get_logger

logger = get_logger(__name__)


class OpportunityService(BaseService[Opportunity]):
    """Service for opportunity business logic and tool functions."""
    
    def __init__(self, db: AsyncSession, user_id: int):
        super().__init__(db)
        self.user_id = user_id
    
    async def create(self, data: OpportunityCreate) -> Opportunity:
        """Create a new opportunity."""
        try:
            logger.info(f"Creating opportunity: {data.name}")
            
            opportunity = Opportunity(
                name=data.name,
                location=data.location,
                contract_months=data.contract_months,
                user_count=data.user_count,
                creator_id=self.user_id,
                client_id=data.client_id,
                stage=Stage.LEAD,
                quote_amount=0.0
            )
            
            # Add products if provided
            if data.product_ids:
                stmt = select(Product).where(Product.id.in_(data.product_ids))
                result = await self.db.execute(stmt)
                products = result.scalars().all()
                opportunity.products = list(products)
            
            self.db.add(opportunity)
            await self.db.flush()
            await self.db.refresh(opportunity)
            
            logger.info(f"Created opportunity ID: {opportunity.id}")
            return opportunity
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating opportunity: {e}")
            raise
    
    async def get_by_id(self, opp_id: int) -> Optional[Opportunity]:
        """
        Get opportunity by ID.
        Only returns opportunity if user is the creator.
        """
        try:
            stmt = select(Opportunity).where(
                Opportunity.id == opp_id,
                Opportunity.creator_id == self.user_id  # Filter by creator
            ).options(
                selectinload(Opportunity.products),
                selectinload(Opportunity.client),
                selectinload(Opportunity.creator_user)
            )
            result = await self.db.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting opportunity: {e}")
            raise
    
    async def list(self, stage: Optional[Stage] = None) -> list[Opportunity]:
        """
        List opportunities created by the current user, optionally filtered by stage.
        """
        try:
            stmt = select(Opportunity).where(
                Opportunity.creator_id == self.user_id  # Filter by creator
            ).options(
                selectinload(Opportunity.products),
                selectinload(Opportunity.client)
            )
            
            if stage:
                stmt = stmt.where(Opportunity.stage == stage)
            
            stmt = stmt.order_by(Opportunity.id.desc())
            result = await self.db.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error listing opportunities: {e}")
            raise
    
    async def update(self, opp_id: int, data: OpportunityUpdate) -> Optional[Opportunity]:
        """
        Update an opportunity.
        Only allows updating if user is the creator.
        """
        try:
            opportunity = await self.get_by_id(opp_id)
            if not opportunity:
                return None
            
            logger.info(f"Updating opportunity ID: {opp_id}")
            
            # Update fields only if they are provided
            update_data = data.model_dump(exclude_unset=True, exclude={"product_ids"}, by_alias=False)
            for field, value in update_data.items():
                if value is not None and hasattr(opportunity, field):
                    setattr(opportunity, field, value)
            
            # Auto-generate quote when moving to Proposal stage
            if data.stage == Stage.PROPOSAL and opportunity.stage != Stage.PROPOSAL:
                logger.info("Generating quote for Proposal stage")
                opportunity.quote_amount = await self._calculate_quote(opportunity)
            
            # Update products if provided
            if data.product_ids is not None:
                stmt = select(Product).where(Product.id.in_(data.product_ids))
                result = await self.db.execute(stmt)
                products = result.scalars().all()
                opportunity.products = list(products)
            
            await self.db.flush()
            await self.db.refresh(opportunity)
            
            logger.info(f"Updated opportunity ID: {opp_id}")
            return opportunity
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating opportunity: {e}")
            raise
    
    async def delete(self, opp_id: int) -> bool:
        """
        Delete an opportunity.
        Only allows deleting if user is the creator.
        """
        try:
            opportunity = await self.get_by_id(opp_id)
            if not opportunity:
                return False
            
            logger.info(f"Deleting opportunity ID: {opp_id}")
            await self.db.delete(opportunity)
            await self.db.flush()
            
            return True
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error deleting opportunity: {e}")
            raise
    
    async def _calculate_quote(self, opportunity: Opportunity) -> float:
        """Calculate quote based on products, contract months, and user count."""
        base_amount = sum(product.price for product in opportunity.products)
        
        if opportunity.contract_months:
            base_amount *= opportunity.contract_months
        
        if opportunity.user_count:
            base_amount *= opportunity.user_count
        
        return round(base_amount, 2)
