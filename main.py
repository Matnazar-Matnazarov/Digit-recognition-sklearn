"""
Main entry point for the Paint Digit Recognizer application.

This file serves as the entry point for running the FastAPI application.
Supports both development and production modes.
"""

import asyncio
import os

import uvicorn
import uvloop

# Set uvloop as the event loop policy for better performance
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

if __name__ == "__main__":
    # Check if we're in development or production mode
    is_development = os.getenv("ENVIRONMENT", "development").lower() == "development"

    if is_development:
        # Development mode with auto-reload
        print("🚀 Starting in DEVELOPMENT mode with auto-reload...")
        uvicorn.run(
            "app.asgi:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info",
            access_log=True,
        )
    else:
        # Production mode
        print("🏭 Starting in PRODUCTION mode...")
        uvicorn.run(
            "app.asgi:app",
            host="0.0.0.0",
            port=8000,
            log_level="info",
            access_log=False,
        )
