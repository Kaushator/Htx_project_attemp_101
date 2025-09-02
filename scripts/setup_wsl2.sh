#!/bin/bash
# Скрипт настройки и установки зависимостей в WSL2

set -e

echo "===== Настройка WSL2 для HTX Project ====="

# Проверка WSL2
WSL_VERSION=$(uname -a | grep -q "microsoft-standard-WSL2" && echo "2" || echo "1")
if [ "$WSL_VERSION" != "2" ]; then
    echo "⚠️ Обнаружен WSL1. Рекомендуется обновиться до WSL2."
    echo "   Выполните в PowerShell: wsl --set-version Ubuntu 2"
    read -p "Продолжить с WSL1? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Проверка текущей директории
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
PROJECT_ROOT=$(dirname "$SCRIPT_DIR")

echo "📂 Корневая директория проекта: $PROJECT_ROOT"

# Создание виртуального окружения WSL2
if [ ! -d "$PROJECT_ROOT/.venv_wsl2" ]; then
    echo "🔧 Создание виртуального окружения WSL2..."
    python3 -m venv "$PROJECT_ROOT/.venv_wsl2"
fi

# Активация виртуального окружения
source "$PROJECT_ROOT/.venv_wsl2/bin/activate"

# Установка зависимостей
echo "📦 Установка зависимостей..."
pip install --upgrade pip
pip install -r "$PROJECT_ROOT/requirements.txt"
pip install scikit-learn pandas redis aiohttp

# Установка утилит для отладки
echo "🔍 Установка утилит для отладки..."
pip install ipython ptpython

# Настройка прав на скрипты
echo "🔑 Настройка прав на скрипты..."
chmod +x "$PROJECT_ROOT/start_wsl2.sh"
chmod +x "$PROJECT_ROOT/scripts/"*.sh

# Проверка подключения к базе данных
echo "🔍 Проверка подключения к базе данных..."
python -c "
import os, sys
sys.path.append('$PROJECT_ROOT')
os.environ['DATABASE_URL'] = 'sqlite:///$PROJECT_ROOT/data/app.db'
try:
    from sqlalchemy import create_engine
    from sqlalchemy.ext.asyncio import create_async_engine
    print('✅ SQLAlchemy импортирован успешно')
    engine = create_engine('sqlite:///$PROJECT_ROOT/data/app.db')
    print('✅ Подключение к базе данных успешно')
except Exception as e:
    print(f'❌ Ошибка: {e}')
    sys.exit(1)
"

echo "✅ Настройка WSL2 завершена успешно!"
echo "   Для запуска проекта выполните: $PROJECT_ROOT/start_wsl2.sh"
