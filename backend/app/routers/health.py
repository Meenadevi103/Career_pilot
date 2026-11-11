"""Health check router verifying API and database operational status."""

import logging

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    summary="Health check endpoint",
    description="Verifies API and validates PostgreSQL database connectivity.",
    responses={
        200: {
            "description": "System operational and database connected",
            "content": {
                "application/json": {
                    "example": {"status": "ok", "database": "connected"}
                }
            },
        },
        503: {
            "description": "Database connection failure",
            "content": {
                "application/json": {
                    "example": {"status": "error", "database": "disconnected"}
                }
            },
        },
    },
)
async def health_check(db: AsyncSession = Depends(get_db)):
    """Check application health and active database connection."""
    try:
        # Execute lightweight ping query to verify database connection
        await db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as exc:
        logger.error("Database health check failed: %s", exc)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "error", "database": "disconnected"},
        )
