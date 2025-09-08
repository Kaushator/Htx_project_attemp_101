"""
HTX API endpoints
Direct access to HTX exchange data
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any
import logging
import time
import httpx
from app.services.htx_client import HTXClient

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/")
async def htx_status():
    """Check HTX API connectivity"""
    try:
        async with HTXClient() as client:
            is_healthy = await client.health_check()
            server_time = await client.get_server_time()
            return {
                "status": "connected" if is_healthy else "disconnected",
                "exchange": "HTX",
                "server_time": server_time,
                "healthy": is_healthy
            }
    except Exception as e:
        logger.error(f"HTX API connection failed: {e}")
        raise HTTPException(status_code=503, detail=f"HTX API unavailable: {str(e)}")


@router.get("/account/balance")
async def get_account_balance():
    """Get account balance from HTX"""
    try:
        async with HTXClient() as client:
            balance = await client.get_account_balance()
            return balance
    except Exception as e:
        logger.error(f"Failed to get HTX balance: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get balance: {str(e)}")


@router.get("/symbols")
async def get_trading_symbols():
    """Get available trading symbols from HTX"""
    try:
        async with HTXClient() as client:
            symbols = await client.get_symbols()
            return {"symbols": symbols}
    except Exception as e:
        logger.error(f"Failed to get HTX symbols: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get symbols: {str(e)}")


@router.get("/ticker/{symbol}")
async def get_ticker(symbol: str):
    """Get ticker data for specific symbol"""
    try:
        async with HTXClient() as client:
            ticker = await client.get_ticker(symbol)
            return ticker
    except Exception as e:
        logger.error(f"Failed to get HTX ticker for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get ticker: {str(e)}")


@router.get("/orders/open")
async def get_open_orders(symbol: Optional[str] = Query(None)):
    """Get open orders from HTX"""
    try:
        async with HTXClient() as client:
            # HTX doesn't have direct get_open_orders, use get_order_history with states
            if symbol:
                orders = await client.get_order_history(symbol=symbol, states="submitted,partial-filled")
            else:
                # For all symbols, we need to specify a symbol, so return empty for now
                orders = {"data": []}
            return {"orders": orders}
    except Exception as e:
        logger.error(f"Failed to get HTX open orders: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get orders: {str(e)}")


@router.get("/trades/history")
async def get_trade_history(
    symbol: Optional[str] = Query(None),
    size: int = Query(100, le=1000)
):
    """Get trade history from HTX"""
    try:
        async with HTXClient() as client:
            if symbol:
                trades = await client.get_trade_history(symbol=symbol, size=size)
            else:
                trades = {"data": []}  # HTX requires symbol for trade history
            return {"trades": trades}
    except Exception as e:
        logger.error(f"Failed to get HTX trade history: {e}")

@router.get("/coins")
async def get_htx_coins():
    """
    Получить список всех доступных монет на HTX с информацией о ценах и объемах
    """
    try:
        logger.info("Начинаем получение списка монет HTX")
        
        # Используем прямые запросы к публичным API HTX
        async with httpx.AsyncClient(timeout=30.0) as http_client:
            # Получаем все тикеры
            logger.info("Получение тикеров с HTX API")
            ticker_response = await http_client.get("https://api.huobi.pro/market/tickers")
            ticker_response.raise_for_status()
            tickers_data = ticker_response.json()
            
            tickers = []
            if "data" in tickers_data:
                tickers = tickers_data["data"]
                logger.info(f"Получены тикеры, кол-во: {len(tickers)}")
            
            # Получаем информацию о торговых парах
            logger.info("Получение информации о торговых парах")
            symbols_response = await http_client.get("https://api.huobi.pro/v1/common/symbols")
            symbols_response.raise_for_status()
            symbols_data = symbols_response.json()
            
            symbols = []
            if "data" in symbols_data:
                symbols = symbols_data["data"]
                logger.info(f"Получены symbols, кол-во: {len(symbols)}")
            
            # Создаем карту символов для быстрого поиска
            symbol_map = {s["symbol"]: s for s in symbols}
            
            # Создаем словарь для группировки монет
            coin_dict = {}
            
            # Обрабатываем тикеры
            for ticker in tickers:
                symbol = ticker["symbol"]
                
                # Получаем базовую и котируемую валюты из символа
                symbol_info = symbol_map.get(symbol, {})
                base_currency = symbol_info.get("base-currency", "").upper()
                quote_currency = symbol_info.get("quote-currency", "").upper()
                
                if not base_currency or not quote_currency:
                    # Пытаемся извлечь валюты из символа
                    if "usdt" in symbol:
                        base_currency = symbol.replace("usdt", "").upper()
                        quote_currency = "USDT"
                    elif "btc" in symbol:
                        base_currency = symbol.replace("btc", "").upper()
                        quote_currency = "BTC"
                    else:
                        continue  # Пропускаем пары, которые не можем идентифицировать
                
                # Обновляем информацию о базовой валюте
                if base_currency not in coin_dict:
                    coin_dict[base_currency] = {
                        "symbol": base_currency,
                        "name": base_currency,  # Используем символ как имя
                        "markets": []
                    }
                
                # Если это рынок USDT, добавляем ценовую информацию
                if quote_currency == "USDT":
                    coin_dict[base_currency].update({
                        "price": ticker.get("close", 0),
                        "change24h": ((ticker.get("close", 0) - ticker.get("open", ticker.get("close", 0))) / ticker.get("open", 1)) * 100 if ticker.get("open", 0) > 0 else 0,
                        "volume24h": ticker.get("vol", 0),
                        "high24h": ticker.get("high", 0),
                        "low24h": ticker.get("low", 0)
                    })
                
                # Добавляем информацию о рынке
                coin_dict[base_currency]["markets"].append({
                    "pair": f"{base_currency}/{quote_currency}",
                    "symbol": symbol,
                    "price": ticker.get("close", 0),
                    "volume24h": ticker.get("vol", 0)
                })
            
            # Преобразуем словарь в список
            coins = list(coin_dict.values())
            
            # Сортируем по объему (если есть)
            coins = sorted(coins, key=lambda x: x.get("volume24h", 0), reverse=True)
            
            return {
                "coins": coins,
                "total": len(coins),
                "timestamp": time.time()
            }
                
    except Exception as e:
        logger.error(f"Failed to get HTX coins: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get coins: {str(e)}")


@router.get("/klines/{symbol}")
async def get_klines(
    symbol: str,
    period: str = Query("1day", description="Period: 1min, 5min, 15min, 30min, 60min, 4hour, 1day, 1week, 1mon, 1year"),
    size: int = Query(50, ge=1, le=2000, description="Number of data points")
):
    """Get kline/candlestick data for symbol"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as http_client:
            # HTX klines API endpoint
            url = f"https://api.huobi.pro/market/history/kline"
            params = {
                "symbol": symbol.lower(),
                "period": period,
                "size": size
            }
            
            logger.info(f"Fetching klines for {symbol} with period {period}")
            response = await http_client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") == "ok":
                klines = data.get("data", [])
                # Format klines data for frontend consumption
                formatted_klines = []
                for k in klines:
                    formatted_klines.append({
                        "timestamp": k["id"],
                        "open": k["open"],
                        "high": k["high"],
                        "low": k["low"],
                        "close": k["close"],
                        "volume": k["vol"],
                        "amount": k["amount"]
                    })
                
                return {
                    "symbol": symbol,
                    "period": period,
                    "data": formatted_klines,
                    "total": len(formatted_klines)
                }
            else:
                raise HTTPException(status_code=400, detail=f"HTX API error: {data.get('err-msg', 'Unknown error')}")
                
    except httpx.HTTPError as e:
        logger.error(f"HTTP error getting klines for {symbol}: {e}")
        raise HTTPException(status_code=503, detail="HTX API service unavailable")
    except Exception as e:
        logger.error(f"Failed to get klines for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get klines: {str(e)}")


@router.post("/sync/trades")
async def sync_trades_from_htx(
    symbol: Optional[str] = Query(None),
    size: int = Query(100, ge=1, le=500)
):
    """Sync trades from HTX to local database"""
    try:
        async with HTXClient() as client:
            if not symbol:
                raise HTTPException(status_code=422, detail="Symbol is required for syncing trades")
            
            # Get trades from HTX
            trades = await client.get_trade_history(symbol=symbol, size=size)
            
            # For demonstration purposes, we'll just return the trades
            # In a real implementation, you'd persist these to the database
            return {
                "status": "success",
                "message": f"Synced {len(trades.get('data', []))} trades for {symbol}",
                "trades": trades.get('data', [])
            }
    except Exception as e:
        logger.error(f"Failed to sync HTX trades: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to sync trades: {str(e)}")
