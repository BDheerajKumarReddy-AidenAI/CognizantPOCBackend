"""Application configuration."""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Application settings."""
    
    # Project Info
    project_name: str = Field(default="CRM Sales Agent", description="Project name")
    version: str = Field(default="1.0.0", description="API version")
    environment: str = Field(default="development", description="Environment (development, production)")
    
    # Database
    database_url: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/sales_db",
        description="Synchronous database URL for Alembic"
    )
    async_database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/sales_db",
        description="Async database URL for application"
    )
    db_echo: bool = Field(default=False, description="Echo SQL queries")
    
    # CORS
    backend_cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="Allowed CORS origins"
    )
    
    # OpenAI
    openai_api_key: str = Field(..., description="OpenAI API key")
    agent_model: str = Field(default="gpt-4o-mini", description="OpenAI model for agent")
    agent_temperature: float = Field(default=0.0, description="Model temperature")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


# Global settings instance
settings = Settings()
