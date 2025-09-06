# HTX Trading Analytics Platform

> **🚧 Active Development Notice**: This repository is being actively restructured on the `copilot-refactor` branch. The legacy `qoder-experience` branch is preserved as historical reference only.

A comprehensive trading analytics platform for HTX (Huobi) exchange with 3Commas integration, featuring async FastAPI backend, React frontend, and real-time PnL analytics.

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/Kaushator/Htx_project_attemp_101.git
cd Htx_project_attemp_101

# Switch to active development branch
git checkout copilot-refactor

# Backend setup
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Start development server
uvicorn app.main:app --reload --host 127.0.0.1 --port 8004

# Frontend setup (optional)
cd ../frontend
npm install
npm run dev
```

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                           HTX Analytics Platform                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │   React     │    │  FastAPI    │    │ SQLAlchemy  │         │
│  │  Frontend   │◄──►│   Backend   │◄──►│  Database   │         │
│  │(TailwindCSS)│    │  (Async)    │    │ (SQLite/PG) │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│                            │                                   │
│                            ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Service Layer                               │   │
│  │ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐        │   │
│  │ │CSV/Excel    │ │    PnL      │ │   HTX API   │        │   │
│  │ │  Parser     │ │ Analytics   │ │   Client    │        │   │
│  │ └─────────────┘ └─────────────┘ └─────────────┘        │   │
│  │ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐        │   │
│  │ │ 3Commas     │ │Background   │ │   Cache     │        │   │
│  │ │Integration  │ │  Workers    │ │ (Redis)     │        │   │
│  │ └─────────────┘ └─────────────┘ └─────────────┘        │   │
│  └─────────────────────────────────────────────────────────┘   │
│                            │                                   │
│                            ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              External Integrations                       │   │
│  │ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐        │   │
│  │ │    HTX      │ │  3Commas    │ │    Redis    │        │   │
│  │ │   Exchange  │ │     API     │ │   Cache     │        │   │
│  │ └─────────────┘ └─────────────┘ └─────────────┘        │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture-overview)
- [Quick Start](#-quick-start)
- [Development](#-development)
- [API Documentation](#-api-documentation)
- [Configuration](#-configuration)
- [Testing](#-testing)
- [Contributing](#-contributing)
- [License](#-license)

## ✨ Features

### Core Analytics
- **Real-time PnL Calculation**: FIFO-based profit/loss analysis with unrealized positions
- **Multi-format File Parsing**: CSV/Excel import with automatic column detection
- **Trade History Management**: Comprehensive trade, deposit, withdrawal tracking
- **Risk Metrics**: Sharpe ratio, drawdown analysis, win/loss statistics

### Platform Integration
- **HTX Exchange API**: Automated balance and trade history synchronization
- **3Commas Integration**: Bot performance monitoring and signal automation
- **Async Processing**: Background file processing and API calls
- **Caching Layer**: Redis-powered response optimization

### Data Pipeline
```
CSV/Excel Upload → Parser → Database → Analytics → API → Frontend
       ↓              ↓         ↓          ↓       ↓        ↓
   Validation    Normalization Schema  Calculation REST   React UI
```

## 🔧 Development

### Prerequisites
- Python 3.8+
- Node.js 16+ (for frontend)
- Redis (optional, for caching)
- PostgreSQL (optional, SQLite default)

### Development Commands

```bash
# Using Makefile
make install    # Install all dependencies
make dev        # Start backend dev server
make test       # Run tests
make lint       # Run linting
make format     # Format code

# Direct commands
cd backend && uvicorn app.main:app --reload
cd frontend && npm run dev
```

### Project Structure
```
backend/app/
├── main.py              # FastAPI entrypoint
├── core/                # Configuration & logging
├── api/v1/endpoints/    # REST API endpoints
├── models/              # SQLAlchemy models
├── schemas/             # Pydantic schemas
├── services/            # Business logic
├── db/                  # Database utilities
└── workers/             # Background tasks

frontend/src/
├── components/          # Reusable UI components
├── pages/               # Route components
└── App.jsx             # Main application
```

## 📊 API Documentation

### Health Check
```http
GET /health
```

### File Operations
```http
POST /api/v1/files/upload    # Upload CSV/Excel files
GET  /api/v1/files          # List uploaded files
```

### Trading Data
```http
GET /api/v1/trades          # List trades with pagination
GET /api/v1/cashflow        # Deposits/withdrawals summary
GET /api/v1/pnl            # PnL analytics
```

### Integration Endpoints
```http
GET /api/v1/htx/sync       # Sync HTX data
GET /api/v1/3commas/bots   # 3Commas bot status
```

## ⚙️ Configuration

### Environment Variables
```bash
# Database
DATABASE_URL=sqlite:///./htx_project.db
# DATABASE_URL=postgresql+asyncpg://user:pass@localhost/htx_project

# HTX API
HTX_ACCESS_KEY=your_access_key
HTX_SECRET_KEY=your_secret_key

# 3Commas API
THREECOMMAS_API_KEY=your_api_key
THREECOMMAS_SECRET=your_secret

# Optional Redis Cache
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key-here
ENCRYPTION_KEY=your-fernet-key-here
```

### Configuration Files
- `backend/env.example` - Environment template
- `backend/alembic.ini` - Database migrations
- `docker-compose.yml` - Container orchestration

## 🧪 Testing

```bash
# Run all tests
cd backend && pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Integration tests
pytest tests/integration/

# Specific test categories
pytest -m "not integration"  # Unit tests only
```

## 🤝 Contributing

1. **Branch Strategy**: All development happens on `copilot-refactor`
2. **Code Standards**: Black, isort, ruff for Python; Prettier for frontend
3. **Commit Convention**: [Conventional Commits](https://conventionalcommits.org/)
4. **Documentation**: Update relevant docs with code changes

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for detailed guidelines.

## 📈 Performance Targets

- **Time-to-Insight**: ≤ 10 seconds from file upload to basic analytics
- **Response Time**: ≤ 200ms for cached endpoints
- **Throughput**: Handle 1000+ trades per analysis
- **Availability**: 99.9% uptime for production deployments

## 🔒 Security

- **API Key Encryption**: Fernet-based secret encryption
- **Input Validation**: Comprehensive file and data validation
- **Rate Limiting**: Configurable per-endpoint limits
- **CORS**: Controlled cross-origin access

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Status**: 🚧 Active restructuring in progress on `copilot-refactor` branch
**Legacy**: The `qoder-experience` branch contains archived experimental code - refer to it as a historical example of approaches to avoid.