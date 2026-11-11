"""FastAPI Application entry point for CareerPilot AI."""

import asyncio
import logging
import sys
from contextlib import asynccontextmanager

# Configure selector event loop on Windows for psycopg async compatibility
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.limiter import limiter
from app.db.session import engine
from app.routers.auth import router as auth_router
from app.routers.health import router as health_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle events management."""
    logger.info(
        "Starting up %s in %s environment...",
        settings.PROJECT_NAME,
        settings.ENVIRONMENT,
    )
    yield
    logger.info("Shutting down %s...", settings.PROJECT_NAME)
    await engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Student Placement and Interview Preparation Platform API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Attach rate limiter to app state and register error handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS strictly allowing frontend origins configured in environment
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register route modules
app.include_router(auth_router)
app.include_router(health_router)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint welcoming clients and directing them to interactive API docs."""
    return {
        "message": "Welcome to CareerPilot AI API",
        "docs": "/docs",
        "health": "/health",
    }
