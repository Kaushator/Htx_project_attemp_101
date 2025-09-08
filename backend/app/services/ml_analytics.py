"""
Machine Learning Analytics Service
Phase 3.1: Predictive Analytics for Trading Data

This service provides ML-powered insights including:
- PnL forecasting using time series analysis
- Market trend prediction
- Risk assessment algorithms
- Pattern recognition in trading data
"""

import logging
import asyncio
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

# ML imports
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split

from app.models.trade import Trade
# NOTE: CashFlow model is not present in current codebase; remove import to prevent startup failure
from app.services.cache import CacheService

logger = logging.getLogger(__name__)


class MLAnalyticsService:
    """Machine Learning Analytics Service for trading insights"""
    
    def __init__(self, cache_service: CacheService):
        self.cache = cache_service
        self.scaler = StandardScaler()
        
    async def predict_pnl_trend(
        self, 
        db: AsyncSession, 
        days_ahead: int = 7,
        symbol: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Predict PnL trend for the next N days using ML
        
        Args:
            db: Database session
            days_ahead: Number of days to forecast
            symbol: Optional symbol filter
            
        Returns:
            Dict with predictions, confidence, and metrics
        """
        cache_key = f"ml_pnl_forecast_{days_ahead}_{symbol or 'all'}"
        cached = await self.cache.get(cache_key)
        if cached:
            return cached
            
        try:
            # Get historical PnL data
            historical_data = await self._get_historical_pnl_data(db, symbol)
            
            if len(historical_data) < 30:  # Need at least 30 data points
                return {
                    "error": "Insufficient data for prediction",
                    "min_required": 30,
                    "available": len(historical_data)
                }
            
            # Prepare features and target
            X, y, dates = self._prepare_pnl_features(historical_data)
            
            # Train model
            model, metrics = self._train_pnl_model(X, y)
            
            # Generate predictions
            predictions = self._generate_pnl_predictions(
                model, historical_data, days_ahead
            )
            
            result = {
                "predictions": predictions,
                "model_metrics": metrics,
                "historical_data_points": len(historical_data),
                "forecast_period": days_ahead,
                "symbol": symbol,
                "generated_at": datetime.utcnow().isoformat(),
                "confidence_level": self._calculate_confidence(metrics)
            }
            
            # Cache for 4 hours
            await self.cache.set(cache_key, result, expire=14400)
            logger.info(f"Generated PnL forecast for {days_ahead} days")
            
            return result
            
        except Exception as e:
            logger.error(f"PnL prediction failed: {e}", exc_info=True)
            return {"error": str(e)}
    
    async def detect_trading_anomalies(
        self, 
        db: AsyncSession,
        lookback_days: int = 30
    ) -> Dict[str, Any]:
        """
        Detect anomalous trading patterns using Isolation Forest
        
        Args:
            db: Database session
            lookback_days: Number of days to analyze
            
        Returns:
            Dict with anomaly detection results
        """
        cache_key = f"ml_anomaly_detection_{lookback_days}"
        cached = await self.cache.get(cache_key)
        if cached:
            return cached
            
        try:
            # Get recent trades
            since = datetime.utcnow() - timedelta(days=lookback_days)
            
            query = await db.execute(
                select(Trade)
                .where(Trade.time >= since)
                .order_by(Trade.time.desc())
            )
            trades = query.scalars().all()
            
            if len(trades) < 10:
                return {
                    "error": "Insufficient trades for anomaly detection",
                    "min_required": 10,
                    "available": len(trades)
                }
            
            # Prepare features for anomaly detection
            features = self._prepare_anomaly_features(trades)
            
            # Train Isolation Forest
            iso_forest = IsolationForest(
                contamination=0.1,  # Expect 10% anomalies
                random_state=42
            )
            anomaly_labels = iso_forest.fit_predict(features)
            
            # Identify anomalous trades
            anomalies = []
            for i, (trade, is_anomaly) in enumerate(zip(trades, anomaly_labels)):
                if is_anomaly == -1:  # Anomaly detected
                    anomalies.append({
                        "trade_id": trade.id,
                        "symbol": trade.symbol,
                        "amount": float(trade.amount),
                        "price": float(trade.price),
                        "time": trade.time.isoformat(),
                        "anomaly_score": iso_forest.decision_function([features[i]])[0],
                        "reason": self._analyze_anomaly_reason(trade, features[i])
                    })
            
            result = {
                "total_trades_analyzed": len(trades),
                "anomalies_detected": len(anomalies),
                "anomaly_rate": len(anomalies) / len(trades),
                "anomalies": sorted(anomalies, key=lambda x: x["anomaly_score"]),
                "analysis_period": lookback_days,
                "generated_at": datetime.utcnow().isoformat()
            }
            
            # Cache for 2 hours
            await self.cache.set(cache_key, result, expire=7200)
            logger.info(f"Detected {len(anomalies)} trading anomalies")
            
            return result
            
        except Exception as e:
            logger.error(f"Anomaly detection failed: {e}", exc_info=True)
            return {"error": str(e)}
    
    async def calculate_risk_metrics(
        self, 
        db: AsyncSession,
        symbol: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calculate advanced risk metrics using ML techniques
        
        Args:
            db: Database session
            symbol: Optional symbol filter
            
        Returns:
            Dict with risk assessment metrics
        """
        cache_key = f"ml_risk_metrics_{symbol or 'all'}"
        cached = await self.cache.get(cache_key)
        if cached:
            return cached
            
        try:
            # Get recent PnL data for risk calculation
            pnl_data = await self._get_historical_pnl_data(db, symbol, days=90)
            
            if len(pnl_data) < 20:
                return {
                    "error": "Insufficient data for risk analysis",
                    "min_required": 20,
                    "available": len(pnl_data)
                }
            
            # Calculate traditional risk metrics
            returns = pd.Series([d['pnl_change'] for d in pnl_data])
            
            # Value at Risk (VaR) calculations
            var_95 = np.percentile(returns, 5)  # 95% VaR
            var_99 = np.percentile(returns, 1)  # 99% VaR
            
            # Expected Shortfall (Conditional VaR)
            es_95 = returns[returns <= var_95].mean()
            es_99 = returns[returns <= var_99].mean()
            
            # ML-based volatility prediction
            volatility_forecast = self._predict_volatility(returns)
            
            # Risk-adjusted returns
            sharpe_ratio = returns.mean() / returns.std() if returns.std() > 0 else 0
            
            # Maximum drawdown analysis
            cumulative_returns = (1 + returns / 100).cumprod()
            running_max = cumulative_returns.expanding().max()
            drawdown = (cumulative_returns - running_max) / running_max
            max_drawdown = drawdown.min()
            
            result = {
                "var_95": float(var_95),
                "var_99": float(var_99),
                "expected_shortfall_95": float(es_95),
                "expected_shortfall_99": float(es_99),
                "volatility_current": float(returns.std()),
                "volatility_forecast": volatility_forecast,
                "sharpe_ratio": float(sharpe_ratio),
                "max_drawdown": float(max_drawdown),
                "risk_score": self._calculate_risk_score(var_95, volatility_forecast["predicted"]),
                "analysis_period_days": len(pnl_data),
                "symbol": symbol,
                "generated_at": datetime.utcnow().isoformat()
            }
            
            # Cache for 6 hours
            await self.cache.set(cache_key, result, expire=21600)
            logger.info(f"Calculated risk metrics for {symbol or 'all symbols'}")
            
            return result
            
        except Exception as e:
            logger.error(f"Risk calculation failed: {e}", exc_info=True)
            return {"error": str(e)}
    
    async def analyze_trading_patterns(
        self, 
        db: AsyncSession,
        pattern_type: str = "hourly"
    ) -> Dict[str, Any]:
        """
        Analyze trading patterns using ML clustering
        
        Args:
            db: Database session
            pattern_type: Type of pattern analysis ("hourly", "daily", "volume")
            
        Returns:
            Dict with pattern analysis results
        """
        cache_key = f"ml_patterns_{pattern_type}"
        cached = await self.cache.get(cache_key)
        if cached:
            return cached
            
        try:
            # Get recent trades for pattern analysis
            since = datetime.utcnow() - timedelta(days=60)
            
            query = await db.execute(
                select(Trade)
                .where(Trade.time >= since)
                .order_by(Trade.time)
            )
            trades = query.scalars().all()
            
            if len(trades) < 50:
                return {
                    "error": "Insufficient trades for pattern analysis",
                    "min_required": 50,
                    "available": len(trades)
                }
            
            # Analyze patterns based on type
            if pattern_type == "hourly":
                patterns = self._analyze_hourly_patterns(trades)
            elif pattern_type == "daily":
                patterns = self._analyze_daily_patterns(trades)
            elif pattern_type == "volume":
                patterns = self._analyze_volume_patterns(trades)
            else:
                return {"error": f"Unknown pattern type: {pattern_type}"}
            
            result = {
                "pattern_type": pattern_type,
                "patterns": patterns,
                "total_trades_analyzed": len(trades),
                "analysis_period_days": 60,
                "generated_at": datetime.utcnow().isoformat()
            }
            
            # Cache for 3 hours
            await self.cache.set(cache_key, result, expire=10800)
            logger.info(f"Analyzed {pattern_type} trading patterns")
            
            return result
            
        except Exception as e:
            logger.error(f"Pattern analysis failed: {e}", exc_info=True)
            return {"error": str(e)}
    
    # Helper methods
    
    async def _get_historical_pnl_data(
        self, 
        db: AsyncSession, 
        symbol: Optional[str] = None,
        days: int = 60
    ) -> List[Dict[str, Any]]:
        """Get historical PnL data for ML analysis"""
        since = datetime.utcnow() - timedelta(days=days)
        
        # Query daily PnL aggregates
        query = select(
            func.date(Trade.time).label("date"),
            func.sum(Trade.amount * Trade.price).label("daily_volume"),
            func.count(Trade.id).label("trade_count"),
            func.avg(Trade.price).label("avg_price")
        ).where(Trade.time >= since)
        
        if symbol:
            query = query.where(Trade.symbol == symbol)
            
        query = query.group_by(func.date(Trade.time)).order_by(func.date(Trade.time))
        
        result = await db.execute(query)
        rows = result.fetchall()
        
        # Calculate PnL changes
        data = []
        prev_volume = None
        
        for row in rows:
            current_volume = float(row.daily_volume)
            pnl_change = 0
            
            if prev_volume is not None:
                pnl_change = ((current_volume - prev_volume) / prev_volume) * 100
            
            data.append({
                "date": row.date,
                "daily_volume": current_volume,
                "trade_count": row.trade_count,
                "avg_price": float(row.avg_price),
                "pnl_change": pnl_change
            })
            
            prev_volume = current_volume
        
        return data
    
    def _prepare_pnl_features(self, historical_data: List[Dict]) -> Tuple[np.ndarray, np.ndarray, List]:
        """Prepare features for PnL prediction"""
        df = pd.DataFrame(historical_data)
        
        # Create time-based features
        df['date'] = pd.to_datetime(df['date'])
        df['day_of_week'] = df['date'].dt.dayofweek
        df['day_of_month'] = df['date'].dt.day
        df['month'] = df['date'].dt.month
        
        # Create lag features
        df['pnl_lag1'] = df['pnl_change'].shift(1)
        df['pnl_lag2'] = df['pnl_change'].shift(2)
        df['pnl_lag3'] = df['pnl_change'].shift(3)
        
        # Rolling statistics
        df['pnl_ma_7'] = df['pnl_change'].rolling(7).mean()
        df['pnl_std_7'] = df['pnl_change'].rolling(7).std()
        
        # Volume features
        df['volume_lag1'] = df['daily_volume'].shift(1)
        df['volume_change'] = df['daily_volume'].pct_change()
        
        # Drop NaN rows
        df = df.dropna()
        
        # Feature columns
        feature_cols = [
            'day_of_week', 'day_of_month', 'month',
            'pnl_lag1', 'pnl_lag2', 'pnl_lag3',
            'pnl_ma_7', 'pnl_std_7',
            'volume_lag1', 'volume_change',
            'trade_count', 'avg_price'
        ]
        
        X = df[feature_cols].values
        y = df['pnl_change'].values
        dates = df['date'].tolist()
        
        return X, y, dates
    
    def _train_pnl_model(self, X: np.ndarray, y: np.ndarray) -> Tuple[Any, Dict[str, float]]:
        """Train PnL prediction model"""
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train Random Forest model
        model = RandomForestRegressor(
            n_estimators=100,
            random_state=42,
            max_depth=10
        )
        model.fit(X_train_scaled, y_train)
        
        # Calculate metrics
        y_pred = model.predict(X_test_scaled)
        
        metrics = {
            "mae": mean_absolute_error(y_test, y_pred),
            "mse": mean_squared_error(y_test, y_pred),
            "rmse": np.sqrt(mean_squared_error(y_test, y_pred)),
            "r2_score": model.score(X_test_scaled, y_test)
        }
        
        return model, metrics
    
    def _generate_pnl_predictions(
        self, 
        model: Any, 
        historical_data: List[Dict], 
        days_ahead: int
    ) -> List[Dict[str, Any]]:
        """Generate future PnL predictions"""
        predictions = []
        
        # Use last known data point as starting point
        last_data = historical_data[-1].copy()
        
        for i in range(days_ahead):
            # Create features for prediction
            future_date = datetime.now() + timedelta(days=i+1)
            
            # Simple feature creation (in real implementation, this would be more sophisticated)
            features = np.array([[
                future_date.weekday(),  # day_of_week
                future_date.day,        # day_of_month
                future_date.month,      # month
                last_data['pnl_change'],  # pnl_lag1
                historical_data[-2]['pnl_change'] if len(historical_data) > 1 else 0,  # pnl_lag2
                historical_data[-3]['pnl_change'] if len(historical_data) > 2 else 0,  # pnl_lag3
                np.mean([d['pnl_change'] for d in historical_data[-7:]]),  # pnl_ma_7
                np.std([d['pnl_change'] for d in historical_data[-7:]]),   # pnl_std_7
                last_data['daily_volume'],  # volume_lag1
                0,  # volume_change (unknown for future)
                last_data['trade_count'],   # trade_count
                last_data['avg_price']      # avg_price
            ]])
            
            # Scale and predict
            features_scaled = self.scaler.transform(features)
            pred_pnl = model.predict(features_scaled)[0]
            
            predictions.append({
                "date": future_date.date().isoformat(),
                "predicted_pnl_change": float(pred_pnl),
                "day_offset": i + 1
            })
            
            # Update last_data for next iteration
            last_data['pnl_change'] = pred_pnl
        
        return predictions
    
    def _calculate_confidence(self, metrics: Dict[str, float]) -> str:
        """Calculate model confidence level"""
        r2_score = metrics.get('r2_score', 0)
        
        if r2_score >= 0.8:
            return "high"
        elif r2_score >= 0.6:
            return "medium"
        else:
            return "low"
    
    def _prepare_anomaly_features(self, trades: List[Trade]) -> np.ndarray:
        """Prepare features for anomaly detection"""
        features = []
        
        for trade in trades:
            # Extract features that might indicate anomalies
            features.append([
                float(trade.amount),
                float(trade.price),
                float(trade.amount * trade.price),  # total value
                trade.time.hour,                    # hour of day
                trade.time.weekday(),              # day of week
                len(trade.symbol),                 # symbol length
            ])
        
        return np.array(features)
    
    def _analyze_anomaly_reason(self, trade: Trade, features: np.ndarray) -> str:
        """Analyze why a trade was flagged as anomalous"""
        reasons = []
        
        if features[0] > np.percentile([f[0] for f in features], 95):  # High amount
            reasons.append("unusually_high_amount")
        
        if features[1] > np.percentile([f[1] for f in features], 95):  # High price
            reasons.append("unusually_high_price")
        
        if features[3] < 6 or features[3] > 22:  # Off-hours trading
            reasons.append("off_hours_trading")
        
        return ", ".join(reasons) if reasons else "pattern_anomaly"
    
    def _predict_volatility(self, returns: pd.Series) -> Dict[str, float]:
        """Predict future volatility using simple ML"""
        # Calculate rolling volatility
        vol_window = min(20, len(returns) // 2)
        rolling_vol = returns.rolling(vol_window).std()
        
        # Simple linear trend prediction
        recent_vol = rolling_vol.dropna()
        if len(recent_vol) > 5:
            X = np.arange(len(recent_vol)).reshape(-1, 1)
            y = recent_vol.values
            
            model = LinearRegression()
            model.fit(X, y)
            
            # Predict next period volatility
            next_x = len(recent_vol)
            predicted_vol = model.predict([[next_x]])[0]
        else:
            predicted_vol = recent_vol.iloc[-1] if len(recent_vol) > 0 else returns.std()
        
        return {
            "current": float(rolling_vol.iloc[-1]) if len(rolling_vol) > 0 else float(returns.std()),
            "predicted": float(predicted_vol),
            "trend": "increasing" if predicted_vol > rolling_vol.iloc[-1] else "decreasing"
        }
    
    def _calculate_risk_score(self, var_95: float, volatility: float) -> Dict[str, Any]:
        """Calculate overall risk score"""
        # Normalize to 0-100 scale
        risk_score = min(100, max(0, (abs(var_95) * 2 + volatility * 3) * 10))
        
        if risk_score >= 70:
            risk_level = "high"
        elif risk_score >= 40:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        return {
            "score": float(risk_score),
            "level": risk_level,
            "factors": {
                "var_contribution": abs(var_95) * 20,
                "volatility_contribution": volatility * 30
            }
        }
    
    def _analyze_hourly_patterns(self, trades: List[Trade]) -> Dict[str, Any]:
        """Analyze hourly trading patterns"""
        hourly_data = {}
        
        for trade in trades:
            hour = trade.time.hour
            if hour not in hourly_data:
                hourly_data[hour] = []
            hourly_data[hour].append(float(trade.amount * trade.price))
        
        patterns = {}
        for hour, volumes in hourly_data.items():
            patterns[f"hour_{hour}"] = {
                "avg_volume": np.mean(volumes),
                "trade_count": len(volumes),
                "total_volume": sum(volumes)
            }
        
        # Find peak hours
        peak_hour = max(patterns.keys(), key=lambda h: patterns[h]["avg_volume"])
        
        return {
            "hourly_breakdown": patterns,
            "peak_trading_hour": int(peak_hour.split("_")[1]),
            "total_hours_active": len(patterns)
        }
    
    def _analyze_daily_patterns(self, trades: List[Trade]) -> Dict[str, Any]:
        """Analyze daily trading patterns"""
        daily_data = {}
        
        for trade in trades:
            day = trade.time.weekday()  # 0=Monday, 6=Sunday
            if day not in daily_data:
                daily_data[day] = []
            daily_data[day].append(float(trade.amount * trade.price))
        
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        patterns = {}
        
        for day, volumes in daily_data.items():
            patterns[day_names[day]] = {
                "avg_volume": np.mean(volumes),
                "trade_count": len(volumes),
                "total_volume": sum(volumes)
            }
        
        return {
            "daily_breakdown": patterns,
            "most_active_day": max(patterns.keys(), key=lambda d: patterns[d]["avg_volume"]),
            "total_active_days": len(patterns)
        }
    
    def _analyze_volume_patterns(self, trades: List[Trade]) -> Dict[str, Any]:
        """Analyze volume-based patterns"""
        volumes = [float(trade.amount * trade.price) for trade in trades]
        
        # Volume distribution analysis
        volume_stats = {
            "mean": np.mean(volumes),
            "median": np.median(volumes),
            "std": np.std(volumes),
            "min": np.min(volumes),
            "max": np.max(volumes),
            "q25": np.percentile(volumes, 25),
            "q75": np.percentile(volumes, 75)
        }
        
        # Categorize trades by volume
        high_volume_threshold = volume_stats["q75"]
        low_volume_threshold = volume_stats["q25"]
        
        high_volume_count = sum(1 for v in volumes if v >= high_volume_threshold)
        low_volume_count = sum(1 for v in volumes if v <= low_volume_threshold)
        
        return {
            "volume_statistics": volume_stats,
            "high_volume_trades": high_volume_count,
            "low_volume_trades": low_volume_count,
            "medium_volume_trades": len(volumes) - high_volume_count - low_volume_count,
            "volume_concentration": {
                "top_10_percent_volume": np.percentile(volumes, 90),
                "bottom_10_percent_volume": np.percentile(volumes, 10)
            }
        }


# Service factory function
async def get_ml_analytics_service(cache_service: CacheService) -> MLAnalyticsService:
    """Get ML Analytics service instance"""
    return MLAnalyticsService(cache_service)
