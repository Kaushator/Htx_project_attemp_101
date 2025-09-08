# HTX Trading Platform - Development Documentation

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Quick Start](#quick-start)
3. [Development Setup](#development-setup)
4. [Architecture](#architecture)
5. [API Documentation](#api-documentation)
6. [WSL Configuration](#wsl-configuration)
7. [Testing](#testing)
8. [Troubleshooting](#troubleshooting)
9. [Development History](#development-history)

---

## Project Overview

HTX Trading Platform is a comprehensive trading analytics system with:
- **FastAPI async backend** (Python 3.12)
- **React frontend** with Material-UI
- **HTX API integration** for real-time trading data
- **CSV/Excel file processing** for trade analysis
- **SQLite/PostgreSQL database** with SQLAlchemy 2.0
- **WebSocket support** for real-time updates

### Key Features
- ✅ Real-time HTX API integration (balance, ticker, trades)
- ✅ File upload and CSV processing
- ✅ Advanced PnL analytics
- ✅ Risk analysis and performance metrics
- ✅ WebSocket real-time updates
- ✅ Material-UI dashboard interface

---

## Quick Start

### 🚀 One-Click Start (Recommended)
```bash
# From Windows PowerShell:
wsl -d Ubuntu -- bash -c "cd /mnt/e/Htx_project_attemp_101 && ./scripts/full_restart.sh"
```

This script will:
1. Stop all running processes
2. Check WSL environment and dependencies
3. Install MCP SDK and required packages
4. Start backend (port 8004) and frontend (port 3000)
5. Run comprehensive health tests
6. Provide detailed status report

### 🔗 Access Points
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8004
- **API Documentation**: http://localhost:8004/docs
- **Health Check**: http://localhost:8004/api/v1/health

---

## Development Setup

### System Requirements
- ⚠️ **WSL 2** with Ubuntu (REQUIRED - Windows-only development not supported)
- Python 3.12+ in WSL
- Node.js 18+ in WSL
- Git

### Manual Setup
```bash
# 1. Clone and navigate
git clone <repository>
cd Htx_project_attemp_101

# 2. Setup WSL environment
./scripts/wsl_setup.sh

# 3. Start services
./scripts/full_restart.sh
```

### Environment Configuration
1. Copy `backend/env.example` to `backend/.env`
2. Add your HTX API credentials:
   ```env
   HTX_ACCESS_KEY=your_access_key
   HTX_SECRET_KEY=your_secret_key
   HTX_BASE_URL=https://api.huobi.pro
   ```

---

## Architecture

### Backend Structure (`backend/`)
```
app/
├── main.py              # FastAPI application entry point
├── core/
│   ├── config.py        # Settings and configuration
│   └── logging.py       # Logging configuration
├── api/v1/endpoints/    # REST API endpoints
│   ├── health.py        # Health checks
│   ├── files.py         # File upload/processing
│   ├── trades.py        # Trading data
│   ├── cashflow.py      # Cash flow analysis
│   └── pnl.py          # PnL analytics
├── models/              # SQLAlchemy database models
├── schemas/             # Pydantic request/response schemas
├── services/            # Business logic
│   ├── htx_client_real.py   # HTX API client
│   ├── parser_csv.py        # CSV file processing
│   └── threecommas.py       # 3Commas integration
└── db/                  # Database configuration
```

### Frontend Structure (`frontend/`)
```
src/
├── main.jsx            # React application entry
├── App.jsx             # Main app component
├── components/         # Reusable components
│   ├── FileUpload.jsx      # File upload interface
│   ├── WebSocketStatus.jsx # Real-time connection
│   └── Dashboard/          # Dashboard components
├── pages/              # Page components
│   ├── UltraSimpleDashboard.jsx  # Main dashboard
│   ├── PnlAnalytics.jsx          # PnL analysis
│   └── TransactionHistory.jsx    # Transaction view
└── styles/             # CSS styling
```

### Data Flow
1. **HTX API** → `htx_client_real.py` → REST endpoints → Frontend
2. **CSV Upload** → `parser_csv.py` → Database → REST endpoints → Frontend
3. **Real-time** → WebSocket → Frontend updates

---

## API Documentation

### HTX Integration Endpoints
```http
GET /api/v1/htx/balance          # Account balance
GET /api/v1/htx/ticker/{symbol}  # Price ticker
GET /api/v1/htx/trades           # Trade history
GET /api/v1/htx/currencies       # Available currencies
GET /api/v1/htx/symbols          # Trading pairs
```

### File Processing Endpoints
```http
POST /api/v1/files/upload        # Upload CSV/Excel files
GET  /api/v1/files/              # List uploaded files
GET  /api/v1/files/{file_id}     # Get file details
```

### Database Endpoints
```http
GET /api/v1/trades/              # Get processed trades
GET /api/v1/pnl/analytics        # PnL analysis
GET /api/v1/cashflow/summary     # Cash flow data
```

### WebSocket
```
WS /api/v1/ws                    # Real-time updates
```

---

## WSL Configuration

### Why WSL Only?
- Python package compatibility (especially numpy, pandas)
- Linux-native development environment
- Better Docker integration
- Consistent deployment environment

### WSL Setup Details
```bash
# Virtual environment location
.venv_wsl/                       # WSL Python environment

# Key configuration files
scripts/wsl_setup.sh             # Environment setup
scripts/full_restart.sh          # Complete restart with tests
WSL_ONLY.md                      # WSL-specific documentation
```

### Common WSL Commands
```bash
# Check WSL status
wsl --list --verbose

# Access project in WSL
wsl -d Ubuntu -- bash -c "cd /mnt/e/Htx_project_attemp_101"

# Run specific commands
wsl -d Ubuntu -- bash -c "cd /mnt/e/Htx_project_attemp_101 && source .venv_wsl/bin/activate && python --version"
```

---

## Testing

### Automated Health Tests
The `full_restart.sh` script includes comprehensive testing:

1. **Service Health**
   - Backend API responsiveness
   - Frontend availability
   - Database connectivity

2. **API Integration**
   - HTX API connection and data retrieval
   - File upload endpoints
   - Real-time WebSocket

3. **Data Processing**
   - CSV parsing functionality
   - Database storage
   - Analytics generation

### Manual Testing
```bash
# Test HTX API
curl http://localhost:8004/api/v1/htx/ticker/btcusdt

# Test file upload
curl -X POST -F "file=@sample_trades.csv" http://localhost:8004/api/v1/files/upload

# Test health
curl http://localhost:8004/api/v1/health
```

---

## Troubleshooting

### Common Issues

#### 1. "Module not found" errors
```bash
# Ensure PYTHONPATH is set
export PYTHONPATH="/mnt/e/Htx_project_attemp_101/backend:$PYTHONPATH"

# Reinstall dependencies
pip install -r backend/requirements.txt
```

#### 2. Port conflicts
```bash
# Kill existing processes
pkill -f uvicorn
pkill -f node

# Check port usage
netstat -tulpn | grep :8004
```

#### 3. WSL environment issues
```bash
# Recreate virtual environment
rm -rf .venv_wsl
python3 -m venv .venv_wsl
source .venv_wsl/bin/activate
pip install -r backend/requirements.txt
```

#### 4. Frontend not loading
```bash
# Check frontend dependencies
cd frontend && npm install

# Clear cache
rm -rf frontend/node_modules/.vite
```

### Debug Commands
```bash
# Check backend logs
tail -f logs/backend.log

# Check frontend logs
tail -f logs/frontend.log

# Test imports
python -c "from app.main import app; print('Success')"
```

---

## Development History

### Phase 5: Current State (Complete)
✅ **Backend Services**
- Advanced PnL Analytics API
- HTX API integration with real authentication
- File upload and CSV processing
- WebSocket support for real-time updates
- SQLite database with SQLAlchemy 2.0

✅ **Frontend Application**
- React dashboard with Material-UI
- 6 comprehensive analysis tabs
- Real-time WebSocket connection
- File upload interface with drag & drop
- Performance metrics and risk analysis

✅ **Infrastructure**
- WSL-only development environment
- Automated testing and health checks
- Production-ready deployment scripts
- Comprehensive documentation

### Key Technical Achievements
1. **Real HTX API Integration**
   - Proper signature generation for authenticated requests
   - Real-time price data (BTC: $107,910.24 confirmed working)
   - Account balance and trade history access

2. **Mock Data Removal**
   - Completely removed all mock/fake data
   - System works with real HTX API and uploaded CSV data only
   - Clear separation between live API data and historical CSV data

3. **CSV Processing Pipeline**
   - Upload → Parse → Store → Analyze workflow
   - Support for multiple file formats
   - Background processing with progress tracking

4. **Automated Environment Management**
   - One-click setup and restart
   - Comprehensive health testing
   - WSL-optimized development workflow

### File Organization Cleanup
- ❌ Removed Windows-specific files (.bat, .ps1, Windows .venv)
- ❌ Removed temporary and duplicate files
- ❌ Cleaned up development artifacts
- ✅ Maintained GitHub compatibility
- ✅ Preserved essential scripts and documentation

---

## Next Development Steps

1. **Enhanced UI Features**
   - Add HTX currencies/symbols endpoints to backend
   - Create comprehensive token list interface
   - Implement advanced filtering and search

2. **Additional Integrations**
   - 3Commas API integration
   - Additional exchange APIs
   - Enhanced analytics engines

3. **Performance Optimization**
   - Database query optimization
   - Caching layer implementation
   - Real-time data streaming improvements

4. **Production Features**
   - User authentication
   - Multi-user support
   - Advanced security measures

---

## Contact & Support

For development questions or issues:
1. Check this documentation first
2. Run `./scripts/full_restart.sh` for automated diagnostics
3. Check logs in `logs/` directory
4. Review API documentation at http://localhost:8004/docs

**Remember: This project requires WSL and is not compatible with native Windows development.**
