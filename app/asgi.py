"""
ASGI application for Paint Digit Recognizer.

This module initializes the FastAPI app with all necessary middleware,
static files, and route configurations for both development and production.
"""

import asyncio
import logging
from contextlib import asynccontextmanager

import uvloop
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware

from app.core import APP_DESCRIPTION, APP_NAME, APP_VERSION, STATIC_DIR
from app.routes import api, home

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging HTTP requests."""

    async def dispatch(self, request: Request, call_next):
        # Skip logging for static files to reduce noise
        if (
            not request.url.path.startswith("/static")
            and request.url.path != "/favicon.ico"
        ):
            logger.info(f"{request.method} {request.url.path}")
        response = await call_next(request)
        if (
            not request.url.path.startswith("/static")
            and request.url.path != "/favicon.ico"
        ):
            logger.info(f"Response status: {response.status_code}")
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info(f"Starting {APP_NAME} v{APP_VERSION}")
    logger.info("Loading ML model...")

    try:
        # Import here to trigger model loading
        from app.models.predictor import Predictor
        from app.routes import api, home

        # Initialize predictor in both modules
        home.predictor = Predictor()
        api.predictor = Predictor()

        logger.info("ML model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load ML model: {e}")
        raise

    yield

    # Shutdown
    logger.info(f"Shutting down {APP_NAME}")


# Create FastAPI application
app = FastAPI(
    title=APP_NAME,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(GZipMiddleware, minimum_size=1000)  # Compress responses > 1KB
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Mount static files with cache headers
class CachedStaticFiles(StaticFiles):
    """Static files with cache headers and security."""

    def is_not_modified(self, response_headers, request_headers) -> bool:
        return super().is_not_modified(response_headers, request_headers)

    async def __call__(self, scope, receive, send):
        response = await super().__call__(scope, receive, send)
        if hasattr(response, "headers"):
            # Cache headers
            response.headers["Cache-Control"] = "public, max-age=31536000"
            # Security headers
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
        return response


app.mount("/static", CachedStaticFiles(directory=str(STATIC_DIR)), name="static")


# Add favicon route for better compatibility
@app.get("/favicon.ico")
async def favicon():
    """Serve favicon from static directory."""
    from fastapi.responses import FileResponse

    return FileResponse(
        str(STATIC_DIR / "favicon.ico"),
        headers={
            "Cache-Control": "public, max-age=31536000",
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
        },
    )


@app.get("/robots.txt")
async def robots():
    """Serve robots.txt from static directory."""
    from fastapi.responses import FileResponse

    return FileResponse(
        str(STATIC_DIR / "robots.txt"),
        headers={
            "Content-Type": "text/plain",
            "Cache-Control": "public, max-age=86400",
            "X-Content-Type-Options": "nosniff",
        },
    )


# Include routers
app.include_router(home.router, tags=["home"])
app.include_router(api.router, tags=["api"])


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/api/health")
async def api_health_check():
    """API health check endpoint."""
    return {"status": "healthy", "app": APP_NAME, "version": APP_VERSION}
