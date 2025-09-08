#!/bin/bash
# HTX Project Setup for WSL/Linux

set -e  # Exit on any error

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
echo "Setting up HTX Project in: $PROJECT_ROOT"

# Create and activate virtual environment
if [ ! -d "$PROJECT_ROOT/.venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$PROJECT_ROOT/.venv"
fi

echo "Activating virtual environment..."
source "$PROJECT_ROOT/.venv/bin/activate"

# Install backend dependencies
echo "Installing backend dependencies..."
cd "$PROJECT_ROOT/backend"
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
echo "Creating directories..."
mkdir -p "$PROJECT_ROOT/backend/data/raw"
mkdir -p "$PROJECT_ROOT/backend/data/processed"
mkdir -p "$PROJECT_ROOT/backend/logs"

# Initialize database
echo "Initializing database..."
cd "$PROJECT_ROOT/backend"
python -c "
import asyncio
from app.db.session import init_db

async def main():
    await init_db()
    print('Database initialized successfully')

if __name__ == '__main__':
    asyncio.run(main())
"

# Run tests
echo "Running tests..."
PYTHONPATH=. pytest

echo "Setup completed successfully!"
echo "To start the backend server:"
echo "  cd $PROJECT_ROOT/backend"
echo "  source ../.venv/bin/activate"
echo "  python -m uvicorn app.main:app --host 127.0.0.1 --port 8004"
