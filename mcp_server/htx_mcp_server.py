#!/usr/bin/env python3
"""
HTX Trading MCP Server

Предоставляет инструменты для работы с HTX API через Model Context Protocol (MCP).
"""

import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.server.session import ServerSession
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequestParams,
    Tool,
    TextContent,
    ErrorCode,
    McpError,
)

# Добавляем путь к нашему backend
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

try:
    from app.services.htx_client_real import htx_client
    from app.core.config import settings
except ImportError as e:
    print(f"Ошибка импорта: {e}", file=sys.stderr)
    print("Убедитесь, что backend зависимости установлены", file=sys.stderr)
    sys.exit(1)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создаем MCP сервер
server = Server("htx-trading")

# Список доступных инструментов
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
        description="Получить тикер для торговой пары",
        inputSchema={
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Символ торговой пары (например: btcusdt)"
                }
            },
            "required": ["symbol"]
        }
    ),
    Tool(
        name="get_htx_currencies",
        description="Получить список всех доступных валют HTX",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": []
        }
    ),
    Tool(
        name="get_htx_symbols",
        description="Получить список всех торговых пар HTX",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": []
        }
    ),
    Tool(
        name="get_htx_trades",
        description="Получить историю торгов HTX",
        inputSchema={
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Символ торговой пары (например: btcusdt)"
                },
                "limit": {
                    "type": "integer",
                    "description": "Максимальное количество записей (по умолчанию 100)",
                    "minimum": 1,
                    "maximum": 2000
                }
            },
            "required": ["symbol"]
        }
    ),
    Tool(
        name="get_htx_klines",
        description="Получить данные свечей (klines) HTX",
        inputSchema={
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Символ торговой пары (например: btcusdt)"
                },
                "period": {
                    "type": "string",
                    "description": "Период свечей (1min, 5min, 15min, 30min, 60min, 4hour, 1day, 1week, 1mon, 1year)",
                    "enum": ["1min", "5min", "15min", "30min", "60min", "4hour", "1day", "1week", "1mon", "1year"]
                },
                "size": {
                    "type": "integer",
                    "description": "Количество свечей (по умолчанию 150)",
                    "minimum": 1,
                    "maximum": 2000
                }
            },
            "required": ["symbol", "period"]
        }
    )
]

@server.list_tools()
async def list_tools() -> ListToolsResponseSchema:
    """Возвращает список доступных инструментов."""
    return ListToolsResponseSchema(tools=TOOLS)

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> ToolResponseSchema:
    """Выполняет вызов инструмента."""
    logger.info(f"Вызов инструмента: {name} с аргументами: {arguments}")
    
    try:
        if name == "get_htx_balance":
            result = await htx_client.get_account_balance()
            return ToolResponseSchema(
                content=[{"type": "text", "text": json.dumps(result, indent=2, ensure_ascii=False)}]
            )
        
        elif name == "get_htx_ticker":
            symbol = arguments.get("symbol", "btcusdt")
            result = await htx_client.get_ticker(symbol)
            return ToolResponseSchema(
                content=[{"type": "text", "text": json.dumps(result, indent=2, ensure_ascii=False)}]
            )
        
        elif name == "get_htx_currencies":
            result = await htx_client.get_currencies()
            return ToolResponseSchema(
                content=[{"type": "text", "text": json.dumps(result, indent=2, ensure_ascii=False)}]
            )
        
        elif name == "get_htx_symbols":
            result = await htx_client.get_symbols()
            return ToolResponseSchema(
                content=[{"type": "text", "text": json.dumps(result, indent=2, ensure_ascii=False)}]
            )
        
        elif name == "get_htx_trades":
            symbol = arguments.get("symbol", "btcusdt")
            limit = arguments.get("limit", 100)
            result = await htx_client.get_order_history(symbol, limit)
            return ToolResponseSchema(
                content=[{"type": "text", "text": json.dumps(result, indent=2, ensure_ascii=False)}]
            )
        
        elif name == "get_htx_klines":
            symbol = arguments.get("symbol", "btcusdt")
            period = arguments.get("period", "1day")
            size = arguments.get("size", 150)
            result = await htx_client.get_klines(symbol, period, size)
            return ToolResponseSchema(
                content=[{"type": "text", "text": json.dumps(result, indent=2, ensure_ascii=False)}]
            )
        
        else:
            return ToolResponseSchema(
                content=[{"type": "text", "text": f"Неизвестный инструмент: {name}"}],
                isError=True
            )
    
    except Exception as e:
        logger.error(f"Ошибка при выполнении {name}: {e}")
        return ToolResponseSchema(
            content=[{"type": "text", "text": f"Ошибка: {str(e)}"}],
            isError=True
        )

async def main():
    """Основная функция для запуска MCP сервера."""
    logger.info("Запуск HTX Trading MCP Server...")
    
    # Проверяем настройки HTX
    if not settings.HTX_API_KEY or not settings.HTX_SECRET_KEY:
        logger.warning("HTX API ключи не настроены. Некоторые функции могут быть недоступны.")
    
    # Запускаем сервер через stdio
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream=read_stream,
            write_stream=write_stream,
            initialization_options={}
        )

if __name__ == "__main__":
    asyncio.run(main())
