#!/usr/bin/env bash
# filepath: scripts/test_ml_endpoints.sh

set -eo pipefail

echo "🧪 Тестирование ML-эндпоинтов HTX Project"
echo "========================================"

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Проверка, запущен ли бэкенд
echo -e "${BLUE}Проверка доступности бэкенда...${NC}"
if ! curl -s http://localhost:8004/api/v1/health | grep -q "healthy"; then
    echo -e "${RED}✗ Бэкенд не запущен. Запустите его командой ./start_wsl2.sh${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Бэкенд доступен${NC}"

# Базовый URL API
BASE_URL="http://localhost:8004/api/v1"

# Функция для тестирования эндпоинта
test_endpoint() {
    local method=$1
    local endpoint=$2
    local data=$3
    local description=$4
    
    echo -e "\n${YELLOW}Тестирование: ${description}${NC}"
    echo -e "${BLUE}${method} ${endpoint}${NC}"
    
    if [ "$method" == "GET" ]; then
        response=$(curl -s -X GET "${BASE_URL}${endpoint}")
    else
        response=$(curl -s -X ${method} "${BASE_URL}${endpoint}" \
            -H "Content-Type: application/json" \
            -d "${data}")
    fi
    
    # Проверка на ошибки
    if echo "$response" | grep -q "error"; then
        echo -e "${RED}✗ Ошибка:${NC}"
        echo "$response" | jq || echo "$response"
    else
        echo -e "${GREEN}✓ Успешный ответ:${NC}"
        echo "$response" | jq || echo "$response"
    fi
}

# 1. Тест базовых метрик риска
test_endpoint "GET" "/ml/risk-metrics?symbol=BTC&days_lookback=30" "" "Расширенные метрики риска"

# 2. Тест анализа рыночных настроений
sentiment_data='{"symbol": "BTC", "period": "daily"}'
test_endpoint "POST" "/ml/analysis/market-sentiment" "$sentiment_data" "Анализ рыночных настроений"

# 3. Тест планирования экспериментов
experiment_data='{
  "experiment_description": "Анализ волатильности Solana",
  "available_data": {"symbols": ["SOL"], "timeframe": "1h", "period": "30d"},
  "constraints": {"execution_time": "fast"}
}'
test_endpoint "POST" "/ml/plan" "$experiment_data" "Планирование ML-эксперимента"

# 4. Тест поиска по сходству
similarity_data='{
  "query_text": "резкое падение цены",
  "collection": "market_events",
  "top_k": 5
}'
test_endpoint "POST" "/ml/similarity-search" "$similarity_data" "Поиск по сходству"

echo -e "\n${GREEN}Тестирование ML-эндпоинтов завершено${NC}"
echo -e "${BLUE}Проверьте логи в logs/wsl2_backend_*.log для дополнительной информации${NC}"
