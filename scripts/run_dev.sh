#!/bin/bash

# HTX Project - Development Run Script

echo "🚀 Starting HTX Project in development mode..."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv .venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r backend/requirements.txt

# Copy environment file if it doesn't exist
if [ ! -f "backend/.env" ]; then
    echo "⚙️  Creating .env file from template..."
    cp backend/env.example backend/.env
    echo "⚠️  Please update backend/.env with your API keys!"
fi

# Create data directories
echo "📁 Creating data directories..."
mkdir -p data/raw data/processed data/samples

# Start the API
echo "🌐 Starting FastAPI server..."
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
