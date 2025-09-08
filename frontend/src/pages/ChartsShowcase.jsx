/**
 * Charts Showcase Page
 * Demonstrates all available chart types with sample data
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  Stack,
  Chip,
  Divider
} from '@mui/material';
import { Refresh, Timeline, BarChart, PieChart } from '@mui/icons-material';

import {
  PriceLineChart,
  CandlestickChart,
  VolumeChart,
  PortfolioPieChart,
  PnLAreaChart,
  MultiSymbolChart,
  ChartTypeSelector,
  ChartSummary
} from '../components/charts/ChartComponents';

import { htxService } from '../services/htxService';
import { useNotifications } from '../components/NotificationSystem';
import { InlineLoading } from '../components/GlobalLoading';

// Generate sample data for charts
const generateSampleData = (days = 30) => {
  const data = [];
  const startDate = new Date();
  startDate.setDate(startDate.getDate() - days);
  
  let basePrice = 45000; // Starting price for BTC
  
  for (let i = 0; i < days; i++) {
    const date = new Date(startDate);
    date.setDate(date.getDate() + i);
    
    // Generate realistic price movements
    const change = (Math.random() - 0.5) * 0.1; // ±5% daily change
    basePrice *= (1 + change);
    
    const high = basePrice * (1 + Math.random() * 0.05);
    const low = basePrice * (1 - Math.random() * 0.05);
    const volume = 1000000 + Math.random() * 5000000;
    
    data.push({
      timestamp: date.toISOString(),
      date: date.toLocaleDateString(),
      price: basePrice,
      close: basePrice,
      high: high,
      low: low,
      open: basePrice * (1 + (Math.random() - 0.5) * 0.02),
      volume: volume
    });
  }
  
  return data;
};

// Generate portfolio data
const generatePortfolioData = () => [
  { name: 'BTC', value: 45000, percent: 45 },
  { name: 'ETH', value: 25000, percent: 25 },
  { name: 'ADA', value: 12000, percent: 12 },
  { name: 'DOT', value: 8000, percent: 8 },
  { name: 'Others', value: 10000, percent: 10 }
];

// Generate P&L data
const generatePnLData = (days = 30) => {
  const data = [];
  let cumulativePnL = 0;
  
  for (let i = 0; i < days; i++) {
    const date = new Date();
    date.setDate(date.getDate() - (days - i));
    
    const dailyPnL = (Math.random() - 0.5) * 2000; // ±$1000 daily P&L
    cumulativePnL += dailyPnL;
    
    data.push({
      date: date.toLocaleDateString(),
      pnl: cumulativePnL,
      dailyPnL: dailyPnL
    });
  }
  
  return data;
};

// Generate multi-symbol data
const generateMultiSymbolData = (days = 30) => {
  const symbols = ['btcusdt', 'ethusdt', 'adausdt', 'dotusdt'];
  const data = [];
  
  const basePrices = {
    btcusdt: 45000,
    ethusdt: 3000,
    adausdt: 0.5,
    dotusdt: 25
  };
  
  for (let i = 0; i < days; i++) {
    const date = new Date();
    date.setDate(date.getDate() - (days - i));
    
    const dataPoint = {
      timestamp: date.toISOString(),
      date: date.toLocaleDateString()
    };
    
    symbols.forEach(symbol => {
      const change = (Math.random() - 0.5) * 0.1;
      basePrices[symbol] *= (1 + change);
      dataPoint[symbol] = basePrices[symbol];
    });
    
    data.push(dataPoint);
  }
  
  return data;
};

const ChartsShowcase = () => {
  const [selectedChart, setSelectedChart] = useState('line');
  const [selectedSymbol, setSelectedSymbol] = useState('btcusdt');
  const [loading, setLoading] = useState(false);
  const [realData, setRealData] = useState(null);
  
  const { showSuccess, showError } = useNotifications();
  
  // Sample data
  const sampleData = generateSampleData();
  const portfolioData = generatePortfolioData();
  const pnlData = generatePnLData();
  const multiSymbolData = generateMultiSymbolData();
  
  const chartTypes = [
    { value: 'line', label: 'Line Chart', icon: <Timeline /> },
    { value: 'candlestick', label: 'Candlestick', icon: <BarChart /> },
    { value: 'volume', label: 'Volume Chart', icon: <BarChart /> },
    { value: 'portfolio', label: 'Portfolio Pie', icon: <PieChart /> },
    { value: 'pnl', label: 'P&L Area Chart', icon: <Timeline /> },
    { value: 'comparison', label: 'Multi-Symbol', icon: <Timeline /> }
  ];
  
  const symbols = ['btcusdt', 'ethusdt', 'adausdt', 'dotusdt', 'bnbusdt'];
  
  // Load real data from API
  const loadRealData = async () => {
    setLoading(true);
    try {
      const response = await htxService.getCoins();
      if (response?.coins) {
        setRealData(response.coins);
        showSuccess('Loaded real market data');
      }
    } catch (error) {
      showError('Failed to load real data');
    } finally {
      setLoading(false);
    }
  };
  
  useEffect(() => {
    loadRealData();
  }, []);
  
  const renderChart = () => {
    const currentData = realData ? 
      realData.slice(0, 30).map((coin, index) => ({
        timestamp: new Date(Date.now() - (30 - index) * 24 * 60 * 60 * 1000).toISOString(),
        price: coin.price || Math.random() * 1000,
        volume: coin.volume24h || Math.random() * 1000000,
        high: (coin.price || 100) * 1.05,
        low: (coin.price || 100) * 0.95,
        close: coin.price || Math.random() * 1000,
        open: (coin.price || 100) * (1 + (Math.random() - 0.5) * 0.02)
      })) : sampleData;
    
    switch (selectedChart) {
      case 'line':
        return (
          <>
            <ChartSummary data={currentData} symbol={selectedSymbol} />
            <PriceLineChart 
              data={currentData} 
              title={`${selectedSymbol.toUpperCase()} Price Chart`}
              height={400}
            />
          </>
        );
      
      case 'candlestick':
        return (
          <>
            <ChartSummary data={currentData} symbol={selectedSymbol} />
            <CandlestickChart 
              data={currentData} 
              title={`${selectedSymbol.toUpperCase()} Candlestick Chart`}
              height={500}
            />
          </>
        );
      
      case 'volume':
        return (
          <VolumeChart 
            data={currentData} 
            title={`${selectedSymbol.toUpperCase()} Volume Analysis`}
            height={350}
          />
        );
      
      case 'portfolio':
        return (
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <PortfolioPieChart 
                data={portfolioData} 
                title="Portfolio Distribution"
                height={400}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Portfolio Summary
                  </Typography>
                  <Stack spacing={2}>
                    {portfolioData.map((item, index) => (
                      <Box key={item.name} sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Box 
                            sx={{ 
                              width: 16, 
                              height: 16, 
                              borderRadius: 1,
                              backgroundColor: ['#8884d8', '#82ca9d', '#ffc658', '#ff7300', '#00ff00'][index]
                            }} 
                          />
                          <Typography variant="body2" fontWeight="bold">
                            {item.name}
                          </Typography>
                        </Box>
                        <Box sx={{ textAlign: 'right' }}>
                          <Typography variant="body2" fontWeight="bold">
                            ${item.value.toLocaleString()}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            {item.percent}%
                          </Typography>
                        </Box>
                      </Box>
                    ))}
                  </Stack>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        );
      
      case 'pnl':
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <PnLAreaChart 
                data={pnlData} 
                title="Profit & Loss Analysis"
                height={400}
              />
            </Grid>
          </Grid>
        );
      
      case 'comparison':
        return (
          <MultiSymbolChart 
            data={multiSymbolData}
            symbols={['btcusdt', 'ethusdt', 'adausdt']}
            title="Multi-Symbol Price Comparison"
            height={450}
          />
        );
      
      default:
        return <Typography>Select a chart type</Typography>;
    }
  };
  
  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" gutterBottom>
          Advanced Charts Showcase
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Interactive financial charts with real-time data support
        </Typography>
      </Box>
      
      {/* Controls */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth size="small">
                <InputLabel>Chart Type</InputLabel>
                <Select
                  value={selectedChart}
                  label="Chart Type"
                  onChange={(e) => setSelectedChart(e.target.value)}
                >
                  {chartTypes.map((type) => (
                    <MenuItem key={type.value} value={type.value}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {type.icon}
                        {type.label}
                      </Box>
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth size="small">
                <InputLabel>Symbol</InputLabel>
                <Select
                  value={selectedSymbol}
                  label="Symbol"
                  onChange={(e) => setSelectedSymbol(e.target.value)}
                  disabled={selectedChart === 'portfolio' || selectedChart === 'pnl' || selectedChart === 'comparison'}
                >
                  {symbols.map((symbol) => (
                    <MenuItem key={symbol} value={symbol}>
                      {symbol.toUpperCase()}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <Button
                variant="outlined"
                startIcon={<Refresh />}
                onClick={loadRealData}
                disabled={loading}
                fullWidth
              >
                {loading ? 'Loading...' : 'Refresh Data'}
              </Button>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <Stack direction="row" spacing={1}>
                <Chip 
                  label={realData ? 'Live Data' : 'Sample Data'} 
                  color={realData ? 'success' : 'default'}
                  size="small"
                />
                <Chip 
                  label={`${sampleData.length} Points`} 
                  variant="outlined"
                  size="small"
                />
              </Stack>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
      
      {/* Chart Display */}
      <InlineLoading loading={loading} message="Loading chart data...">
        {renderChart()}
      </InlineLoading>
      
      {/* Chart Features Info */}
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Chart Features
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={4}>
              <Typography variant="subtitle2" gutterBottom>
                Interactive Elements
              </Typography>
              <Typography variant="body2" color="text.secondary">
                • Hover tooltips with detailed data<br/>
                • Responsive design for all screen sizes<br/>
                • Real-time data updates<br/>
                • Zoom and pan capabilities
              </Typography>
            </Grid>
            <Grid item xs={12} sm={6} md={4}>
              <Typography variant="subtitle2" gutterBottom>
                Data Sources
              </Typography>
              <Typography variant="body2" color="text.secondary">
                • HTX Exchange API integration<br/>
                • Historical price data<br/>
                • Volume and market indicators<br/>
                • Portfolio analytics
              </Typography>
            </Grid>
            <Grid item xs={12} sm={6} md={4}>
              <Typography variant="subtitle2" gutterBottom>
                Chart Types
              </Typography>
              <Typography variant="body2" color="text.secondary">
                • Line charts for price trends<br/>
                • Candlestick for OHLC data<br/>
                • Volume analysis charts<br/>
                • Portfolio distribution views
              </Typography>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    </Box>
  );
};

export default ChartsShowcase;