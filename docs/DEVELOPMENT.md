# Development Guide - HTX Trading Analytics Platform

This guide provides detailed instructions for setting up and working with the HTX Trading Analytics Platform development environment.

## 🏁 Quick Start

```bash
# 1. Clone and setup
git clone https://github.com/Kaushator/Htx_project_attemp_101.git
cd Htx_project_attemp_101
git checkout copilot-refactor

# 2. Backend setup
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt

# 3. Database setup
alembic upgrade head

# 4. Start development
uvicorn app.main:app --reload --host 127.0.0.1 --port 8004
```

## 📋 Prerequisites

### System Requirements
- **Python**: 3.8+ (3.10+ recommended)
- **Node.js**: 16+ (for frontend development)
- **Git**: Latest version
- **PostgreSQL**: 13+ (optional, SQLite default)
- **Redis**: 6+ (optional, for caching)

### Recommended Tools
- **IDE**: VS Code with Python extension
- **Database**: DBeaver or pgAdmin for PostgreSQL
- **API Testing**: Postman or Insomnia
- **Container**: Docker & Docker Compose

## 🐍 Backend Development

### Environment Setup

#### 1. Python Virtual Environment
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate

# Verify activation
which python  # Should point to .venv/bin/python
python --version  # Should show Python 3.8+
```

#### 2. Install Dependencies
```bash
cd backend

# Install production dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Verify installation
pip list | grep fastapi
pip list | grep pytest
```

#### 3. Environment Configuration
```bash
# Copy environment template
cp env.example .env

# Edit configuration
nano .env  # or your preferred editor
```

**Required environment variables**:
```bash
# Database (SQLite default)
DATABASE_URL=sqlite:///./htx_project.db
# DATABASE_URL=postgresql+asyncpg://user:pass@localhost/htx_project

# Security
SECRET_KEY=your-super-secret-key-here
ENCRYPTION_KEY=your-fernet-key-here

# HTX API (optional for development)
HTX_ACCESS_KEY=your_htx_access_key
HTX_SECRET_KEY=your_htx_secret_key

# 3Commas API (optional)
THREECOMMAS_API_KEY=your_3commas_key
THREECOMMAS_SECRET=your_3commas_secret

# Redis (optional)
REDIS_URL=redis://localhost:6379/0

# Development settings
DEBUG=true
LOG_LEVEL=DEBUG
```

#### 4. Database Setup
```bash
# Initialize Alembic (if not already done)
alembic upgrade head

# Create initial data (optional)
python -c "
from app.db.init_db import init_db
import asyncio
asyncio.run(init_db())
"
```

### Development Server

#### Start Development Server
```bash
# Using uvicorn directly
uvicorn app.main:app --reload --host 127.0.0.1 --port 8004

# Using Makefile
make dev

# With specific settings
uvicorn app.main:app --reload --host 0.0.0.0 --port 8004 --log-level debug
```

#### Verify Installation
```bash
# Health check
curl http://localhost:8004/health

# API documentation
open http://localhost:8004/docs  # Swagger UI
open http://localhost:8004/redoc  # ReDoc
```

### Development Commands

#### Code Quality
```bash
# Format code
black .
isort .

# Lint code
ruff check .

# Type checking
mypy .

# All quality checks
make lint
make format
```

#### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest -k "test_pnl"

# Run tests with verbose output
pytest -v

# Continuous testing
pytest-watch
```

#### Database Operations
```bash
# Generate migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Downgrade migration
alembic downgrade -1

# Reset database
python -c "
from app.db.init_db import reset_db
import asyncio
asyncio.run(reset_db())
"
```

### Project Structure Deep Dive

```
backend/
├── app/
│   ├── main.py                 # FastAPI application factory
│   ├── core/
│   │   ├── config.py          # Pydantic settings
│   │   ├── logging.py         # Logging configuration
│   │   └── security.py        # Security utilities
│   ├── api/
│   │   └── v1/
│   │       ├── api.py         # Router aggregation
│   │       └── endpoints/     # API endpoint modules
│   ├── models/                # SQLAlchemy models
│   ├── schemas/               # Pydantic schemas
│   ├── services/              # Business logic
│   ├── db/                    # Database utilities
│   └── workers/               # Background tasks
├── alembic/                   # Database migrations
├── tests/                     # Test suite
├── data/                      # Development data
├── logs/                      # Application logs
└── [config files]
```

### Service Development Patterns

#### Creating a New Service
```python
# services/new_service.py
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.trade import Trade
from app.schemas.trade import TradeCreate, TradeResponse

class NewService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_trade(self, trade_data: TradeCreate) -> TradeResponse:
        """Create a new trade record."""
        trade = Trade(**trade_data.dict())
        self.db.add(trade)
        await self.db.commit()
        await self.db.refresh(trade)
        return TradeResponse.from_orm(trade)
    
    async def get_trades(
        self, 
        skip: int = 0, 
        limit: int = 100,
        symbol: Optional[str] = None
    ) -> List[TradeResponse]:
        """Get trades with optional filtering."""
        query = select(Trade)
        if symbol:
            query = query.where(Trade.symbol == symbol)
        query = query.offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        trades = result.scalars().all()
        return [TradeResponse.from_orm(trade) for trade in trades]
```

#### Creating a New Endpoint
```python
# api/v1/endpoints/new_endpoint.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.deps import get_db
from app.services.new_service import NewService
from app.schemas.trade import TradeCreate, TradeResponse

router = APIRouter()

@router.post("/", response_model=TradeResponse)
async def create_trade(
    trade_data: TradeCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new trade."""
    service = NewService(db)
    try:
        return await service.create_trade(trade_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[TradeResponse])
async def get_trades(
    skip: int = 0,
    limit: int = 100,
    symbol: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get trades with pagination and filtering."""
    service = NewService(db)
    return await service.get_trades(skip=skip, limit=limit, symbol=symbol)
```

## ⚛️ Frontend Development

### Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Project Structure
```
frontend/
├── src/
│   ├── components/         # Reusable UI components
│   │   ├── common/        # Generic components
│   │   ├── forms/         # Form components
│   │   └── charts/        # Chart components
│   ├── pages/             # Route components
│   ├── hooks/             # Custom React hooks
│   ├── utils/             # Utility functions
│   ├── services/          # API service layer
│   ├── styles/            # Global styles
│   ├── App.jsx           # Main application
│   └── main.jsx          # Application entry point
├── public/               # Static assets
├── tests/               # Test files
└── [config files]
```

### Development Patterns

#### Creating Components
```jsx
// components/PnLCard.jsx
import React from 'react';
import { formatCurrency } from '../utils/formatting';

export const PnLCard = ({ 
  title, 
  value, 
  change, 
  className = '' 
}) => {
  const isPositive = change >= 0;
  
  return (
    <div className={`bg-white rounded-lg shadow p-6 ${className}`}>
      <h3 className="text-lg font-medium text-gray-900">{title}</h3>
      <p className="text-2xl font-bold text-gray-900">
        {formatCurrency(value)}
      </p>
      <p className={`text-sm ${
        isPositive ? 'text-green-600' : 'text-red-600'
      }`}>
        {isPositive ? '+' : ''}{formatCurrency(change)}
      </p>
    </div>
  );
};
```

#### API Service Layer
```jsx
// services/api.js
const API_BASE_URL = 'http://localhost:8004/api/v1';

class ApiService {
  async request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
      },
      ...options,
    };
    
    const response = await fetch(url, config);
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }
    
    return response.json();
  }
  
  async getTrades(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request(`/trades?${query}`);
  }
  
  async getPnL() {
    return this.request('/pnl');
  }
  
  async uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    return this.request('/files/upload', {
      method: 'POST',
      body: formData,
      headers: {}, // Let browser set Content-Type for FormData
    });
  }
}

export const apiService = new ApiService();
```

## 🐳 Docker Development

### Development with Docker

```bash
# Build and start all services
docker-compose up --build

# Start specific service
docker-compose up backend
docker-compose up frontend

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop services
docker-compose down
```

### Docker Configuration

#### Backend Dockerfile
```dockerfile
# backend/Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8004

# Start application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8004"]
```

#### Docker Compose
```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8004:8004"
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:password@postgres:5432/htx_project
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - postgres
      - redis
    volumes:
      - ./backend:/app
      - ./backend/data:/app/data

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - VITE_API_URL=http://localhost:8004
    volumes:
      - ./frontend:/app

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=htx_project
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

## 🧪 Testing

### Backend Testing

#### Test Structure
```
tests/
├── unit/
│   ├── test_services/
│   │   ├── test_pnl_service.py
│   │   ├── test_parser_service.py
│   │   └── test_htx_client.py
│   ├── test_models/
│   └── test_utils/
├── integration/
│   ├── test_api_endpoints.py
│   ├── test_database.py
│   └── test_file_processing.py
├── fixtures/
│   ├── sample_data.py
│   └── conftest.py
└── e2e/
    └── test_user_workflows.py
```

#### Writing Tests
```python
# tests/unit/test_services/test_pnl_service.py
import pytest
from decimal import Decimal
from app.services.pnl import PnLService
from tests.fixtures.sample_data import create_sample_trades

@pytest.mark.asyncio
async def test_calculate_realized_pnl():
    """Test realized PnL calculation with FIFO method."""
    # Arrange
    service = PnLService(mock_db_service)
    trades = create_sample_trades([
        {"symbol": "BTC", "side": "buy", "amount": 1, "price": 50000},
        {"symbol": "BTC", "side": "sell", "amount": 0.5, "price": 60000},
    ])
    
    # Act
    result = await service.calculate_realized_pnl(trades)
    
    # Assert
    assert result == Decimal('5000.00')  # (60000 - 50000) * 0.5

@pytest.mark.asyncio
async def test_calculate_pnl_with_empty_trades():
    """Test PnL calculation with no trades."""
    service = PnLService(mock_db_service)
    
    result = await service.calculate_realized_pnl([])
    
    assert result == Decimal('0.00')
```

#### Test Configuration
```python
# tests/conftest.py
import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.main import app

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def db_session():
    """Create test database session."""
    engine = create_async_engine("sqlite+aiosqlite:///./test.db")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    Session = sessionmaker(engine, class_=AsyncSession)
    async with Session() as session:
        yield session
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
def client():
    """Create test client."""
    from fastapi.testclient import TestClient
    return TestClient(app)
```

### Frontend Testing

#### Component Testing
```jsx
// tests/components/PnLCard.test.jsx
import { render, screen } from '@testing-library/react';
import { PnLCard } from '../components/PnLCard';

describe('PnLCard', () => {
  test('renders title and value correctly', () => {
    render(
      <PnLCard 
        title="Total PnL" 
        value={1234.56} 
        change={123.45} 
      />
    );
    
    expect(screen.getByText('Total PnL')).toBeInTheDocument();
    expect(screen.getByText('$1,234.56')).toBeInTheDocument();
    expect(screen.getByText('+$123.45')).toBeInTheDocument();
  });
  
  test('shows negative change in red', () => {
    render(
      <PnLCard 
        title="Total PnL" 
        value={1000} 
        change={-50} 
      />
    );
    
    const changeElement = screen.getByText('-$50.00');
    expect(changeElement).toHaveClass('text-red-600');
  });
});
```

## 🔧 Development Tools

### VS Code Configuration

#### Recommended Extensions
```json
// .vscode/extensions.json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.black-formatter",
    "ms-python.isort",
    "charliermarsh.ruff",
    "bradlc.vscode-tailwindcss",
    "esbenp.prettier-vscode",
    "ms-vscode.vscode-typescript-next"
  ]
}
```

#### Settings
```json
// .vscode/settings.json
{
  "python.defaultInterpreterPath": "./backend/.venv/bin/python",
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter"
  },
  "[javascript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  }
}
```

### Git Hooks

#### Pre-commit Setup
```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run on all files
pre-commit run --all-files
```

#### Pre-commit Configuration
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort

  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.0.270
    hooks:
      - id: ruff

  - repo: https://github.com/pre-commit/mirrors-prettier
    rev: v3.0.0
    hooks:
      - id: prettier
        files: \.(js|jsx|ts|tsx|json|css|md)$
```

## 🐛 Debugging

### Backend Debugging

#### Using Debugger
```python
# Add breakpoint in code
import debugpy
debugpy.breakpoint()

# Or use built-in breakpoint (Python 3.7+)
breakpoint()
```

#### VS Code Debug Configuration
```json
// .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "FastAPI Debug",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/backend/.venv/bin/uvicorn",
      "args": [
        "app.main:app",
        "--reload",
        "--host", "127.0.0.1",
        "--port", "8004"
      ],
      "cwd": "${workspaceFolder}/backend",
      "console": "integratedTerminal"
    }
  ]
}
```

#### Logging
```python
# Use structured logging
import logging
from app.core.logging import get_logger

logger = get_logger(__name__)

# Log with context
logger.info(
    "Processing file upload",
    extra={
        "filename": filename,
        "size": file_size,
        "user_id": user_id
    }
)

# Log exceptions
try:
    result = await process_file(file)
except Exception as e:
    logger.exception(
        "File processing failed",
        extra={"filename": filename, "error": str(e)}
    )
    raise
```

### Frontend Debugging

#### Browser DevTools
- Use React Developer Tools extension
- Enable verbose logging in development
- Use console.log() for debugging (remove before commit)

#### Error Boundaries
```jsx
// components/ErrorBoundary.jsx
import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="p-6 bg-red-50 border border-red-200 rounded">
          <h2 className="text-lg font-semibold text-red-800">
            Something went wrong
          </h2>
          <p className="text-red-600">{this.state.error?.message}</p>
        </div>
      );
    }

    return this.props.children;
  }
}
```

## 📈 Performance Monitoring

### Backend Performance

#### Profiling
```python
# Use cProfile for profiling
python -m cProfile -o profile.stats your_script.py

# Analyze with snakeviz
pip install snakeviz
snakeviz profile.stats
```

#### Database Query Monitoring
```python
# Log slow queries
import time
from sqlalchemy import event
from sqlalchemy.engine import Engine

@event.listens_for(Engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    context._query_start_time = time.time()

@event.listens_for(Engine, "after_cursor_execute")
def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = time.time() - context._query_start_time
    if total > 0.1:  # Log queries taking more than 100ms
        logger.warning("Slow query", extra={
            "duration": total,
            "statement": statement[:200]
        })
```

### Frontend Performance

#### Bundle Analysis
```bash
# Analyze bundle size
npm run build -- --analyze

# Check for duplicate dependencies
npx duplicate-package-checker-webpack-plugin
```

#### Performance Monitoring
```jsx
// Use React Profiler
import { Profiler } from 'react';

function onRenderCallback(id, phase, actualDuration) {
  if (actualDuration > 16) { // More than 1 frame
    console.warn(`Slow render: ${id} took ${actualDuration}ms`);
  }
}

<Profiler id="App" onRender={onRenderCallback}>
  <App />
</Profiler>
```

## 🚀 Deployment

### Environment Preparation

#### Production Environment Variables
```bash
# Production .env
DATABASE_URL=postgresql+asyncpg://user:pass@prod-db:5432/htx_project
REDIS_URL=redis://prod-redis:6379/0
SECRET_KEY=production-secret-key
ENCRYPTION_KEY=production-encryption-key
DEBUG=false
LOG_LEVEL=INFO
```

#### Health Checks
```python
# app/api/v1/endpoints/health.py
@router.get("/health")
async def health_check():
    """Comprehensive health check."""
    try:
        # Check database
        await db_service.check_connection()
        
        # Check Redis (if configured)
        if settings.REDIS_URL:
            await cache_service.ping()
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow(),
            "version": "1.0.0",
            "components": {
                "database": "healthy",
                "cache": "healthy" if settings.REDIS_URL else "disabled"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Health check failed: {e}")
```

### Build Process

#### Backend Build
```bash
# Build optimized Docker image
docker build -t htx-backend:latest ./backend

# Run production container
docker run -p 8004:8004 \
  -e DATABASE_URL="$DATABASE_URL" \
  -e SECRET_KEY="$SECRET_KEY" \
  htx-backend:latest
```

#### Frontend Build
```bash
# Build for production
npm run build

# Serve static files
npx serve -s dist -l 3000
```

---

This development guide provides comprehensive instructions for working with the HTX Trading Analytics Platform. For additional help, refer to the [Contributing Guide](CONTRIBUTING.md) or open an issue on GitHub.