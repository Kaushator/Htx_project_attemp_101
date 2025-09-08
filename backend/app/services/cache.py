"""
Redis caching service for performance optimization
Based on implementation plan: time-to-insight ≤ 10 seconds
"""
import json
import logging
from typing import Any, Optional, Union, Dict, List
from datetime import datetime, timedelta
import redis.asyncio as redis
from redis.asyncio import Redis

from app.core.config import settings

logger = logging.getLogger(__name__)


class CacheService:
    """Redis-based caching service for analytics queries"""
    
    def __init__(self):
        self.redis: Optional[Redis] = None
        self._connected = False
    
    async def connect(self):
        """Initialize Redis connection"""
        try:
            self.redis = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_keepalive=True,
                socket_keepalive_options={},
                health_check_interval=30
            )
            # Test connection
            await self.redis.ping()
            self._connected = True
            logger.info("Redis cache connected successfully")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Cache disabled.")
            self._connected = False
    
    async def disconnect(self):
        """Close Redis connection"""
        if self.redis:
            await self.redis.aclose()
            self._connected = False
    
    def _serialize_key(self, prefix: str, **kwargs) -> str:
        """Create cache key from prefix and parameters"""
        # Sort kwargs for consistent keys
        key_parts = [prefix]
        for k, v in sorted(kwargs.items()):
            if isinstance(v, datetime):
                v = v.isoformat()
            key_parts.append(f"{k}:{v}")
        return ":".join(key_parts)
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self._connected or not self.redis:
            return None
        
        try:
            value = await self.redis.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
        return None
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        expire: Optional[int] = None
    ) -> bool:
        """Set value in cache with optional expiration"""
        if not self._connected or not self.redis:
            return False
        
        try:
            serialized = json.dumps(value, default=str)
            await self.redis.set(key, serialized, ex=expire)
            return True
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self._connected or not self.redis:
            return False
        
        try:
            await self.redis.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        if not self._connected or not self.redis:
            return 0
        
        try:
            keys = await self.redis.keys(pattern)
            if keys:
                deleted = await self.redis.delete(*keys)
                logger.info(f"Cleared {deleted} cache keys matching: {pattern}")
                return deleted
            return 0
        except Exception as e:
            logger.error(f"Cache clear pattern error for {pattern}: {e}")
            return 0
    
    # PnL Analytics Cache Methods
    async def get_pnl_summary(
        self, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        symbol: Optional[str] = None
    ) -> Optional[Dict]:
        """Get cached PnL summary"""
        key = self._serialize_key(
            "pnl_summary",
            start=start_date,
            end=end_date,
            symbol=symbol
        )
        return await self.get(key)
    
    async def set_pnl_summary(
        self,
        data: Dict,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        symbol: Optional[str] = None,
        expire: int = 300  # 5 minutes
    ) -> bool:
        """Cache PnL summary data"""
        key = self._serialize_key(
            "pnl_summary",
            start=start_date,
            end=end_date,
            symbol=symbol
        )
        return await self.set(key, data, expire)
    
    # Trade Analytics Cache Methods
    async def get_trade_stats(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        symbol: Optional[str] = None
    ) -> Optional[Dict]:
        """Get cached trade statistics"""
        key = self._serialize_key(
            "trade_stats",
            start=start_date,
            end=end_date,
            symbol=symbol
        )
        return await self.get(key)
    
    async def set_trade_stats(
        self,
        data: Dict,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        symbol: Optional[str] = None,
        expire: int = 300  # 5 minutes
    ) -> bool:
        """Cache trade statistics"""
        key = self._serialize_key(
            "trade_stats",
            start=start_date,
            end=end_date,
            symbol=symbol
        )
        return await self.set(key, data, expire)
    
    # Balance Cache Methods
    async def get_balance_summary(self) -> Optional[Dict]:
        """Get cached balance summary"""
        return await self.get("balance_summary")
    
    async def set_balance_summary(
        self, 
        data: Dict, 
        expire: int = 120  # 2 minutes for balance
    ) -> bool:
        """Cache balance summary"""
        return await self.set("balance_summary", data, expire)
    
    # HTX API Cache Methods
    async def get_htx_symbols(self) -> Optional[List]:
        """Get cached HTX symbols"""
        return await self.get("htx_symbols")
    
    async def set_htx_symbols(
        self, 
        data: List, 
        expire: int = 3600  # 1 hour for symbols
    ) -> bool:
        """Cache HTX symbols"""
        return await self.set("htx_symbols", data, expire)
    
    # File Processing Cache
    async def get_file_analysis(self, file_hash: str) -> Optional[Dict]:
        """Get cached file analysis results"""
        key = f"file_analysis:{file_hash}"
        return await self.get(key)
    
    async def set_file_analysis(
        self, 
        file_hash: str, 
        data: Dict,
        expire: int = 86400  # 24 hours for file analysis
    ) -> bool:
        """Cache file analysis results"""
        key = f"file_analysis:{file_hash}"
        return await self.set(key, data, expire)
    
    async def invalidate_trades_cache(self):
        """Clear all trade-related cache entries"""
        patterns = [
            "pnl_summary:*",
            "trade_stats:*",
            "balance_summary"
        ]
        total_cleared = 0
        for pattern in patterns:
            cleared = await self.clear_pattern(pattern)
            total_cleared += cleared
        logger.info(f"Invalidated {total_cleared} trade cache entries")
        return total_cleared


# Global cache instance (lazy initialization)
cache: Optional[CacheService] = None


# Dependency for FastAPI
async def get_cache() -> CacheService:
    """Dependency to get cache service (lazy initialization)"""
    global cache
    if cache is None:
        cache = CacheService()
    return cache
