"""Base service class."""
from typing import TypeVar, Generic
from sqlalchemy.ext.asyncio import AsyncSession

ModelType = TypeVar("ModelType")


class BaseService(Generic[ModelType]):
    """Base service providing common database operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
