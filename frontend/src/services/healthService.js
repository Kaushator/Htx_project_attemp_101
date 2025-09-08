/**
 * Health Service
 * Handles system health checks and status monitoring
 */

import { apiClient } from './apiClient.js';
import { ENDPOINTS } from '../config/apiConfig.js';

class HealthService {
  // Check overall system health
  async checkHealth() {
    try {
      const response = await apiClient.get(ENDPOINTS.HEALTH);
      return response.data;
    } catch (error) {
      console.error('Health check failed:', error);
      throw error;
    }
  }

  // Check if backend is accessible
  async checkBackendStatus() {
    try {
      const health = await this.checkHealth();
      return {
        isHealthy: health.status === 'healthy',
        message: health.message,
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      return {
        isHealthy: false,
        message: error.message || 'Backend not accessible',
        timestamp: new Date().toISOString()
      };
    }
  }

  // Periodic health monitoring
  startHealthMonitoring(callback, interval = 30000) {
    const monitor = async () => {
      const status = await this.checkBackendStatus();
      callback(status);
    };

    // Initial check
    monitor();
    
    // Set up interval
    const intervalId = setInterval(monitor, interval);
    
    // Return cleanup function
    return () => clearInterval(intervalId);
  }
}

// Export singleton instance
export const healthService = new HealthService();
export default healthService;