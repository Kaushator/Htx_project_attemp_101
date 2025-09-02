/**
 * Enhanced Token Analytics with Comprehensive Filters
 * Demonstrates usage of advanced filtering, global error handling and loading states
 */

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import {
  Box, Typography, Grid, TextField, Card, CardContent, 
  Table, TableBody, TableCell, TableContainer, TableHead, 
  TableRow, Paper, InputAdornment, IconButton, Chip, 
  Tabs, Tab, Tooltip, Button, TableSortLabel, Pagination
} from '@mui/material';
import {
  Search, Refresh, CloudUpload, TrendingUp, TrendingDown,
  Star, StarOutline, GetApp, FilterList
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';

// Import the new components and hooks
import { InlineLoading, useGlobalLoading, useRequestLoading } from '../components/GlobalLoading';
import { useNotifications } from '../components/NotificationSystem';
import { htxService } from '../services/htxService';
import { ApiError } from '../services/apiClient';
import DataFilters from '../components/filters/DataFilters';
import useDataFilters from '../hooks/useDataFilters';
import { AdvancedExportButton, MultiExportButton } from '../components/export/ExportButton';

// Styled components
const PriceChange = styled(Box)(({ theme, value }) => ({
  color: value > 0 ? theme.palette.success.main : value < 0 ? theme.palette.error.main : 'inherit',
  display: 'flex',
  alignItems: 'center',
}));

const FormatVolume = ({ volume }) => {
  if (!volume) return '0';
  if (volume >= 1e9) return `$${(volume / 1e9).toFixed(2)}B`;
  if (volume >= 1e6) return `$${(volume / 1e6).toFixed(2)}M`;
  if (volume >= 1e3) return `$${(volume / 1e3).toFixed(2)}K`;
  return `$${volume.toFixed(2)}`;
};

const EnhancedTokenAnalytics = () => {
  // State management
  const [currencies, setCurrencies] = useState([]);
  const [loading, setLoading] = useState(false);
  const [tabValue, setTabValue] = useState(0);
  const [favorites, setFavorites] = useState([]);
  const [showFilters, setShowFilters] = useState(false);

  // Global hooks
  const { showSuccess, showError, showWarning, handleApiError } = useNotifications();
  const isGlobalLoading = useGlobalLoading();

  // Enhanced data with favorites
  const enhancedCurrencies = useMemo(() => {
    return currencies.map(currency => ({
      ...currency,
      isFavorite: favorites.includes(currency.symbol),
      timestamp: new Date().toISOString() // Add timestamp for filtering
    }));
  }, [currencies, favorites]);

  // Filter hook
  const {
    filters,
    filteredData,
    paginatedData,
    filterStats,
    updateFilters,
    updateFilter,
    clearFilters,
    getUniqueValues,
    quickFilters,
    exportFilteredData,
    nextPage,
    prevPage,
    goToPage
  } = useDataFilters(enhancedCurrencies, {
    sortBy: 'volume24h',
    sortDirection: 'desc',
    pageSize: 20
  });

  // Available symbols for filtering
  const availableSymbols = useMemo(() => 
    getUniqueValues('symbol'),
    [getUniqueValues]
  );

  // Load data on component mount
  useEffect(() => {
    fetchCurrencies();
    loadFavorites();
  }, []);

  // Load favorites from localStorage
  const loadFavorites = () => {
    try {
      const savedFavorites = localStorage.getItem('favorite_tokens');
      if (savedFavorites) {
        setFavorites(JSON.parse(savedFavorites));
      }
    } catch (error) {
      showWarning('Failed to load favorites from storage');
    }
  };

  // Fetch currencies with proper error handling
  const fetchCurrencies = useCallback(async () => {
    setLoading(true);
    
    try {
      const response = await htxService.getCoins();
      
      if (response?.coins) {
        setCurrencies(response.coins);
        showSuccess(`Loaded ${response.coins.length} currencies successfully`);
      } else {
        showWarning('No currency data received from API');
        setCurrencies([]);
      }
      
    } catch (error) {
      console.error('Failed to fetch currencies:', error);
      
      // Use the global error handler
      if (error instanceof ApiError) {
        handleApiError(error, 'Failed to load currency data');
      } else {
        showError('Failed to load currency data. Please try again.');
      }
      
      // Set empty array on error
      setCurrencies([]);
    } finally {
      setLoading(false);
    }
  }, [showSuccess, showError, showWarning, handleApiError]);

  // Toggle favorite with persistence
  const toggleFavorite = useCallback((symbol) => {
    try {
      const newFavorites = favorites.includes(symbol)
        ? favorites.filter(f => f !== symbol)
        : [...favorites, symbol];
      
      setFavorites(newFavorites);
      localStorage.setItem('favorite_tokens', JSON.stringify(newFavorites));
      
      const action = newFavorites.includes(symbol) ? 'added to' : 'removed from';
      showSuccess(`${symbol} ${action} favorites`);
      
    } catch (error) {
      showError('Failed to update favorites');
    }
  }, [favorites, showSuccess, showError]);

  // Handle sorting
  const handleSort = useCallback((property) => {
    const isAsc = filters.sortBy === property && filters.sortDirection === 'asc';
    updateFilter('sortDirection', isAsc ? 'desc' : 'asc');
    updateFilter('sortBy', property);
  }, [filters.sortBy, filters.sortDirection, updateFilter]);

  // Handle tab changes
  const handleTabChange = useCallback((event, newValue) => {
    setTabValue(newValue);
    if (newValue === 1) {
      updateFilter('onlyFavorites', true);
    } else {
      updateFilter('onlyFavorites', false);
    }
  }, [updateFilter]);

  // Export data function
  const handleExport = useCallback((format) => {
    try {
      const data = exportFilteredData(format);
      const blob = new Blob([data], { 
        type: format === 'csv' ? 'text/csv' : 'application/json' 
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `token_analytics_${new Date().toISOString().split('T')[0]}.${format}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      
      showSuccess(`Data exported as ${format.toUpperCase()}`);
    } catch (error) {
      showError('Failed to export data');
    }
  }, [exportFilteredData, showSuccess, showError]);

  // Prepare export data with additional metadata
  const getExportData = useCallback(() => {
    return displayedCurrencies.map(currency => ({
      symbol: currency.symbol,
      name: currency.name || currency.symbol,
      price: currency.price || 0,
      change_24h: currency.change24h || 0,
      volume_24h: currency.volume24h || 0,
      is_favorite: currency.isFavorite,
      markets_count: currency.markets?.length || 0,
      export_timestamp: new Date().toISOString()
    }));
  }, [displayedCurrencies]);

  // Filter and sort currencies based on tabs
  const displayedCurrencies = useMemo(() => {
    const tabFiltered = tabValue === 1 
      ? filteredData.filter(currency => currency.isFavorite)
      : filteredData;
    
    return tabFiltered;
  }, [filteredData, tabValue]);

  // Calculate summary statistics from filtered data
  const totalVolume = useMemo(() => 
    displayedCurrencies.reduce((sum, curr) => sum + (curr.volume24h || 0), 0),
    [displayedCurrencies]
  );
  
  const positiveCount = useMemo(() => 
    displayedCurrencies.filter(curr => (curr.change24h || 0) > 0).length,
    [displayedCurrencies]
  );
  
  const negativeCount = useMemo(() => 
    displayedCurrencies.filter(curr => (curr.change24h || 0) < 0).length,
    [displayedCurrencies]
  );

  return (
    <Box sx={{ padding: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Enhanced Token Analytics
        </Typography>
        
        <Box>
          <Tooltip title="Refresh data">
            <IconButton 
              onClick={fetchCurrencies} 
              disabled={loading || isGlobalLoading}
            >
              <Refresh />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Total Tokens
              </Typography>
              <Typography variant="h4">
                {currencies.length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Total Volume (24h)
              </Typography>
              <Typography variant="h4">
                <FormatVolume volume={totalVolume} />
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom color="success.main">
                Gaining
              </Typography>
              <Typography variant="h4" color="success.main">
                {positiveCount}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom color="error.main">
                Losing
              </Typography>
              <Typography variant="h4" color="error.main">
                {negativeCount}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Filters and Controls */}
      <Box sx={{ mb: 3 }}>
        {/* Quick Controls */}
        <Card sx={{ mb: 2 }}>
          <CardContent sx={{ py: 2 }}>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  placeholder="Search tokens..."
                  value={filters.searchTerm || ''}
                  onChange={(e) => updateFilter('searchTerm', e.target.value)}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <Search />
                      </InputAdornment>
                    ),
                  }}
                  size="small"
                />
              </Grid>
              
              <Grid item xs={12} md={4}>
                <Tabs value={tabValue} onChange={handleTabChange}>
                  <Tab label={`All (${filterStats.filtered})`} />
                  <Tab label={`Favorites (${favorites.length})`} />
                </Tabs>
              </Grid>
              
              <Grid item xs={12} md={4}>
                <Box sx={{ display: 'flex', gap: 1, justifyContent: 'flex-end' }}>
                  <Button
                    size="small"
                    variant="outlined"
                    startIcon={<FilterList />}
                    onClick={() => setShowFilters(!showFilters)}
                  >
                    Advanced Filters
                  </Button>
                  
                  <MultiExportButton
                    data={getExportData()}
                    filename={`token_analytics_${new Date().toISOString().split('T')[0]}`}
                    formats={['csv', 'json']}
                    size="small"
                  />
                  
                  <AdvancedExportButton
                    data={getExportData()}
                    title="Token Analytics Export"
                    filename={`token_analytics_${new Date().toISOString().split('T')[0]}`}
                    size="small"
                  />
                </Box>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
        
        {/* Advanced Filters */}
        {showFilters && (
          <DataFilters
            filters={filters}
            onFiltersChange={updateFilters}
            availableSymbols={availableSymbols}
            showAdvanced={true}
          />
        )}
        
        {/* Filter Summary */}
        {filterStats.filtered !== filterStats.total && (
          <Card variant="outlined" sx={{ mb: 2 }}>
            <CardContent sx={{ py: 1 }}>
              <Typography variant="body2" color="text.secondary">
                Showing {filterStats.filtered} of {filterStats.total} tokens 
                ({filterStats.filtered_percentage}% of total)
                {filters.searchTerm && ` • Search: "${filters.searchTerm}"`}
                {filters.symbols.length > 0 && ` • Symbols: ${filters.symbols.join(', ')}`}
              </Typography>
            </CardContent>
          </Card>
        )}
      </Box>

      {/* Data Table */}
      <InlineLoading 
        loading={loading}
        message="Loading currency data..."
        minHeight={300}
      >
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Favorite</TableCell>
                
                <TableCell>
                  <TableSortLabel
                    active={filters.sortBy === 'symbol'}
                    direction={filters.sortBy === 'symbol' ? filters.sortDirection : 'asc'}
                    onClick={() => handleSort('symbol')}
                  >
                    Symbol
                  </TableSortLabel>
                </TableCell>
                
                <TableCell align="right">
                  <TableSortLabel
                    active={filters.sortBy === 'price'}
                    direction={filters.sortBy === 'price' ? filters.sortDirection : 'asc'}
                    onClick={() => handleSort('price')}
                  >
                    Price
                  </TableSortLabel>
                </TableCell>
                
                <TableCell align="right">
                  <TableSortLabel
                    active={filters.sortBy === 'change24h'}
                    direction={filters.sortBy === 'change24h' ? filters.sortDirection : 'asc'}
                    onClick={() => handleSort('change24h')}
                  >
                    24h Change
                  </TableSortLabel>
                </TableCell>
                
                <TableCell align="right">
                  <TableSortLabel
                    active={filters.sortBy === 'volume24h'}
                    direction={filters.sortBy === 'volume24h' ? filters.sortDirection : 'asc'}
                    onClick={() => handleSort('volume24h')}
                  >
                    Volume (24h)
                  </TableSortLabel>
                </TableCell>
                
                <TableCell>Markets</TableCell>
              </TableRow>
            </TableHead>
            
            <TableBody>
              {displayedCurrencies.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} align="center">
                    <Typography variant="body2" color="text.secondary" sx={{ py: 4 }}>
                      {filters.searchTerm ? 'No tokens match your search criteria' : 
                       filterStats.total === 0 ? 'No token data available' :
                       'No tokens match the selected filters'}
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                paginatedData.map((currency) => (
                  <TableRow key={currency.symbol} hover>
                    <TableCell>
                      <IconButton
                        size="small"
                        onClick={() => toggleFavorite(currency.symbol)}
                      >
                        {currency.isFavorite ? (
                          <Star color="warning" />
                        ) : (
                          <StarOutline />
                        )}
                      </IconButton>
                    </TableCell>
                    
                    <TableCell>
                      <Box>
                        <Typography variant="body1" fontWeight="bold">
                          {currency.symbol}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {currency.name || currency.symbol}
                        </Typography>
                      </Box>
                    </TableCell>
                    
                    <TableCell align="right">
                      <Typography variant="body1">
                        ${(currency.price || 0).toFixed(4)}
                      </Typography>
                    </TableCell>
                    
                    <TableCell align="right">
                      <PriceChange value={currency.change24h || 0}>
                        {(currency.change24h || 0) > 0 ? <TrendingUp /> : <TrendingDown />}
                        <Typography variant="body2" sx={{ ml: 0.5 }}>
                          {(currency.change24h || 0).toFixed(2)}%
                        </Typography>
                      </PriceChange>
                    </TableCell>
                    
                    <TableCell align="right">
                      <FormatVolume volume={currency.volume24h || 0} />
                    </TableCell>
                    
                    <TableCell>
                      <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                        {currency.markets?.slice(0, 3).map((market, index) => (
                          <Chip
                            key={index}
                            label={market.pair}
                            size="small"
                            variant="outlined"
                          />
                        ))}
                        {currency.markets?.length > 3 && (
                          <Chip
                            label={`+${currency.markets.length - 3}`}
                            size="small"
                            variant="outlined"
                          />
                        )}
                      </Box>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
        
        {/* Pagination */}
        {filterStats.pages > 1 && (
          <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
            <Pagination
              count={filterStats.pages}
              page={filterStats.currentPage}
              onChange={(event, page) => goToPage(page - 1)}
              color="primary"
              showFirstButton
              showLastButton
            />
          </Box>
        )}
      </InlineLoading>
    </Box>
  );
};

export default EnhancedTokenAnalytics;