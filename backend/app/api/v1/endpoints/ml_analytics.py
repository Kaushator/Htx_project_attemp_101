"""
ML Analytics API Endpoints
Phase 3.1: Machine Learning powered insights

Provides endpoints for:
- PnL forecasting
- Anomaly detection  
- Risk analysis
- Pattern recognition
"""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.ml_analytics import get_ml_analytics_service, MLAnalyticsService
from app.services.cache import get_cache, CacheService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/predict-pnl")
async def predict_pnl_trend(
    days_ahead: int = Query(7, description="Number of days to forecast", ge=1, le=30),
    symbol: Optional[str] = Query(None, description="Optional symbol filter"),
    db: AsyncSession = Depends(get_db),
    cache_service: CacheService = Depends(get_cache)
):
    """
    🔮 Predict PnL trend for the next N days using ML
    
    **Features:**
    - Time series forecasting with Random Forest
    - Technical indicators integration
    - Confidence scoring
    - Historical model validation
    
    **Parameters:**
    - `days_ahead`: Number of days to forecast (1-30)
    - `symbol`: Optional symbol to filter analysis
    
    **Returns:**
    - Daily PnL predictions
    - Model confidence metrics
    - Historical accuracy
    """
    try:
        ml_service = await get_ml_analytics_service(cache_service)
        result = await ml_service.predict_pnl_trend(
            db=db,
            days_ahead=days_ahead,
            symbol=symbol
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "success": True,
            "data": result,
            "message": f"Generated {days_ahead}-day PnL forecast"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"PnL prediction endpoint failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/detect-anomalies")
async def detect_trading_anomalies(
    lookback_days: int = Query(30, description="Days to analyze", ge=7, le=90),
    db: AsyncSession = Depends(get_db),
    cache_service: CacheService = Depends(get_cache)
):
    """
    🚨 Detect anomalous trading patterns using ML
    
    **Features:**
    - Isolation Forest algorithm
    - Multi-dimensional anomaly scoring
    - Pattern analysis and reasoning
    - Real-time anomaly alerts
    
    **Parameters:**
    - `lookback_days`: Number of days to analyze (7-90)
    
    **Returns:**
    - Detected anomalies with scores
    - Anomaly reasons and patterns
    - Historical anomaly rates
    """
    try:
        ml_service = await get_ml_analytics_service(cache_service)
        result = await ml_service.detect_trading_anomalies(
            db=db,
            lookback_days=lookback_days
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "success": True,
            "data": result,
            "message": f"Analyzed {lookback_days} days for anomalies"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Anomaly detection endpoint failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/risk-analysis")
async def calculate_risk_metrics(
    symbol: Optional[str] = Query(None, description="Optional symbol filter"),
    db: AsyncSession = Depends(get_db),
    cache_service: CacheService = Depends(get_cache)
):
    """
    📊 Calculate advanced risk metrics using ML
    
    **Features:**
    - Value at Risk (VaR) calculation
    - Expected Shortfall analysis
    - Volatility forecasting
    - Risk-adjusted returns
    - Maximum drawdown analysis
    
    **Parameters:**
    - `symbol`: Optional symbol to filter analysis
    
    **Returns:**
    - VaR and Expected Shortfall
    - Volatility predictions
    - Risk scores and levels
    - Sharpe ratio and drawdown
    """
    try:
        ml_service = await get_ml_analytics_service(cache_service)
        result = await ml_service.calculate_risk_metrics(
            db=db,
            symbol=symbol
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "success": True,
            "data": result,
            "message": f"Risk analysis completed for {symbol or 'all symbols'}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Risk analysis endpoint failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/patterns/{pattern_type}")
async def analyze_trading_patterns(
    pattern_type: str,
    db: AsyncSession = Depends(get_db),
    cache_service: CacheService = Depends(get_cache)
):
    """
    🔍 Analyze trading patterns using ML clustering
    
    **Supported Pattern Types:**
    - `hourly`: Hour-by-hour trading analysis
    - `daily`: Day-of-week patterns
    - `volume`: Volume distribution patterns
    
    **Features:**
    - Statistical pattern recognition
    - Peak activity identification
    - Volume concentration analysis
    - Behavioral insights
    
    **Returns:**
    - Pattern breakdown and statistics
    - Peak activity periods
    - Behavioral insights
    """
    if pattern_type not in ["hourly", "daily", "volume"]:
        raise HTTPException(
            status_code=400, 
            detail="Invalid pattern type. Use: hourly, daily, or volume"
        )
    
    try:
        ml_service = await get_ml_analytics_service(cache_service)
        result = await ml_service.analyze_trading_patterns(
            db=db,
            pattern_type=pattern_type
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "success": True,
            "data": result,
            "message": f"Analyzed {pattern_type} trading patterns"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Pattern analysis endpoint failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/ml-dashboard")
async def ml_dashboard_summary(
    db: AsyncSession = Depends(get_db),
    cache_service: CacheService = Depends(get_cache)
):
    """
    🎯 ML Analytics Dashboard Summary
    
    **Provides:**
    - Quick PnL forecast (7 days)
    - Latest anomaly detection results
    - Current risk assessment
    - Key pattern insights
    
    **Optimized for:**
    - Fast response times
    - Dashboard visualization
    - Real-time monitoring
    """
    try:
        ml_service = await get_ml_analytics_service(cache_service)
        
        # Run multiple analyses in parallel
        import asyncio
        
        tasks = [
            ml_service.predict_pnl_trend(db, days_ahead=7),
            ml_service.detect_trading_anomalies(db, lookback_days=30),
            ml_service.calculate_risk_metrics(db),
            ml_service.analyze_trading_patterns(db, pattern_type="hourly")
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        dashboard_data = {
            "pnl_forecast": results[0] if not isinstance(results[0], Exception) else None,
            "anomalies": results[1] if not isinstance(results[1], Exception) else None,
            "risk_metrics": results[2] if not isinstance(results[2], Exception) else None,
            "hourly_patterns": results[3] if not isinstance(results[3], Exception) else None,
        }
        
        # Create summary with safe access
        summary = {
            "forecast_available": (
                dashboard_data["pnl_forecast"] is not None and
                isinstance(dashboard_data["pnl_forecast"], dict) and
                "error" not in dashboard_data["pnl_forecast"]
            ),
            "anomalies_detected": (
                dashboard_data["anomalies"].get("anomalies_detected", 0)
                if isinstance(dashboard_data["anomalies"], dict) else 0
            ),
            "risk_level": (
                dashboard_data["risk_metrics"].get("risk_score", {}).get("level", "unknown")
                if isinstance(dashboard_data["risk_metrics"], dict) else "unknown"
            ),
            "peak_trading_hour": (
                dashboard_data["hourly_patterns"].get("patterns", {}).get("peak_trading_hour")
                if isinstance(dashboard_data["hourly_patterns"], dict) else None
            )
        }
        
        return {
            "success": True,
            "data": dashboard_data,
            "summary": summary,
            "message": "ML dashboard data compiled"
        }
        
    except Exception as e:
        logger.error(f"ML dashboard endpoint failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/model-status")
async def get_model_status(
    cache_service: CacheService = Depends(get_cache)
):
    """
    ⚡ Get ML model status and health
    
    **Returns:**
    - Model availability
    - Last training times
    - Cache status
    - Performance metrics
    """
    try:
        # Check cached model data availability
        cache_keys = [
            "ml_pnl_forecast_7_all",
            "ml_anomaly_detection_30",
            "ml_risk_metrics_all",
            "ml_patterns_hourly"
        ]
        
        status = {}
        for key in cache_keys:
            cached_data = await cache_service.get(key)
            status[key] = {
                "available": cached_data is not None,
                "last_updated": (
                    cached_data.get("generated_at") 
                    if cached_data else None
                )
            }
        
        return {
            "success": True,
            "data": {
                "cache_status": status,
                "ml_service_available": True,
                "supported_features": [
                    "pnl_forecasting",
                    "anomaly_detection", 
                    "risk_analysis",
                    "pattern_recognition"
                ]
            },
            "message": "ML service status retrieved"
        }
        
    except Exception as e:
        logger.error(f"Model status endpoint failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
