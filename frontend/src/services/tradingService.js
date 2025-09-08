/**
 * Trading Service
 * Handles trading data, P&L calculations, and analytics
 */

import { apiClient } from './apiClient.js';
import { ENDPOINTS } from '../config/apiConfig.js';

class TradingService {
  // Get trades from database
  async getTrades(params = {}) {
    try {
      const defaultParams = {
        limit: 100,
        offset: 0,
        ...params
      };
      const response = await apiClient.get(ENDPOINTS.TRADES.LIST, defaultParams);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch trades:', error);
      throw error;
    }
  }

  // Get P&L data
  async getPnL(params = {}) {
    try {
      const response = await apiClient.get(ENDPOINTS.ANALYTICS.PNL, params);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch P&L data:', error);
      throw error;
    }
  }

  // Get advanced P&L analytics
  async getAdvancedPnL(params = {}) {
    try {
      const response = await apiClient.get(ENDPOINTS.ANALYTICS.ADVANCED_PNL, params);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch advanced P&L:', error);
      throw error;
    }
  }

  // Get cashflow data
  async getCashflow(params = {}) {
    try {
      const response = await apiClient.get(ENDPOINTS.ANALYTICS.CASHFLOW, params);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch cashflow data:', error);
      throw error;
    }
  }

  // Get trading insights
  async getInsights(params = {}) {
    try {
      const response = await apiClient.get(ENDPOINTS.ANALYTICS.INSIGHTS, params);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch insights:', error);
      throw error;
    }
  }

  // Analyze uploaded file
  async analyzeFile(fileId, params = {}) {
    try {
      const response = await apiClient.get(ENDPOINTS.ANALYTICS.ANALYZE_FILE(fileId), params);
      return response.data;
    } catch (error) {
      console.error(`Failed to analyze file ${fileId}:`, error);
      throw error;
    }
  }
}

// Export singleton instance
export const tradingService = new TradingService();
export default tradingService;