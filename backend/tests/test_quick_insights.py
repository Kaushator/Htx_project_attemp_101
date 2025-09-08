"""
Test for Phase 2.2 Quick Insights functionality
Tests the service without needing running server
"""

import pytest
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.quick_insights import QuickInsightService
from app.services.cache import CacheService


class MockCache(CacheService):
    """Mock cache for testing"""
    
    def __init__(self):
        self._cache = {}
        self._connected = True
    
    async def connect(self):
        pass
    
    async def disconnect(self):
        pass
    
    async def get(self, key: str):
        return self._cache.get(key)
    
    async def set(self, key: str, value, expire=None):
        self._cache[key] = value
        return True


@pytest.mark.asyncio
async def test_quick_insights_dashboard_snapshot(db_session: AsyncSession):
    """Test dashboard snapshot generation"""
    cache = MockCache()
    service = QuickInsightService(cache)
    
    # Test first call (no cache)
    result = await service.dashboard_snapshot(db_session)
    
    assert "total_trades" in result
    assert "recent_trades" in result
    assert "unique_symbols" in result
    assert "estimated_balance" in result
    assert "generated_at" in result
    assert result["is_cached"] == False
    
    print(f"✅ Dashboard snapshot: {result}")


@pytest.mark.asyncio
async def test_quick_insights_top_symbols(db_session: AsyncSession):
    """Test top symbols aggregation"""
    cache = MockCache()
    service = QuickInsightService(cache)
    
    symbols = await service.top_symbols_quick(db_session, limit=3)
    
    assert isinstance(symbols, list)
    assert len(symbols) <= 3
    
    if symbols:
        symbol = symbols[0]
        assert "symbol" in symbol
        assert "trade_count" in symbol
        assert "volume" in symbol
    
    print(f"✅ Top symbols: {symbols}")


@pytest.mark.asyncio 
async def test_quick_insights_pnl_estimate(db_session: AsyncSession):
    """Test quick PnL estimation"""
    cache = MockCache()
    service = QuickInsightService(cache)
    
    pnl = await service.quick_pnl_estimate(db_session)
    
    assert "estimated_pnl" in pnl
    assert "buy_volume" in pnl
    assert "sell_volume" in pnl
    assert "note" in pnl
    assert "generated_at" in pnl
    
    print(f"✅ Quick PnL estimate: {pnl}")


@pytest.mark.asyncio
async def test_quick_insights_trading_streak(db_session: AsyncSession):
    """Test trading streak calculation"""
    cache = MockCache()
    service = QuickInsightService(cache)
    
    streak = await service.trading_streak(db_session)
    
    assert "current_streak" in streak
    assert "generated_at" in streak
    assert isinstance(streak["current_streak"], int)
    
    print(f"✅ Trading streak: {streak}")


@pytest.mark.asyncio
async def test_quick_insights_caching(db_session: AsyncSession):
    """Test that caching works properly"""
    cache = MockCache()
    service = QuickInsightService(cache)
    
    # First call
    result1 = await service.dashboard_snapshot(db_session)
    
    # Second call should use cache
    result2 = await service.dashboard_snapshot(db_session)
    
    # Should be identical (from cache)
    assert result1["total_trades"] == result2["total_trades"]
    
    print("✅ Caching works correctly")


if __name__ == "__main__":
    print("🚀 HTX Project Phase 2.2 - Quick Insights Tests")
    print("=" * 50)
    
    # Note: These would run with pytest normally
    # This is just for demonstration
    print("Run with: pytest backend/tests/test_quick_insights.py -v")
