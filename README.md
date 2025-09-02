# HTX Trading Platform

> 🚀 **Production-Ready Trading Analytics Platform with Real-Time HTX Integration**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://reactjs.org/)
[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org/)
[![WSL](https://img.shields.io/badge/WSL-Required-orange.svg)](https://docs.microsoft.com/en-us/windows/wsl/)

## 📋 Overview

HTX Trading Platform is a comprehensive, real-time trading analytics system that integrates with HTX (Huobi) exchange API to provide advanced trading insights, portfolio analysis, and risk management tools.

### 🎯 Key Features

- ✅ **Real-Time HTX API Integration** - Live price data, account balance, trading history
- ✅ **Advanced Analytics Dashboard** - P&L analysis, risk metrics, performance tracking
- ✅ **File Processing Engine** - CSV/Excel trade data import and analysis
- ✅ **WebSocket Real-Time Updates** - Live price feeds and notifications
- ✅ **Material-UI Interface** - Modern, responsive React dashboard
- ✅ **Automated Testing & Health Checks** - Comprehensive system monitoring

### 🛠️ Tech Stack

**Backend:**
- FastAPI (Python 3.12) - Async REST API
- SQLAlchemy 2.0 - Database ORM with async support
- HTX API - Real exchange integration
- WebSocket - Real-time communication

**Frontend:**
- React 18 - Modern UI framework
- Material-UI - Component library
- Vite - Fast development and build tool
- React Query - Server state management

**Infrastructure:**
- WSL 2 - Development environment
- SQLite/PostgreSQL - Database options
- Docker - Containerization support

---

## 🚀 Quick Start

### Prerequisites
- ⚠️ **WSL 2 with Ubuntu** (Required - Windows-only development not supported)
- Python 3.12+ in WSL
- Node.js 18+ in WSL

### One-Command Launch
```bash
# From Windows PowerShell:
wsl -d Ubuntu -- bash -c "cd /mnt/e/Htx_project_attemp_101 && ./scripts/full_restart.sh"
```

This will automatically:
1. 🛑 Stop all existing processes
2. 🔧 Verify WSL environment and dependencies
3. 📦 Install/update required packages (MCP SDK, aiohttp, etc.)
4. 🚀 Start backend (port 8004) and frontend (port 3000)
5. 🧪 Run comprehensive health tests
6. 📊 Provide detailed status report

### Access Your Application
- **🏠 Frontend Dashboard**: http://localhost:3000
- **⚡ Backend API**: http://localhost:8004
- **📖 API Documentation**: http://localhost:8004/docs
- **❤️ Health Check**: http://localhost:8004/api/v1/health

---

## 📚 Documentation

| Document | Purpose | Audience |
|----------|---------|----------|
| [DEVELOPMENT.md](DEVELOPMENT.md) | Complete development guide with setup, API docs, testing | Developers |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Technical architecture, design patterns, system design | Engineers |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Production deployment, Docker, monitoring, security | DevOps |
| [WSL_ONLY.md](WSL_ONLY.md) | WSL-specific setup and troubleshooting | Windows Users |

---

## 🎛️ Dashboard Features

### 📈 Analytics Tabs
1. **PnL Overview** - Daily profit/loss charts and position tracking
2. **Risk Analysis** - VaR calculations, Sharpe ratios, drawdown metrics
3. **Trading Patterns** - Temporal analysis and correlation matrices
4. **Performance Metrics** - Return analysis and risk attribution
5. **Real-Time Data** - Live HTX price feeds and account data
6. **File Management** - CSV/Excel upload and processing status

### 💰 HTX Integration
- **Account Balance** - Real-time balance display
- **Price Tickers** - Live cryptocurrency prices
- **Trade History** - Historical trading data
- **Market Data** - Trading pairs and currency information

---

## 🔧 Quick Commands

```bash
# Full restart with testing
./scripts/full_restart.sh

# Manual backend start
cd backend && source ../.venv_wsl/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8004 --reload

# Manual frontend start
cd frontend && npm run dev -- --host 0.0.0.0 --port 3000

# Health check
curl http://localhost:8004/api/v1/health
```

---

## 🎉 Project Status

**Current Version**: 1.0.0 - Production Ready ✅

### Recent Achievements
- ✅ Complete HTX API integration with real authentication
- ✅ Mock data removal - system uses only real/uploaded data
- ✅ WSL-optimized development environment
- ✅ Automated testing and health monitoring
- ✅ Production-ready deployment configuration
- ✅ Comprehensive documentation structure

**Remember**: This is a WSL-only project optimized for Linux development environments. 🐧