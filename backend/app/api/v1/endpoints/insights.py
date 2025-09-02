"""
Quick Insights endpoints for Phase 2.2
Fast dashboard data with aggressive caching
Target: time-to-insight ≤ 10 seconds
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.cache import get_cache, CacheService
from app.services.quick_insights import QuickInsightService
from typing import Optional

router = APIRouter()


@router.get("/dashboard")
async def get_dashboard_snapshot(
    db: AsyncSession = Depends(get_db),
    cache: CacheService = Depends(get_cache)
):
    """
    Ultra-fast dashboard snapshot
    Core metrics with 2min cache for instant loading
    """
    service = QuickInsightService(cache)
    return await service.dashboard_snapshot(db)


@router.get("/top-symbols")
async def get_top_symbols(
    limit: int = Query(5, le=20, description="Number of top symbols to return"),
    db: AsyncSession = Depends(get_db),
    cache: CacheService = Depends(get_cache)
):
    """
    Top symbols by trading volume
    Fast aggregation with 5min cache
    """
    service = QuickInsightService(cache)
    symbols = await service.top_symbols_quick(db, limit)
    return {
        "symbols": symbols,
        "limit": limit,
        "total": len(symbols)
    }


@router.get("/activity")
async def get_recent_activity(
    hours: int = Query(24, le=168, description="Hours to look back (max 1 week)"),
    db: AsyncSession = Depends(get_db),
    cache: CacheService = Depends(get_cache)
):
    """
    Recent trading activity breakdown
    Hourly trade counts for mini-charts
    """
    service = QuickInsightService(cache)
    return await service.recent_activity(db, hours)


@router.get("/pnl-estimate") 
async def get_quick_pnl_estimate(
    db: AsyncSession = Depends(get_db),
    cache: CacheService = Depends(get_cache)
):
    """
    Fast PnL approximation (not FIFO accurate)
    For immediate user feedback while accurate calc loads
    """
    service = QuickInsightService(cache)
    return await service.quick_pnl_estimate(db)


@router.get("/streak")
async def get_trading_streak(
    db: AsyncSession = Depends(get_db),
    cache: CacheService = Depends(get_cache)
):
    """
    Current trading streak (consecutive days)
    Gamification element for user engagement
    """
    service = QuickInsightService(cache)
    return await service.trading_streak(db)


@router.get("/health-quick")
async def quick_health_check():
    """
    Minimal health check for monitoring
    No DB queries - fastest possible response
    """
    return {
        "status": "healthy",
        "service": "quick-insights",
        "timestamp": "now",
        "response_time_target": "< 100ms"
    }
