/**
 * Advanced Chart Components for HTX Trading Platform
 * Provides multiple chart types for financial data visualization
 */

import React, { useMemo } from 'react';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
  ComposedChart
} from 'recharts';
import {
  Box,
  Card,
  CardContent,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Chip,
  useTheme
} from '@mui/material';
import { TrendingUp, TrendingDown } from '@mui/icons-material';

// Color palette for charts
const CHART_COLORS = [
  '#8884d8', '#82ca9d', '#ffc658', '#ff7300', '#00ff00',
  '#0088fe', '#00c49f', '#ffbb28', '#ff8042', '#8dd1e1'
];

// Price Line Chart Component
export const PriceLineChart = ({ data, title = "Price Chart", height = 300 }) => {
  const theme = useTheme();
  
  const formatPrice = (value) => `$${value?.toFixed(4) || '0'}`;
  const formatDate = (tickItem) => {
    const date = new Date(tickItem);
    return date.toLocaleDateString();
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          {title}
        </Typography>
        <ResponsiveContainer width="100%" height={height}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />
            <XAxis 
              dataKey="timestamp" 
              tickFormatter={formatDate}
              stroke={theme.palette.text.secondary}
            />
            <YAxis 
              tickFormatter={formatPrice}
              stroke={theme.palette.text.secondary}
            />
            <Tooltip 
              formatter={[formatPrice, 'Price']}
              labelFormatter={(label) => `Date: ${new Date(label).toLocaleString()}`}
              contentStyle={{
                backgroundColor: theme.palette.background.paper,
                border: `1px solid ${theme.palette.divider}`,
                borderRadius: theme.shape.borderRadius
              }}
            />
            <Line 
              type="monotone" 
              dataKey="price" 
              stroke={theme.palette.primary.main}
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4, stroke: theme.palette.primary.main, strokeWidth: 2 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};

// Candlestick Chart Component (using composed chart)
export const CandlestickChart = ({ data, title = "Candlestick Chart", height = 400 }) => {
  const theme = useTheme();
  
  const formatPrice = (value) => `$${value?.toFixed(4) || '0'}`;
  const formatVolume = (value) => {
    if (value >= 1e9) return `${(value / 1e9).toFixed(2)}B`;
    if (value >= 1e6) return `${(value / 1e6).toFixed(2)}M`;
    if (value >= 1e3) return `${(value / 1e3).toFixed(2)}K`;
    return value?.toFixed(2) || '0';
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          {title}
        </Typography>
        <ResponsiveContainer width="100%" height={height}>
          <ComposedChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />
            <XAxis 
              dataKey="timestamp"
              tickFormatter={(tickItem) => new Date(tickItem).toLocaleDateString()}
              stroke={theme.palette.text.secondary}
            />
            <YAxis 
              yAxisId="price"
              orientation="right"
              tickFormatter={formatPrice}
              stroke={theme.palette.text.secondary}
            />
            <YAxis 
              yAxisId="volume"
              orientation="left"
              tickFormatter={formatVolume}
              stroke={theme.palette.text.secondary}
            />
            <Tooltip 
              formatter={(value, name) => {
                if (name === 'Volume') return [formatVolume(value), name];
                return [formatPrice(value), name];
              }}
              labelFormatter={(label) => `Date: ${new Date(label).toLocaleString()}`}
              contentStyle={{
                backgroundColor: theme.palette.background.paper,
                border: `1px solid ${theme.palette.divider}`,
                borderRadius: theme.shape.borderRadius
              }}
            />
            <Bar 
              yAxisId="volume"
              dataKey="volume" 
              fill={theme.palette.action.hover}
              opacity={0.3}
            />
            <Line 
              yAxisId="price"
              type="monotone" 
              dataKey="high" 
              stroke={theme.palette.success.main}
              strokeWidth={1}
              dot={false}
            />
            <Line 
              yAxisId="price"
              type="monotone" 
              dataKey="low" 
              stroke={theme.palette.error.main}
              strokeWidth={1}
              dot={false}
            />
            <Line 
              yAxisId="price"
              type="monotone" 
              dataKey="close" 
              stroke={theme.palette.primary.main}
              strokeWidth={2}
              dot={false}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};

// Volume Chart Component
export const VolumeChart = ({ data, title = "Volume Chart", height = 250 }) => {
  const theme = useTheme();
  
  const formatVolume = (value) => {
    if (value >= 1e9) return `${(value / 1e9).toFixed(2)}B`;
    if (value >= 1e6) return `${(value / 1e6).toFixed(2)}M`;
    if (value >= 1e3) return `${(value / 1e3).toFixed(2)}K`;
    return value?.toFixed(2) || '0';
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          {title}
        </Typography>
        <ResponsiveContainer width="100%" height={height}>
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />
            <XAxis 
              dataKey="timestamp"
              tickFormatter={(tickItem) => new Date(tickItem).toLocaleDateString()}
              stroke={theme.palette.text.secondary}
            />
            <YAxis 
              tickFormatter={formatVolume}
              stroke={theme.palette.text.secondary}
            />
            <Tooltip 
              formatter={[formatVolume, 'Volume']}
              labelFormatter={(label) => `Date: ${new Date(label).toLocaleString()}`}
              contentStyle={{
                backgroundColor: theme.palette.background.paper,
                border: `1px solid ${theme.palette.divider}`,
                borderRadius: theme.shape.borderRadius
              }}
            />
            <Bar dataKey="volume" fill={theme.palette.secondary.main} />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};

// Portfolio Distribution Pie Chart
export const PortfolioPieChart = ({ data, title = "Portfolio Distribution", height = 300 }) => {
  const theme = useTheme();
  
  const renderLabel = ({ name, value, percent }) => {
    return `${name}: ${(percent * 100).toFixed(1)}%`;
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          {title}
        </Typography>
        <ResponsiveContainer width="100%" height={height}>
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={renderLabel}
              outerRadius={80}
              fill="#8884d8"
              dataKey="value"
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
              ))}
            </Pie>
            <Tooltip 
              formatter={(value, name) => [`$${value.toFixed(2)}`, name]}
              contentStyle={{
                backgroundColor: theme.palette.background.paper,
                border: `1px solid ${theme.palette.divider}`,
                borderRadius: theme.shape.borderRadius
              }}
            />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};

// P&L Area Chart
export const PnLAreaChart = ({ data, title = "Profit & Loss", height = 300 }) => {
  const theme = useTheme();
  
  const formatCurrency = (value) => `$${value?.toFixed(2) || '0'}`;

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          {title}
        </Typography>
        <ResponsiveContainer width="100%" height={height}>
          <AreaChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />
            <XAxis 
              dataKey="date"
              stroke={theme.palette.text.secondary}
            />
            <YAxis 
              tickFormatter={formatCurrency}
              stroke={theme.palette.text.secondary}
            />
            <Tooltip 
              formatter={[formatCurrency, 'P&L']}
              contentStyle={{
                backgroundColor: theme.palette.background.paper,
                border: `1px solid ${theme.palette.divider}`,
                borderRadius: theme.shape.borderRadius
              }}
            />
            <ReferenceLine y={0} stroke={theme.palette.text.secondary} strokeDasharray="2 2" />
            <Area 
              type="monotone" 
              dataKey="pnl" 
              stroke={theme.palette.primary.main}
              fill={theme.palette.primary.light}
              fillOpacity={0.3}
            />
          </AreaChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};

// Multi-Symbol Comparison Chart
export const MultiSymbolChart = ({ data, symbols, title = "Symbol Comparison", height = 350 }) => {
  const theme = useTheme();
  
  const formatPrice = (value) => `$${value?.toFixed(4) || '0'}`;

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          {title}
        </Typography>
        <Box sx={{ mb: 2, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
          {symbols.map((symbol, index) => (
            <Chip
              key={symbol}
              label={symbol.toUpperCase()}
              size="small"
              sx={{ 
                backgroundColor: CHART_COLORS[index % CHART_COLORS.length],
                color: 'white'
              }}
            />
          ))}
        </Box>
        <ResponsiveContainer width="100%" height={height}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />
            <XAxis 
              dataKey="timestamp"
              tickFormatter={(tickItem) => new Date(tickItem).toLocaleDateString()}
              stroke={theme.palette.text.secondary}
            />
            <YAxis 
              tickFormatter={formatPrice}
              stroke={theme.palette.text.secondary}
            />
            <Tooltip 
              formatter={(value, name) => [formatPrice(value), name.toUpperCase()]}
              labelFormatter={(label) => `Date: ${new Date(label).toLocaleString()}`}
              contentStyle={{
                backgroundColor: theme.palette.background.paper,
                border: `1px solid ${theme.palette.divider}`,
                borderRadius: theme.shape.borderRadius
              }}
            />
            <Legend />
            {symbols.map((symbol, index) => (
              <Line
                key={symbol}
                type="monotone"
                dataKey={symbol}
                stroke={CHART_COLORS[index % CHART_COLORS.length]}
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 4 }}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};

// Chart Type Selector Component
export const ChartTypeSelector = ({ currentType, onTypeChange, availableTypes }) => {
  return (
    <FormControl size="small" sx={{ minWidth: 150 }}>
      <InputLabel>Chart Type</InputLabel>
      <Select
        value={currentType}
        label="Chart Type"
        onChange={(e) => onTypeChange(e.target.value)}
      >
        {availableTypes.map((type) => (
          <MenuItem key={type.value} value={type.value}>
            {type.label}
          </MenuItem>
        ))}
      </Select>
    </FormControl>
  );
};

// Summary Statistics Component
export const ChartSummary = ({ data, symbol }) => {
  const theme = useTheme();
  
  const stats = useMemo(() => {
    if (!data || data.length === 0) return null;
    
    const prices = data.map(d => d.price || d.close).filter(p => p != null);
    const volumes = data.map(d => d.volume).filter(v => v != null);
    
    if (prices.length === 0) return null;
    
    const currentPrice = prices[prices.length - 1];
    const previousPrice = prices[prices.length - 2] || currentPrice;
    const change = currentPrice - previousPrice;
    const changePercent = previousPrice !== 0 ? (change / previousPrice) * 100 : 0;
    
    const high24h = Math.max(...prices);
    const low24h = Math.min(...prices);
    const avgVolume = volumes.length > 0 ? volumes.reduce((a, b) => a + b, 0) / volumes.length : 0;
    
    return {
      currentPrice,
      change,
      changePercent,
      high24h,
      low24h,
      avgVolume
    };
  }, [data]);

  if (!stats) return null;

  const isPositive = stats.change >= 0;

  return (
    <Card variant="outlined" sx={{ mb: 2 }}>
      <CardContent>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} sm={3}>
            <Box>
              <Typography variant="subtitle2" color="text.secondary">
                {symbol?.toUpperCase() || 'Price'}
              </Typography>
              <Typography variant="h6" fontWeight="bold">
                ${stats.currentPrice.toFixed(4)}
              </Typography>
            </Box>
          </Grid>
          
          <Grid item xs={12} sm={3}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              {isPositive ? <TrendingUp color="success" /> : <TrendingDown color="error" />}
              <Box>
                <Typography 
                  variant="body2" 
                  color={isPositive ? 'success.main' : 'error.main'}
                  fontWeight="bold"
                >
                  {isPositive ? '+' : ''}${stats.change.toFixed(4)}
                </Typography>
                <Typography 
                  variant="body2" 
                  color={isPositive ? 'success.main' : 'error.main'}
                >
                  ({isPositive ? '+' : ''}{stats.changePercent.toFixed(2)}%)
                </Typography>
              </Box>
            </Box>
          </Grid>
          
          <Grid item xs={12} sm={3}>
            <Box>
              <Typography variant="body2" color="text.secondary">
                24h High/Low
              </Typography>
              <Typography variant="body2">
                ${stats.high24h.toFixed(4)} / ${stats.low24h.toFixed(4)}
              </Typography>
            </Box>
          </Grid>
          
          <Grid item xs={12} sm={3}>
            <Box>
              <Typography variant="body2" color="text.secondary">
                Avg Volume
              </Typography>
              <Typography variant="body2">
                {stats.avgVolume >= 1e6 ? `${(stats.avgVolume / 1e6).toFixed(2)}M` : 
                 stats.avgVolume >= 1e3 ? `${(stats.avgVolume / 1e3).toFixed(2)}K` : 
                 stats.avgVolume.toFixed(2)}
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
};

export default {
  PriceLineChart,
  CandlestickChart,
  VolumeChart,
  PortfolioPieChart,
  PnLAreaChart,
  MultiSymbolChart,
  ChartTypeSelector,
  ChartSummary
};