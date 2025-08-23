# HTX Project Makefile

.PHONY: help install dev test lint format clean docker-build docker-run

# Default target
help:
	@echo "HTX Project - Available commands:"
	@echo ""
	@echo "Development:"
	@echo "  install     - Install dependencies"
	@echo "  dev         - Start development server"
	@echo "  test        - Run tests"
	@echo "  lint        - Run linting"
	@echo "  format      - Format code"
	@echo ""
	@echo "Docker:"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-run   - Run with Docker Compose"
	@echo ""
	@echo "Utilities:"
	@echo "  clean       - Clean up generated files"
	@echo "  help        - Show this help"

# Install dependencies
install:
	@echo "Installing Python dependencies..."
	pip install -r backend/requirements.txt
	@echo "Installing development dependencies..."
	pip install -r backend/requirements-dev.txt

# Start development server
dev:
	@echo "Starting development server..."
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
test:
	@echo "Running tests..."
	cd backend && pytest -v

# Run linting
lint:
	@echo "Running linting..."
	cd backend && ruff check .

# Format code
format:
	@echo "Formatting code..."
	cd backend && black .
	cd backend && isort .

# Clean up
clean:
	@echo "Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +

# Docker commands
docker-build:
	@echo "Building Docker image..."
	docker build -t htx-project ./backend

docker-run:
	@echo "Running with Docker Compose..."
	docker-compose up --build

docker-stop:
	@echo "Stopping Docker containers..."
	docker-compose down

# Database commands
db-init:
	@echo "Initializing database..."
	cd backend && python -c "from app.db.init_db import init_db; import asyncio; asyncio.run(init_db())"

db-reset:
	@echo "Resetting database..."
	cd backend && python -c "from app.db.init_db import reset_db; import asyncio; asyncio.run(reset_db())"

# Frontend commands (if needed)
frontend-install:
	@echo "Installing frontend dependencies..."
	cd frontend && npm install

frontend-dev:
	@echo "Starting frontend development server..."
	cd frontend && npm run dev

frontend-build:
	@echo "Building frontend..."
	cd frontend && npm run build
