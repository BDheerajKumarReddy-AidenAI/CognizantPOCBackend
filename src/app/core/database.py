"""Database engine and session factory."""
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import settings


# Sync engine for migrations
sync_engine = create_engine(
    settings.database_url,
    echo=settings.app_env == "development",
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Async engine for application
async_engine = create_async_engine(
    settings.async_database_url,
    echo=settings.app_env == "development",
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Session factories
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False
)

SessionLocal = sessionmaker(
    bind=sync_engine,
    autoflush=False,
    autocommit=False
)


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


# Import all models to ensure they're registered with SQLAlchemy
# This must happen AFTER Base is defined
def import_models():
    """Import all models to register them with SQLAlchemy."""
    from app.db.models import (
        User,
        Client,
        Product,
        Opportunity,
        Conversation,
        opportunity_product,
    )


# Call import_models to register everything
import_models()
