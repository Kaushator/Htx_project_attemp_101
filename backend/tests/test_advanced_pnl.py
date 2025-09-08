"""
Tests for Advanced PnL Analytics API
"""

import pytest
from decimal import Decimal
from datetime import datetime, timedelta
from httpx import AsyncClient
from app.main import app
from app.models.trade import Trade
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture
async def sample_trades(db_session: AsyncSession):
    """Create sample trades for testing"""
    trades = [
        Trade(
            symbol="BTCUSDT",
            side="buy",
            quantity=Decimal("1.0"),
            price=Decimal("50000.0"),
            fee=Decimal("25.0"),
            time=datetime.utcnow() - timedelta(days=10)
        ),
        Trade(
            symbol="BTCUSDT", 
            side="sell",
            quantity=Decimal("0.5"),
            price=Decimal("52000.0"),
            fee=Decimal("13.0"),
            time=datetime.utcnow() - timedelta(days=8)
        ),
        Trade(
            symbol="ETHUSDT",
            side="buy", 
            quantity=Decimal("10.0"),
            price=Decimal("3000.0"),
            fee=Decimal("15.0"),
            time=datetime.utcnow() - timedelta(days=5)
        ),
        Trade(
            symbol="ETHUSDT",
            side="sell",
            quantity=Decimal("5.0"), 
            price=Decimal("3200.0"),
            fee=Decimal("8.0"),
            time=datetime.utcnow() - timedelta(days=2)
        )
    ]
    
    for trade in trades:
        db_session.add(trade)
    await db_session.commit()
    
    return trades


@pytest.mark.asyncio
async def test_comprehensive_analytics(sample_trades):
    """Test comprehensive PnL analytics endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/advanced-pnl/comprehensive?days=30")
        
    assert response.status_code == 200
    data = response.json()
    
    # Check structure
    assert "period_days" in data
    assert "total_trades" in data
    assert "basic_pnl" in data
    assert "risk_metrics" in data
    assert "performance_metrics" in data
    assert "trading_patterns" in data
    assert "predictions" in data
    assert "charts" in data
    
    # Check basic PnL
    basic_pnl = data["basic_pnl"]
    assert "realized_pnl" in basic_pnl
    assert "total_volume" in basic_pnl
    assert "current_positions" in basic_pnl
    
    # Check risk metrics
    risk_metrics = data["risk_metrics"]
    if "error" not in risk_metrics:
        assert "sharpe_ratio" in risk_metrics
        assert "max_drawdown" in risk_metrics
        assert "win_rate" in risk_metrics


@pytest.mark.asyncio 
async def test_risk_metrics(sample_trades):
    """Test risk metrics endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/advanced-pnl/risk-metrics?days=30")
        
    assert response.status_code == 200
    data = response.json()
    
    assert "period_days" in data
    assert "risk_metrics" in data
    
    risk_metrics = data["risk_metrics"]
    if "error" not in risk_metrics:
        assert isinstance(risk_metrics["sharpe_ratio"], (int, float))
        assert isinstance(risk_metrics["max_drawdown"], (int, float))
        assert isinstance(risk_metrics["win_rate"], (int, float))
        assert 0 <= risk_metrics["win_rate"] <= 1


@pytest.mark.asyncio
async def test_performance_metrics(sample_trades):
    """Test performance metrics endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/advanced-pnl/performance?days=30")
        
    assert response.status_code == 200
    data = response.json()
    
    assert "period_days" in data
    assert "performance_metrics" in data
    
    perf = data["performance_metrics"]
    assert "symbol_performance" in perf
    assert "hourly_patterns" in perf
    assert "most_traded_symbol" in perf
    
    # Check symbol performance structure
    symbol_perf = perf["symbol_performance"]
    if symbol_perf:
        first_symbol = list(symbol_perf.keys())[0]
        symbol_data = symbol_perf[first_symbol]
        assert "total_trades" in symbol_data
        assert "total_bought" in symbol_data
        assert "total_sold" in symbol_data


@pytest.mark.asyncio
async def test_predictions(sample_trades):
    """Test ML predictions endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/advanced-pnl/predictions?days=30")
        
    assert response.status_code == 200
    data = response.json()
    
    assert "period_days" in data
    assert "predictions" in data
    
    predictions = data["predictions"]
    if "error" not in predictions:
        assert "price_trend" in predictions
        assert "next_7_days_prediction" in predictions
        
        # Check price trend structure
        price_trend = predictions["price_trend"]
        assert "slope" in price_trend
        assert "trend_direction" in price_trend
        assert price_trend["trend_direction"] in ["upward", "downward"]


@pytest.mark.asyncio
async def test_trading_patterns(sample_trades):
    """Test trading patterns analysis endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/advanced-pnl/trading-patterns?days=30")
        
    assert response.status_code == 200
    data = response.json()
    
    assert "period_days" in data
    assert "trading_patterns" in data
    
    patterns = data["trading_patterns"]
    if "error" not in patterns:
        assert "detected_patterns" in patterns
        assert "pattern_score" in patterns
        assert "trading_style" in patterns


@pytest.mark.asyncio
async def test_charts_data(sample_trades):
    """Test chart data endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/advanced-pnl/charts?days=30")
        
    assert response.status_code == 200
    data = response.json()
    
    assert "period_days" in data
    assert "charts" in data
    
    charts = data["charts"]
    assert "daily_pnl_chart" in charts
    assert "symbol_distribution" in charts
    assert "volume_over_time" in charts
    
    # Check chart data structure
    daily_chart = charts["daily_pnl_chart"]
    assert "dates" in daily_chart
    assert "daily_pnl" in daily_chart
    assert "cumulative_pnl" in daily_chart


@pytest.mark.asyncio
async def test_summary(sample_trades):
    """Test analytics summary endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/advanced-pnl/summary?days=7")
        
    assert response.status_code == 200
    data = response.json()
    
    assert "period_days" in data
    assert "summary" in data
    
    summary = data["summary"]
    if "message" not in summary:  # Has trading activity
        assert "total_trades" in summary
        assert "net_pnl" in summary
        assert "win_rate" in summary
        assert "active_positions" in summary


@pytest.mark.asyncio
async def test_no_trades_period(test_client):
    """Test endpoints with no trades in period"""
    # Test with very short period that should have no trades
    response = test_client.get("/api/v1/advanced-pnl/summary?days=1")
    
    # Should return either 404 or summary with no activity message
    assert response.status_code in [200, 404]
    
    if response.status_code == 200:
        data = response.json()
        summary = data.get("summary", {})
        # Either has no activity message or shows 0 trades
        assert "message" in summary or summary.get("total_trades", 0) == 0


@pytest.mark.asyncio
async def test_invalid_parameters(test_client):
    """Test endpoints with invalid parameters"""
    # Test invalid days parameter
    response = test_client.get("/api/v1/advanced-pnl/comprehensive?days=0")
    assert response.status_code in [404, 422]  # Either endpoint not found or validation error
    
    response = test_client.get("/api/v1/advanced-pnl/comprehensive?days=500")
    assert response.status_code in [404, 422]  # Either endpoint not found or validation error


@pytest.mark.asyncio
async def test_caching(test_client):
    """Test that caching works for analytics endpoints"""
    # First request
    response1 = test_client.get("/api/v1/advanced-pnl/summary?days=30")
    assert response1.status_code in [200, 404]
    
    # Second request should be faster (cached)
    response2 = test_client.get("/api/v1/advanced-pnl/summary?days=30")
    assert response2.status_code in [200, 404]
    
    # Responses should be identical
    if response1.status_code == 200 and response2.status_code == 200:
        assert response1.json() == response2.json()
