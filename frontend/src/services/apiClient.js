/**
 * API Client Service for HTX Trading Platform
 * Provides centralized HTTP client with error handling, retries, and loading states
 */

import { buildUrl, REQUEST_CONFIG } from '../config/apiConfig.js';

// Error types for better error handling
export const ERROR_TYPES = {
  NETWORK_ERROR: 'NETWORK_ERROR',
  TIMEOUT_ERROR: 'TIMEOUT_ERROR',
  SERVER_ERROR: 'SERVER_ERROR',
  CLIENT_ERROR: 'CLIENT_ERROR',
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  AUTHENTICATION_ERROR: 'AUTHENTICATION_ERROR'
};

// Custom error class for API errors
export class ApiError extends Error {
  constructor(message, type, status, data = null) {
    super(message);
    this.name = 'ApiError';
    this.type = type;
    this.status = status;
    this.data = data;
    this.timestamp = new Date().toISOString();
  }
}

// Loading state manager
class LoadingManager {
  constructor() {
    this.activeRequests = new Set();
    this.listeners = new Set();
  }

  addRequest(requestId) {
    this.activeRequests.add(requestId);
    this.notifyListeners();
  }

  removeRequest(requestId) {
    this.activeRequests.delete(requestId);
    this.notifyListeners();
  }

  isLoading(requestId = null) {
    if (requestId) {
      return this.activeRequests.has(requestId);
    }
    return this.activeRequests.size > 0;
  }

  addListener(callback) {
    this.listeners.add(callback);
    return () => this.listeners.delete(callback);
  }

  notifyListeners() {
    this.listeners.forEach(callback => callback(this.isLoading()));
  }
}

// Global loading manager instance
export const loadingManager = new LoadingManager();

// Sleep utility for retry delays
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

// Retry wrapper with exponential backoff
async function withRetry(operation, config = REQUEST_CONFIG.retry) {
  let lastError;
  
  for (let attempt = 1; attempt <= config.attempts; attempt++) {
    try {
      return await operation();
    } catch (error) {
      lastError = error;
      
      // Don't retry client errors (4xx) or authentication errors
      if (error.status >= 400 && error.status < 500) {
        throw error;
      }
      
      // Don't retry on the last attempt
      if (attempt === config.attempts) {
        break;
      }
      
      // Calculate delay with exponential backoff
      const delay = config.delay * Math.pow(config.factor, attempt - 1);
      console.warn(`🔄 API request failed (attempt ${attempt}/${config.attempts}), retrying in ${delay}ms...`, error.message);
      await sleep(delay);
    }
  }
  
  throw lastError;
}

// Request interceptor for common headers and processing
function prepareRequest(url, options = {}) {
  const requestId = `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  
  const config = {
    ...REQUEST_CONFIG,
    ...options,
    headers: {
      ...REQUEST_CONFIG.headers,
      ...options.headers
    }
  };

  // Add request ID for tracking
  config.headers['X-Request-ID'] = requestId;
  
  return { config, requestId };
}

// Response interceptor for error handling and processing
async function processResponse(response, requestId) {
  const contentType = response.headers.get('content-type');
  let data;
  
  try {
    if (contentType && contentType.includes('application/json')) {
      data = await response.json();
    } else {
      data = await response.text();
    }
  } catch (parseError) {
    throw new ApiError(
      'Failed to parse response',
      ERROR_TYPES.SERVER_ERROR,
      response.status,
      { parseError: parseError.message }
    );
  }

  // Handle error responses
  if (!response.ok) {
    let errorType = ERROR_TYPES.SERVER_ERROR;
    let message = data?.message || data?.detail || `HTTP ${response.status}`;
    
    if (response.status >= 400 && response.status < 500) {
      errorType = response.status === 401 ? ERROR_TYPES.AUTHENTICATION_ERROR : ERROR_TYPES.CLIENT_ERROR;
    } else if (response.status >= 500) {
      errorType = ERROR_TYPES.SERVER_ERROR;
    }
    
    throw new ApiError(message, errorType, response.status, data);
  }

  return {
    data,
    status: response.status,
    headers: response.headers,
    requestId
  };
}

// Main API client class
class ApiClient {
  constructor() {
    this.abortControllers = new Map();
  }

  // Generic request method
  async request(endpoint, options = {}) {
    const url = buildUrl(endpoint);
    const { config, requestId } = prepareRequest(url, options);
    
    // Create abort controller for request cancellation
    const abortController = new AbortController();
    this.abortControllers.set(requestId, abortController);
    config.signal = abortController.signal;

    // Add to loading state
    loadingManager.addRequest(requestId);
    
    try {
      const response = await withRetry(async () => {
        const fetchResponse = await fetch(url, config);
        return fetchResponse;
      });
      
      const result = await processResponse(response, requestId);
      return result;
      
    } catch (error) {
      // Handle different error types
      if (error.name === 'AbortError') {
        throw new ApiError('Request was cancelled', ERROR_TYPES.NETWORK_ERROR, 0);
      } else if (error.name === 'TypeError' && error.message.includes('fetch')) {
        throw new ApiError('Network connection failed', ERROR_TYPES.NETWORK_ERROR, 0);
      } else if (error instanceof ApiError) {
        throw error;
      } else {
        throw new ApiError('Unknown error occurred', ERROR_TYPES.NETWORK_ERROR, 0, error);
      }
    } finally {
      // Cleanup
      loadingManager.removeRequest(requestId);
      this.abortControllers.delete(requestId);
    }
  }

  // HTTP method shortcuts
  async get(endpoint, params = {}, options = {}) {
    const url = new URL(buildUrl(endpoint));
    Object.keys(params).forEach(key => {
      if (params[key] !== undefined && params[key] !== null) {
        url.searchParams.append(key, params[key]);
      }
    });
    
    return this.request(url.pathname + url.search, {
      method: 'GET',
      ...options
    });
  }

  async post(endpoint, data = null, options = {}) {
    return this.request(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
      ...options
    });
  }

  async put(endpoint, data = null, options = {}) {
    return this.request(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
      ...options
    });
  }

  async delete(endpoint, options = {}) {
    return this.request(endpoint, {
      method: 'DELETE',
      ...options
    });
  }

  // File upload with form data
  async upload(endpoint, file, additionalData = {}, options = {}) {
    const formData = new FormData();
    formData.append('file', file);
    
    Object.keys(additionalData).forEach(key => {
      formData.append(key, additionalData[key]);
    });

    return this.request(endpoint, {
      method: 'POST',
      body: formData,
      headers: {
        // Don't set Content-Type for FormData, let browser set it with boundary
        ...options.headers
      },
      ...options
    });
  }

  // Cancel specific request
  cancelRequest(requestId) {
    const abortController = this.abortControllers.get(requestId);
    if (abortController) {
      abortController.abort();
      this.abortControllers.delete(requestId);
    }
  }

  // Cancel all pending requests
  cancelAllRequests() {
    this.abortControllers.forEach(controller => controller.abort());
    this.abortControllers.clear();
  }
}

// Create and export singleton instance
export const apiClient = new ApiClient();

// React hook for loading state
export function useApiLoading(requestId = null) {
  const [isLoading, setIsLoading] = React.useState(
    requestId ? loadingManager.isLoading(requestId) : loadingManager.isLoading()
  );

  React.useEffect(() => {
    const unsubscribe = loadingManager.addListener((loading) => {
      setIsLoading(requestId ? loadingManager.isLoading(requestId) : loading);
    });
    
    return unsubscribe;
  }, [requestId]);

  return isLoading;
}

// Helper for handling API errors in components
export function handleApiError(error, showNotification = null) {
  console.error('🚨 API Error:', error);
  
  let userMessage = 'An unexpected error occurred';
  
  if (error instanceof ApiError) {
    switch (error.type) {
      case ERROR_TYPES.NETWORK_ERROR:
        userMessage = 'Connection failed. Please check your internet connection.';
        break;
      case ERROR_TYPES.TIMEOUT_ERROR:
        userMessage = 'Request timed out. Please try again.';
        break;
      case ERROR_TYPES.AUTHENTICATION_ERROR:
        userMessage = 'Authentication failed. Please check your credentials.';
        break;
      case ERROR_TYPES.SERVER_ERROR:
        userMessage = 'Server error occurred. Please try again later.';
        break;
      case ERROR_TYPES.CLIENT_ERROR:
        userMessage = error.message || 'Invalid request. Please check your input.';
        break;
      default:
        userMessage = error.message || userMessage;
    }
  }
  
  // Show notification if provided
  if (showNotification) {
    showNotification(userMessage, 'error');
  }
  
  return userMessage;
}

export default apiClient;