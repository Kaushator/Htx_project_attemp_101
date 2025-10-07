# API Reference

The HTX Trading Platform provides a comprehensive REST API built with FastAPI.

## Base URL
```
http://localhost:8004/api/v1
```

## Endpoint Categories

### Core Endpoints
- **GET /health** - System health check
- **POST /files/upload** - Upload CSV/Excel files
- **GET /trades** - List trades with filtering
- **GET /pnl/calculate** - Calculate P&L metrics

### Machine Learning Endpoints
- **POST /ml/plan** - Plan ML experiments using AI
- **POST /ml/batch_label** - Automated data labeling
- **POST /ml/search/similar** - Vector similarity search
- **POST /ml/risk_analysis** - Comprehensive risk metrics
- **POST /ml/fingpt/analyze_trade** - Financial LLM analysis
- **POST /ml/mistral/trading_signals** - Trading signal generation

### Exchange Integration
- **GET /htx/balance** - Get HTX account balance
- **GET /htx/trades** - Fetch HTX trade history
- **WebSocket /ws** - Real-time data streaming

## Response Format
```json
{
  "success": true,
  "message": "Operation completed",
  "data": { ... },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## Authentication
- HTX API: Requires HTX_API_KEY and HTX_API_SECRET
- OpenAI: Requires OPENAI_API_KEY for ML features

## Rate Limiting
- Default: 100 requests/minute
- ML endpoints: 20 requests/minute
- Batch operations: 5 requests/minute

## Examples

### Plan ML Experiment
```bash
curl -X POST "http://localhost:8004/api/v1/ml/plan" \
  -H "Content-Type: application/json" \
  -d '{
    "experiment_description": "Predict Bitcoin price movements",
    "available_data": {
      "sources": ["trades", "market_data"],
      "timeframe": "1H"
    }
  }'
```

### Generate Embeddings
```bash
curl -X POST "http://localhost:8004/api/v1/ml/embeddings/compute" \
  -H "Content-Type: application/json" \
  -d '{
    "content_type": "trades",
    "symbol": "BTCUSDT",
    "limit": 100
  }'
```

### Risk Analysis
```bash
curl -X POST "http://localhost:8004/api/v1/ml/risk_analysis" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BTCUSDT",
    "days_lookback": 365
  }'
```

## Interactive Documentation
- **Swagger UI**: http://localhost:8004/docs
- **ReDoc**: http://localhost:8004/redoc
