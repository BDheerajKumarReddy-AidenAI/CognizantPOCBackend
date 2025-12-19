"""Application configuration."""

from typing import List
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict, TomlConfigSettingsSource
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
TOML_PATH = BASE_DIR / "settings.toml"


# ===============================
# Nested Model Definitions
# ===============================

class AppSettings(BaseModel):
    project_name: str = Field("CRM Sales Agent", description="Project name")
    version: str = Field("1.0.0", description="Application version")
    environment: str = Field("development", description="Environment")
    # app_env: str = Field("development", description="App environment")
    api_host: str = Field("0.0.0.0", description="API host")
    api_port: int = Field(8000, description="API port")
    log_level: str = Field("INFO", description="Log level")


class DatabaseSettings(BaseModel):
    database_url: str = Field(..., description="Synchronous database URL")
    async_database_url: str = Field(..., description="Async database URL")
    echo: bool = Field(False, description="Echo SQL queries")


class CorsSettings(BaseModel):
    backend_origins: List[str] = Field(default_factory=list, description="CORS origins")


class OpenAISettings(BaseModel):
    api_key: str = Field(..., description="OpenAI API key")


class AgentSettings(BaseModel):
    model: str = Field("gpt-4o-mini", description="LLM model")
    temperature: float = Field(0.0, description="Model temperature")


class DynamicsAuthSettings(BaseModel):
    client_id: str = Field(..., description="Azure AD client ID")
    client_secret: str = Field(..., description="Azure AD client secret")
    tenant_id: str = Field(..., description="Azure AD tenant ID")


class DynamicsSettings(BaseModel):
    auth: DynamicsAuthSettings  # Nested auth section
    org: str = Field(..., description="Dynamics 365 organization")
    region: str = Field(..., description="Dynamics 365 region")
    api_version: str = Field("v9.2", description="API version")
    scope: str = Field(..., description="OAuth scope")


class MCPSettings(BaseModel):
    enabled: bool = Field(True, description="Enable MCP")
    url: str = Field(..., description="MCP server URL")
    transport: str = Field("streamable_http", description="Transport type")


# ===============================
# Main Settings Class
# ===============================

class Settings(BaseSettings):
    """
    Central application configuration.
    Loads values from:
    - settings.toml
    - environment variables (override)
    """
    
    app: AppSettings
    database: DatabaseSettings
    cors: CorsSettings
    openai: OpenAISettings
    agent: AgentSettings
    dynamics: DynamicsSettings
    mcp: MCPSettings

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ):
        return (
            init_settings,
            TomlConfigSettingsSource(settings_cls, toml_file=TOML_PATH),
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )

    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore"
    )


# Global settings instance
settings = Settings()
