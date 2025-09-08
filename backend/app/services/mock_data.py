"""
Предзагруженные данные для демонстрации
Избегаем зависания на внешних API
"""

MOCK_HEALTH_DATA = {
    "status": "healthy",
    "timestamp": "2025-08-30T12:00:00Z",
    "version": "1.0.0",
    "database": "connected",
    "api_status": "operational"
}

MOCK_TRADES_DATA = [
    {
        "id": 1,
        "symbol": "BTCUSDT",
        "side": "buy",
        "amount": 0.1,
        "price": 65000,
        "timestamp": "2025-08-30T10:00:00Z",
        "pnl": 150.50
    },
    {
        "id": 2,
        "symbol": "ETHUSDT", 
        "side": "sell",
        "amount": 2.5,
        "price": 3200,
        "timestamp": "2025-08-30T11:00:00Z",
        "pnl": -45.20
    },
    {
        "id": 3,
        "symbol": "ADAUSDT",
        "side": "buy", 
        "amount": 1000,
        "price": 0.35,
        "timestamp": "2025-08-30T09:30:00Z",
        "pnl": 25.75
    }
]

MOCK_BALANCE_DATA = {
    "total_balance": 10000.00,
    "available_balance": 8500.00,
    "frozen_balance": 1500.00,
    "total_pnl": 130.05,
    "daily_pnl": 25.30
}
