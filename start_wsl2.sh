#!/usr/bin/env bash
# filepath: start_wsl2.sh

set -eo pipefail

echo "🚀 HTX Project - Запуск в WSL2"
echo "=============================="

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Переходим в корень проекта
cd "$(dirname "$0")"
PROJECT_ROOT=$(pwd)

# Остановка процессов
echo -e "${YELLOW}Останавливаем активные процессы...${NC}"
pkill -f uvicorn || true
pkill -f node || true
pkill -f "python.*run_backend_wsl.py" || true

# Активация виртуального окружения WSL2
echo -e "${BLUE}Активация виртуального окружения WSL2...${NC}"
if [ ! -d ".venv_wsl2" ]; then
    echo -e "${YELLOW}Создаем виртуальное окружение WSL2...${NC}"
    python3 -m venv .venv_wsl2
fi

source .venv_wsl2/bin/activate

# Проверка зависимостей
echo -e "${BLUE}Проверка зависимостей...${NC}"
pip install -r backend/requirements.txt
pip install scikit-learn pandas redis aiohttp --quiet

# Запуск бэкенда
echo -e "${GREEN}Запуск бэкенда...${NC}"
python3 run_backend_wsl.py &
BACKEND_PID=$!

# Запуск фронтенда
echo -e "${GREEN}Запуск фронтенда...${NC}"
cd frontend
# Устанавливаем таймаут для npm install
timeout 60 npm install || echo -e "${YELLOW}Установка фронтенд-зависимостей превысила таймаут, но мы продолжим...${NC}"
# Запускаем фронтенд
timeout 10 npm run dev &
FRONTEND_PID=$!

cd "$PROJECT_ROOT"

# Проверка статуса
echo -e "${BLUE}Ожидание запуска сервисов...${NC}"
sleep 5

# Проверка бэкенда
echo -e "${BLUE}Проверка бэкенда...${NC}"
if curl -s http://localhost:8004/api/v1/health | grep -q "healthy"; then
    echo -e "${GREEN}✓ Бэкенд работает: http://localhost:8004${NC}"
else
    echo -e "${RED}✗ Бэкенд не отвечает${NC}"
fi

# Проверка фронтенда
echo -e "${BLUE}Проверка фронтенда...${NC}"
if curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 | grep -q "200"; then
    echo -e "${GREEN}✓ Фронтенд работает: http://localhost:3000${NC}"
else
    echo -e "${RED}✗ Фронтенд не отвечает${NC}"
fi

echo -e "${GREEN}Запуск завершен! Сервисы работают в фоновом режиме.${NC}"
echo -e "${YELLOW}Для остановки: pkill -f uvicorn; pkill -f node${NC}"

# Вывод информации о процессах
ps aux | grep -E 'uvicorn|node' | grep -v grep
