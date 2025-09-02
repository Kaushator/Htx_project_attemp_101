"""
Advanced PnL Analytics Service with ML
Phase 3.1: Risk metrics, performance analysis, and predictive analytics
"""

import logging
from typing import Dict, List, Optional, Any, Tuple, Sequence
from datetime import datetime, timedelta, date
from decimal import Decimal
import numpy as np
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

from app.models.trade import Trade
from app.services.pnl import _fifo_realized_pnl, _to_decimal
from app.services.cache import CacheService

logger = logging.getLogger(__name__)


class AdvancedPnLAnalytics:
    """Advanced PnL analytics with ML and risk metrics"""
    
    def __init__(self, cache_service: CacheService):
        self.cache = cache_service
        
    async def comprehensive_pnl_analysis(self, db: AsyncSession, days: int = 30) -> Dict[str, Any]:
        """
        Comprehensive PnL analysis with all metrics
        """
        cache_key = f"comprehensive_pnl:{days}"
        cached = await self.cache.get(cache_key)
        if cached:
            return cached
            
        # Get trades for the period
        since = datetime.utcnow() - timedelta(days=days)
        trades_query = await db.execute(
            select(Trade).where(Trade.time >= since).order_by(Trade.time)
        )
        trades = list(trades_query.scalars().all())
        
        if not trades:
            return {"error": "No trades found for the period"}
            
        # Calculate all metrics
        result = {
            "period_days": days,
            "total_trades": len(trades),
            "analysis_timestamp": datetime.utcnow().isoformat(),
            
            # Basic PnL
            "basic_pnl": await self._calculate_basic_pnl(trades),
            
            # Risk metrics
            "risk_metrics": await self._calculate_risk_metrics(trades),
            
            # Performance metrics
            "performance_metrics": await self._calculate_performance_metrics(trades),
            
            # Trading patterns
            "trading_patterns": await self._analyze_trading_patterns(trades),
            
            # Predictions
            "predictions": await self._generate_predictions(trades),
            
            # Visualizations
            "charts": await self._generate_charts(trades)
        }
        
        # Cache for 1 hour
        await self.cache.set(cache_key, result, expire=3600)
        return result
        
    async def _calculate_basic_pnl(self, trades: List[Trade]) -> Dict[str, Any]:
        """Calculate basic PnL metrics"""
        if not trades:
            return {}
            
        # Use existing FIFO calculation
        realized_pnl, positions, daily_pnl = _fifo_realized_pnl(trades)
        
        # Calculate additional metrics
        total_volume = sum(_to_decimal(t.quantity) * _to_decimal(t.price) for t in trades)
        total_fees = sum(_to_decimal(t.fee or Decimal('0')) for t in trades)
        
        return {
            "realized_pnl": float(realized_pnl),
            "total_volume": float(total_volume),
            "total_fees": float(total_fees),
            "net_pnl": float(realized_pnl - total_fees),
            "daily_pnl": {str(k): float(v) for k, v in daily_pnl.items()},
            "current_positions": {
                sym: {
                    "quantity": float(sum(Decimal(str(lot[0])) for lot in lots)),
                    "avg_price": float(sum(Decimal(str(lot[0])) * Decimal(str(lot[1])) for lot in lots) / sum(Decimal(str(lot[0])) for lot in lots)) if lots else 0
                }
                for sym, lots in positions.items() if lots
            }
        }
        
    async def _calculate_risk_metrics(self, trades: List[Trade]) -> Dict[str, Any]:
        """Calculate risk metrics using ML techniques"""
        if len(trades) < 10:
            return {"error": "Insufficient data for risk analysis"}
            
        # Convert to DataFrame for analysis
        df = pd.DataFrame([{
            'time': t.time,
            'symbol': t.symbol,
            'side': t.side,
            'quantity': float(_to_decimal(t.quantity)),
            'price': float(_to_decimal(t.price)),
            'fee': float(_to_decimal(t.fee or Decimal('0')))
        } for t in trades])
        
        # Calculate daily returns
        df['date'] = df['time'].dt.date
        df['notional'] = df['quantity'] * df['price']
        df['pnl'] = df.apply(lambda row: row['notional'] if row['side'].lower() == 'sell' else -row['notional'], axis=1)
        
        daily_pnl = df.groupby('date')['pnl'].sum()
        
        if len(daily_pnl) < 2:
            return {"error": "Insufficient daily data"}
            
        # Risk calculations
        returns = daily_pnl.pct_change().dropna()
        
        # Sharpe Ratio (assuming risk-free rate of 2% annually)
        risk_free_rate = 0.02 / 365  # Daily risk-free rate
        excess_returns = returns - risk_free_rate
        sharpe_ratio = np.sqrt(365) * excess_returns.mean() / returns.std() if returns.std() > 0 else 0
        
        # Maximum Drawdown
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()
        
        # Value at Risk (VaR) - 95% confidence
        var_95 = np.percentile(returns, 5) if len(returns) > 0 else 0
        
        # Win/Loss ratios
        winning_days = len(daily_pnl[daily_pnl > 0])
        losing_days = len(daily_pnl[daily_pnl < 0])
        win_rate = winning_days / len(daily_pnl) if len(daily_pnl) > 0 else 0
        
        avg_win = daily_pnl[daily_pnl > 0].mean() if winning_days > 0 else 0
        avg_loss = daily_pnl[daily_pnl < 0].mean() if losing_days > 0 else 0
        profit_factor = abs(avg_win / avg_loss) if avg_loss != 0 else float('inf')
        
        return {
            "sharpe_ratio": float(sharpe_ratio),
            "max_drawdown": float(max_drawdown),
            "var_95": float(var_95),
            "win_rate": float(win_rate),
            "profit_factor": float(profit_factor),
            "avg_win": float(avg_win),
            "avg_loss": float(avg_loss),
            "volatility": float(returns.std() * np.sqrt(365)) if len(returns) > 0 else 0,
            "total_trading_days": len(daily_pnl),
            "winning_days": winning_days,
            "losing_days": losing_days
        }
        
    async def _calculate_performance_metrics(self, trades: List[Trade]) -> Dict[str, Any]:
        """Calculate performance metrics"""
        df = pd.DataFrame([{
            'time': t.time,
            'symbol': t.symbol,
            'side': t.side,
            'quantity': float(_to_decimal(t.quantity)),
            'price': float(_to_decimal(t.price))
        } for t in trades])
        
        # Symbol performance
        symbol_stats = {}
        for symbol in df['symbol'].unique():
            symbol_trades = df[df['symbol'] == symbol]
            buys = symbol_trades[symbol_trades['side'].str.lower() == 'buy']
            sells = symbol_trades[symbol_trades['side'].str.lower() == 'sell']
            
            total_bought = buys['quantity'].sum() if len(buys) > 0 else 0
            total_sold = sells['quantity'].sum() if len(sells) > 0 else 0
            avg_buy_price = (buys['quantity'] * buys['price']).sum() / total_bought if total_bought > 0 else 0
            avg_sell_price = (sells['quantity'] * sells['price']).sum() / total_sold if total_sold > 0 else 0
            
            symbol_stats[symbol] = {
                "total_trades": len(symbol_trades),
                "total_bought": float(total_bought),
                "total_sold": float(total_sold),
                "avg_buy_price": float(avg_buy_price),
                "avg_sell_price": float(avg_sell_price),
                "gross_profit": float((avg_sell_price - avg_buy_price) * min(total_bought, total_sold)) if avg_buy_price > 0 else 0
            }
            
        # Time-based analysis
        df['hour'] = df['time'].dt.hour
        hourly_volume = df.groupby('hour').agg({
            'quantity': 'sum',
            'symbol': 'count'
        }).to_dict()
        
        return {
            "symbol_performance": symbol_stats,
            "hourly_patterns": {
                "volume_by_hour": {str(k): float(v) for k, v in hourly_volume['quantity'].items()},
                "trades_by_hour": {str(k): int(v) for k, v in hourly_volume['symbol'].items()}
            },
            "most_traded_symbol": df['symbol'].value_counts().index[0] if len(df) > 0 else None,
            "trading_frequency": len(trades) / max(1, (df['time'].max() - df['time'].min()).days) if len(df) > 1 else 0
        }
        
    async def _analyze_trading_patterns(self, trades: List[Trade]) -> Dict[str, Any]:
        """Analyze trading patterns using ML"""
        if len(trades) < 20:
            return {"error": "Insufficient data for pattern analysis"}
            
        df = pd.DataFrame([{
            'time': t.time,
            'symbol': t.symbol,
            'side': t.side,
            'price': float(_to_decimal(t.price)),
            'quantity': float(_to_decimal(t.quantity))
        } for t in trades])
        
        # Pattern detection
        patterns = {
            "trend_following": 0,
            "mean_reversion": 0,
            "momentum": 0
        }
        
        # Simple pattern detection logic
        for symbol in df['symbol'].unique():
            symbol_data = df[df['symbol'] == symbol].sort_values('time')
            if len(symbol_data) < 3:
                continue
                
            prices = symbol_data['price'].values
            sides = symbol_data['side'].str.lower().values
            
            # Trend following: buying on uptrends, selling on downtrends
            for i in range(2, len(prices)):
                if prices[i] > prices[i-1] > prices[i-2] and sides[i] == 'buy':
                    patterns["trend_following"] += 1
                elif prices[i] < prices[i-1] < prices[i-2] and sides[i] == 'sell':
                    patterns["trend_following"] += 1
                    
        return {
            "detected_patterns": patterns,
            "pattern_score": sum(patterns.values()) / len(trades) if len(trades) > 0 else 0,
            "trading_style": max(patterns.items(), key=lambda x: x[1])[0] if any(patterns.values()) else "mixed"
        }
        
    async def _generate_predictions(self, trades: List[Trade]) -> Dict[str, Any]:
        """Generate predictions using simple ML models"""
        if len(trades) < 30:
            return {"error": "Insufficient data for predictions"}
            
        try:
            df = pd.DataFrame([{
                'time': t.time,
                'price': float(_to_decimal(t.price)),
                'quantity': float(_to_decimal(t.quantity))
            } for t in trades])
            
            # Prepare time series data
            df['timestamp'] = df['time'].astype(np.int64) // 10**9  # Unix timestamp
            df = df.sort_values('time')
            
            # Simple linear regression for price trend
            X = np.array(df['timestamp'].values).reshape(-1, 1)
            y = df['price'].values
            
            model = LinearRegression()
            model.fit(X, y)
            
            # Predict next 7 days
            last_timestamp = df['timestamp'].iloc[-1]
            future_timestamps = np.array([last_timestamp + i * 86400 for i in range(1, 8)]).reshape(-1, 1)  # 7 days
            predicted_prices = model.predict(future_timestamps)
            
            # Calculate model performance
            y_pred = model.predict(X)
            r2 = r2_score(y, y_pred)
            
            return {
                "price_trend": {
                    "slope": float(model.coef_[0]),
                    "r2_score": float(r2),
                    "trend_direction": "upward" if model.coef_[0] > 0 else "downward",
                    "confidence": "high" if r2 > 0.7 else "medium" if r2 > 0.4 else "low"
                },
                "next_7_days_prediction": [float(p) for p in predicted_prices],
                "volume_trend": {
                    "avg_daily_volume": float(df['quantity'].mean()),
                    "volume_volatility": float(df['quantity'].std())
                }
            }
            
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return {"error": f"Prediction failed: {str(e)}"}
            
    async def _generate_charts(self, trades: List[Trade]) -> Dict[str, Any]:
        """Generate chart configurations for frontend"""
        if len(trades) < 2:
            return {}
            
        df = pd.DataFrame([{
            'time': t.time,
            'symbol': t.symbol,
            'side': t.side,
            'price': float(_to_decimal(t.price)),
            'quantity': float(_to_decimal(t.quantity))
        } for t in trades])
        
        # Daily PnL chart data
        df['date'] = df['time'].dt.date
        df['notional'] = df['quantity'] * df['price']
        df['pnl'] = df.apply(lambda row: row['notional'] if row['side'].lower() == 'sell' else -row['notional'], axis=1)
        
        daily_pnl = df.groupby('date')['pnl'].sum().reset_index()
        daily_pnl['cumulative_pnl'] = daily_pnl['pnl'].cumsum()
        
        return {
            "daily_pnl_chart": {
                "dates": [str(d) for d in daily_pnl['date']],
                "daily_pnl": daily_pnl['pnl'].tolist(),
                "cumulative_pnl": daily_pnl['cumulative_pnl'].tolist()
            },
            "symbol_distribution": df['symbol'].value_counts().to_dict(),
            "volume_over_time": {
                "dates": [str(d) for d in df.groupby('date')['quantity'].sum().index],
                "volumes": df.groupby('date')['quantity'].sum().tolist()
            }
        }


async def get_advanced_pnl_analytics(cache_service: CacheService) -> AdvancedPnLAnalytics:
    """Get advanced PnL analytics service instance"""
    return AdvancedPnLAnalytics(cache_service)
