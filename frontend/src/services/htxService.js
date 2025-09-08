/**
 * HTX Exchange Service
 * Handles all HTX exchange related API calls
 */

import { apiClient } from './apiClient.js';
import { ENDPOINTS } from '../config/apiConfig.js';

class HTXService {
  // Get account balance from HTX
  async getBalance() {
    try {
      const response = await apiClient.get(ENDPOINTS.HTX.BALANCE);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch HTX balance:', error);
      throw error;
    }
  }

  // Get trading history from HTX
  async getTrades(params = {}) {
    try {
      const response = await apiClient.get(ENDPOINTS.HTX.TRADES, params);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch HTX trades:', error);
      throw error;
    }
  }

  // Get all available coins/currencies from HTX
  async getCoins(params = {}) {
    try {
      const response = await apiClient.get(ENDPOINTS.HTX.COINS, params);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch HTX coins:', error);
      throw error;
    }
  }

  // Get ticker data for a specific symbol
  async getTicker(symbol, params = {}) {
    try {
      const response = await apiClient.get(ENDPOINTS.HTX.TICKER(symbol), params);
      return response.data;
    } catch (error) {
      console.error(`Failed to fetch ticker for ${symbol}:`, error);
      throw error;
    }
  }

  // Get kline/candlestick data for a specific symbol
  async getKlines(symbol, params = {}) {
    try {
      const defaultParams = {
        period: '1day',
        size: 50,
        ...params
      };
      const response = await apiClient.get(ENDPOINTS.HTX.KLINES(symbol), defaultParams);
      return response.data;
    } catch (error) {
      console.error(`Failed to fetch klines for ${symbol}:`, error);
      throw error;
    }
  }

  // Get HTX reference data
  async getReferenceData(params = {}) {
    try {
      const response = await apiClient.get(ENDPOINTS.HTX.REFERENCE, params);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch HTX reference data:', error);
      throw error;
    }
  }
}

// Export singleton instance
export const htxService = new HTXService();
export default htxService;