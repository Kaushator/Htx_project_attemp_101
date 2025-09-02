#!/usr/bin/env python3
"""
HTX Trading MCP Server - Простой и рабочий MCP сервер для HTX API
"""

import asyncio
import json
import sys
import traceback
from typing import Any, Dict, List

# Импорты MCP
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        Tool,
        TextContent,
    )
except ImportError as e:
    print(f"❌ Ошибка импорта MCP: {e}")
    print("💡 Установите MCP SDK: pip install mcp")
    sys.exit(1)

# Настройка путей для импорта backend компонентов
import os
backend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend')
sys.path.insert(0, backend_path)

# Импорты backend компонентов
try:
    from app.services.htx_client_real import htx_client
    from app.core.config import settings
except ImportError as e:
    print(f"❌ Ошибка импорта backend: {e}")
    print("💡 Проверьте, что backend настроен правильно")
    # Продолжаем без backend для тестирования
    htx_client = None
    settings = None

# Определяем доступные инструменты
TOOLS = [
    Tool(
        name="get_htx_balance",
        description="Получить баланс аккаунта HTX",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": []
        }
    ),
    Tool(
        name="get_htx_ticker",
        description="Получить тикер цены для криптовалютной пары",
        inputSchema={
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Символ пары (например: btcusdt)"
                }
            },
            "required": ["symbol"]
        }
    ),
    Tool(
        name="get_htx_currencies",
        description="Получить список всех доступных валют на HTX",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": []
        }
    ),
    Tool(
        name="get_htx_symbols",
        description="Получить список всех торговых пар на HTX",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": []
        }
    ),
    Tool(
        name="get_htx_trades",
        description="Получить историю сделок HTX",
        inputSchema={
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Символ пары (необязательно)"
                },
                "limit": {
                    "type": "integer",
                    "description": "Лимит записей (по умолчанию: 100)"
                }
            },
            "required": []
        }
    )
]

# Создаем MCP сервер
app = Server("htx-trading-server")

@app.list_tools()
async def list_tools() -> List[Tool]:
    """Возвращает список доступных инструментов"""
    return TOOLS

@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Обрабатывает вызов инструмента"""
    
    if htx_client is None:
        return [TextContent(
            type="text",
            text="❌ HTX клиент недоступен. Проверьте настройки backend."
        )]
    
    try:
        if name == "get_htx_balance":
            result = await htx_client.get_account_balance()
            return [TextContent(
                type="text",
                text=f"💰 Баланс HTX:\n{json.dumps(result, ensure_ascii=False, indent=2)}"
            )]
            
        elif name == "get_htx_ticker":
            symbol = arguments.get("symbol", "btcusdt")
            result = await htx_client.get_ticker(symbol)
            return [TextContent(
                type="text",
                text=f"📈 Тикер {symbol.upper()}:\n{json.dumps(result, ensure_ascii=False, indent=2)}"
            )]
            
        elif name == "get_htx_currencies":
            result = await htx_client.get_currencies()
            currency_count = len(result) if isinstance(result, list) else "неизвестно"
            return [TextContent(
                type="text",
                text=f"💱 Валюты HTX (всего: {currency_count}):\n{json.dumps(result, ensure_ascii=False, indent=2)}"
            )]
            
        elif name == "get_htx_symbols":
            result = await htx_client.get_symbols()
            symbols_count = len(result) if isinstance(result, list) else "неизвестно"
            return [TextContent(
                type="text",
                text=f"📊 Торговые пары HTX (всего: {symbols_count}):\n{json.dumps(result, ensure_ascii=False, indent=2)}"
            )]
            
        elif name == "get_htx_trades":
            symbol = arguments.get("symbol")
            limit = arguments.get("limit", 100)
            result = await htx_client.get_order_history(symbol=symbol, limit=limit)
            return [TextContent(
                type="text",
                text=f"📋 История сделок HTX:\n{json.dumps(result, ensure_ascii=False, indent=2)}"
            )]
            
        else:
            return [TextContent(
                type="text",
                text=f"❌ Неизвестный инструмент: {name}"
            )]
            
    except Exception as e:
        error_msg = f"❌ Ошибка выполнения {name}: {str(e)}\n{traceback.format_exc()}"
        return [TextContent(
            type="text",
            text=error_msg
        )]

async def main():
    """Основная функция запуска MCP сервера"""
    print("🚀 Запуск HTX Trading MCP Server...")
    print(f"📋 Доступные инструменты: {len(TOOLS)}")
    
    for tool in TOOLS:
        print(f"  - {tool.name}: {tool.description}")
    
    if htx_client is None:
        print("⚠️  HTX клиент недоступен - работаем в режиме тестирования")
    else:
        print("✅ HTX клиент подключен")
    
    # Запускаем stdio сервер
    async with stdio_server() as streams:
        await app.run(streams[0], streams[1], app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
