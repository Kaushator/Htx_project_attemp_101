"""
Machine Learning Service for File Analysis

Этот модуль обрабатывает загруженные файлы и применяет ML-анализ 
для извлечения паттернов, аномалий и прогнозирования данных.
"""

import logging
import asyncio
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import os

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

# Определим функции-заглушки для ML, которые будут использоваться,
# если sklearn не установлен (тем самым избегаем ошибок импорта)
try:
    from sklearn.ensemble import RandomForestRegressor, IsolationForest
    from sklearn.preprocessing import StandardScaler
    from sklearn.cluster import KMeans
    from sklearn.model_selection import train_test_split
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    # Определяем заглушки для ML-классов
    class MockScaler:
        def fit_transform(self, X): return X
        def transform(self, X): return X
    
    StandardScaler = lambda: MockScaler()

from app.core.config import settings
from app.services.cache import CacheService

logger = logging.getLogger(__name__)


class MLFileAnalyticsService:
    """
    Сервис для анализа загруженных файлов с использованием ML
    """
    
    def __init__(self, cache_service: CacheService = None):
        self.cache = cache_service
        self.scaler = StandardScaler()
        self.upload_dir = Path(settings.UPLOAD_DIR)
        
        # Создаем директорию для хранения моделей, если её нет
        self.models_dir = Path(settings.BASE_DIR) / "data" / "ml_models"
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
    async def analyze_uploaded_file(
        self, 
        file_id: str, 
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Анализирует загруженный файл и выдает результаты ML-анализа
        
        Args:
            file_id: ID загруженного файла
            db: Сессия базы данных
            
        Returns:
            Словарь с результатами анализа
        """
        cache_key = f"ml_file_analysis_{file_id}"
        if self.cache:
            cached = await self.cache.get(cache_key)
            if cached:
                return cached
        
        try:
            # Находим файл по ID в директории загрузок
            file_path = await self._find_file_by_id(file_id)
            if not file_path:
                return {
                    "error": f"File with ID {file_id} not found",
                    "success": False
                }
            
            # Читаем и анализируем файл
            df = await self._read_file(file_path)
            if df is None or df.empty:
                return {
                    "error": "Could not read file or file is empty",
                    "success": False
                }
            
            # Выполняем базовый анализ данных
            basic_analysis = await self._basic_file_analysis(df)
            
            # Выполняем ML-анализ, если данные подходят
            ml_analysis = await self._ml_file_analysis(df)
            
            # Объединяем результаты анализа
            result = {
                "success": True,
                "file_id": file_id,
                "file_name": os.path.basename(file_path),
                "basic_analysis": basic_analysis,
                "ml_analysis": ml_analysis,
                "generated_at": datetime.utcnow().isoformat()
            }
            
            # Кешируем результаты на 1 час
            if self.cache:
                await self.cache.set(cache_key, result, expire=3600)
                
            return result
            
        except Exception as e:
            logger.error(f"File analysis failed: {e}", exc_info=True)
            return {
                "error": str(e),
                "success": False
            }
            
    async def _find_file_by_id(self, file_id: str) -> Optional[str]:
        """
        Находит файл по ID в директории загрузок
        
        Args:
            file_id: ID файла (может быть timestamp или UUID)
            
        Returns:
            Путь к файлу или None, если файл не найден
        """
        # Для простоты, предположим, что file_id - это timestamp или часть имени файла
        if not self.upload_dir.exists():
            return None
            
        for file_path in self.upload_dir.iterdir():
            if file_path.is_file() and file_id in file_path.name:
                return str(file_path)
                
        # Если не нашли по ID, попробуем просто найти последний загруженный файл
        files = [(f, f.stat().st_mtime) for f in self.upload_dir.iterdir() if f.is_file()]
        if files:
            files.sort(key=lambda x: x[1], reverse=True)
            return str(files[0][0])
                
        return None
        
    async def _read_file(self, file_path: str) -> Optional[pd.DataFrame]:
        """
        Читает файл и возвращает DataFrame
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            DataFrame с данными или None, если файл не удалось прочитать
        """
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.csv':
                return pd.read_csv(file_path)
            elif file_ext in ['.xlsx', '.xls']:
                return pd.read_excel(file_path)
            else:
                logger.error(f"Unsupported file extension: {file_ext}")
                return None
                
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return None
            
    async def _basic_file_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Выполняет базовый анализ данных файла
        
        Args:
            df: DataFrame с данными
            
        Returns:
            Словарь с результатами базового анализа
        """
        try:
            # Общая информация о данных
            basic_info = {
                "rows": len(df),
                "columns": list(df.columns),
                "missing_values": df.isnull().sum().to_dict(),
                "data_types": {col: str(dtype) for col, dtype in df.dtypes.items()}
            }
            
            # Анализ числовых столбцов
            numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
            numeric_stats = {}
            
            for col in numeric_columns:
                numeric_stats[col] = {
                    "min": float(df[col].min()) if not pd.isna(df[col].min()) else None,
                    "max": float(df[col].max()) if not pd.isna(df[col].max()) else None,
                    "mean": float(df[col].mean()) if not pd.isna(df[col].mean()) else None,
                    "median": float(df[col].median()) if not pd.isna(df[col].median()) else None,
                    "std": float(df[col].std()) if not pd.isna(df[col].std()) else None
                }
                
            # Анализ временных рядов (если есть дата)
            date_columns = []
            for col in df.columns:
                if 'date' in col.lower() or 'time' in col.lower():
                    try:
                        df[col] = pd.to_datetime(df[col])
                        date_columns.append(col)
                    except:
                        pass
                        
            time_analysis = {}
            if date_columns:
                date_col = date_columns[0]  # Берем первый столбец с датой
                time_analysis = {
                    "date_column": date_col,
                    "start_date": df[date_col].min().isoformat() if not pd.isna(df[date_col].min()) else None,
                    "end_date": df[date_col].max().isoformat() if not pd.isna(df[date_col].max()) else None,
                    "date_range_days": (df[date_col].max() - df[date_col].min()).days if not pd.isna(df[date_col].min()) and not pd.isna(df[date_col].max()) else None
                }
                
            # Анализ категориальных данных
            categorical_columns = df.select_dtypes(include=['object']).columns.tolist()
            categorical_stats = {}
            
            for col in categorical_columns:
                if df[col].nunique() <= 50:  # Ограничиваем анализ столбцов с небольшим числом уникальных значений
                    value_counts = df[col].value_counts().head(10).to_dict()
                    categorical_stats[col] = {
                        "unique_values": df[col].nunique(),
                        "top_values": value_counts
                    }
            
            return {
                "basic_info": basic_info,
                "numeric_stats": numeric_stats,
                "time_analysis": time_analysis,
                "categorical_stats": categorical_stats
            }
            
        except Exception as e:
            logger.error(f"Error in basic file analysis: {e}")
            return {"error": str(e)}
            
    async def _ml_file_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Выполняет ML-анализ данных файла
        
        Args:
            df: DataFrame с данными
            
        Returns:
            Словарь с результатами ML-анализа
        """
        try:
            result = {}
            
            # Определяем, есть ли достаточно данных для ML
            if len(df) < 30:
                return {
                    "error": "Insufficient data for ML analysis",
                    "min_required": 30,
                    "available": len(df)
                }
                
            # 1. Обнаружение аномалий с помощью Isolation Forest
            anomalies_result = await self._detect_anomalies(df)
            if anomalies_result:
                result["anomalies"] = anomalies_result
                
            # 2. Кластеризация данных
            clustering_result = await self._cluster_data(df)
            if clustering_result:
                result["clustering"] = clustering_result
                
            # 3. Важность признаков
            feature_importance = await self._calculate_feature_importance(df)
            if feature_importance:
                result["feature_importance"] = feature_importance
                
            # 4. Если есть временной ряд, сделаем прогнозирование
            date_columns = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
            numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
            
            if date_columns and numeric_columns:
                forecasting_result = await self._forecast_time_series(df, date_columns[0], numeric_columns[0])
                if forecasting_result:
                    result["forecasting"] = forecasting_result
                    
            # Если не удалось выполнить ML-анализ
            if not result:
                return {
                    "error": "Could not perform ML analysis on provided data",
                    "reason": "Data format not suitable for ML analysis"
                }
                
            return result
            
        except Exception as e:
            logger.error(f"Error in ML file analysis: {e}")
            return {"error": str(e)}
            
    async def _detect_anomalies(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Обнаруживает аномалии в данных с помощью Isolation Forest
        """
        try:
            # Выбираем только числовые столбцы
            numeric_df = df.select_dtypes(include=['number']).dropna()
            
            if numeric_df.empty or len(numeric_df.columns) < 2:
                return None
                
            # Нормализуем данные
            scaled_data = self.scaler.fit_transform(numeric_df)
            
            # Применяем Isolation Forest
            iso_forest = IsolationForest(
                contamination=0.05,  # Ожидаем 5% аномалий
                random_state=42
            )
            
            # Предсказываем аномалии
            anomalies = iso_forest.fit_predict(scaled_data)
            
            # Индексы аномалий (где значение -1)
            anomaly_indices = np.where(anomalies == -1)[0]
            
            # Формируем результат
            anomaly_records = []
            for idx in anomaly_indices[:10]:  # Возвращаем только первые 10 аномалий
                anomaly_records.append({
                    "index": int(idx),
                    "anomaly_score": float(iso_forest.decision_function([scaled_data[idx]])[0]),
                    "values": {col: float(numeric_df.iloc[idx][col]) for col in numeric_df.columns}
                })
            
            return {
                "total_records": len(numeric_df),
                "anomaly_count": len(anomaly_indices),
                "anomaly_percentage": len(anomaly_indices) / len(numeric_df) * 100,
                "top_anomalies": anomaly_records
            }
            
        except Exception as e:
            logger.error(f"Error in anomaly detection: {e}")
            return None
            
    async def _cluster_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Кластеризует данные с помощью KMeans
        """
        try:
            # Выбираем только числовые столбцы
            numeric_df = df.select_dtypes(include=['number']).dropna()
            
            if numeric_df.empty or len(numeric_df.columns) < 2 or len(numeric_df) < 30:
                return None
                
            # Нормализуем данные
            scaled_data = self.scaler.fit_transform(numeric_df)
            
            # Определяем оптимальное количество кластеров (до 10)
            max_clusters = min(10, len(numeric_df) // 5)  # Не более 10 кластеров и не менее 5 точек в кластере
            
            # Применяем K-means с оптимальным числом кластеров
            kmeans = KMeans(n_clusters=max_clusters, random_state=42)
            cluster_labels = kmeans.fit_predict(scaled_data)
            
            # Определяем центры кластеров
            cluster_centers = kmeans.cluster_centers_
            
            # Формируем результат
            cluster_info = []
            for i in range(max_clusters):
                cluster_indices = np.where(cluster_labels == i)[0]
                cluster_info.append({
                    "cluster_id": i,
                    "size": int(len(cluster_indices)),
                    "percentage": float(len(cluster_indices) / len(numeric_df) * 100),
                    "center": {col: float(cluster_centers[i][j]) for j, col in enumerate(numeric_df.columns)}
                })
            
            return {
                "clusters_count": max_clusters,
                "cluster_info": cluster_info
            }
            
        except Exception as e:
            logger.error(f"Error in clustering: {e}")
            return None
            
    async def _calculate_feature_importance(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Вычисляет важность признаков с помощью RandomForest
        """
        try:
            # Выбираем только числовые столбцы
            numeric_df = df.select_dtypes(include=['number']).dropna()
            
            if numeric_df.empty or len(numeric_df.columns) < 2:
                return None
                
            # Выбираем случайную целевую переменную
            target_col = numeric_df.columns[-1]
            feature_cols = [col for col in numeric_df.columns if col != target_col]
            
            if not feature_cols:
                return None
                
            # Подготавливаем данные
            X = numeric_df[feature_cols].values
            y = numeric_df[target_col].values
            
            # Обучаем RandomForest
            rf = RandomForestRegressor(n_estimators=50, random_state=42)
            rf.fit(X, y)
            
            # Получаем важность признаков
            feature_importance = []
            for i, col in enumerate(feature_cols):
                feature_importance.append({
                    "feature": col,
                    "importance": float(rf.feature_importances_[i])
                })
                
            # Сортируем по важности
            feature_importance.sort(key=lambda x: x["importance"], reverse=True)
            
            return {
                "target_variable": target_col,
                "features": feature_importance
            }
            
        except Exception as e:
            logger.error(f"Error in feature importance calculation: {e}")
            return None
            
    async def _forecast_time_series(
        self, 
        df: pd.DataFrame, 
        date_col: str, 
        value_col: str, 
        forecast_days: int = 7
    ) -> Dict[str, Any]:
        """
        Прогнозирует временной ряд
        """
        try:
            # Проверяем, что указанные столбцы существуют
            if date_col not in df.columns or value_col not in df.columns:
                return None
                
            # Преобразуем дату в datetime
            try:
                df[date_col] = pd.to_datetime(df[date_col])
            except:
                return None
                
            # Формируем временной ряд
            ts_df = df[[date_col, value_col]].dropna().copy()
            ts_df = ts_df.sort_values(date_col)
            
            if len(ts_df) < 30:  # Требуется минимум 30 точек для прогноза
                return None
                
            # Добавляем признаки даты
            ts_df['day'] = ts_df[date_col].dt.day
            ts_df['month'] = ts_df[date_col].dt.month
            ts_df['year'] = ts_df[date_col].dt.year
            ts_df['dayofweek'] = ts_df[date_col].dt.dayofweek
            
            # Добавляем лаговые признаки
            for lag in range(1, 4):  # Лаги 1, 2, 3 дня
                ts_df[f'lag_{lag}'] = ts_df[value_col].shift(lag)
                
            # Добавляем скользящие средние
            ts_df['rolling_mean_7'] = ts_df[value_col].rolling(window=7).mean()
            
            # Удаляем строки с NaN
            ts_df = ts_df.dropna()
            
            # Готовим признаки и целевую переменную
            features = ['day', 'month', 'year', 'dayofweek', 
                        'lag_1', 'lag_2', 'lag_3', 'rolling_mean_7']
            
            X = ts_df[features].values
            y = ts_df[value_col].values
            
            # Разделяем на обучающую и тестовую выборки
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, shuffle=False, random_state=42
            )
            
            # Обучаем модель
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X_train, y_train)
            
            # Оцениваем качество модели
            train_score = model.score(X_train, y_train)
            test_score = model.score(X_test, y_test)
            
            # Готовим прогноз
            last_date = ts_df[date_col].max()
            forecast = []
            
            current_features = ts_df.iloc[-1][features].values.reshape(1, -1)
            
            for i in range(1, forecast_days + 1):
                next_date = last_date + timedelta(days=i)
                
                # Обновляем временные признаки
                current_features[0][0] = next_date.day
                current_features[0][1] = next_date.month
                current_features[0][2] = next_date.year
                current_features[0][3] = next_date.dayofweek
                
                # Предсказываем значение
                prediction = model.predict(current_features)[0]
                
                # Добавляем в прогноз
                forecast.append({
                    "date": next_date.isoformat(),
                    "value": float(prediction),
                    "confidence": float(train_score * test_score)  # Приблизительная оценка уверенности
                })
                
                # Обновляем признаки для следующего прогноза
                current_features[0][4] = prediction  # lag_1
                current_features[0][5] = current_features[0][4]  # lag_2
                current_features[0][6] = current_features[0][5]  # lag_3
                
                # Приблизительно обновляем скользящую среднюю
                current_features[0][7] = (current_features[0][7] * 6 + prediction) / 7
                
            return {
                "value_column": value_col,
                "date_column": date_col,
                "train_score": float(train_score),
                "test_score": float(test_score),
                "forecast_days": forecast_days,
                "forecast": forecast
            }
            
        except Exception as e:
            logger.error(f"Error in time series forecasting: {e}")
            return None


def get_ml_file_analytics_service(cache_service: CacheService = None) -> MLFileAnalyticsService:
    """
    Factory для сервиса анализа файлов
    """
    return MLFileAnalyticsService(cache_service=cache_service)
