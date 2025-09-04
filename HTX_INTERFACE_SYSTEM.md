# HTX Analytics Interface - Полное Руководство по Системе

## 📊 Общий Обзор Системы

HTX Analytics Interface представляет собой комплексную аналитическую платформу, объединяющую мощный AI-powered backend с современным React frontend.

## 🎯 Ключевые Компоненты

### Frontend Application
- React + TypeScript + Material-UI
- Four-Color Indicators система
- WebSocket Real-time updates

### Backend Services  
- FastAPI + OpenAI Integration
- ML Analytics + Technical Indicators
- HTX API Client

### Infrastructure
- Docker Compose (dev)
- GCP Terraform (production)
- PostgreSQL + TimescaleDB + Redis

## 🚀 Quick Start

### Local Development
\\\ash
# Backend
cd backend && pip install -r requirements.txt
uvicorn app.main:app --reload --port 8004

# Frontend
cd frontend && npm install && npm run dev
\\\

### Docker
\\\ash
docker-compose up -d
\\\

## 📊 API Endpoints

- GET /api/v1/coins/analytics
- POST /api/v1/ai/analyze-trading-data  
- WS /ws/forecasts

## 🔧 MCP Server

Available tools:
- analyze_trading_data
- generate_forecast
- calculate_technical_indicators
- get_market_data

Ready for production deployment!
