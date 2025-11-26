"""Async PostgreSQL checkpointer for LangGraph."""
from typing import Optional
from psycopg_pool import AsyncConnectionPool
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from app.config import settings
from app.core.logging import get_logger
import sys
import asyncio

# Fix for Windows - set event loop policy BEFORE creating pool
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

logger = get_logger(__name__)


class AgentCheckpointer:
    """Manages async PostgreSQL checkpointer for agent state persistence."""
    
    def __init__(self):
        self.pool: Optional[AsyncConnectionPool] = None
        self.checkpointer: Optional[AsyncPostgresSaver] = None
    
    async def setup(self) -> AsyncPostgresSaver:
        """Initialize connection pool and checkpointer."""
        if self.checkpointer:
            return self.checkpointer
        
        logger.info("🔧 Setting up agent checkpointer...")
        
        # Clean the connection string - psycopg needs plain postgresql:// format
        conninfo = settings.database_url
        
        # Remove any dialect suffixes
        conninfo = conninfo.replace("postgresql+asyncpg://", "postgresql://")
        conninfo = conninfo.replace("postgresql+psycopg://", "postgresql://")
        
        logger.info(f"📡 Connecting to: {conninfo.split('@')[1] if '@' in conninfo else 'database'}")
        
        # Connection kwargs - IMPORTANT: autocommit=True to avoid transaction block issues
        connection_kwargs = {
            "autocommit": True,
            "prepare_threshold": None,
        }
        
        # Create connection pool with proper configuration
        self.pool = AsyncConnectionPool(
            conninfo=conninfo,
            kwargs=connection_kwargs,
            min_size=2,
            max_size=10,
            open=False
        )
        
        # Open pool properly
        await self.pool.open(wait=True)
        logger.info("✅ Connection pool opened")
        
        # Initialize checkpointer
        self.checkpointer = AsyncPostgresSaver(self.pool)
        await self.checkpointer.setup()
        
        logger.info("✅ Agent checkpointer ready")
        return self.checkpointer
    
    async def close(self):
        """Close connection pool and cleanup resources."""
        if self.pool:
            logger.info("🔒 Closing checkpointer pool...")
            await self.pool.close()
            self.pool = None
            self.checkpointer = None
    
    def get(self) -> AsyncPostgresSaver:
        """Get the initialized checkpointer."""
        if not self.checkpointer:
            raise RuntimeError("Checkpointer not initialized. Call setup() first.")
        return self.checkpointer


# Global checkpointer instance
agent_checkpointer = AgentCheckpointer()
