# MCP Python Example Server

Этот проект — минимальный MCP сервер на Python для отладки и расширения.

- Использует официальный Python SDK MCP: https://github.com/modelcontextprotocol/python-sdk
- Пример сервера реализует один MCP tool (echo).
- Для запуска требуется Python 3.10+ и пакет mcp[cli].

## Быстрый старт

1. Установите зависимости:
   ```sh
   pip install "mcp[cli]"
   ```
2. Запустите сервер:
   ```sh
   python server.py
   ```

## MCP спецификация и документация
- https://modelcontextprotocol.io/quickstart/server
- https://github.com/modelcontextprotocol/python-sdk
