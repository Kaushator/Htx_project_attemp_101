#!/bin/bash

# HTX Project - WSL/Linux Environment Setup Script
# This script sets up the development environment for WSL and Linux

set -e

echo "🚀 Setting up HTX Project environment for WSL/Linux..."

# Check if we're in the right directory
if [ ! -f "README.md" ] || [ ! -d "backend" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
python -m pip install --upgrade pip

# Install backend dependencies
if [ -f "backend/requirements.txt" ]; then
    echo "📥 Installing backend dependencies..."
    pip install -r backend/requirements.txt
fi

# Install development dependencies
if [ -f "backend/requirements-dev.txt" ]; then
    echo "📥 Installing development dependencies..."
    pip install -r backend/requirements-dev.txt
fi

# Create environment file if it doesn't exist
if [ ! -f "backend/.env" ] && [ -f "backend/env.example" ]; then
    echo "⚙️  Creating .env file from template..."
    cp backend/env.example backend/.env
    echo "⚠️  Please update backend/.env with your API keys!"
fi

# Create data directories
echo "📁 Creating data directories..."
mkdir -p data/{raw,processed,samples} logs

# Make scripts executable
echo "🔧 Making scripts executable..."
chmod +x scripts/*.sh 2>/dev/null || true

echo "✅ Environment setup complete!"
echo "📝 To activate the environment, run: source .venv/bin/activate"
echo "🌐 To start the API server, run: cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8004"