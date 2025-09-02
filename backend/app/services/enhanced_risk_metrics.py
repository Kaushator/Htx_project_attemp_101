"""
Enhanced Risk Metrics Service
Imports and extends risk calculations from legacy pnl_report.py
Provides comprehensive risk analysis for trading portfolios
"""

import logging
import asyncio
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from scipy import stats
import math

from app.models.trade import Trade
from app.services.cache import CacheService
from app.core.config import settings

logger = logging.getLogger(__name__)


class RiskMetricsService:
    """Enhanced risk metrics service with comprehensive analysis"""
    
    def __init__(self, cache_service: CacheService):
        self.cache = cache_service
        
    async def calculate_comprehensive_risk_metrics(
        self,
        db: AsyncSession,
        symbol: Optional[str] = None,
        days_lookback: int = 365
    ) -> Dict[str, Any]:
        """Calculate comprehensive risk metrics for trading portfolio"""
        try:
            # Get trade data
            trades_df = await self._get_trades_dataframe(db, symbol, days_lookback)
            
            if trades_df.empty:
                return {"error": "No trade data available", "symbol": symbol}
            
            # Calculate all risk metrics
            risk_metrics = {
                "basic_metrics": await self._calculate_basic_metrics(trades_df),
                "advanced_metrics": await self._calculate_advanced_metrics(trades_df),
                "drawdown_analysis": await self._calculate_enhanced_drawdown(trades_df),
                "volatility_metrics": await self._calculate_volatility_metrics(trades_df),
                "risk_ratios": await self._calculate_risk_ratios(trades_df),
                "var_analysis": await self._calculate_var_metrics(trades_df),
                "concentration_risk": await self._calculate_concentration_risk(trades_df),
                "performance_attribution": await self._calculate_performance_attribution(trades_df),
                "risk_adjusted_returns": await self._calculate_risk_adjusted_returns(trades_df),
                "tail_risk_metrics": await self._calculate_tail_risk_metrics(trades_df)
            }
            
            # Add metadata
            risk_metrics["metadata"] = {
                "symbol": symbol,
                "analysis_period_days": days_lookback,
                "total_trades": len(trades_df),
                "data_start": trades_df['time'].min().isoformat() if not trades_df.empty else None,
                "data_end": trades_df['time'].max().isoformat() if not trades_df.empty else None,
                "generated_at": datetime.utcnow().isoformat()
            }
            
            return risk_metrics
            
        except Exception as e:
            logger.error(f"Risk metrics calculation failed: {e}")
            return {"error": str(e)}
    
    async def _get_trades_dataframe(
        self,
        db: AsyncSession,
        symbol: Optional[str] = None,
        days_lookback: int = 365
    ) -> pd.DataFrame:
        """Get trades as pandas DataFrame"""
        since = datetime.utcnow() - timedelta(days=days_lookback)
        
        query = select(Trade).where(Trade.time >= since)
        if symbol:
            query = query.where(Trade.symbol == symbol)
        
        query = query.order_by(Trade.time.asc())
        
        result = await db.execute(query)
        trades = result.scalars().all()
        
        if not trades:
            return pd.DataFrame()
        
        # Convert to DataFrame
        data = []
        for trade in trades:
            data.append({
                'id': trade.id,
                'symbol': trade.symbol,
                'side': trade.side,
                'amount': float(trade.amount),
                'price': float(trade.price),
                'fee': float(trade.fee or 0),
                'time': trade.time
            })
        
        df = pd.DataFrame(data)
        
        # Calculate PnL for each trade
        df = self._calculate_trade_pnl(df)
        
        return df
    
    def _calculate_trade_pnl(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate PnL for each trade (imported from legacy pnl_report.py)"""
        if df.empty:
            return df
        
        df = df.sort_values('time').copy()
        df['trade_pnl'] = 0.0
        df['position'] = 0.0
        df['avg_price'] = 0.0
        
        # Calculate position and PnL
        position = 0.0
        total_cost = 0.0
        
        for i, row in df.iterrows():
            if row['side'] == 'buy':
                position += row['amount']
                total_cost += row['amount'] * row['price']
                df.at[i, 'position'] = position
                df.at[i, 'avg_price'] = total_cost / position if position != 0 else 0
            else:  # sell
                if position > 0:
                    avg_price = total_cost / position
                    pnl = (row['price'] - avg_price) * row['amount'] - row['fee']
                    df.at[i, 'trade_pnl'] = pnl
                    
                    # Update position
                    position -= row['amount']
                    if position > 0:
                        total_cost = position * avg_price
                    else:
                        total_cost = 0
                        
                df.at[i, 'position'] = position
                df.at[i, 'avg_price'] = total_cost / position if position != 0 else 0
        
        return df
    
    async def _calculate_basic_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate basic trading metrics (from legacy pnl_report.py)"""
        if df.empty:
            return {}
        
        # Win/Loss statistics
        winning_trades = df[df['trade_pnl'] > 0]
        losing_trades = df[df['trade_pnl'] < 0]
        
        total_trades = len(df[df['trade_pnl'] != 0])
        win_count = len(winning_trades)
        loss_count = len(losing_trades)
        
        return {
            "total_trades": total_trades,
            "winning_trades": win_count,
            "losing_trades": loss_count,
            "win_rate": win_count / total_trades if total_trades > 0 else 0,
            "loss_rate": loss_count / total_trades if total_trades > 0 else 0,
            "avg_win": winning_trades['trade_pnl'].mean() if len(winning_trades) > 0 else 0,
            "avg_loss": losing_trades['trade_pnl'].mean() if len(losing_trades) > 0 else 0,
            "largest_win": winning_trades['trade_pnl'].max() if len(winning_trades) > 0 else 0,
            "largest_loss": losing_trades['trade_pnl'].min() if len(losing_trades) > 0 else 0,
            "total_pnl": df['trade_pnl'].sum(),
            "total_fees": df['fee'].sum(),
            "net_pnl": df['trade_pnl'].sum() - df['fee'].sum(),
            "profit_factor": self._calculate_profit_factor(winning_trades, losing_trades)
        }
    
    def _calculate_profit_factor(self, winning_trades: pd.DataFrame, losing_trades: pd.DataFrame) -> float:
        """Calculate profit factor (imported logic)"""
        if len(losing_trades) == 0:
            return float('inf')
        
        total_wins = winning_trades['trade_pnl'].sum()
        total_losses = abs(losing_trades['trade_pnl'].sum())
        
        return total_wins / total_losses if total_losses > 0 else float('inf')
    
    async def _calculate_enhanced_drawdown(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate enhanced drawdown metrics (imported from legacy)"""
        if df.empty:
            return {}
        
        # Daily PnL
        df['date'] = df['time'].dt.date
        daily_pnl = df.groupby('date')['trade_pnl'].sum().reset_index()
        daily_pnl['cumulative_pnl'] = daily_pnl['trade_pnl'].cumsum()
        
        # Calculate drawdown
        daily_pnl['running_max'] = daily_pnl['cumulative_pnl'].expanding().max()
        daily_pnl['drawdown'] = daily_pnl['cumulative_pnl'] - daily_pnl['running_max']
        daily_pnl['drawdown_pct'] = (daily_pnl['drawdown'] / daily_pnl['running_max']) * 100
        
        # Drawdown periods
        drawdown_periods = self._identify_drawdown_periods(daily_pnl)
        
        return {
            "max_drawdown": daily_pnl['drawdown'].min(),
            "max_drawdown_pct": daily_pnl['drawdown_pct'].min(),
            "current_drawdown": daily_pnl['drawdown'].iloc[-1] if not daily_pnl.empty else 0,
            "current_drawdown_pct": daily_pnl['drawdown_pct'].iloc[-1] if not daily_pnl.empty else 0,
            "avg_drawdown": daily_pnl[daily_pnl['drawdown'] < 0]['drawdown'].mean(),
            "drawdown_periods": len(drawdown_periods),
            "longest_drawdown_days": max([p['duration_days'] for p in drawdown_periods]) if drawdown_periods else 0,
            "recovery_factor": self._calculate_recovery_factor(daily_pnl),
            "ulcer_index": self._calculate_ulcer_index(daily_pnl)
        }
    
    def _identify_drawdown_periods(self, daily_pnl: pd.DataFrame) -> List[Dict[str, Any]]:
        """Identify distinct drawdown periods"""
        periods = []
        in_drawdown = False
        start_date = None
        
        for _, row in daily_pnl.iterrows():
            if row['drawdown'] < 0 and not in_drawdown:
                # Start of drawdown
                in_drawdown = True
                start_date = row['date']
            elif row['drawdown'] == 0 and in_drawdown:
                # End of drawdown
                in_drawdown = False
                if start_date:
                    periods.append({
                        'start_date': start_date,
                        'end_date': row['date'],
                        'duration_days': (row['date'] - start_date).days,
                        'max_drawdown': daily_pnl[
                            (daily_pnl['date'] >= start_date) & 
                            (daily_pnl['date'] <= row['date'])
                        ]['drawdown'].min()
                    })
        
        return periods
    
    async def _calculate_risk_ratios(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate risk-adjusted return ratios"""
        if df.empty:
            return {}
        
        # Daily PnL
        df['date'] = df['time'].dt.date
        daily_pnl = df.groupby('date')['trade_pnl'].sum()
        
        if len(daily_pnl) == 0:
            return {}
        
        annual_return = daily_pnl.mean() * 252
        annual_vol = daily_pnl.std() * math.sqrt(252)
        
        # Risk-free rate (assume 2% annual)
        risk_free_rate = 0.02
        
        return {
            "sharpe_ratio": (annual_return - risk_free_rate) / annual_vol if annual_vol > 0 else 0,
            "sortino_ratio": self._calculate_sortino_ratio(daily_pnl, risk_free_rate),
            "calmar_ratio": self._calculate_calmar_ratio(daily_pnl),
            "sterling_ratio": self._calculate_sterling_ratio(daily_pnl),
            "information_ratio": annual_return / annual_vol if annual_vol > 0 else 0,
            "treynor_ratio": annual_return / 1.0,  # Assuming beta = 1 for crypto
            "omega_ratio": self._calculate_omega_ratio(daily_pnl)
        }
    
    def _calculate_sortino_ratio(self, daily_pnl: pd.Series, risk_free_rate: float) -> float:
        """Calculate Sortino ratio"""
        annual_return = daily_pnl.mean() * 252
        downside_deviation = self._calculate_downside_deviation(daily_pnl)
        annual_downside_dev = downside_deviation * math.sqrt(252)
        
        return (annual_return - risk_free_rate) / annual_downside_dev if annual_downside_dev > 0 else 0
    
    def _calculate_downside_deviation(self, returns: pd.Series, target: float = 0) -> float:
        """Calculate downside deviation"""
        downside_returns = returns[returns < target]
        if len(downside_returns) == 0:
            return 0
        
        return math.sqrt(((downside_returns - target) ** 2).mean())
    
    async def _calculate_var_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate Value at Risk metrics"""
        if df.empty:
            return {}
        
        # Daily PnL
        df['date'] = df['time'].dt.date
        daily_pnl = df.groupby('date')['trade_pnl'].sum()
        
        if len(daily_pnl) == 0:
            return {}
        
        return {
            "var_95": np.percentile(daily_pnl, 5),
            "var_99": np.percentile(daily_pnl, 1),
            "cvar_95": daily_pnl[daily_pnl <= np.percentile(daily_pnl, 5)].mean(),
            "cvar_99": daily_pnl[daily_pnl <= np.percentile(daily_pnl, 1)].mean(),
            "parametric_var_95": self._calculate_parametric_var(daily_pnl, 0.95),
            "parametric_var_99": self._calculate_parametric_var(daily_pnl, 0.99),
            "expected_shortfall_95": self._calculate_expected_shortfall(daily_pnl, 0.95)
        }
    
    def _calculate_parametric_var(self, daily_pnl: pd.Series, confidence: float) -> float:
        """Calculate parametric VaR assuming normal distribution"""
        mean = daily_pnl.mean()
        std = daily_pnl.std()
        z_score = stats.norm.ppf(1 - confidence)
        
        return mean + z_score * std


# Global service instance
_risk_metrics_service: Optional[RiskMetricsService] = None


async def get_risk_metrics_service() -> RiskMetricsService:
    """Get or create risk metrics service instance"""
    global _risk_metrics_service
    if _risk_metrics_service is None:
        from app.services.cache import get_cache_service
        cache_service = await get_cache_service()
        _risk_metrics_service = RiskMetricsService(cache_service)
    return _risk_metrics_service