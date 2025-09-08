#!/bin/bash
# Скрипт для сборки и запуска MCP сервера в Docker (WSL2)
set -e

cd "$(dirname "$0")"

IMAGE_NAME="htx-mcp-server"
PORT=8003

# Сборка Docker-образа

echo "[1/3] Сборка Docker-образа..."
docker build -t $IMAGE_NAME .

echo "[2/3] Остановка старого контейнера (если есть)..."
docker stop $IMAGE_NAME 2>/dev/null || true

echo "[3/3] Запуск контейнера на порту $PORT..."
docker run --rm -d --name $IMAGE_NAME -p $PORT:$PORT $IMAGE_NAME

echo "Готово! MCP сервер доступен на http://localhost:$PORT/"
echo "Для логов: docker logs -f $IMAGE_NAME"
