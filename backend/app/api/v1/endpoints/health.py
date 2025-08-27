"""
Health check endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "message": "HTX Trading Analysis API is running"
    }


@router.get("/health/db")
async def database_health_check(db: AsyncSession = Depends(get_db)):
    """Database health check"""
    try:
        # Simple database connection test
        await db.execute("SELECT 1")
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }


@router.get("/health/full")
async def full_health_check(db: AsyncSession = Depends(get_db)):
    """Full system health check"""
    health_status = {
        "status": "healthy",
        "checks": {
            "api": "healthy",
            "database": "unknown"
        }
    }
    
    # Check database
    try:
        await db.execute("SELECT 1")
        health_status["checks"]["database"] = "healthy"
    except Exception as e:
        health_status["checks"]["database"] = "unhealthy"
        health_status["status"] = "unhealthy"
        health_status["database_error"] = str(e)
    
    return health_status
