"""Main FastAPI application."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    try:
        # Startup
        logger.info(f"🚀 Starting {settings.project_name} v{settings.version}")
        logger.info(f"📊 Environment: {settings.environment}")
        logger.info(f"🤖 Agent Model: {settings.agent_model}")
        
        # Import here to avoid circular imports
        from app.agent.checkpointer import agent_checkpointer
        
        # Initialize agent checkpointer
        try:
            await agent_checkpointer.setup()
            logger.info("✅ Agent checkpointer initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize checkpointer: {e}")
            import traceback
            traceback.print_exc()
        
        yield
        
        # Shutdown
        logger.info(f"🛑 Shutting down {settings.project_name}")
        
        # Cleanup checkpointer
        try:
            await agent_checkpointer.close()
            logger.info("✅ Agent checkpointer closed")
        except Exception as e:
            logger.error(f"❌ Error closing checkpointer: {e}")
            
    except Exception as e:
        logger.error(f"❌ Error in lifespan: {e}")
        import traceback
        traceback.print_exc()
        raise


# Create FastAPI app with lifespan
app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
from app.api.v1 import api_router
from app.agent.endpoints import router as agent_router

app.include_router(api_router, prefix="/api/v1")
app.include_router(agent_router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.project_name,
        "version": settings.version,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "environment": settings.environment
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
