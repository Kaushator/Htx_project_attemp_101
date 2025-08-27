"""
HTX (Huobi) API client
Handles communication with HTX exchange API
"""

import httpx
import hmac
import hashlib
import time
import logging
from typing import Dict, List, Optional, Any
from urllib.parse import urlencode
from app.core.config import settings

logger = logging.getLogger(__name__)


class HTXClient:
    """Client for HTX (Huobi) API"""
    
    def __init__(self):
        self.base_url = settings.HTX_BASE_URL
        self.api_key = settings.HTX_API_KEY
        self.api_secret = settings.HTX_API_SECRET
        self.subuid = settings.HTX_SUBUID
        
        self.client = httpx.AsyncClient(
            timeout=30.0,
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
        )
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    def _generate_signature(self, method: str, path: str, params: Dict = None) -> Dict[str, str]:
        """Generate API signature for authenticated requests"""
        if not self.api_key or not self.api_secret:
            raise ValueError("API key and secret are required for authenticated requests")
        
        timestamp = str(int(time.time() * 1000))
        
        # Prepare parameters
        params = params or {}
        params.update({
            'AccessKeyId': self.api_key,
            'SignatureMethod': 'HmacSHA256',
            'SignatureVersion': '2',
            'Timestamp': timestamp
        })
        
        if self.subuid:
            params['SubUid'] = self.subuid
        
        # Create signature string
        param_str = '&'.join([f"{k}={v}" for k, v in sorted(params.items())])
        payload = f"{method}\napi.huobi.pro\n{path}\n{param_str}"
        
        # Generate signature
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        params['Signature'] = signature
        return params
    
    async def _make_request(self, method: str, path: str, params: Dict = None, signed: bool = False) -> Dict:
        """Make HTTP request to HTX API"""
        url = f"{self.base_url}{path}"
        
        if signed:
            params = self._generate_signature(method, path, params)
        
        try:
            if method.upper() == 'GET':
                response = await self.client.get(url, params=params)
            else:
                response = await self.client.post(url, data=params)
            
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 'error':
                raise Exception(f"HTX API error: {data.get('err-msg', 'Unknown error')}")
            
            return data
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Request failed: {e}")
            raise
    
    async def get_account_balance(self) -> Dict:
        """Get account balance"""
        return await self._make_request('GET', '/v1/account/accounts/balance', signed=True)
    
    async def get_ticker(self, symbol: str) -> Dict:
        """Get ticker information for a symbol"""
        params = {'symbol': symbol}
        return await self._make_request('GET', '/market/detail/merged', params)
    
    async def get_klines(self, symbol: str, period: str = '1day', size: int = 200) -> Dict:
        """Get kline/candlestick data"""
        params = {
            'symbol': symbol,
            'period': period,
            'size': size
        }
        return await self._make_request('GET', '/market/history/kline', params)
    
    async def place_order(self, symbol: str, side: str, amount: float, price: float = None) -> Dict:
        """Place a new order"""
        params = {
            'symbol': symbol,
            'type': f"{side}-limit" if price else f"{side}-market",
            'amount': str(amount)
        }
        
        if price:
            params['price'] = str(price)
        
        return await self._make_request('POST', '/v1/order/orders/place', params, signed=True)
    
    async def get_order_history(self, symbol: str = None, states: str = None, size: int = 100) -> Dict:
        """Get order history"""
        params = {'size': size}
        
        if symbol:
            params['symbol'] = symbol
        if states:
            params['states'] = states
        
        return await self._make_request('GET', '/v1/order/orders', params, signed=True)
    
    async def get_trade_history(self, symbol: str = None, size: int = 100) -> Dict:
        """Get trade history"""
        params = {'size': size}
        
        if symbol:
            params['symbol'] = symbol
        
        return await self._make_request('GET', '/v1/order/matchresults', params, signed=True)
    
    async def get_deposit_history(self, currency: str = None, size: int = 100) -> Dict:
        """Get deposit history"""
        params = {'size': size}
        
        if currency:
            params['currency'] = currency
        
        return await self._make_request('GET', '/v1/query/deposit-withdraw', params, signed=True)
    
    async def get_withdraw_history(self, currency: str = None, size: int = 100) -> Dict:
        """Get withdrawal history"""
        params = {'size': size}
        
        if currency:
            params['currency'] = currency
        
        return await self._make_request('GET', '/v1/query/deposit-withdraw', params, signed=True)
    
    async def get_symbols(self) -> Dict:
        """Get all trading symbols"""
        return await self._make_request('GET', '/v1/common/symbols')
    
    async def get_currencies(self) -> Dict:
        """Get all currencies"""
        return await self._make_request('GET', '/v1/common/currencys')
    
    async def get_server_time(self) -> Dict:
        """Get server time"""
        return await self._make_request('GET', '/v1/common/timestamp')
    
    async def health_check(self) -> bool:
        """Check if HTX API is accessible"""
        try:
            await self.get_server_time()
            return True
        except Exception as e:
            logger.error(f"HTX API health check failed: {e}")
            return False
