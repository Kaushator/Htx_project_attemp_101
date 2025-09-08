#!/usr/bin/env bash

# Скрипт для запуска Docker с PostgreSQL и переноса данных

set -e

echo "=== Настройка PostgreSQL для HTX Project ==="

# Проверяем Docker
if ! command -v docker >/dev/null 2>&1; then
    echo "Ошибка: Docker не установлен"
    exit 1
fi

echo "1. Запускаем PostgreSQL и Redis"
docker-compose up -d db redis

echo "2. Ожидаем готовность PostgreSQL (10 секунд)"
sleep 10

echo "3. Устанавливаем переменные окружения для миграции"
export PG_DATABASE_URL="postgresql+asyncpg://htx:htx@localhost:5432/htx"

echo "4. Запускаем миграцию данных"
cd backend
source ../.venv/bin/activate
python scripts/migrate_to_postgres.py

echo "5. Копируем PostgreSQL .env"
if [ -f ".env" ]; then
    cp .env .env.sqlite.bak
    echo "Создана резервная копия .env → .env.sqlite.bak"
fi
cp env.postgres .env
echo "Конфигурация для PostgreSQL скопирована в .env"

echo "6. Устанавливаем asyncpg"
pip install asyncpg

echo "=== Миграция завершена ==="
echo "Теперь вы можете запустить API с PostgreSQL:"
echo "cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 --loop uvloop --http httptools"
