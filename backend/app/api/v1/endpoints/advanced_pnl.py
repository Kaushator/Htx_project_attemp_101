"""
Advanced PnL Analytics API Endpoints
Phase 3.1: ML-powered trading analytics
"""

from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.advanced_pnl import get_advanced_pnl_analytics, AdvancedPnLAnalytics
from app.services.cache import get_cache, CacheService

router = APIRouter()


@router.get("/comprehensive", response_model=Dict[str, Any])
async def get_comprehensive_pnl_analysis(
    days: int = Query(30, description="Number of days to analyze", ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    cache_service: CacheService = Depends(get_cache)
):
    """
    Get comprehensive PnL analysis with all metrics:
    - Basic PnL (realized, unrealized, positions)
    - Risk metrics (Sharpe ratio, max drawdown, VaR)
    - Performance metrics (win rate, profit factor)
    - Trading patterns analysis
    - ML predictions
    - Chart data for visualizations
    """
    try:
        analytics = await get_advanced_pnl_analytics(cache_service)
        result = await analytics.comprehensive_pnl_analysis(db, days=days)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/risk-metrics", response_model=Dict[str, Any])
async def get_risk_metrics(
    days: int = Query(30, description="Number of days to analyze", ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    cache_service: CacheService = Depends(get_cache)
):
    """
    Get detailed risk metrics:
    - Sharpe ratio
    - Maximum drawdown
    - Value at Risk (VaR)
    - Win/loss ratios
    - Volatility measures
    """
    try:
        analytics = await get_advanced_pnl_analytics(cache_service)
        
        # Get trades for the period
        from datetime import datetime, timedelta
        from sqlalchemy import select
        from app.models.trade import Trade
        
        since = datetime.utcnow() - timedelta(days=days)
        trades_query = await db.execute(
            select(Trade).where(Trade.time >= since).order_by(Trade.time)
        )
        trades = list(trades_query.scalars().all())
        
        if not trades:
            raise HTTPException(status_code=404, detail="No trades found for the period")
            
        risk_metrics = await analytics._calculate_risk_metrics(trades)
        return {
            "period_days": days,
            "risk_metrics": risk_metrics,
            "analysis_timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Risk analysis failed: {str(e)}")


@router.get("/performance", response_model=Dict[str, Any])
async def get_performance_metrics(
    days: int = Query(30, description="Number of days to analyze", ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    cache_service: CacheService = Depends(get_cache)
):
    """
    Get performance metrics:
    - Symbol-wise performance
    - Trading frequency analysis
    - Hourly trading patterns
    - Volume analysis
    """
    try:
        analytics = await get_advanced_pnl_analytics(cache_service)
        
        # Get trades for the period
        from datetime import datetime, timedelta
        from sqlalchemy import select
        from app.models.trade import Trade
        
        since = datetime.utcnow() - timedelta(days=days)
        trades_query = await db.execute(
            select(Trade).where(Trade.time >= since).order_by(Trade.time)
        )
        trades = list(trades_query.scalars().all())
        
        if not trades:
            raise HTTPException(status_code=404, detail="No trades found for the period")
            
        performance_metrics = await analytics._calculate_performance_metrics(trades)
        return {
            "period_days": days,
            "performance_metrics": performance_metrics,
            "analysis_timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Performance analysis failed: {str(e)}")


@router.get("/predictions", response_model=Dict[str, Any])
async def get_ml_predictions(
    days: int = Query(30, description="Number of days of historical data for predictions", ge=7, le=365),
    db: AsyncSession = Depends(get_db),
    cache_service: CacheService = Depends(get_cache)
):
    """
    Get ML-powered predictions:
    - Price trend analysis
    - 7-day price predictions
    - Volume trend predictions
    - Model confidence scores
    """
    try:
        analytics = await get_advanced_pnl_analytics(cache_service)
        
        # Get trades for the period
        from datetime import datetime, timedelta
        from sqlalchemy import select
        from app.models.trade import Trade
        
        since = datetime.utcnow() - timedelta(days=days)
        trades_query = await db.execute(
            select(Trade).where(Trade.time >= since).order_by(Trade.time)
        )
        trades = list(trades_query.scalars().all())
        
        if not trades:
            raise HTTPException(status_code=404, detail="No trades found for the period")
            
        predictions = await analytics._generate_predictions(trades)
        return {
            "period_days": days,
            "predictions": predictions,
            "analysis_timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.get("/trading-patterns", response_model=Dict[str, Any])
async def get_trading_patterns(
    days: int = Query(30, description="Number of days to analyze", ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    cache_service: CacheService = Depends(get_cache)
):
    """
    Analyze trading patterns:
    - Trend following patterns
    - Mean reversion patterns
    - Momentum patterns
    - Trading style classification
    """
    try:
        analytics = await get_advanced_pnl_analytics(cache_service)
        
        # Get trades for the period
        from datetime import datetime, timedelta
        from sqlalchemy import select
        from app.models.trade import Trade
        
        since = datetime.utcnow() - timedelta(days=days)
        trades_query = await db.execute(
            select(Trade).where(Trade.time >= since).order_by(Trade.time)
        )
        trades = list(trades_query.scalars().all())
        
        if not trades:
            raise HTTPException(status_code=404, detail="No trades found for the period")
            
        patterns = await analytics._analyze_trading_patterns(trades)
        return {
            "period_days": days,
            "trading_patterns": patterns,
            "analysis_timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pattern analysis failed: {str(e)}")


@router.get("/charts", response_model=Dict[str, Any])
async def get_chart_data(
    days: int = Query(30, description="Number of days for chart data", ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    cache_service: CacheService = Depends(get_cache)
):
    """
    Get chart data for visualizations:
    - Daily PnL chart data
    - Cumulative PnL data
    - Symbol distribution
    - Volume over time
    """
    try:
        analytics = await get_advanced_pnl_analytics(cache_service)
        
        # Get trades for the period
        from datetime import datetime, timedelta
        from sqlalchemy import select
        from app.models.trade import Trade
        
        since = datetime.utcnow() - timedelta(days=days)
        trades_query = await db.execute(
            select(Trade).where(Trade.time >= since).order_by(Trade.time)
        )
        trades = list(trades_query.scalars().all())
        
        if not trades:
            raise HTTPException(status_code=404, detail="No trades found for the period")
            
        charts = await analytics._generate_charts(trades)
        return {
            "period_days": days,
            "charts": charts,
            "analysis_timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chart generation failed: {str(e)}")


@router.get("/summary", response_model=Dict[str, Any])
async def get_analytics_summary(
    days: int = Query(7, description="Number of days for quick summary", ge=1, le=90),
    db: AsyncSession = Depends(get_db),
    cache_service: CacheService = Depends(get_cache)
):
    """
    Get quick analytics summary:
    - Key performance indicators
    - Risk highlights
    - Recent trading activity
    - Quick insights
    """
    try:
        analytics = await get_advanced_pnl_analytics(cache_service)
        
        # Get trades for the period
        from datetime import datetime, timedelta
        from sqlalchemy import select
        from app.models.trade import Trade
        
        since = datetime.utcnow() - timedelta(days=days)
        trades_query = await db.execute(
            select(Trade).where(Trade.time >= since).order_by(Trade.time)
        )
        trades = list(trades_query.scalars().all())
        
        if not trades:
            return {
                "period_days": days,
                "summary": {"message": "No recent trading activity"},
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
        # Get key metrics
        basic_pnl = await analytics._calculate_basic_pnl(trades)
        risk_metrics = await analytics._calculate_risk_metrics(trades)
        
        # Create summary
        summary = {
            "total_trades": len(trades),
            "net_pnl": basic_pnl.get("net_pnl", 0),
            "win_rate": risk_metrics.get("win_rate", 0) if "error" not in risk_metrics else 0,
            "sharpe_ratio": risk_metrics.get("sharpe_ratio", 0) if "error" not in risk_metrics else 0,
            "active_positions": len(basic_pnl.get("current_positions", {})),
            "most_traded_symbol": trades[0].symbol if trades else None,
            "trading_days": len(set(t.time.date() for t in trades))
        }
        
        return {
            "period_days": days,
            "summary": summary,
            "analysis_timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summary generation failed: {str(e)}")
