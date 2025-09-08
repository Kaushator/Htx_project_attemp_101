#!/usr/bin/env python3
"""
Тестовый клиент для HTX MCP сервера
"""

import asyncio
import json
import subprocess
import sys

async def test_mcp_server():
    """Тестирует MCP сервер через subprocess"""
    
    # Команда для запуска MCP сервера
    cmd = [
        "wsl", "-d", "Ubuntu", "--", "bash", "-c",
        "cd /mnt/e/Htx_project_attemp_101 && source .venv_wsl/bin/activate && "
        "export PYTHONPATH=/mnt/e/Htx_project_attemp_101/backend:$PYTHONPATH && "
        "python mcp_server/htx_mcp_server.py"
    ]
    
    # Запускаем процесс
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    # Тестовые запросы
    test_requests = [
        # Инициализация
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"}
            }
        },
        # Список инструментов
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        },
        # Тест get_htx_ticker
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "get_htx_ticker",
                "arguments": {"symbol": "btcusdt"}
            }
        }
    ]
    
    try:
        for i, request in enumerate(test_requests):
            print(f"\n🔄 Отправка запроса {i+1}: {request['method']}")
            
            # Отправляем запрос
            request_str = json.dumps(request) + "\n"
            process.stdin.write(request_str.encode())
            await process.stdin.drain()
            
            # Читаем ответ
            response_line = await process.stdout.readline()
            if response_line:
                response = json.loads(response_line.decode().strip())
                print(f"✅ Ответ: {json.dumps(response, indent=2, ensure_ascii=False)}")
            else:
                print("❌ Нет ответа от сервера")
                break
                
        # Завершаем процесс
        process.terminate()
        await process.wait()
        
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        process.terminate()

def main():
    """Основная функция"""
    print("🧪 Тестирование HTX MCP Server")
    print("=" * 40)
    
    try:
        asyncio.run(test_mcp_server())
    except KeyboardInterrupt:
        print("\n🛑 Тестирование прервано пользователем")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    main()
