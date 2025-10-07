# Machine Learning Overview

Advanced ML capabilities for trading analytics and risk assessment.

## 🎯 Core Features

### 1. OpenAI Integration
- **JSON Mode**: Structured responses for experiment planning
- **Batch Labeling**: Automated data annotation
- **Embeddings**: High-quality vector representations
- **Rate Limiting**: Built-in request throttling

### 2. Local LLM Services
- **FinGPT**: Financial analysis and market insights
- **Mistral**: Trading strategies and signal generation
- **Hardware Optimization**: GPU/CPU with 4-bit quantization
- **Privacy**: On-premises inference

### 3. Vector Search
- **Embeddings**: Convert text to vectors
- **Similarity Search**: Find similar trades/patterns
- **pgvector**: PostgreSQL vector extension
- **Performance**: Optimized with caching

### 4. Risk Analytics
- **Advanced Metrics**: Sharpe, Sortino, VaR, drawdown
- **Real-time**: Continuous monitoring
- **Portfolio**: Multi-asset analysis

## 🚀 Quick Start

### Environment Setup
```bash
# Set OpenAI key (optional)
export OPENAI_API_KEY="your_key"

# Configure hardware
export ML_DEVICE="cuda"  # or "cpu"
export LOAD_IN_4BIT="true"
```

### Basic Usage
```python
# Plan experiment
response = await client.post("/ml/plan", json={
    "experiment_description": "Predict volatility",
    "available_data": {"sources": ["trades"]}
})

# Generate embeddings  
embeddings = await client.post("/ml/embeddings/compute", json={
    "content_type": "trades",
    "limit": 1000
})

# Risk analysis
risk = await client.post("/ml/risk_analysis", json={
    "symbol": "BTCUSDT",
    "days_lookback": 365
})
```

## 📊 Use Cases

### Strategy Development
1. Pattern recognition in historical data
2. Risk assessment using ML metrics
3. Strategy optimization with AI
4. Enhanced backtesting

### Portfolio Management
1. Real-time risk monitoring
2. Correlation analysis
3. Position sizing recommendations
4. Automated rebalancing

### Market Analysis
1. Sentiment analysis from trading data
2. Trend prediction models
3. Anomaly detection
4. News impact analysis

## ⚙️ Configuration

### Hardware Requirements
- **Minimum**: 16GB RAM, modern CPU
- **Recommended**: 32GB RAM, NVIDIA GPU (12GB+ VRAM)
- **Models**: FinGPT (~7B params), Mistral (~7B params)

### Performance
- **OpenAI API**: 1-3 seconds
- **Local LLMs (GPU)**: 2-5 seconds  
- **Local LLMs (CPU)**: 15-45 seconds
- **Vector Search**: <100ms

## 🛡️ Security
- **Local Processing**: LLMs run on your infrastructure
- **Encryption**: Data encrypted at rest and in transit
- **Rate Limiting**: Prevent resource abuse
- **Input Validation**: Sanitize all ML inputs
