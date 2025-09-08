"""
HTX API Reference endpoints: currencies, symbols, and market data
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional, Dict, Any
import logging
import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.htx_client import HTXClient
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/reference", tags=["reference"])


@router.get("/currencies")
async def get_currencies():
    """
    Получить список всех валют, доступных на бирже HTX
    """
    try:
        async with HTXClient() as client:
            # Вызов метода для получения списка валют
            currencies = await client.get_currencies()
            
            # Обработка данных для удобства использования на фронтенде
            processed_currencies = []
            
            for currency in currencies.get("data", []):
                processed_currencies.append({
                    "currency": currency.get("currency", ""),
                    "chains": currency.get("chains", []),
                    "name": currency.get("full-name", ""),
                    "withdraw_enabled": currency.get("withdraw-enabled", False),
                    "deposit_enabled": currency.get("deposit-enabled", False),
                    "visible": currency.get("visible", True),
                    "status": "active" if currency.get("visible", True) else "inactive"
                })
                
            return {
                "success": True,
                "count": len(processed_currencies),
                "currencies": processed_currencies
            }
    except Exception as e:
        logger.error(f"Failed to get HTX currencies: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get currencies: {str(e)}")


@router.get("/symbols")
async def get_symbols():
    """
    Получить список всех торговых пар (символов), доступных на бирже HTX
    """
    try:
        async with HTXClient() as client:
            # Вызов метода для получения списка торговых пар
            symbols = await client.get_symbols()
            
            # Обработка данных для удобства использования на фронтенде
            processed_symbols = []
            
            for symbol in symbols.get("data", []):
                processed_symbols.append({
                    "symbol": symbol.get("symbol", ""),
                    "base_currency": symbol.get("base-currency", ""),
                    "quote_currency": symbol.get("quote-currency", ""),
                    "price_precision": symbol.get("price-precision", 0),
                    "amount_precision": symbol.get("amount-precision", 0),
                    "value_precision": symbol.get("value-precision", 0),
                    "min_order_amt": symbol.get("min-order-amt", 0),
                    "max_order_amt": symbol.get("max-order-amt", 0),
                    "min_order_value": symbol.get("min-order-value", 0),
                    "leverage_ratio": symbol.get("leverage-ratio", 0),
                    "state": symbol.get("state", ""),
                    "tags": symbol.get("tags", ""),
                })
            
            return {
                "success": True,
                "count": len(processed_symbols),
                "symbols": processed_symbols
            }
    except Exception as e:
        logger.error(f"Failed to get HTX symbols: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get symbols: {str(e)}")


@router.get("/currency/{currency}")
async def get_currency_details(currency: str):
    """
    Получить детальную информацию о конкретной валюте
    """
    try:
        async with HTXClient() as client:
            currencies = await client.get_currencies()
            
            for curr in currencies.get("data", []):
                if curr.get("currency", "").lower() == currency.lower():
                    # Получаем дополнительную информацию о цене
                    symbol = f"{currency.lower()}usdt"
                    
                    try:
                        ticker = await client.get_ticker(symbol)
                        price_data = ticker.get("tick", {})
                        
                        price = price_data.get("close", 0)
                        change = price_data.get("close", 0) - price_data.get("open", 0)
                        change_percent = (change / price_data.get("open", 1)) * 100 if price_data.get("open", 0) > 0 else 0
                    except Exception:
                        price = 0
                        change = 0
                        change_percent = 0
                    
                    return {
                        "currency": curr.get("currency", ""),
                        "name": curr.get("full-name", ""),
                        "chains": curr.get("chains", []),
                        "withdraw_enabled": curr.get("withdraw-enabled", False),
                        "deposit_enabled": curr.get("deposit-enabled", False),
                        "withdraw_precision": curr.get("withdraw-precision", 0),
                        "visible": curr.get("visible", True),
                        "price_usd": price,
                        "change_24h": change,
                        "change_percent_24h": change_percent
                    }
            
            raise HTTPException(status_code=404, detail=f"Currency {currency} not found")
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Failed to get HTX currency details: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get currency details: {str(e)}")


@router.get("/market-info")
async def get_market_info(
    symbols: Optional[List[str]] = Query(None, description="List of symbols to get info for"),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить сводную информацию о рынке: тикеры, объемы, изменения цен
    """
    try:
        async with HTXClient() as client:
            # Если символы не указаны, получим топ-50 по объему
            default_symbols = ["btcusdt", "ethusdt", "dogeusdt", "xrpusdt", "ltcusdt"]
            
            if not symbols:
                symbols = default_symbols
                try:
                    # Получаем все тикеры
                    async with httpx.AsyncClient(timeout=30.0) as http_client:
                        tickers_response = await http_client.get("https://api.huobi.pro/market/tickers")
                        tickers_response.raise_for_status()
                        tickers_data = tickers_response.json()
                        
                        if tickers_data.get("status") == "ok":
                            all_tickers = tickers_data.get("data", [])
                            
                            # Сортируем по объему и берем топ-50
                            all_tickers.sort(key=lambda x: float(x.get("vol", 0)), reverse=True)
                            top_tickers = all_tickers[:50]
                            
                            # Извлекаем только символы
                            symbols = [ticker.get("symbol") for ticker in top_tickers]
                except Exception as e:
                    logger.warning(f"Could not fetch tickers: {e}")
                    # Используем default_symbols, который уже установлен выше
            
            # Получаем информацию по каждому символу
            results = []
            
            for symbol in symbols:
                try:
                    ticker = await client.get_ticker(symbol)
                    
                    if ticker and ticker.get("status") == "ok":
                        tick_data = ticker.get("tick", {})
                        
                        # Разбираем символ на базовую и котировочную валюту
                        base_currency = symbol
                        quote_currency = "usdt"
                        
                        if "usdt" in symbol:
                            base_currency = symbol.replace("usdt", "")
                            quote_currency = "usdt"
                        elif "btc" in symbol:
                            base_currency = symbol.replace("btc", "")
                            quote_currency = "btc"
                        
                        # Расчет изменения цены
                        open_price = float(tick_data.get("open", 0))
                        close_price = float(tick_data.get("close", 0))
                        change = close_price - open_price
                        change_percent = (change / open_price * 100) if open_price > 0 else 0
                        
                        results.append({
                            "symbol": symbol,
                            "base_currency": base_currency,
                            "quote_currency": quote_currency,
                            "price": close_price,
                            "high_24h": float(tick_data.get("high", 0)),
                            "low_24h": float(tick_data.get("low", 0)),
                            "volume_24h": float(tick_data.get("vol", 0)),
                            "change_24h": change,
                            "change_percent_24h": change_percent
                        })
                except Exception as e:
                    logger.warning(f"Could not fetch data for symbol {symbol}: {e}")
            
            return {
                "success": True,
                "count": len(results),
                "markets": results
            }
    except Exception as e:
        logger.error(f"Failed to get market info: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get market info: {str(e)}")


@router.get("/analyze-file/{file_id}")
async def analyze_file_data(file_id: str, db: AsyncSession = Depends(get_db)):
    """
    Анализировать данные из загруженного файла
    """
    try:
        # Здесь будет код для обработки файла и анализа данных
        # Для этого нам нужно:
        # 1. Найти файл по ID
        # 2. Парсить файл (CSV/Excel)
        # 3. Анализировать данные
        # 4. Вернуть результаты
        
        # Пока что заглушка
        return {
            "success": True,
            "file_id": file_id,
            "analysis": {
                "total_records": 0,
                "date_range": {
                    "start": None,
                    "end": None
                },
                "symbols": [],
                "summary": {
                    "message": "Файл успешно загружен, но анализ еще в разработке."
                }
            }
        }
    except Exception as e:
        logger.error(f"Failed to analyze file data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze file: {str(e)}")
