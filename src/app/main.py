"""
Main FastAPI application combining backend API and agent endpoints.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.core.logging import setup_logging, get_logger

# Import database and models EARLY
from app.core.database import Base
from app.db import models  # This triggers model registration

from app.agent.checkpointer import agent_checkpointer
from app.api.routers import health, opportunities
from app.agent.endpoints import router as agent_router

# Setup logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for startup and shutdown events."""
    # Startup
    logger.info("🚀 Starting Sales Agent API...")
    logger.info(f"📍 Environment: {settings.app_env}")
    
    # Initialize agent checkpointer
    try:
        await agent_checkpointer.setup()
        logger.info("✅ Agent checkpointer initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize agent checkpointer: {e}")
        raise
    
    logger.info("✅ Application started successfully")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down...")
    await agent_checkpointer.close()
    logger.info("✅ Cleanup completed")


# Create FastAPI app
app = FastAPI(
    title="Sales Agent API",
    description="Unified API for sales opportunity management with AI agent",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if not settings.is_production else ["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(opportunities.router, prefix="/api/v1")
app.include_router(agent_router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Sales Agent API",
        "version": "1.0.0",
        "environment": settings.app_env,
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"🚀 Starting server on {settings.api_host}:{settings.api_port}")
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.app_env == "development"
    )
