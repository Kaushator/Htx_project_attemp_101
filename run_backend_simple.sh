#!/usr/bin/env bash
# Скрипт для запуска только бэкенда в WSL2

set -e

echo "🚀 HTX Backend - Запуск в WSL2"
echo "=============================="

# Цвета для вывода
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Переходим в корень проекта
cd "$(dirname "$0")"
PROJECT_ROOT=$(pwd)

# Остановка процессов
echo -e "${YELLOW}Останавливаем активные процессы бэкенда...${NC}"
pkill -f uvicorn || true
pkill -f "python.*run_backend_wsl.py" || true

# Активация виртуального окружения WSL2
echo -e "${BLUE}Активация виртуального окружения WSL2...${NC}"
if [ ! -d ".venv_wsl2" ]; then
    echo -e "${YELLOW}Создаем виртуальное окружение WSL2...${NC}"
    python -m venv .venv_wsl2
fi

source .venv_wsl2/bin/activate

# Проверка зависимостей
echo -e "${BLUE}Установка базовых зависимостей...${NC}"
pip install fastapi uvicorn sqlalchemy httpx

# Запуск бэкенда напрямую
echo -e "${GREEN}Запуск бэкенда...${NC}"
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8004 --reload
