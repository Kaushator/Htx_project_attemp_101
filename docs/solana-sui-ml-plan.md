# План интеграции и анализа Solana и Sui

## Цель
Расширить аналитические возможности HTX проекта за счет добавления инструментов для анализа блокчейнов Solana и Sui, включая ML-модели для прогнозирования и классификации.

## 1. Интеграция данных

### 1.1. Solana API
- Реализовать клиент для Solana JSON RPC API
- Добавить возможность получения данных о транзакциях, аккаунтах и токенах
- Интегрировать данные о стоимости газа и активности сети

```python
# Пример интеграции Solana API
from solana.rpc.api import Client as SolanaClient
from solana.publickey import PublicKey

async def fetch_solana_account(account_address: str):
    client = SolanaClient("https://api.mainnet-beta.solana.com")
    pubkey = PublicKey(account_address)
    return await client.get_account_info(pubkey)
```

### 1.2. Sui SDK
- Реализовать клиент для Sui RPC API
- Добавить получение данных о кошельках, объектах и транзакциях
- Интегрировать данные об NFT и других активах

```python
# Пример интеграции Sui API
import httpx

async def fetch_sui_objects(owner_address: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://fullnode.mainnet.sui.io/",
            json={"jsonrpc": "2.0", "method": "sui_getOwnedObjects", 
                  "params": [owner_address, None, None, True], "id": 1}
        )
        return response.json()
```

## 2. ML-модели для Solana и Sui

### 2.1. Анализ временных рядов
- Разработать модель LSTM/GRU для прогнозирования цен и активности
- Использовать данные об on-chain активности как входные признаки
- Интегрировать с существующим ML-сервисом

```python
# Структура модели для временных рядов
class SolanaTimeSeries:
    def __init__(self, lookback_period=14):
        self.lookback = lookback_period
        # Создание модели на базе PyTorch
        
    async def train(self, historical_data):
        # Обучение модели
        pass
        
    async def predict(self, recent_data):
        # Прогноз на основе последних данных
        pass
```

### 2.2. Классификация транзакций
- Разработать классификатор для типов транзакций в Solana и Sui
- Интегрировать с существующим функционалом анализа транзакций
- Добавить метрики и визуализацию для анализа

### 2.3. Обнаружение аномалий
- Реализовать алгоритмы обнаружения аномалий для выявления необычной активности
- Интегрировать с системой оповещений для отслеживания подозрительной активности

## 3. API для доступа к данным

### 3.1. REST API
- Добавить эндпоинты для получения данных Solana и Sui
- Интегрировать с существующим API

```python
# Пример FastAPI эндпоинтов
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.solana_service import get_solana_service

router = APIRouter()

@router.get("/solana/account/{address}")
async def get_solana_account(address: str, db: AsyncSession = Depends(get_db)):
    solana_service = get_solana_service()
    result = await solana_service.get_account_info(address)
    if not result:
        raise HTTPException(status_code=404, detail="Аккаунт не найден")
    return result
```

### 3.2. WebSocket API
- Реализовать WebSocket подключение для получения данных в реальном времени
- Интегрировать с существующей инфраструктурой

## 4. Интерфейс пользователя

### 4.1. Дашборд для Solana
- Добавить специализированный дашборд для аналитики Solana
- Включить графики активности, транзакций и взаимодействий с контрактами

### 4.2. Дашборд для Sui
- Разработать интерфейс для отображения аналитики Sui
- Включить визуализацию объектов, транзакций и активности

## 5. Модели данных

### 5.1. База данных
- Расширить существующие модели для хранения данных о Solana и Sui
- Добавить таблицы для хранения транзакций, аккаунтов и результатов анализа

```python
# Пример моделей SQLAlchemy
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from app.db.base_class import Base

class SolanaTransaction(Base):
    __tablename__ = "solana_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    signature = Column(String, unique=True, index=True)
    block_time = Column(DateTime)
    slot = Column(Integer)
    success = Column(Boolean)
    fee = Column(Float)
    transaction_data = Column(JSON)
    # Другие поля...
```

## 6. План внедрения

### 6.1. Фаза 1: Базовая интеграция (2 недели)
- Создание клиентов для API Solana и Sui
- Разработка основных моделей данных
- Создание базовых эндпоинтов API

### 6.2. Фаза 2: ML-модели (3 недели)
- Разработка и обучение ML-моделей
- Интеграция с существующей ML-инфраструктурой
- Тестирование и оптимизация моделей

### 6.3. Фаза 3: Интерфейс и визуализация (2 недели)
- Разработка дашбордов для анализа данных
- Интеграция с существующим UI
- Тестирование и оптимизация интерфейса

## 7. Требования к окружению

- WSL2 с поддержкой GPU для ML-моделей
- Python 3.9+ с библиотеками PyTorch, scikit-learn
- Расширение базы данных (PostgreSQL с pgvector рекомендуется)
- Клиентские библиотеки для Solana и Sui

## 8. Критерии успеха

- Успешная интеграция данных из Solana и Sui
- Работающие ML-модели с точностью > 70%
- Интерактивные дашборды для анализа данных
- Скорость выполнения запросов < 2 секунд
