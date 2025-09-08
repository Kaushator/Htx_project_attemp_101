#!/bin/bash

echo "🚀 Запуск HTX Trading MCP Server..."
echo "============================================"

# Переходим в папку проекта
cd "$(dirname "$0")/.."

# Активируем виртуальное окружение
source .venv_wsl/bin/activate

# Проверяем, что MCP установлен
python -c "import mcp; print('✅ MCP SDK доступен')" || {
    echo "❌ MCP SDK не найден. Устанавливаем..."
    pip install mcp
}

# Экспортируем PYTHONPATH для доступа к backend модулям
export PYTHONPATH="$PWD/backend:$PYTHONPATH"

# Проверяем доступность backend модулей
python -c "from app.services.htx_client_real import htx_client; print('✅ HTX Client доступен')" || {
    echo "❌ Не удается импортировать HTX Client"
    exit 1
}

echo "🔧 Настройки:"
echo "   PYTHONPATH: $PYTHONPATH"
echo "   Python: $(which python)"
echo "   Версия Python: $(python --version)"

echo "📡 Запуск MCP сервера..."
echo "   Сервер будет слушать на stdio"
echo "   Для подключения используйте mcp_config.json"

# Запускаем MCP сервер
python mcp_server/htx_mcp_server.py
