"""Test if config is loading correctly."""
from app.config import settings

print(f"✅ Environment: {settings.app_env}")
print(f"✅ Database URL: {settings.database_url[:30]}...")
print(f"✅ OpenAI API Key: {settings.openai_api_key[:10]}..." if settings.openai_api_key else "❌ OpenAI API Key not found!")
print(f"✅ Agent Model: {settings.agent_model}")
