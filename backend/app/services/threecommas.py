"""
3Commas API integration service
"""

import httpx
import logging
from typing import Dict, Optional, Any
from app.core.config import settings

logger = logging.getLogger(__name__)


class ThreeCommasClient:
    """Client for 3Commas API"""

    def __init__(self):
        self.base_url = settings.THREECOMMAS_BASE_URL
        self.api_key = settings.THREECOMMAS_API_KEY
        self.api_secret = settings.THREECOMMAS_API_SECRET

        self.client = httpx.AsyncClient(
            timeout=30.0,
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    async def _make_request(self, method: str, path: str, params: Dict = None) -> Dict:
        """Make HTTP request to 3Commas API"""
        url = f"{self.base_url}{path}"

        headers = {"APIKEY": self.api_key, "Signature": self.api_secret}

        try:
            if method.upper() == "GET":
                response = await self.client.get(url, params=params, headers=headers)
            else:
                response = await self.client.post(url, data=params, headers=headers)

            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Request failed: {e}")
            raise

    async def get_accounts(self) -> Dict:
        """Get 3Commas accounts"""
        return await self._make_request("GET", "/ver1/accounts")

    async def get_bots(self) -> Dict:
        """Get 3Commas bots"""
        return await self._make_request("GET", "/ver1/bots")

    async def get_deals(self, bot_id: Optional[int] = None) -> Dict:
        """Get 3Commas deals"""
        params = {}
        if bot_id:
            params["bot_id"] = bot_id

        return await self._make_request("GET", "/ver1/deals", params)

    async def health_check(self) -> bool:
        """Check if 3Commas API is accessible"""
        try:
            await self.get_accounts()
            return True
        except Exception as e:
            logger.error(f"3Commas API health check failed: {e}")
            return False


class ThreeCommasIntegration:
    """Integration service for 3Commas"""

    def __init__(self):
        self.client = ThreeCommasClient()

    async def sync_trades(self, db) -> Dict[str, Any]:
        """Sync trades from 3Commas"""
        # TODO: Implement trade synchronization
        return {"synced_trades": 0, "status": "not_implemented"}

    async def get_bot_performance(self, bot_id: int) -> Dict[str, Any]:
        """Get bot performance metrics"""
        # TODO: Implement bot performance calculation
        return {
            "bot_id": bot_id,
            "total_profit": 0.0,
            "total_deals": 0,
            "win_rate": 0.0,
        }
