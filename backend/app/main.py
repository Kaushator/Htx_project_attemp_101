"""
HTX Project - FastAPI Application
Main entry point for the HTX trading analysis API
"""

import sys
import os
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.logging import setup_logging

# Setup logging first
setup_logging()
logger = logging.getLogger(__name__)

# Core endpoints (always available)
from app.api.v1.endpoints import (
    health, files, trades, cashflow, pnl, htx, 
    websockets, insights, orders, secrets
)
from app.api.v1 import reference

# Optional advanced_pnl (may fail if ML dependencies not installed)
try:
    from app.api.v1.endpoints import advanced_pnl
    ADVANCED_PNL_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Advanced P&L endpoints disabled due to missing dependencies: {e}")
    ADVANCED_PNL_AVAILABLE = False
    advanced_pnl = None

# Optional ML endpoints (may fail if ML dependencies not installed)
try:
    from app.api.v1.endpoints import ml, ml_analytics
    ML_ENDPOINTS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"ML endpoints disabled due to missing dependencies: {e}")
    ML_ENDPOINTS_AVAILABLE = False
    ml = ml_analytics = None

# Optional GCP endpoints (may fail if GCP dependencies not installed)
try:
    from app.api.v1.endpoints import gcp
    GCP_ENDPOINTS_AVAILABLE = True
except (ImportError, SyntaxError) as e:
    logger.warning(f"GCP endpoints disabled due to missing dependencies or syntax errors: {e}")
    GCP_ENDPOINTS_AVAILABLE = False
    gcp = None

from app.db.session import engine
from app.db.init_db import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting HTX Project API...")
    
    # Initialize database
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down HTX Project API...")
    await engine.dispose()


# Create FastAPI application
app = FastAPI(
    title="HTX Trading Analysis API",
    description="Comprehensive trading analysis and reporting tool for HTX exchange",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_hosts_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(files.router, prefix="/api/v1", tags=["files"])
app.include_router(trades.router, prefix="/api/v1", tags=["trades"])
app.include_router(cashflow.router, prefix="/api/v1", tags=["cashflow"])
app.include_router(pnl.router, prefix="/api/v1", tags=["pnl"])
# Include advanced_pnl conditionally
if ADVANCED_PNL_AVAILABLE and advanced_pnl is not None:
    app.include_router(advanced_pnl.router, prefix="/api/v1", tags=["advanced-pnl"])
    logger.info("Advanced P&L endpoints enabled")
else:
    logger.info("Advanced P&L endpoints disabled - install ML dependencies to enable")
app.include_router(htx.router, prefix="/api/v1", tags=["htx"])
app.include_router(orders.router, prefix="/api/v1", tags=["orders"])
app.include_router(insights.router, prefix="/api/v1", tags=["insights"])
app.include_router(websockets.router, prefix="/api/v1", tags=["websockets"])
app.include_router(reference.router, prefix="/api/v1", tags=["reference"])
app.include_router(secrets.router, prefix="/api/v1/secrets", tags=["secrets"])

# Include optional ML endpoints if available
if ML_ENDPOINTS_AVAILABLE and ml is not None and ml_analytics is not None:
    app.include_router(ml.router, prefix="/api/v1/ml", tags=["ml"])
    app.include_router(ml_analytics.router, prefix="/api/v1/ml", tags=["ml-analytics"])
    logger.info("ML endpoints enabled")
else:
    logger.info("ML endpoints disabled - install ML dependencies to enable")

# Include optional GCP endpoints if available
if GCP_ENDPOINTS_AVAILABLE and gcp is not None:
    app.include_router(gcp.router, prefix="/api/v1/gcp", tags=["gcp"])
    logger.info("GCP endpoints enabled")
else:
    logger.info("GCP endpoints disabled - install GCP dependencies to enable")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


@app.get("/")
async def root():
    """Root endpoint with system status"""
    available_endpoints = {
        "core": ["health", "files", "trades", "cashflow", "pnl", "htx", "orders", "insights", "websockets", "reference", "secrets"],
        "advanced_pnl": "enabled" if ADVANCED_PNL_AVAILABLE else "disabled",
        "ml": "enabled" if ML_ENDPOINTS_AVAILABLE else "disabled",
        "gcp": "enabled" if GCP_ENDPOINTS_AVAILABLE else "disabled"
    }
    
    return {
        "message": "HTX Trading Analysis API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": available_endpoints,
        "status": "operational"
    }


if __name__ == "__main__":
    # When running directly, use the app module reference
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
