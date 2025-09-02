#!/bin/bash
# HTX Trading Project - Quick Start Script
# Запуск полного приложения (backend + frontend)

echo "🚀 HTX Trading Project - Starting Application..."
echo "================================================"

# Проверяем, что мы в правильной директории
if [ ! -f "backend/app/main.py" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Функция для остановки процессов при выходе
cleanup() {
    echo "🛑 Stopping services..."
    pkill -f uvicorn
    pkill -f vite
    exit
}

# Устанавливаем обработчик сигнала
trap cleanup SIGINT SIGTERM

# Запускаем backend
echo "📦 Starting Backend (FastAPI)..."
cd backend
source ../.venv_wsl/bin/activate
ENABLE_BACKGROUND_TASKS=false uvicorn app.main:app --host 0.0.0.0 --port 8004 --reload &
BACKEND_PID=$!

# Ждем, пока backend запустится
echo "⏳ Waiting for backend to start..."
sleep 5

# Проверяем backend
if curl -s http://localhost:8004/api/v1/health > /dev/null; then
    echo "✅ Backend is running on http://localhost:8004"
else
    echo "❌ Backend failed to start"
    exit 1
fi

# Запускаем frontend
cd ../frontend
echo "🎨 Starting Frontend (React + Vite)..."
npm run dev -- --host 0.0.0.0 --port 3000 &
FRONTEND_PID=$!

# Ждем, пока frontend запустится
echo "⏳ Waiting for frontend to start..."
sleep 5

# Проверяем frontend
if curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 | grep -q "200"; then
    echo "✅ Frontend is running on http://localhost:3000"
else
    echo "❌ Frontend failed to start"
    exit 1
fi

echo ""
echo "🎉 HTX Trading Project is now running!"
echo "======================================"
echo "📊 Frontend: http://localhost:3000"
echo "🔧 Backend:  http://localhost:8004"
echo "📖 API Docs: http://localhost:8004/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Ожидаем
wait
