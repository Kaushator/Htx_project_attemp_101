/**
 * Comprehensive Data Filters Component
 * Provides filtering capabilities for dates, symbols, trade types, and other criteria
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
  IconButton,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Slider,
  Switch,
  FormControlLabel,
  Autocomplete,
  Stack,
  Divider
} from '@mui/material';
import {
  FilterList,
  Clear,
  ExpandMore,
  DateRange,
  TrendingUp,
  TrendingDown,
  AttachMoney,
  ShowChart
} from '@mui/icons-material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';

const DataFilters = ({
  filters = {},
  onFiltersChange,
  availableSymbols = [],
  availableTradeTypes = ['buy', 'sell'],
  showAdvanced = true,
  compact = false
}) => {
  const [localFilters, setLocalFilters] = useState({
    // Date filters
    dateFrom: null,
    dateTo: null,
    dateRange: 'all', // 'all', '1d', '7d', '30d', '90d', 'custom'
    
    // Symbol filters
    symbols: [],
    symbolSearch: '',
    
    // Trade type filters
    tradeTypes: [],
    
    // Price filters
    priceMin: 0,
    priceMax: 100000,
    priceEnabled: false,
    
    // Volume filters
    volumeMin: 0,
    volumeMax: 10000000,
    volumeEnabled: false,
    
    // Change filters
    changeMin: -100,
    changeMax: 100,
    changeEnabled: false,
    onlyGainers: false,
    onlyLosers: false,
    
    // Advanced filters
    sortBy: 'timestamp',
    sortDirection: 'desc',
    limit: 100,
    
    ...filters
  });

  const [expanded, setExpanded] = useState(!compact);

  // Date range presets
  const dateRangeOptions = [
    { value: 'all', label: 'All Time' },
    { value: '1d', label: 'Last 24 Hours' },
    { value: '7d', label: 'Last 7 Days' },
    { value: '30d', label: 'Last 30 Days' },
    { value: '90d', label: 'Last 90 Days' },
    { value: 'custom', label: 'Custom Range' }
  ];

  const sortOptions = [
    { value: 'timestamp', label: 'Date' },
    { value: 'symbol', label: 'Symbol' },
    { value: 'price', label: 'Price' },
    { value: 'volume', label: 'Volume' },
    { value: 'change24h', label: '24h Change' }
  ];

  // Update local filters when props change
  useEffect(() => {
    setLocalFilters(prev => ({ ...prev, ...filters }));
  }, [filters]);

  // Apply date range preset
  useEffect(() => {
    if (localFilters.dateRange !== 'custom') {
      const now = new Date();
      let from = null;
      
      switch (localFilters.dateRange) {
        case '1d':
          from = new Date(now.getTime() - 24 * 60 * 60 * 1000);
          break;
        case '7d':
          from = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
          break;
        case '30d':
          from = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
          break;
        case '90d':
          from = new Date(now.getTime() - 90 * 24 * 60 * 60 * 1000);
          break;
        default:
          from = null;
      }
      
      updateFilter('dateFrom', from);
      updateFilter('dateTo', localFilters.dateRange === 'all' ? null : now);
    }
  }, [localFilters.dateRange]);

  const updateFilter = (key, value) => {
    const newFilters = { ...localFilters, [key]: value };
    setLocalFilters(newFilters);
    onFiltersChange?.(newFilters);
  };

  const clearAllFilters = () => {
    const clearedFilters = {
      dateFrom: null,
      dateTo: null,
      dateRange: 'all',
      symbols: [],
      symbolSearch: '',
      tradeTypes: [],
      priceMin: 0,
      priceMax: 100000,
      priceEnabled: false,
      volumeMin: 0,
      volumeMax: 10000000,
      volumeEnabled: false,
      changeMin: -100,
      changeMax: 100,
      changeEnabled: false,
      onlyGainers: false,
      onlyLosers: false,
      sortBy: 'timestamp',
      sortDirection: 'desc',
      limit: 100
    };
    setLocalFilters(clearedFilters);
    onFiltersChange?.(clearedFilters);
  };

  const getActiveFiltersCount = () => {
    let count = 0;
    if (localFilters.dateRange !== 'all') count++;
    if (localFilters.symbols.length > 0) count++;
    if (localFilters.tradeTypes.length > 0) count++;
    if (localFilters.priceEnabled) count++;
    if (localFilters.volumeEnabled) count++;
    if (localFilters.changeEnabled) count++;
    if (localFilters.onlyGainers || localFilters.onlyLosers) count++;
    return count;
  };

  if (compact) {
    return (
      <Card variant="outlined">
        <CardContent sx={{ py: 1 }}>
          <Stack direction="row" spacing={2} alignItems="center" flexWrap="wrap">
            <FormControl size="small" sx={{ minWidth: 120 }}>
              <InputLabel>Date Range</InputLabel>
              <Select
                value={localFilters.dateRange}
                onChange={(e) => updateFilter('dateRange', e.target.value)}
                label="Date Range"
              >
                {dateRangeOptions.map(option => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <Autocomplete
              multiple
              size="small"
              sx={{ minWidth: 200 }}
              options={availableSymbols}
              value={localFilters.symbols}
              onChange={(event, newValue) => updateFilter('symbols', newValue)}
              renderTags={(value, getTagProps) =>
                value.map((option, index) => (
                  <Chip variant="outlined" label={option} size="small" {...getTagProps({ index })} />
                ))
              }
              renderInput={(params) => (
                <TextField {...params} variant="outlined" label="Symbols" placeholder="Select symbols" />
              )}
            />

            <Button
              size="small"
              variant="outlined"
              startIcon={<FilterList />}
              onClick={() => setExpanded(!expanded)}
            >
              Filters ({getActiveFiltersCount()})
            </Button>

            {getActiveFiltersCount() > 0 && (
              <IconButton size="small" onClick={clearAllFilters} title="Clear all filters">
                <Clear />
              </IconButton>
            )}
          </Stack>
        </CardContent>
      </Card>
    );
  }

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
            <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <FilterList />
              Data Filters
              {getActiveFiltersCount() > 0 && (
                <Chip label={`${getActiveFiltersCount()} active`} size="small" color="primary" />
              )}
            </Typography>
            
            <Stack direction="row" spacing={1}>
              <Button size="small" onClick={clearAllFilters} startIcon={<Clear />}>
                Clear All
              </Button>
            </Stack>
          </Box>

          <Grid container spacing={3}>
            {/* Date Filters */}
            <Grid item xs={12}>
              <Accordion expanded={expanded} onChange={() => setExpanded(!expanded)}>
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Typography sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <DateRange />
                    Date Range
                  </Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Grid container spacing={2}>
                    <Grid item xs={12} md={4}>
                      <FormControl fullWidth>
                        <InputLabel>Quick Select</InputLabel>
                        <Select
                          value={localFilters.dateRange}
                          onChange={(e) => updateFilter('dateRange', e.target.value)}
                          label="Quick Select"
                        >
                          {dateRangeOptions.map(option => (
                            <MenuItem key={option.value} value={option.value}>
                              {option.label}
                            </MenuItem>
                          ))}
                        </Select>
                      </FormControl>
                    </Grid>
                    
                    {localFilters.dateRange === 'custom' && (
                      <>
                        <Grid item xs={12} md={4}>
                          <DatePicker
                            label="From Date"
                            value={localFilters.dateFrom}
                            onChange={(date) => updateFilter('dateFrom', date)}
                            renderInput={(params) => <TextField {...params} fullWidth />}
                          />
                        </Grid>
                        <Grid item xs={12} md={4}>
                          <DatePicker
                            label="To Date"
                            value={localFilters.dateTo}
                            onChange={(date) => updateFilter('dateTo', date)}
                            renderInput={(params) => <TextField {...params} fullWidth />}
                          />
                        </Grid>
                      </>
                    )}
                  </Grid>
                </AccordionDetails>
              </Accordion>
            </Grid>

            {/* Symbol Filters */}
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle2" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <ShowChart />
                Symbols
              </Typography>
              <Autocomplete
                multiple
                options={availableSymbols}
                value={localFilters.symbols}
                onChange={(event, newValue) => updateFilter('symbols', newValue)}
                renderTags={(value, getTagProps) =>
                  value.map((option, index) => (
                    <Chip variant="outlined" label={option} {...getTagProps({ index })} />
                  ))
                }
                renderInput={(params) => (
                  <TextField
                    {...params}
                    variant="outlined"
                    placeholder="Search and select symbols"
                  />
                )}
              />
            </Grid>

            {/* Trade Type Filters */}
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle2" gutterBottom>
                Trade Types
              </Typography>
              <Autocomplete
                multiple
                options={availableTradeTypes}
                value={localFilters.tradeTypes}
                onChange={(event, newValue) => updateFilter('tradeTypes', newValue)}
                renderTags={(value, getTagProps) =>
                  value.map((option, index) => (
                    <Chip 
                      variant="outlined" 
                      label={option} 
                      color={option === 'buy' ? 'success' : 'error'}
                      {...getTagProps({ index })} 
                    />
                  ))
                }
                renderInput={(params) => (
                  <TextField
                    {...params}
                    variant="outlined"
                    placeholder="Select trade types"
                  />
                )}
              />
            </Grid>

            {/* Advanced Filters */}
            {showAdvanced && (
              <>
                <Grid item xs={12}>
                  <Divider sx={{ my: 1 }} />
                  <Typography variant="subtitle2" gutterBottom>
                    Advanced Filters
                  </Typography>
                </Grid>

                {/* Price Range */}
                <Grid item xs={12} md={4}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={localFilters.priceEnabled}
                        onChange={(e) => updateFilter('priceEnabled', e.target.checked)}
                      />
                    }
                    label={
                      <Typography sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <AttachMoney />
                        Price Range
                      </Typography>
                    }
                  />
                  {localFilters.priceEnabled && (
                    <Box sx={{ px: 2 }}>
                      <Slider
                        value={[localFilters.priceMin, localFilters.priceMax]}
                        onChange={(e, newValue) => {
                          updateFilter('priceMin', newValue[0]);
                          updateFilter('priceMax', newValue[1]);
                        }}
                        valueLabelDisplay="auto"
                        min={0}
                        max={100000}
                        step={100}
                      />
                      <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Typography variant="caption">${localFilters.priceMin}</Typography>
                        <Typography variant="caption">${localFilters.priceMax}</Typography>
                      </Box>
                    </Box>
                  )}
                </Grid>

                {/* Volume Range */}
                <Grid item xs={12} md={4}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={localFilters.volumeEnabled}
                        onChange={(e) => updateFilter('volumeEnabled', e.target.checked)}
                      />
                    }
                    label="Volume Range"
                  />
                  {localFilters.volumeEnabled && (
                    <Box sx={{ px: 2 }}>
                      <Slider
                        value={[localFilters.volumeMin, localFilters.volumeMax]}
                        onChange={(e, newValue) => {
                          updateFilter('volumeMin', newValue[0]);
                          updateFilter('volumeMax', newValue[1]);
                        }}
                        valueLabelDisplay="auto"
                        min={0}
                        max={10000000}
                        step={10000}
                      />
                    </Box>
                  )}
                </Grid>

                {/* Change Filters */}
                <Grid item xs={12} md={4}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={localFilters.changeEnabled}
                        onChange={(e) => updateFilter('changeEnabled', e.target.checked)}
                      />
                    }
                    label="24h Change Range"
                  />
                  {localFilters.changeEnabled && (
                    <Box sx={{ px: 2 }}>
                      <Slider
                        value={[localFilters.changeMin, localFilters.changeMax]}
                        onChange={(e, newValue) => {
                          updateFilter('changeMin', newValue[0]);
                          updateFilter('changeMax', newValue[1]);
                        }}
                        valueLabelDisplay="auto"
                        min={-100}
                        max={100}
                        step={1}
                      />
                    </Box>
                  )}
                </Grid>

                {/* Quick Filters */}
                <Grid item xs={12}>
                  <Stack direction="row" spacing={2}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={localFilters.onlyGainers}
                          onChange={(e) => {
                            updateFilter('onlyGainers', e.target.checked);
                            if (e.target.checked) updateFilter('onlyLosers', false);
                          }}
                          color="success"
                        />
                      }
                      label={
                        <Typography sx={{ display: 'flex', alignItems: 'center', gap: 1, color: 'success.main' }}>
                          <TrendingUp />
                          Only Gainers
                        </Typography>
                      }
                    />
                    
                    <FormControlLabel
                      control={
                        <Switch
                          checked={localFilters.onlyLosers}
                          onChange={(e) => {
                            updateFilter('onlyLosers', e.target.checked);
                            if (e.target.checked) updateFilter('onlyGainers', false);
                          }}
                          color="error"
                        />
                      }
                      label={
                        <Typography sx={{ display: 'flex', alignItems: 'center', gap: 1, color: 'error.main' }}>
                          <TrendingDown />
                          Only Losers
                        </Typography>
                      }
                    />
                  </Stack>
                </Grid>

                {/* Sorting */}
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth>
                    <InputLabel>Sort By</InputLabel>
                    <Select
                      value={localFilters.sortBy}
                      onChange={(e) => updateFilter('sortBy', e.target.value)}
                      label="Sort By"
                    >
                      {sortOptions.map(option => (
                        <MenuItem key={option.value} value={option.value}>
                          {option.label}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>

                <Grid item xs={12} md={6}>
                  <FormControl fullWidth>
                    <InputLabel>Sort Direction</InputLabel>
                    <Select
                      value={localFilters.sortDirection}
                      onChange={(e) => updateFilter('sortDirection', e.target.value)}
                      label="Sort Direction"
                    >
                      <MenuItem value="asc">Ascending</MenuItem>
                      <MenuItem value="desc">Descending</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
              </>
            )}
          </Grid>
        </CardContent>
      </Card>
    </LocalizationProvider>
  );
};

export default DataFilters;