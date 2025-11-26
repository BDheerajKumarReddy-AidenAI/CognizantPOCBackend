"""Product service."""
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate
from app.services.base import BaseService
from app.core.logging import get_logger

logger = get_logger(__name__)


class ProductService(BaseService[Product]):
    """Service for product operations."""
    
    async def create(self, data: ProductCreate) -> Product:
        """Create a new product."""
        try:
            logger.info(f"✨ Creating product: {data.name}")
            
            product = Product(
                name=data.name,
                description=data.description,
                unit_price=data.unit_price,
                category=data.category,
                is_active=data.is_active
            )
            
            self.db.add(product)
            await self.db.flush()
            await self.db.refresh(product)
            
            logger.info(f"✅ Created product ID: {product.id}")
            return product
        except Exception as e:
            await self.db.rollback()
            logger.error(f"❌ Error creating product: {e}")
            raise
    
    async def get_by_id(self, product_id: int) -> Optional[Product]:
        """Get product by ID."""
        try:
            stmt = select(Product).where(Product.id == product_id)
            result = await self.db.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"❌ Error getting product: {e}")
            raise
    
    async def list(self, active_only: bool = True) -> list[Product]:
        """List products."""
        try:
            stmt = select(Product)
            if active_only:
                stmt = stmt.where(Product.is_active == True)
            stmt = stmt.order_by(Product.name)
            
            result = await self.db.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"❌ Error listing products: {e}")
            raise
    
    async def update(self, product_id: int, data: ProductUpdate) -> Optional[Product]:
        """Update a product."""
        try:
            product = await self.get_by_id(product_id)
            if not product:
                return None
            
            logger.info(f"📝 Updating product ID: {product_id}")
            
            update_data = data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                if value is not None and hasattr(product, field):
                    setattr(product, field, value)
            
            await self.db.flush()
            await self.db.refresh(product)
            
            logger.info(f"✅ Updated product ID: {product_id}")
            return product
        except Exception as e:
            await self.db.rollback()
            logger.error(f"❌ Error updating product: {e}")
            raise
