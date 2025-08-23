"""
3Commas Integration Module
Provides integration with 3Commas trading platform
"""

import requests
import hmac
import hashlib
import time
import json
from typing import Dict, List, Any, Optional
from urllib.parse import urlencode
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ThreeCommasClient:
    """3Commas API Client"""
    
    def __init__(self, api_key: str, secret_key: str, base_url: str = "https://api.3commas.io"):
        """
        Initialize 3Commas API client
        
        Args:
            api_key: 3Commas API key
            secret_key: 3Commas secret key
            base_url: 3Commas API base URL
        """
        self.api_key = api_key
        self.secret_key = secret_key
        self.base_url = base_url
        self.session = requests.Session()
    
    def _generate_signature(self, method: str, path: str, params: Dict[str, Any] = None) -> Dict[str, str]:
        """Generate signature for authenticated requests"""
        if not self.api_key or not self.secret_key:
            return {}
        
        # Add API key to parameters
        params = params or {}
        params['api_key'] = self.api_key
        
        # Create signature string
        signature_string = f"{method}{path}{urlencode(sorted(params.items()))}"
        
        # Generate signature
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            signature_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        params['signature'] = signature
        return params
    
    def _make_request(self, method: str, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make authenticated request to 3Commas API"""
        url = f"{self.base_url}{endpoint}"
        signed_params = self._generate_signature(method, endpoint, params)
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, params=signed_params)
            elif method.upper() == 'POST':
                response = self.session.post(url, data=signed_params)
            elif method.upper() == 'PUT':
                response = self.session.put(url, data=signed_params)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, params=signed_params)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise
    
    def get_accounts(self) -> List[Dict[str, Any]]:
        """Get list of connected accounts"""
        endpoint = '/public/api/ver1/accounts'
        return self._make_request('GET', endpoint)
    
    def get_bots(self, account_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get list of bots
        
        Args:
            account_id: Filter by account ID (optional)
        """
        endpoint = '/public/api/ver1/bots'
        params = {}
        if account_id:
            params['account_id'] = account_id
        
        return self._make_request('GET', endpoint, params)
    
    def get_bot(self, bot_id: int) -> Dict[str, Any]:
        """
        Get specific bot details
        
        Args:
            bot_id: Bot ID
        """
        endpoint = f'/public/api/ver1/bots/{bot_id}/show'
        return self._make_request('GET', endpoint)
    
    def create_bot(self, bot_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new bot
        
        Args:
            bot_config: Bot configuration dictionary
        """
        endpoint = '/public/api/ver1/bots/create_bot'
        return self._make_request('POST', endpoint, bot_config)
    
    def update_bot(self, bot_id: int, bot_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update bot configuration
        
        Args:
            bot_id: Bot ID
            bot_config: Updated bot configuration
        """
        endpoint = f'/public/api/ver1/bots/{bot_id}/update'
        return self._make_request('POST', endpoint, bot_config)
    
    def delete_bot(self, bot_id: int) -> Dict[str, Any]:
        """
        Delete a bot
        
        Args:
            bot_id: Bot ID
        """
        endpoint = f'/public/api/ver1/bots/{bot_id}/delete'
        return self._make_request('POST', endpoint)
    
    def start_bot(self, bot_id: int) -> Dict[str, Any]:
        """
        Start a bot
        
        Args:
            bot_id: Bot ID
        """
        endpoint = f'/public/api/ver1/bots/{bot_id}/start'
        return self._make_request('POST', endpoint)
    
    def stop_bot(self, bot_id: int) -> Dict[str, Any]:
        """
        Stop a bot
        
        Args:
            bot_id: Bot ID
        """
        endpoint = f'/public/api/ver1/bots/{bot_id}/stop'
        return self._make_request('POST', endpoint)
    
    def get_bot_deals(self, bot_id: int, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get bot deals
        
        Args:
            bot_id: Bot ID
            limit: Number of deals to retrieve
        """
        endpoint = f'/public/api/ver1/bots/{bot_id}/deals'
        params = {'limit': limit}
        return self._make_request('GET', endpoint, params)
    
    def get_deals(self, account_id: Optional[int] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get all deals
        
        Args:
            account_id: Filter by account ID (optional)
            limit: Number of deals to retrieve
        """
        endpoint = '/public/api/ver1/deals'
        params = {'limit': limit}
        if account_id:
            params['account_id'] = account_id
        
        return self._make_request('GET', endpoint, params)
    
    def get_deal(self, deal_id: int) -> Dict[str, Any]:
        """
        Get specific deal details
        
        Args:
            deal_id: Deal ID
        """
        endpoint = f'/public/api/ver1/deals/{deal_id}/show'
        return self._make_request('GET', endpoint)
    
    def cancel_deal(self, deal_id: int) -> Dict[str, Any]:
        """
        Cancel a deal
        
        Args:
            deal_id: Deal ID
        """
        endpoint = f'/public/api/ver1/deals/{deal_id}/cancel'
        return self._make_request('POST', endpoint)
    
    def panic_sell_deal(self, deal_id: int) -> Dict[str, Any]:
        """
        Panic sell a deal
        
        Args:
            deal_id: Deal ID
        """
        endpoint = f'/public/api/ver1/deals/{deal_id}/panic_sell'
        return self._make_request('POST', endpoint)
    
    def get_markets(self, exchange: str) -> List[Dict[str, Any]]:
        """
        Get available markets for an exchange
        
        Args:
            exchange: Exchange name
        """
        endpoint = f'/public/api/ver1/accounts/{exchange}/market_pairs'
        return self._make_request('GET', endpoint)
    
    def get_exchange_info(self, exchange: str) -> Dict[str, Any]:
        """
        Get exchange information
        
        Args:
            exchange: Exchange name
        """
        endpoint = f'/public/api/ver1/accounts/{exchange}/exchange_info'
        return self._make_request('GET', endpoint)
    
    def get_currency_rates(self, currency: str = 'USD') -> Dict[str, Any]:
        """
        Get currency exchange rates
        
        Args:
            currency: Base currency
        """
        endpoint = '/public/api/ver1/currency_rates'
        params = {'currency': currency}
        return self._make_request('GET', endpoint, params)
    
    def get_verification_token(self) -> Dict[str, Any]:
        """Get verification token for API access"""
        endpoint = '/public/api/ver1/verification_token'
        return self._make_request('GET', endpoint)


class ThreeCommasIntegration:
    """Integration class for 3Commas platform"""
    
    def __init__(self, api_key: str, secret_key: str):
        """
        Initialize 3Commas integration
        
        Args:
            api_key: 3Commas API key
            secret_key: 3Commas secret key
        """
        self.client = ThreeCommasClient(api_key, secret_key)
    
    def sync_trades_from_3commas(self, account_id: Optional[int] = None, 
                                start_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Sync trades from 3Commas to local format
        
        Args:
            account_id: Specific account ID to sync
            start_date: Start date for filtering trades (YYYY-MM-DD)
            
        Returns:
            List of trades in standardized format
        """
        try:
            # Get deals from 3Commas
            deals = self.client.get_deals(account_id=account_id, limit=1000)
            
            # Convert to standardized format
            trades = []
            for deal in deals:
                # Filter by start date if provided
                if start_date:
                    deal_date = deal.get('created_at', '').split('T')[0]
                    if deal_date < start_date:
                        continue
                
                trade = {
                    'timestamp': deal.get('created_at'),
                    'symbol': deal.get('pair'),
                    'side': 'buy' if deal.get('type') == 'buy' else 'sell',
                    'price': float(deal.get('price', 0)),
                    'volume': float(deal.get('amount', 0)),
                    'fee': float(deal.get('fee', 0)),
                    'order_id': str(deal.get('id')),
                    'status': deal.get('status'),
                    'bot_id': deal.get('bot_id'),
                    'account_id': deal.get('account_id')
                }
                trades.append(trade)
            
            logger.info(f"Synced {len(trades)} trades from 3Commas")
            return trades
            
        except Exception as e:
            logger.error(f"Error syncing trades from 3Commas: {e}")
            raise
    
    def sync_bots_from_3commas(self, account_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Sync bots from 3Commas
        
        Args:
            account_id: Specific account ID to sync
            
        Returns:
            List of bots
        """
        try:
            bots = self.client.get_bots(account_id=account_id)
            logger.info(f"Synced {len(bots)} bots from 3Commas")
            return bots
            
        except Exception as e:
            logger.error(f"Error syncing bots from 3Commas: {e}")
            raise
    
    def create_grid_bot(self, account_id: int, pair: str, base_order_volume: float,
                       safety_order_volume: float, safety_order_step_percentage: float,
                       max_safety_orders: int, price_deviation: float) -> Dict[str, Any]:
        """
        Create a grid bot
        
        Args:
            account_id: Account ID
            pair: Trading pair
            base_order_volume: Base order volume
            safety_order_volume: Safety order volume
            safety_order_step_percentage: Safety order step percentage
            max_safety_orders: Maximum safety orders
            price_deviation: Price deviation percentage
            
        Returns:
            Created bot configuration
        """
        bot_config = {
            'account_id': account_id,
            'pair': pair,
            'base_order_volume': base_order_volume,
            'safety_order_volume': safety_order_volume,
            'safety_order_step_percentage': safety_order_step_percentage,
            'max_safety_orders': max_safety_orders,
            'price_deviation': price_deviation,
            'strategy': 'long',
            'active': True
        }
        
        try:
            result = self.client.create_bot(bot_config)
            logger.info(f"Created grid bot for {pair}")
            return result
            
        except Exception as e:
            logger.error(f"Error creating grid bot: {e}")
            raise
    
    def create_dca_bot(self, account_id: int, pair: str, base_order_volume: float,
                      safety_order_volume: float, safety_order_step_percentage: float,
                      max_safety_orders: int, take_profit: float) -> Dict[str, Any]:
        """
        Create a DCA (Dollar Cost Averaging) bot
        
        Args:
            account_id: Account ID
            pair: Trading pair
            base_order_volume: Base order volume
            safety_order_volume: Safety order volume
            safety_order_step_percentage: Safety order step percentage
            max_safety_orders: Maximum safety orders
            take_profit: Take profit percentage
            
        Returns:
            Created bot configuration
        """
        bot_config = {
            'account_id': account_id,
            'pair': pair,
            'base_order_volume': base_order_volume,
            'safety_order_volume': safety_order_volume,
            'safety_order_step_percentage': safety_order_step_percentage,
            'max_safety_orders': max_safety_orders,
            'take_profit': take_profit,
            'strategy': 'long',
            'active': True
        }
        
        try:
            result = self.client.create_bot(bot_config)
            logger.info(f"Created DCA bot for {pair}")
            return result
            
        except Exception as e:
            logger.error(f"Error creating DCA bot: {e}")
            raise
    
    def get_account_balance(self, account_id: int) -> Dict[str, Any]:
        """
        Get account balance
        
        Args:
            account_id: Account ID
            
        Returns:
            Account balance information
        """
        try:
            accounts = self.client.get_accounts()
            for account in accounts:
                if account.get('id') == account_id:
                    return account
            return {}
            
        except Exception as e:
            logger.error(f"Error getting account balance: {e}")
            raise
    
    def export_trades_to_csv(self, account_id: Optional[int] = None, 
                           filename: str = "3commas_trades.csv") -> None:
        """
        Export trades to CSV file
        
        Args:
            account_id: Specific account ID to export
            filename: Output filename
        """
        try:
            import pandas as pd
            
            trades = self.sync_trades_from_3commas(account_id)
            df = pd.DataFrame(trades)
            df.to_csv(filename, index=False)
            logger.info(f"Exported {len(trades)} trades to {filename}")
            
        except Exception as e:
            logger.error(f"Error exporting trades to CSV: {e}")
            raise
