#!/usr/bin/env bash

# Скрипт для обновления docker-compose.yml и запуска контейнеров

set -e

echo "=== Настройка PostgreSQL и Docker для HTX Project ==="

# Создаем обновленный docker-compose.yml
cat > docker-compose.yml << 'EOL'
version: "3.9"
services:
  api:
    build: ./backend
    env_file: ./backend/.env
    volumes:
      - ./backend/data:/app/data
      - ./backend/logs:/app/logs
    ports:
      - "8000:8000"
    command: ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
    depends_on:
      - db

  # PostgreSQL database
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: htx
      POSTGRES_USER: htx
      POSTGRES_PASSWORD: htx
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

  # Redis для фоновых задач
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  pgdata:
  redis_data:
EOL

echo "Обновлен docker-compose.yml"

# Проверяем Docker
if ! command -v docker-compose >/dev/null 2>&1; then
    echo "Ошибка: docker-compose не установлен"
    exit 1
fi

echo "Запускаем контейнеры..."
docker-compose up -d

echo "=== Настройка завершена ==="
echo "Контейнеры запущены в фоновом режиме"
echo "API доступен по адресу: http://localhost:8000"
echo "PostgreSQL доступен по адресу: localhost:5432"
echo "Redis доступен по адресу: localhost:6379"
