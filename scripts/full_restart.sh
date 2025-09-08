#!/usr/bin/env bash

set -eo pipefail

echo "🚀 HTX Project - Полный перезапуск и тестирование"
echo "=================================================="

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для логирования
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Функция для проверки health endpoint
check_health() {
    local url="$1"
    local service_name="$2"
    local max_attempts=10
    local attempt=1
    
    log_info "Проверяем здоровье $service_name ($url)..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s -f "$url" > /dev/null 2>&1; then
            local response=$(curl -s "$url")
            log_success "$service_name работает! Ответ: $response"
            return 0
        fi
        
        log_warning "Попытка $attempt/$max_attempts не удалась, ждем 2 сек..."
        sleep 2
        ((attempt++))
    done
    
    log_error "$service_name не отвечает после $max_attempts попыток!"
    return 1
}

# Функция для проверки процесса
check_process() {
    local process_name="$1"
    if pgrep -f "$process_name" > /dev/null; then
        log_success "Процесс $process_name запущен (PID: $(pgrep -f "$process_name"))"
        return 0
    else
        log_error "Процесс $process_name НЕ запущен!"
        return 1
    fi
}

# 1. ОСТАНОВКА ВСЕХ ПРОЦЕССОВ
log_info "Шаг 1/6: Остановка всех процессов..."
pkill -f uvicorn || true
pkill -f node || true
pkill -f python.*mcp || true
sleep 2
log_success "Все процессы остановлены"

# 2. ПРОВЕРКА ОКРУЖЕНИЯ
log_info "Шаг 2/6: Проверка WSL окружения..."

# Проверяем Python
if command -v python3 >/dev/null 2>&1; then
    PY=python3
else
    PY=python
fi

# Активируем виртуальное окружение
if [ ! -f ".venv_wsl/bin/activate" ]; then
    log_error "Виртуальное окружение .venv_wsl не найдено!"
    exit 1
fi

source .venv_wsl/bin/activate
log_success "Виртуальное окружение активировано (Python: $($PY --version))"

# 3. УСТАНОВКА MCP И ЗАВИСИМОСТЕЙ
log_info "Шаг 3/6: Установка зависимостей..."

# Проверяем и устанавливаем MCP
if ! $PY -c "import mcp" 2>/dev/null; then
    log_warning "MCP SDK не найден, устанавливаем..."
    pip install mcp
fi

# Проверяем и устанавливаем aiohttp
if ! $PY -c "import aiohttp" 2>/dev/null; then
    log_warning "aiohttp не найден, устанавливаем..."
    pip install aiohttp
fi

log_success "Все зависимости установлены"

# 4. ЗАПУСК СЕРВИСОВ
log_info "Шаг 4/6: Запуск сервисов..."

# Настраиваем PYTHONPATH
export PYTHONPATH="${PWD}/backend:${PYTHONPATH:-}"

# Запускаем backend
log_info "Запускаем backend (порт 8004)..."
cd backend
nohup $PY -m uvicorn app.main:app --host 0.0.0.0 --port 8004 --reload > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
cd ..
log_success "Backend запущен (PID: $BACKEND_PID)"

# Ждем запуска backend
sleep 5

# Запускаем frontend
log_info "Запускаем frontend (порт 3000)..."
cd frontend
nohup npm run dev -- --host 0.0.0.0 --port 3000 > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
log_success "Frontend запущен (PID: $FRONTEND_PID)"

# Ждем запуска frontend
sleep 5

# 5. ТЕСТИРОВАНИЕ ЗДОРОВЬЯ
log_info "Шаг 5/6: Тестирование здоровья сервисов..."

# Создаем папку для логов
mkdir -p logs

# Тестируем backend
if check_health "http://localhost:8004/api/v1/health" "Backend"; then
    BACKEND_OK=true
else
    BACKEND_OK=false
fi

# Тестируем frontend
if check_health "http://localhost:3000" "Frontend"; then
    FRONTEND_OK=true
else
    FRONTEND_OK=false
fi

# Тестируем HTX API
log_info "Тестируем HTX API интеграцию..."
if htx_response=$(curl -s "http://localhost:8004/api/v1/htx/ticker/btcusdt" 2>/dev/null); then
    if echo "$htx_response" | grep -q "price"; then
        btc_price=$(echo "$htx_response" | grep -o '"price":"[^"]*"' | cut -d'"' -f4)
        log_success "HTX API работает! BTC цена: \$$btc_price"
        HTX_OK=true
    else
        log_error "HTX API отвечает, но данные некорректные: $htx_response"
        HTX_OK=false
    fi
else
    log_error "HTX API недоступен"
    HTX_OK=false
fi

# Тестируем загрузку файлов
log_info "Тестируем endpoints загрузки файлов..."
if files_response=$(curl -s "http://localhost:8004/api/v1/files/" 2>/dev/null); then
    log_success "Files API работает"
    FILES_OK=true
else
    log_error "Files API недоступен"
    FILES_OK=false
fi

# 6. ИТОГОВЫЙ ОТЧЕТ
log_info "Шаг 6/6: Итоговый отчет состояния..."

echo "=================================================="
echo "🎯 ИТОГОВЫЙ ОТЧЕТ HTX PROJECT"
echo "=================================================="

echo "📊 Статус сервисов:"
if [ "$BACKEND_OK" = true ]; then
    echo "  ✅ Backend (FastAPI): http://localhost:8004"
else
    echo "  ❌ Backend (FastAPI): НЕДОСТУПЕН"
fi

if [ "$FRONTEND_OK" = true ]; then
    echo "  ✅ Frontend (React): http://localhost:3000"
else
    echo "  ❌ Frontend (React): НЕДОСТУПЕН"
fi

echo ""
echo "🔌 API интеграции:"
if [ "$HTX_OK" = true ]; then
    echo "  ✅ HTX API: Работает (BTC: \$$btc_price)"
else
    echo "  ❌ HTX API: НЕ РАБОТАЕТ"
fi

if [ "$FILES_OK" = true ]; then
    echo "  ✅ Files API: Работает"
else
    echo "  ❌ Files API: НЕ РАБОТАЕТ"
fi

echo ""
echo "📋 Полезные ссылки:"
echo "  🏠 Главная: http://localhost:3000"
echo "  📖 API Docs: http://localhost:8004/docs"
echo "  ❤️  Health: http://localhost:8004/api/v1/health"
echo "  💰 HTX Balance: http://localhost:8004/api/v1/htx/balance"

echo ""
echo "📁 Логи:"
echo "  📜 Backend: logs/backend.log"
echo "  📜 Frontend: logs/frontend.log"

echo ""
echo "🔧 Управление:"
echo "  Остановить все: pkill -f uvicorn; pkill -f node"
echo "  Перезапустить: ./scripts/full_restart.sh"

# Финальная проверка
if [ "$BACKEND_OK" = true ] && [ "$FRONTEND_OK" = true ] && [ "$HTX_OK" = true ]; then
    echo ""
    log_success "🎉 ВСЕ СИСТЕМЫ РАБОТАЮТ! Проект готов к использованию!"
    exit 0
else
    echo ""
    log_error "⚠️  ЕСТЬ ПРОБЛЕМЫ! Проверьте логи для диагностики."
    exit 1
fi
