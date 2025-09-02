"""
Background workers for Phase 2.2
Automated HTX sync and cache warming
"""

import logging
import asyncio
from typing import Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal
from app.services.htx_client import HTXClient
from app.services.cache import cache
from app.services.quick_insights import QuickInsightService
from app.services.websocket import notification_service
from app.core.config import settings

logger = logging.getLogger(__name__)


class BackgroundWorkers:
    """Background task workers for automation"""
    
    def __init__(self):
        self.htx_client = HTXClient()
    
    async def sync_htx_data(self):
        """
        Sync latest data from HTX API
        Called every 15 minutes by scheduler
        """
        logger.info("Starting HTX data sync...")
        
        try:
            async with AsyncSessionLocal() as db:
                account_data = None
                trades = None
                symbols = None
                
                # 1. Update account balance in cache
                balance = await self.htx_client.get_account_balance()
                if balance:
                    await cache.set_balance_summary(balance, expire=900)  # 15 min
                    logger.info("Updated balance cache")
                    account_data = balance
                
                # 2. Sync recent trades 
                trades = await self.htx_client.get_trade_history()
                if trades:
                    # Here we would store new trades in DB
                    # For now just log the count
                    logger.info(f"Fetched {len(trades)} recent trades from HTX")
                
                # 3. Update symbols cache
                symbols = await self.htx_client.get_symbols()
                if symbols and isinstance(symbols, list):
                    await cache.set_htx_symbols(symbols, expire=3600)  # 1 hour
                    logger.info(f"Updated {len(symbols)} symbols in cache")
                
                # 4. Invalidate related caches to trigger refresh
                await cache.clear_pattern("dashboard_snapshot")
                await cache.clear_pattern("quick_pnl_estimate")
                
                # 5. Send WebSocket notification about HTX sync
                try:
                    await notification_service.notify_htx_sync(
                        "completed", 
                        {
                            "account_synced": account_data is not None,
                            "trades_count": len(trades) if trades else 0,
                            "symbols_count": len(symbols) if symbols else 0
                        }
                    )
                except Exception as ws_error:
                    logger.warning(f"Failed to send WebSocket notification: {ws_error}")
                
                logger.info("HTX data sync completed successfully")
        
        except Exception as e:
            logger.error(f"HTX sync failed: {e}", exc_info=True)
    
    async def warm_cache(self):
        """
        Warm frequently accessed cache entries
        Called every 5 minutes
        """
        logger.info("Starting cache warming...")
        
        try:
            async with AsyncSessionLocal() as db:
                service = QuickInsightService(cache)
                
                # Warm dashboard data
                await service.dashboard_snapshot(db)
                logger.debug("Warmed dashboard cache")
                
                # Warm top symbols
                await service.top_symbols_quick(db, limit=10)
                logger.debug("Warmed top symbols cache")
                
                # Warm quick PnL estimate
                await service.quick_pnl_estimate(db)
                logger.debug("Warmed PnL estimate cache")
                
                # Warm recent activity
                await service.recent_activity(db, hours=24)
                logger.debug("Warmed activity cache")
                
                # Send cache update notification
                try:
                    await notification_service.notify_cache_update("warm_complete", "warmed")
                except Exception as ws_error:
                    logger.warning(f"Failed to send cache notification: {ws_error}")
                
                logger.info("Cache warming completed")
        
        except Exception as e:
            logger.error(f"Cache warming failed: {e}", exc_info=True)
    
    async def cleanup_old_cache(self):
        """
        Cleanup expired cache entries
        Called daily
        """
        logger.info("Starting cache cleanup...")
        
        try:
            # Redis handles expiration automatically, but we can clean patterns
            patterns_to_clean = [
                "file_analysis:*",  # Old file analysis
                "htx_symbols",      # Force refresh symbols
            ]
            
            total_cleaned = 0
            for pattern in patterns_to_clean:
                cleaned = await cache.clear_pattern(pattern)
                total_cleaned += cleaned
            
            logger.info(f"Cache cleanup completed - removed {total_cleaned} entries")
        
        except Exception as e:
            logger.error(f"Cache cleanup failed: {e}", exc_info=True)
    
    async def health_check_background(self):
        """
        Background health monitoring
        """
        try:
            # Check HTX API connectivity
            try:
                balance = await self.htx_client.get_account_balance()
                if balance:
                    logger.debug("HTX API is healthy")
                else:
                    logger.warning("HTX API check failed")
            except Exception:
                logger.warning("HTX API connectivity check failed")
            
            # Check cache connectivity
            if cache._connected and cache.redis:
                try:
                    await cache.redis.ping()
                    logger.debug("Cache is healthy")
                except Exception:
                    logger.warning("Cache ping failed")
            else:
                logger.warning("Cache is not connected")
        
        except Exception as e:
            logger.error(f"Background health check failed: {e}")


# Global instance
background_workers = BackgroundWorkers()


# Task functions for scheduler
async def sync_htx_task():
    """Wrapper for HTX sync task"""
    await background_workers.sync_htx_data()


async def warm_cache_task():
    """Wrapper for cache warming task"""
    await background_workers.warm_cache()


async def cleanup_cache_task():
    """Wrapper for cache cleanup task"""
    await background_workers.cleanup_old_cache()


async def health_check_task():
    """Wrapper for health check task"""
    await background_workers.health_check_background()
