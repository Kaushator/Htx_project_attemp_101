/**
 * Trading-specific Filters Component
 * Specialized filters for trading data, orders, and market analysis
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Grid,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Typography,
  Button,
  ButtonGroup,
  Stack,
  Switch,
  FormControlLabel,
  Slider,
  Autocomplete,
  ToggleButton,
  ToggleButtonGroup
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  SwapHoriz,
  AccountBalance,
  Timeline,
  PieChart,
  Clear,
  Refresh
} from '@mui/icons-material';

const TradingFilters = ({
  filters = {},
  onFiltersChange,
  availablePairs = [],
  availableExchanges = ['HTX', 'Binance', 'Coinbase'],
  showRealTimeToggle = true
}) => {
  const [localFilters, setLocalFilters] = useState({
    // Trading pair filters
    tradingPairs: [],
    baseAssets: [],
    quoteAssets: [],
    
    // Order filters
    orderTypes: [], // 'market', 'limit', 'stop-loss', 'take-profit'
    orderSides: [], // 'buy', 'sell'
    orderStatuses: [], // 'open', 'filled', 'cancelled', 'partial'
    
    // Exchange filters
    exchanges: [],
    
    // Market filters
    marketCap: [0, 1000000000],
    marketCapEnabled: false,
    liquidity: [0, 10000000],
    liquidityEnabled: false,
    
    // Performance filters
    performanceType: 'all', // 'all', 'profitable', 'loss'
    minProfit: 0,
    maxLoss: 0,
    
    // Time-based filters
    timeframe: '1d', // '1h', '4h', '1d', '1w', '1M'
    candleCount: 100,
    
    // Real-time settings
    realTimeUpdates: true,
    updateInterval: 5000, // ms
    
    // Technical analysis filters
    rsiMin: 0,
    rsiMax: 100,
    rsiEnabled: false,
    
    ...filters
  });

  const orderTypeOptions = [
    { value: 'market', label: 'Market', icon: '⚡' },
    { value: 'limit', label: 'Limit', icon: '🎯' },
    { value: 'stop-loss', label: 'Stop Loss', icon: '🛑' },
    { value: 'take-profit', label: 'Take Profit', icon: '💰' }
  ];

  const orderStatusOptions = [
    { value: 'open', label: 'Open', color: 'primary' },
    { value: 'filled', label: 'Filled', color: 'success' },
    { value: 'cancelled', label: 'Cancelled', color: 'error' },
    { value: 'partial', label: 'Partial', color: 'warning' }
  ];

  const timeframeOptions = [
    { value: '1m', label: '1 Minute' },
    { value: '5m', label: '5 Minutes' },
    { value: '15m', label: '15 Minutes' },
    { value: '1h', label: '1 Hour' },
    { value: '4h', label: '4 Hours' },
    { value: '1d', label: '1 Day' },
    { value: '1w', label: '1 Week' },
    { value: '1M', label: '1 Month' }
  ];

  useEffect(() => {
    setLocalFilters(prev => ({ ...prev, ...filters }));
  }, [filters]);

  const updateFilter = (key, value) => {
    const newFilters = { ...localFilters, [key]: value };
    setLocalFilters(newFilters);
    onFiltersChange?.(newFilters);
  };

  const clearAllFilters = () => {
    const clearedFilters = {
      tradingPairs: [],
      baseAssets: [],
      quoteAssets: [],
      orderTypes: [],
      orderSides: [],
      orderStatuses: [],
      exchanges: [],
      marketCap: [0, 1000000000],
      marketCapEnabled: false,
      liquidity: [0, 10000000],
      liquidityEnabled: false,
      performanceType: 'all',
      minProfit: 0,
      maxLoss: 0,
      timeframe: '1d',
      candleCount: 100,
      realTimeUpdates: true,
      updateInterval: 5000,
      rsiMin: 0,
      rsiMax: 100,
      rsiEnabled: false
    };
    setLocalFilters(clearedFilters);
    onFiltersChange?.(clearedFilters);
  };

  // Extract unique base and quote assets from trading pairs
  const getUniqueAssets = (type) => {
    const assets = new Set();
    availablePairs.forEach(pair => {
      if (typeof pair === 'string') {
        const parts = pair.split('/') || pair.split('-') || pair.split('_');
        if (parts.length >= 2) {
          assets.add(type === 'base' ? parts[0] : parts[1]);
        }
      }
    });
    return Array.from(assets).sort();
  };

  const baseAssets = getUniqueAssets('base');
  const quoteAssets = getUniqueAssets('quote');

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <SwapHoriz />
            Trading Filters
          </Typography>
          
          <Stack direction="row" spacing={1}>
            <Button size="small" onClick={clearAllFilters} startIcon={<Clear />}>
              Clear All
            </Button>
            <Button size="small" startIcon={<Refresh />}>
              Refresh
            </Button>
          </Stack>
        </Box>

        <Grid container spacing={3}>
          {/* Trading Pairs */}
          <Grid item xs={12} md={6}>
            <Typography variant="subtitle2" gutterBottom>
              Trading Pairs
            </Typography>
            <Autocomplete
              multiple
              options={availablePairs}
              value={localFilters.tradingPairs}
              onChange={(event, newValue) => updateFilter('tradingPairs', newValue)}
              renderTags={(value, getTagProps) =>
                value.map((option, index) => (
                  <Chip variant="outlined" label={option} size="small" {...getTagProps({ index })} />
                ))
              }
              renderInput={(params) => (
                <TextField
                  {...params}
                  variant="outlined"
                  placeholder="Select trading pairs"
                  size="small"
                />
              )}
            />
          </Grid>

          {/* Base Assets */}
          <Grid item xs={12} md={3}>
            <Typography variant="subtitle2" gutterBottom>
              Base Assets
            </Typography>
            <Autocomplete
              multiple
              options={baseAssets}
              value={localFilters.baseAssets}
              onChange={(event, newValue) => updateFilter('baseAssets', newValue)}
              renderTags={(value, getTagProps) =>
                value.map((option, index) => (
                  <Chip variant="outlined" label={option} size="small" {...getTagProps({ index })} />
                ))
              }
              renderInput={(params) => (
                <TextField
                  {...params}
                  variant="outlined"
                  placeholder="Base assets"
                  size="small"
                />
              )}
            />
          </Grid>

          {/* Quote Assets */}
          <Grid item xs={12} md={3}>
            <Typography variant="subtitle2" gutterBottom>
              Quote Assets
            </Typography>
            <Autocomplete
              multiple
              options={quoteAssets}
              value={localFilters.quoteAssets}
              onChange={(event, newValue) => updateFilter('quoteAssets', newValue)}
              renderTags={(value, getTagProps) =>
                value.map((option, index) => (
                  <Chip variant="outlined" label={option} size="small" {...getTagProps({ index })} />
                ))
              }
              renderInput={(params) => (
                <TextField
                  {...params}
                  variant="outlined"
                  placeholder="Quote assets"
                  size="small"
                />
              )}
            />
          </Grid>

          {/* Order Sides */}
          <Grid item xs={12} md={6}>
            <Typography variant="subtitle2" gutterBottom>
              Order Sides
            </Typography>
            <ToggleButtonGroup
              value={localFilters.orderSides}
              onChange={(e, newSides) => updateFilter('orderSides', newSides)}
              aria-label="order sides"
            >
              <ToggleButton value="buy" color="success">
                <TrendingUp sx={{ mr: 1 }} />
                Buy Orders
              </ToggleButton>
              <ToggleButton value="sell" color="error">
                <TrendingDown sx={{ mr: 1 }} />
                Sell Orders
              </ToggleButton>
            </ToggleButtonGroup>
          </Grid>

          {/* Order Types */}
          <Grid item xs={12} md={6}>
            <Typography variant="subtitle2" gutterBottom>
              Order Types
            </Typography>
            <Stack direction="row" spacing={1} flexWrap="wrap">
              {orderTypeOptions.map(option => (
                <Chip
                  key={option.value}
                  label={`${option.icon} ${option.label}`}
                  variant={localFilters.orderTypes.includes(option.value) ? "filled" : "outlined"}
                  onClick={() => {
                    const newTypes = localFilters.orderTypes.includes(option.value)
                      ? localFilters.orderTypes.filter(t => t !== option.value)
                      : [...localFilters.orderTypes, option.value];
                    updateFilter('orderTypes', newTypes);
                  }}
                  color="primary"
                />
              ))}
            </Stack>
          </Grid>

          {/* Order Status */}
          <Grid item xs={12}>
            <Typography variant="subtitle2" gutterBottom>
              Order Status
            </Typography>
            <Stack direction="row" spacing={1} flexWrap="wrap">
              {orderStatusOptions.map(option => (
                <Chip
                  key={option.value}
                  label={option.label}
                  variant={localFilters.orderStatuses.includes(option.value) ? "filled" : "outlined"}
                  onClick={() => {
                    const newStatuses = localFilters.orderStatuses.includes(option.value)
                      ? localFilters.orderStatuses.filter(s => s !== option.value)
                      : [...localFilters.orderStatuses, option.value];
                    updateFilter('orderStatuses', newStatuses);
                  }}
                  color={option.color}
                />
              ))}
            </Stack>
          </Grid>

          {/* Performance Filter */}
          <Grid item xs={12} md={4}>
            <Typography variant="subtitle2" gutterBottom>
              Performance Filter
            </Typography>
            <ToggleButtonGroup
              value={localFilters.performanceType}
              exclusive
              onChange={(e, newType) => newType && updateFilter('performanceType', newType)}
              aria-label="performance type"
              size="small"
            >
              <ToggleButton value="all">
                <PieChart sx={{ mr: 1 }} />
                All
              </ToggleButton>
              <ToggleButton value="profitable" color="success">
                <TrendingUp sx={{ mr: 1 }} />
                Profitable
              </ToggleButton>
              <ToggleButton value="loss" color="error">
                <TrendingDown sx={{ mr: 1 }} />
                Loss
              </ToggleButton>
            </ToggleButtonGroup>
          </Grid>

          {/* Timeframe */}
          <Grid item xs={12} md={4}>
            <FormControl fullWidth size="small">
              <InputLabel>Timeframe</InputLabel>
              <Select
                value={localFilters.timeframe}
                onChange={(e) => updateFilter('timeframe', e.target.value)}
                label="Timeframe"
                startAdornment={<Timeline />}
              >
                {timeframeOptions.map(option => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          {/* Candle Count */}
          <Grid item xs={12} md={4}>
            <Typography variant="subtitle2" gutterBottom>
              Candle Count: {localFilters.candleCount}
            </Typography>
            <Slider
              value={localFilters.candleCount}
              onChange={(e, newValue) => updateFilter('candleCount', newValue)}
              min={10}
              max={1000}
              step={10}
              valueLabelDisplay="auto"
            />
          </Grid>

          {/* Exchanges */}
          <Grid item xs={12} md={6}>
            <Typography variant="subtitle2" gutterBottom>
              Exchanges
            </Typography>
            <Autocomplete
              multiple
              options={availableExchanges}
              value={localFilters.exchanges}
              onChange={(event, newValue) => updateFilter('exchanges', newValue)}
              renderTags={(value, getTagProps) =>
                value.map((option, index) => (
                  <Chip 
                    variant="outlined" 
                    label={option} 
                    size="small" 
                    icon={<AccountBalance />}
                    {...getTagProps({ index })} 
                  />
                ))
              }
              renderInput={(params) => (
                <TextField
                  {...params}
                  variant="outlined"
                  placeholder="Select exchanges"
                  size="small"
                />
              )}
            />
          </Grid>

          {/* Real-time Settings */}
          {showRealTimeToggle && (
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle2" gutterBottom>
                Real-time Settings
              </Typography>
              <Stack spacing={2}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={localFilters.realTimeUpdates}
                      onChange={(e) => updateFilter('realTimeUpdates', e.target.checked)}
                    />
                  }
                  label="Enable Real-time Updates"
                />
                
                {localFilters.realTimeUpdates && (
                  <Box>
                    <Typography variant="caption" gutterBottom display="block">
                      Update Interval: {localFilters.updateInterval / 1000}s
                    </Typography>
                    <Slider
                      value={localFilters.updateInterval}
                      onChange={(e, newValue) => updateFilter('updateInterval', newValue)}
                      min={1000}
                      max={60000}
                      step={1000}
                      valueLabelFormat={(value) => `${value / 1000}s`}
                      valueLabelDisplay="auto"
                    />
                  </Box>
                )}
              </Stack>
            </Grid>
          )}

          {/* Advanced Market Filters */}
          <Grid item xs={12}>
            <Typography variant="subtitle2" gutterBottom>
              Advanced Market Filters
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={localFilters.marketCapEnabled}
                      onChange={(e) => updateFilter('marketCapEnabled', e.target.checked)}
                    />
                  }
                  label="Market Cap Filter"
                />
                {localFilters.marketCapEnabled && (
                  <Box sx={{ px: 2 }}>
                    <Slider
                      value={localFilters.marketCap}
                      onChange={(e, newValue) => updateFilter('marketCap', newValue)}
                      valueLabelDisplay="auto"
                      min={0}
                      max={1000000000}
                      step={1000000}
                      valueLabelFormat={(value) => `$${(value / 1000000).toFixed(0)}M`}
                    />
                  </Box>
                )}
              </Grid>

              <Grid item xs={12} md={6}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={localFilters.rsiEnabled}
                      onChange={(e) => updateFilter('rsiEnabled', e.target.checked)}
                    />
                  }
                  label="RSI Filter"
                />
                {localFilters.rsiEnabled && (
                  <Box sx={{ px: 2 }}>
                    <Slider
                      value={[localFilters.rsiMin, localFilters.rsiMax]}
                      onChange={(e, newValue) => {
                        updateFilter('rsiMin', newValue[0]);
                        updateFilter('rsiMax', newValue[1]);
                      }}
                      valueLabelDisplay="auto"
                      min={0}
                      max={100}
                      step={1}
                    />
                  </Box>
                )}
              </Grid>
            </Grid>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
};

export default TradingFilters;