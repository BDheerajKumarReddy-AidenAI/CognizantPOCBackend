"""Startup script with Windows asyncio fix."""
import sys
import asyncio

# CRITICAL: Set event loop policy BEFORE any other imports
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    print("✅ Set Windows event loop policy")

# Now import and run uvicorn
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Disable reload to prevent event loop issues
        log_level="info"
    )
