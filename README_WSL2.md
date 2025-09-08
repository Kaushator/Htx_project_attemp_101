# HTX Trading Platform

> 🚀 **Production-Ready Trading Analytics Platform with Real-Time HTX Integration**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://reactjs.org/)
[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org/)
[![WSL2](https://img.shields.io/badge/WSL2-Recommended-orange.svg)](https://docs.microsoft.com/en-us/windows/wsl/)

## 📋 Overview

HTX Trading Platform is a comprehensive, real-time trading analytics system that integrates with HTX (Huobi) exchange API to provide advanced trading insights, portfolio analysis, and risk management tools.

### 🎯 Key Features

- ✅ **Real-Time HTX API Integration** - Live price data, account balance, trading history
- ✅ **Advanced Analytics Dashboard** - P&L analysis, risk metrics, performance tracking
- ✅ **File Processing Engine** - CSV/Excel trade data import and analysis
- ✅ **WebSocket Real-Time Updates** - Live price feeds and notifications
- ✅ **Material-UI Interface** - Modern, responsive React dashboard
- ✅ **WSL2 Support** - Enhanced performance for ML components and data analysis

## 🚀 Quick Start

### WSL2 (Recommended)

WSL2 offers superior performance for ML components and better compatibility:

```bash
# 1. Clone repository
git clone https://github.com/Kaushator/Htx_project_attemp_101.git
cd Htx_project_attemp_101

# 2. Setup WSL2 environment
./scripts/setup_wsl2.sh

# 3. Start the application
./start_wsl2.sh
```

See [WSL2 Migration Guide](docs/wsl-migration.md) for detailed instructions.

### Windows (Legacy)

```bash
# 1. Setup environment
scripts\setup_env.bat

# 2. Start the application
start_app.bat
```
