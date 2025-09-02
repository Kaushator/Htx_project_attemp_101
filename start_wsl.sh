#!/bin/bash

echo "🚀 Starting HTX Project in WSL..."

# Go to project directory
cd /mnt/e/Htx_project_attemp_101

# Kill existing processes
echo "🛑 Stopping existing processes..."
pkill -f uvicorn 2>/dev/null || true
pkill -f node 2>/dev/null || true
sleep 2

# Activate virtual environment
source .venv_wsl/bin/activate

# Start backend
echo "📦 Starting Backend..."
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8004 --reload &
BACKEND_PID=$!
cd ..

# Wait for backend to start
echo "⏳ Waiting for backend..."
sleep 10

# Start frontend
echo "🎨 Starting Frontend..."
cd frontend
npm run dev -- --host 0.0.0.0 --port 3000 &
FRONTEND_PID=$!
cd ..

echo "✅ Services started:"
echo "   Backend: http://localhost:8004 (PID: $BACKEND_PID)"
echo "   Frontend: http://localhost:3000 (PID: $FRONTEND_PID)"
echo "   API Docs: http://localhost:8004/docs"

echo "Press Ctrl+C to stop services..."
wait
