/**
 * Comprehensive Filter Hook
 * Manages filter state and provides filtered data with advanced filtering logic
 */

import { useState, useMemo, useCallback } from 'react';

// Filter utilities
const filterUtils = {
  // Date filtering
  isWithinDateRange: (itemDate, dateFrom, dateTo) => {
    if (!itemDate) return true;
    const date = new Date(itemDate);
    const from = dateFrom ? new Date(dateFrom) : null;
    const to = dateTo ? new Date(dateTo) : null;
    
    if (from && date < from) return false;
    if (to && date > to) return false;
    return true;
  },

  // Symbol filtering
  matchesSymbols: (item, symbols) => {
    if (!symbols || symbols.length === 0) return true;
    const itemSymbol = item.symbol || item.pair || item.name;
    return symbols.some(symbol => 
      itemSymbol?.toLowerCase().includes(symbol.toLowerCase())
    );
  },

  // Price range filtering
  isWithinPriceRange: (price, min, max, enabled) => {
    if (!enabled || price === undefined || price === null) return true;
    return price >= min && price <= max;
  },

  // Volume range filtering
  isWithinVolumeRange: (volume, min, max, enabled) => {
    if (!enabled || volume === undefined || volume === null) return true;
    return volume >= min && volume <= max;
  },

  // Change filtering
  isWithinChangeRange: (change, min, max, enabled, onlyGainers, onlyLosers) => {
    if (change === undefined || change === null) return true;
    
    if (onlyGainers && change <= 0) return false;
    if (onlyLosers && change >= 0) return false;
    
    if (!enabled) return true;
    return change >= min && change <= max;
  },

  // Trade type filtering
  matchesTradeTypes: (item, tradeTypes) => {
    if (!tradeTypes || tradeTypes.length === 0) return true;
    const side = item.side || item.type || item.direction;
    return tradeTypes.includes(side);
  },

  // Order status filtering
  matchesOrderStatuses: (item, statuses) => {
    if (!statuses || statuses.length === 0) return true;
    const status = item.status || item.state;
    return statuses.includes(status);
  },

  // Exchange filtering
  matchesExchanges: (item, exchanges) => {
    if (!exchanges || exchanges.length === 0) return true;
    const exchange = item.exchange || item.source;
    return exchanges.includes(exchange);
  }
};

// Sorting utilities
const sortUtils = {
  sortData: (data, sortBy, sortDirection) => {
    if (!sortBy) return data;
    
    return [...data].sort((a, b) => {
      let aValue = a[sortBy];
      let bValue = b[sortBy];
      
      // Handle different data types
      if (typeof aValue === 'string') {
        aValue = aValue.toLowerCase();
        bValue = bValue?.toLowerCase() || '';
      }
      
      if (aValue === undefined || aValue === null) aValue = 0;
      if (bValue === undefined || bValue === null) bValue = 0;
      
      let result = 0;
      if (aValue < bValue) result = -1;
      else if (aValue > bValue) result = 1;
      
      return sortDirection === 'desc' ? -result : result;
    });
  }
};

// Main hook
const useDataFilters = (data = [], initialFilters = {}) => {
  const [filters, setFilters] = useState({
    // Date filters
    dateFrom: null,
    dateTo: null,
    dateRange: 'all',
    
    // Search and symbols
    searchTerm: '',
    symbols: [],
    
    // Trade filters
    tradeTypes: [],
    orderStatuses: [],
    exchanges: [],
    
    // Range filters
    priceMin: 0,
    priceMax: 100000,
    priceEnabled: false,
    volumeMin: 0,
    volumeMax: 10000000,
    volumeEnabled: false,
    changeMin: -100,
    changeMax: 100,
    changeEnabled: false,
    
    // Quick filters
    onlyGainers: false,
    onlyLosers: false,
    onlyFavorites: false,
    
    // Sorting
    sortBy: 'timestamp',
    sortDirection: 'desc',
    limit: 100,
    
    // Pagination
    page: 0,
    pageSize: 50,
    
    ...initialFilters
  });

  // Update filters function
  const updateFilters = useCallback((newFilters) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
  }, []);

  const updateFilter = useCallback((key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  }, []);

  const clearFilters = useCallback(() => {
    setFilters({
      dateFrom: null,
      dateTo: null,
      dateRange: 'all',
      searchTerm: '',
      symbols: [],
      tradeTypes: [],
      orderStatuses: [],
      exchanges: [],
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
      onlyFavorites: false,
      sortBy: 'timestamp',
      sortDirection: 'desc',
      limit: 100,
      page: 0,
      pageSize: 50
    });
  }, []);

  // Apply all filters to data
  const filteredData = useMemo(() => {
    if (!data || data.length === 0) return [];

    let result = data.filter(item => {
      // Search term filter
      if (filters.searchTerm) {
        const searchTerm = filters.searchTerm.toLowerCase();
        const searchableText = [
          item.symbol,
          item.name,
          item.pair,
          item.currency
        ].filter(Boolean).join(' ').toLowerCase();
        
        if (!searchableText.includes(searchTerm)) return false;
      }

      // Date range filter
      if (!filterUtils.isWithinDateRange(
        item.timestamp || item.date || item.created_at,
        filters.dateFrom,
        filters.dateTo
      )) {
        return false;
      }

      // Symbol filter
      if (!filterUtils.matchesSymbols(item, filters.symbols)) {
        return false;
      }

      // Trade type filter
      if (!filterUtils.matchesTradeTypes(item, filters.tradeTypes)) {
        return false;
      }

      // Order status filter
      if (!filterUtils.matchesOrderStatuses(item, filters.orderStatuses)) {
        return false;
      }

      // Exchange filter
      if (!filterUtils.matchesExchanges(item, filters.exchanges)) {
        return false;
      }

      // Price range filter
      if (!filterUtils.isWithinPriceRange(
        item.price,
        filters.priceMin,
        filters.priceMax,
        filters.priceEnabled
      )) {
        return false;
      }

      // Volume range filter
      if (!filterUtils.isWithinVolumeRange(
        item.volume || item.volume24h,
        filters.volumeMin,
        filters.volumeMax,
        filters.volumeEnabled
      )) {
        return false;
      }

      // Change range filter
      if (!filterUtils.isWithinChangeRange(
        item.change24h || item.change,
        filters.changeMin,
        filters.changeMax,
        filters.changeEnabled,
        filters.onlyGainers,
        filters.onlyLosers
      )) {
        return false;
      }

      // Favorites filter
      if (filters.onlyFavorites && !item.isFavorite) {
        return false;
      }

      return true;
    });

    // Apply sorting
    result = sortUtils.sortData(result, filters.sortBy, filters.sortDirection);

    // Apply limit
    if (filters.limit && filters.limit > 0) {
      result = result.slice(0, filters.limit);
    }

    return result;
  }, [data, filters]);

  // Paginated data
  const paginatedData = useMemo(() => {
    const startIndex = filters.page * filters.pageSize;
    const endIndex = startIndex + filters.pageSize;
    return filteredData.slice(startIndex, endIndex);
  }, [filteredData, filters.page, filters.pageSize]);

  // Filter statistics
  const filterStats = useMemo(() => {
    const total = data.length;
    const filtered = filteredData.length;
    const filtered_percentage = total > 0 ? (filtered / total * 100).toFixed(1) : 0;
    
    return {
      total,
      filtered,
      filtered_percentage,
      pages: Math.ceil(filtered / filters.pageSize),
      currentPage: filters.page + 1
    };
  }, [data.length, filteredData.length, filters.page, filters.pageSize]);

  // Get unique values for filter options
  const getUniqueValues = useCallback((field) => {
    if (!data || data.length === 0) return [];
    
    const values = new Set();
    data.forEach(item => {
      const value = item[field];
      if (value !== undefined && value !== null && value !== '') {
        values.add(value);
      }
    });
    
    return Array.from(values).sort();
  }, [data]);

  // Quick filter functions
  const quickFilters = {
    showGainersOnly: () => updateFilter('onlyGainers', true),
    showLosersOnly: () => updateFilter('onlyLosers', true),
    showAll: () => updateFilters({ onlyGainers: false, onlyLosers: false }),
    sortByPrice: () => updateFilter('sortBy', 'price'),
    sortByVolume: () => updateFilter('sortBy', 'volume24h'),
    sortByChange: () => updateFilter('sortBy', 'change24h'),
    setTimeRange: (range) => updateFilter('dateRange', range)
  };

  // Export functions
  const exportFilteredData = useCallback((format = 'json') => {
    const dataToExport = {
      filters,
      stats: filterStats,
      data: filteredData
    };

    if (format === 'csv') {
      // Convert to CSV format
      if (filteredData.length === 0) return '';
      
      const headers = Object.keys(filteredData[0]).join(',');
      const rows = filteredData.map(item => 
        Object.values(item).map(value => 
          typeof value === 'string' ? `"${value}"` : value
        ).join(',')
      );
      
      return [headers, ...rows].join('\n');
    }

    return JSON.stringify(dataToExport, null, 2);
  }, [filters, filterStats, filteredData]);

  return {
    // State
    filters,
    filteredData,
    paginatedData,
    filterStats,
    
    // Actions
    updateFilters,
    updateFilter,
    clearFilters,
    
    // Utilities
    getUniqueValues,
    quickFilters,
    exportFilteredData,
    
    // Pagination helpers
    nextPage: () => updateFilter('page', Math.min(filters.page + 1, filterStats.pages - 1)),
    prevPage: () => updateFilter('page', Math.max(filters.page - 1, 0)),
    goToPage: (page) => updateFilter('page', Math.max(0, Math.min(page, filterStats.pages - 1))),
  };
};

export default useDataFilters;