/**
 * API Configuration for HTX Trading Platform
 * Centralizes all API endpoint configurations and environment-based settings
 */

// Environment-based configuration with fallbacks
const API_CONFIG = {
  // Base API URL - uses environment variable or defaults to Docker backend
  BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
  
  // WebSocket URL for real-time data
  WS_URL: import.meta.env.VITE_WS_URL || 'ws://localhost:8000/api/v1/ws',
  
  // Request timeout in milliseconds
  TIMEOUT: parseInt(import.meta.env.VITE_API_TIMEOUT) || 15000,
  
  // Feature flags
  FEATURES: {
    REAL_TIME: import.meta.env.VITE_ENABLE_REAL_TIME === 'true',
    ML_FEATURES: import.meta.env.VITE_ENABLE_ML_FEATURES === 'true',
    ADVANCED_ANALYTICS: import.meta.env.VITE_ENABLE_ADVANCED_ANALYTICS === 'true',
    SECRET_MANAGER: import.meta.env.VITE_ENABLE_SECRET_MANAGER === 'true',
    EXPORT: import.meta.env.VITE_ENABLE_EXPORT === 'true'
  },
  
  // Development settings
  DEV_MODE: import.meta.env.VITE_DEV_MODE === 'true',
  LOG_LEVEL: import.meta.env.VITE_LOG_LEVEL || 'info'
};

// API endpoint paths
export const ENDPOINTS = {
  // Core endpoints
  HEALTH: '/health',
  
  // HTX Exchange endpoints
  HTX: {
    BALANCE: '/htx/balance',
    TRADES: '/htx/trades', 
    COINS: '/htx/coins',
    TICKER: (symbol) => `/htx/ticker/${symbol}`,
    KLINES: (symbol) => `/htx/klines/${symbol}`,
    REFERENCE: '/htx/reference'
  },
  
  // Trading data endpoints
  TRADES: {
    LIST: '/trades',
    UPLOAD: '/trades/upload',
    ANALYSIS: '/trades/analysis'
  },
  
  // File management endpoints
  FILES: {
    UPLOAD: '/files/upload',
    LIST: '/files',
    DELETE: (id) => `/files/${id}`,
    DOWNLOAD: (id) => `/files/${id}/download`
  },
  
  // Analytics endpoints
  ANALYTICS: {
    PNL: '/pnl',
    ADVANCED_PNL: '/advanced-pnl',
    INSIGHTS: '/insights',
    ANALYZE_FILE: (id) => `/insights/analyze-file/${id}`,
    CASHFLOW: '/cashflow'
  },
  
  // Order management endpoints
  ORDERS: {
    LIST: '/orders',
    CREATE: '/orders',
    CANCEL: (id) => `/orders/${id}/cancel`,
    HISTORY: '/orders/history'
  },
  
  // WebSocket endpoint
  WEBSOCKET: {
    LIVE: '/live',
    DASHBOARD: '/dashboard'
  },
  
  // Secret Manager endpoints (when enabled)
  SECRETS: {
    SETUP: '/secrets/setup',
    STATUS: '/secrets/status',
    VALIDATE: '/secrets/validate',
    TEST: (service) => `/secrets/test/${service}`
  },
  
  // Machine Learning endpoints (when enabled)
  ML: {
    MODELS: '/ml/models',
    PREDICT: '/ml/predict',
    ANALYTICS: '/ml/analytics'
  }
};

// Helper function to build full URL
export const buildUrl = (endpoint) => {
  return `${API_CONFIG.BASE_URL}${endpoint}`;
};

// Helper function to build WebSocket URL
export const buildWsUrl = (endpoint = '') => {
  return `${API_CONFIG.WS_URL}${endpoint}`;
};

// Request configuration defaults
export const REQUEST_CONFIG = {
  timeout: API_CONFIG.TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
  // Retry configuration
  retry: {
    attempts: 3,
    delay: 1000, // Start with 1 second
    factor: 2    // Exponential backoff
  }
};

// Export main configuration
export default API_CONFIG;

// Development helper to log configuration
if (API_CONFIG.DEV_MODE && API_CONFIG.LOG_LEVEL === 'debug') {
  console.log('🔧 API Configuration Loaded:', {
    baseUrl: API_CONFIG.BASE_URL,
    wsUrl: API_CONFIG.WS_URL,
    timeout: API_CONFIG.TIMEOUT,
    features: API_CONFIG.FEATURES
  });
}