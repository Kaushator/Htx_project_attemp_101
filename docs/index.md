# HTX Trading Platform Documentation

Welcome to the comprehensive documentation for the HTX Trading Analytics Platform.

## 🚀 Quick Start

- **[Installation Guide](setup/installation.md)** - Get up and running
- **[API Documentation](api/overview.md)** - Complete API reference  
- **[ML Features](ml/overview.md)** - AI and machine learning
- **[Configuration](setup/configuration.md)** - Environment setup

## 📊 Key Features

### Trading Analytics
- Real-time HTX API Integration
- P&L Analysis and Risk Management
- Portfolio Analytics and Performance Tracking

### AI & Machine Learning
- OpenAI Integration for experiment planning
- Local LLMs (FinGPT, Mistral) for financial insights
- Vector embeddings and similarity search
- Automated batch processing

### Data Processing
- CSV/Excel file import and processing
- Real-time WebSocket updates
- Background task processing

## 🏗️ Architecture

**Microservices-style layered architecture:**
- Frontend: React 18 + Material-UI + Vite
- Backend: FastAPI (Python 3.12) with async support
- Database: SQLite/PostgreSQL with pgvector
- ML: OpenAI API + Local LLMs with GPU/CPU support

## 🛠️ Quick Commands

```bash
# Setup and start development
make install
make dev

# Build and deploy
make docker-build
make docker-run
```

## 📈 Latest Updates

**Version 1.0.0** - October 2025
- ✅ Complete ML integration with OpenAI and local LLMs
- ✅ Advanced risk metrics and portfolio analytics  
- ✅ Vector embeddings and similarity search
- ✅ Real-time WebSocket integration

---

**Need Help?** Check our [Troubleshooting Guide](troubleshooting/common-issues.md).
