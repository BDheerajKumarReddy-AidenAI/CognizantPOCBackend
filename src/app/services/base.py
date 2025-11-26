"""Base service class."""
from typing import Generic, TypeVar, TYPE_CHECKING
from sqlalchemy.ext.asyncio import AsyncSession

if TYPE_CHECKING:
    from app.core.database import Base

ModelType = TypeVar("ModelType")


class BaseService(Generic[ModelType]):
    """Base service with common database operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
