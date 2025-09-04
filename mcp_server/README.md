# HTX Analytics Platform - MCP Server

## Overview
Model Context Protocol (MCP) server for HTX Analytics Platform providing AI-powered crypto analytics tools.

## Features
- Real-time market data analysis
- AI-powered forecasting
- Technical indicators calculation
- Portfolio risk analysis
- Trading signals generation
- CSV data processing

## Installation
\\\ash
cd mcp_server
pip install -r requirements.txt
\\\

## Usage

### Start MCP Server
\\\ash
python -m mcp_server
\\\

### Available Tools
- \nalyze_trading_data\: AI analysis of trading data
- \generate_forecast\: Generate market forecasts
- \calculate_technical_indicators\: RSI, MACD, Bollinger Bands
- \get_market_data\: Real-time market data
- \generate_trading_signals\: Trading recommendations
- \nalyze_portfolio_risk\: Portfolio risk metrics

### Configuration
Edit \config.json\ to customize MCP server settings:
\\\json
{
  \
mcpServers\: {
    \htx-analytics-platform\: {
      \command\: \python\,
      \args\: [\-m\, \mcp_server\],
      \cwd\: \E:/Htx_project_attemp_101\
    }
  }
}
\\\

## Integration
The MCP server integrates with HTX Analytics Platform backend services when available:
- OpenAI Service for AI analysis
- ML Analytics for technical indicators
- HTX Client for market data

Ready for production use!
