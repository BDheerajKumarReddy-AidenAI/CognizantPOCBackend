"""Quote service with business logic and pricing tiers."""
from typing import Optional
from datetime import date, timedelta
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.db.models.quote import Quote, QuoteStatus
from app.db.models.quote_item import QuoteItem
from app.db.models.opportunity import Opportunity
from app.db.models.user import UserRole
from app.db.models.product import Product
from app.schemas.quote import QuoteCreate, QuoteUpdate
from app.services.base import BaseService
from app.core.logging import get_logger

logger = get_logger(__name__)


class QuoteService(BaseService[Quote]):
    """Service for quote business logic with automatic pricing tiers."""
    
    # Volume discount tiers
    VOLUME_TIERS = [
        (1000, Decimal("0.85")),  # 1000+ units: 15% discount
        (500, Decimal("0.90")),   # 500-999 units: 10% discount
        (100, Decimal("0.95")),   # 100-499 units: 5% discount
        (1, Decimal("1.0"))       # 1-99 units: no discount
    ]
    
    # Contract term discounts
    TERM_DISCOUNTS = {
        36: Decimal("0.80"),  # 36 months: 20% discount
        24: Decimal("0.88"),  # 24 months: 12% discount
        12: Decimal("0.95"),  # 12 months: 5% discount
    }
    
    def __init__(self, db: AsyncSession, user_id: int, user_role: UserRole):
        super().__init__(db)
        self.user_id = user_id
        self.user_role = user_role
    
    def _get_volume_discount(self, quantity: Decimal) -> Decimal:
        """Get volume discount multiplier based on quantity."""
        for threshold, multiplier in self.VOLUME_TIERS:
            if quantity >= threshold:
                return multiplier
        return Decimal("1.0")
    
    def _get_term_discount(self, months: int) -> Decimal:
        """Get term discount multiplier based on contract length."""
        return self.TERM_DISCOUNTS.get(months, Decimal("1.0"))
    
    def _generate_quote_number(self) -> str:
        """Generate unique quote number."""
        import uuid
        return f"Q-{date.today().strftime('%Y%m')}-{uuid.uuid4().hex[:6].upper()}"
    
    async def create(self, data: QuoteCreate, contract_months: Optional[int] = 12) -> Quote:
        """Create a new quote with automatic pricing calculation."""
        try:
            logger.info(f"✨ Creating quote for opportunity: {data.opportunity_id}")
            
            # Check opportunity exists and user has access
            opp_stmt = select(Opportunity).where(Opportunity.id == data.opportunity_id)
            if self.user_role == UserRole.SALES:
                opp_stmt = opp_stmt.where(Opportunity.owner_id == self.user_id)
            
            opp_result = await self.db.execute(opp_stmt)
            opportunity = opp_result.scalar_one_or_none()
            
            if not opportunity:
                raise PermissionError("Opportunity not found or access denied")
            
            # Create quote
            quote = Quote(
                opportunity_id=data.opportunity_id,
                quote_number=self._generate_quote_number(),
                quote_date=data.quote_date,
                valid_until=data.valid_until or (data.quote_date + timedelta(days=30)),
                notes=data.notes,
                created_by_id=self.user_id,
                status=QuoteStatus.DRAFT
            )
            
            self.db.add(quote)
            await self.db.flush()
            
            # Add quote items with automatic discounts
            subtotal = Decimal("0")
            
            for item_data in data.items:
                # Get product if specified
                unit_price = item_data.unit_price
                description = item_data.item_description
                
                if item_data.product_id:
                    product_result = await self.db.execute(
                        select(Product).where(Product.id == item_data.product_id)
                    )
                    product = product_result.scalar_one_or_none()
                    if product:
                        unit_price = product.unit_price
                        description = product.name
                
                # Apply pricing tiers
                quantity = item_data.quantity
                volume_discount = self._get_volume_discount(quantity)
                term_discount = self._get_term_discount(contract_months or 12)
                
                # Calculate line total with automatic discounts
                base_price = unit_price * quantity
                discounted_price = base_price * volume_discount * term_discount
                
                # Apply additional item-level discount if specified
                discount_percent = item_data.discount_percent or Decimal("0")
                line_total = discounted_price * (Decimal("1") - discount_percent / Decimal("100"))
                
                quote_item = QuoteItem(
                    quote_id=quote.id,
                    product_id=item_data.product_id,
                    item_description=description,
                    quantity=quantity,
                    unit_price=unit_price,
                    discount_percent=discount_percent,
                    line_total=line_total
                )
                
                self.db.add(quote_item)
                subtotal += line_total
            
            # Update quote totals
            quote.subtotal = subtotal
            quote.total_amount = subtotal + quote.tax_amount - quote.discount_amount
            
            await self.db.flush()
            await self.db.refresh(quote, ["items", "opportunity", "creator"])
            
            logger.info(f"✅ Created quote {quote.quote_number} | Total: ${quote.total_amount}")
            return quote
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"❌ Error creating quote: {e}")
            raise
    
    async def get_by_id(self, quote_id: int) -> Optional[Quote]:
        """Get quote by ID with permission check and eager loading."""
        try:
            stmt = (
                select(Quote)
                .where(Quote.id == quote_id)
                .options(
                    selectinload(Quote.items).selectinload(QuoteItem.product),
                    selectinload(Quote.opportunity).selectinload(Opportunity.client),
                    selectinload(Quote.opportunity).selectinload(Opportunity.owner),
                    selectinload(Quote.creator)
                )
            )
            
            result = await self.db.execute(stmt)
            quote = result.scalar_one_or_none()
            
            if not quote:
                return None
            
            # Check permissions
            if self.user_role == UserRole.SALES:
                # Sales can only see quotes for their opportunities
                if quote.opportunity.owner_id != self.user_id:
                    return None
            
            return quote
        except Exception as e:
            logger.error(f"❌ Error getting quote: {e}")
            raise
    
    async def list_by_opportunity(self, opportunity_id: int) -> list[Quote]:
        """List all quotes for an opportunity."""
        try:
            stmt = (
                select(Quote)
                .where(Quote.opportunity_id == opportunity_id)
                .options(
                    selectinload(Quote.items).selectinload(QuoteItem.product),
                    selectinload(Quote.creator)
                )
                .order_by(Quote.created_date.desc())
            )
            
            result = await self.db.execute(stmt)
            quotes = list(result.scalars().all())
            
            logger.info(f"Found {len(quotes)} quotes for opportunity {opportunity_id}")
            return quotes
            
        except Exception as e:
            logger.error(f"❌ Error listing quotes: {e}")
            raise
    
    async def update(self, quote_id: int, data: QuoteUpdate) -> Optional[Quote]:
        """Update quote (Pricing can update any, Sales only their own)."""
        try:
            quote = await self.get_by_id(quote_id)
            if not quote:
                return None
            
            logger.info(f"📝 Updating quote: {quote.quote_number}")
            
            # Update fields
            update_data = data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                if value is not None and hasattr(quote, field):
                    setattr(quote, field, value)
            
            # Recalculate total if tax or discount changed
            if data.tax_amount is not None or data.discount_amount is not None:
                quote.total_amount = quote.subtotal + quote.tax_amount - quote.discount_amount
            
            await self.db.flush()
            
            # Re-fetch with eager loading to ensure relationships are loaded
            stmt = (
                select(Quote)
                .where(Quote.id == quote_id)
                .options(
                    selectinload(Quote.items).selectinload(QuoteItem.product),
                    selectinload(Quote.opportunity).selectinload(Opportunity.client),
                    selectinload(Quote.opportunity).selectinload(Opportunity.owner),
                    selectinload(Quote.creator)
                )
            )
            result = await self.db.execute(stmt)
            quote = result.scalar_one()
            
            logger.info(f"✅ Updated quote: {quote.quote_number} | Status: {quote.status.value}")
            return quote
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"❌ Error updating quote: {e}")
            raise
