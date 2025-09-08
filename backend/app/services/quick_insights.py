"""
Quick Insight Service for Phase 2.2
Fast summary generation with minimal processing
Target: time-to-insight ≤ 10 seconds
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_, text
from app.models.trade import Trade
from app.models.deposit import Deposit
from app.models.withdraw import Withdraw
from app.services.cache import CacheService

logger = logging.getLogger(__name__)


def get_hour_truncate(column, engine_name: str = "postgresql"):
    """
    Get hour truncation expression that works for both PostgreSQL and SQLite
    """
    if engine_name == "postgresql":
        # PostgreSQL uses date_trunc
        return func.date_trunc('hour', column)
    else:
        # SQLite uses strftime  
        return func.strftime('%Y-%m-%d %H:00:00', column)


class QuickInsightService:
    """Fast analytics for immediate user feedback"""
    
    def __init__(self, cache: CacheService):
        self.cache = cache
    
    async def dashboard_snapshot(self, db: AsyncSession) -> Dict[str, Any]:
        """
        Ultra-fast dashboard data - cached with 2min expiration
        Returns core metrics user needs immediately
        """
        cache_key = "dashboard_snapshot"
        cached = await self.cache.get(cache_key)
        if cached:
            return cached
        
        # Quick parallel queries for core metrics
        snapshot = {}
        
        # 1. Basic trade count (fastest query)
        total_trades = await db.scalar(select(func.count(Trade.id)))
        snapshot["total_trades"] = total_trades or 0
        
        # 2. Recent activity (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_trades = await db.scalar(
            select(func.count(Trade.id)).where(Trade.time >= week_ago)
        )
        snapshot["recent_trades"] = recent_trades or 0
        
        # 3. Unique symbols traded
        unique_symbols = await db.scalar(
            select(func.count(func.distinct(Trade.symbol)))
        )
        snapshot["unique_symbols"] = unique_symbols or 0
        
        # 4. Quick balance approximation (sum of deposits - withdrawals)
        deposits_sum = await db.scalar(
            select(func.coalesce(func.sum(Deposit.amount), 0))
        ) or Decimal("0")
        
        withdrawals_sum = await db.scalar(
            select(func.coalesce(func.sum(Withdraw.amount), 0))
        ) or Decimal("0")
        
        snapshot["estimated_balance"] = float(deposits_sum - withdrawals_sum)
        
        # 5. Last trade info for activity indicator
        last_trade = await db.scalar(
            select(Trade).order_by(desc(Trade.time)).limit(1)
        )
        
        if last_trade:
            snapshot["last_trade"] = {
                "symbol": last_trade.symbol,
                "time": last_trade.time.isoformat(),
                "side": last_trade.side
            }
        else:
            snapshot["last_trade"] = None
        
        snapshot["generated_at"] = datetime.utcnow().isoformat()
        snapshot["is_cached"] = False
        
        # Cache for 2 minutes
        await self.cache.set(cache_key, snapshot, expire=120)
        
        return snapshot
    
    async def top_symbols_quick(self, db: AsyncSession, limit: int = 5) -> List[Dict]:
        """
        Fast top symbols by trade volume
        """
        cache_key = f"top_symbols_{limit}"
        cached = await self.cache.get(cache_key)
        if cached:
            return cached
        
        # Quick aggregation query
        result = await db.execute(
            select(
                Trade.symbol,
                func.count(Trade.id).label("trade_count"),
                func.sum(Trade.quantity * Trade.price).label("volume")
            )
            .group_by(Trade.symbol)
            .order_by(desc("volume"))
            .limit(limit)
        )
        
        symbols = []
        for row in result:
            symbols.append({
                "symbol": row.symbol,
                "trade_count": row.trade_count,
                "volume": float(row.volume or 0)
            })
        
        # Cache for 5 minutes
        await self.cache.set(cache_key, symbols, expire=300)
        
        return symbols
    
    async def recent_activity(self, db: AsyncSession, hours: int = 24) -> Dict[str, Any]:
        """
        Activity in last N hours for quick overview
        """
        cache_key = f"recent_activity_{hours}h"
        cached = await self.cache.get(cache_key)
        if cached:
            return cached
        
        since = datetime.utcnow() - timedelta(hours=hours)
        
        # Determine database engine
        engine_name = str(db.bind.dialect.name) if db.bind else "postgresql"
        hour_truncate = get_hour_truncate(Trade.time, engine_name)
        
        # Count recent trades by hour for mini-chart (database agnostic)
        hourly_query = await db.execute(
            select(
                hour_truncate.label("hour"),
                func.count(Trade.id).label("count")
            )
            .where(Trade.time >= since)
            .group_by(hour_truncate)
            .order_by(hour_truncate)
        )
        
        hourly_data = []
        for row in hourly_query:
            hourly_data.append({
                "hour": row.hour.isoformat() if row.hour else None,
                "trades": row.count
            })
        
        # Recent trades count
        recent_count = await db.scalar(
            select(func.count(Trade.id)).where(Trade.time >= since)
        ) or 0
        
        activity = {
            "period_hours": hours,
            "total_trades": recent_count,
            "hourly_breakdown": hourly_data,
            "generated_at": datetime.utcnow().isoformat()
        }
        
        # Cache for 10 minutes
        await self.cache.set(cache_key, activity, expire=600)
        
        return activity
    
    async def quick_pnl_estimate(self, db: AsyncSession) -> Dict[str, Any]:
        """
        Fast PnL approximation without full FIFO calculation
        Uses simple buy/sell volume difference
        """
        cache_key = "quick_pnl_estimate"
        cached = await self.cache.get(cache_key)
        if cached:
            return cached
        
        # Simple buy vs sell volume calculation
        buys = await db.execute(
            select(
                func.coalesce(func.sum(Trade.quantity * Trade.price), 0)
            ).where(Trade.side == 'buy')
        )
        buy_volume = buys.scalar() or Decimal("0")
        
        sells = await db.execute(
            select(
                func.coalesce(func.sum(Trade.quantity * Trade.price), 0)
            ).where(Trade.side == 'sell')
        )
        sell_volume = sells.scalar() or Decimal("0")
        
        # Rough PnL estimate (not accurate but fast)
        rough_pnl = float(sell_volume - buy_volume)
        
        estimate = {
            "estimated_pnl": rough_pnl,
            "buy_volume": float(buy_volume),
            "sell_volume": float(sell_volume),
            "note": "Quick estimate - use /pnl/summary for accurate FIFO calculation",
            "generated_at": datetime.utcnow().isoformat()
        }
        
        # Cache for 5 minutes
        await self.cache.set(cache_key, estimate, expire=300)
        
        return estimate
    
    async def trading_streak(self, db: AsyncSession) -> Dict[str, Any]:
        """
        Find current trading streak (consecutive days with trades)
        """
        cache_key = "trading_streak"
        cached = await self.cache.get(cache_key)
        if cached:
            return cached
        
        # Get unique trading days in descending order
        trading_days = await db.execute(
            select(func.date(Trade.time).label("trade_date"))
            .group_by(func.date(Trade.time))
            .order_by(desc("trade_date"))
            .limit(30)  # Check last 30 days max
        )
        
        dates = [row.trade_date for row in trading_days]
        
        if not dates:
            streak_data = {
                "current_streak": 0,
                "last_trade_date": None,
                "max_streak_checked": 0
            }
        else:
            # Calculate streak
            current_streak = 0
            today = datetime.utcnow().date()
            
            # Check if we traded today or yesterday
            latest_date = dates[0]
            if latest_date >= today - timedelta(days=1):
                current_streak = 1
                
                # Count consecutive days backwards
                for i in range(1, len(dates)):
                    expected_date = dates[i-1] - timedelta(days=1)
                    if dates[i] == expected_date:
                        current_streak += 1
                    else:
                        break
            
            streak_data = {
                "current_streak": current_streak,
                "last_trade_date": latest_date.isoformat(),
                "max_streak_checked": len(dates)
            }
        
        streak_data["generated_at"] = datetime.utcnow().isoformat()
        
        # Cache for 1 hour
        await self.cache.set(cache_key, streak_data, expire=3600)
        
        return streak_data
