"""Async PostgreSQL checkpointer for LangGraph."""
from typing import Optional
from psycopg_pool import AsyncConnectionPool
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from app.config import settings
from app.core.logging import get_logger

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
        
        # Connection kwargs - IMPORTANT: autocommit=True to avoid transaction block issues
        connection_kwargs = {
            "autocommit": True,
            "prepare_threshold": None,
        }
        
        # Create connection pool with proper configuration
        self.pool = AsyncConnectionPool(
            conninfo=settings.async_database_url.replace("+psycopg", ""),
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
