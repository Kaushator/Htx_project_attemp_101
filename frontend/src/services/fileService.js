/**
 * File Service
 * Handles file upload, download, and management operations
 */

import { apiClient } from './apiClient.js';
import { ENDPOINTS } from '../config/apiConfig.js';

class FileService {
  // Upload a file
  async uploadFile(file, additionalData = {}) {
    try {
      const response = await apiClient.upload(ENDPOINTS.FILES.UPLOAD, file, additionalData);
      return response.data;
    } catch (error) {
      console.error('Failed to upload file:', error);
      throw error;
    }
  }

  // Get list of uploaded files
  async getFiles(params = {}) {
    try {
      const response = await apiClient.get(ENDPOINTS.FILES.LIST, params);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch files:', error);
      throw error;
    }
  }

  // Delete a file
  async deleteFile(fileId) {
    try {
      const response = await apiClient.delete(ENDPOINTS.FILES.DELETE(fileId));
      return response.data;
    } catch (error) {
      console.error(`Failed to delete file ${fileId}:`, error);
      throw error;
    }
  }

  // Download a file
  async downloadFile(fileId) {
    try {
      const response = await apiClient.get(ENDPOINTS.FILES.DOWNLOAD(fileId), {}, {
        headers: {
          'Accept': 'application/octet-stream'
        }
      });
      return response.data;
    } catch (error) {
      console.error(`Failed to download file ${fileId}:`, error);
      throw error;
    }
  }

  // Validate file before upload
  validateFile(file, options = {}) {
    const {
      maxSize = 50 * 1024 * 1024, // 50MB default
      allowedTypes = ['.csv', '.xlsx', '.xls'],
      requireExtension = true
    } = options;

    const errors = [];

    // Check file size
    if (file.size > maxSize) {
      errors.push(`File size (${(file.size / 1024 / 1024).toFixed(2)}MB) exceeds maximum allowed size (${(maxSize / 1024 / 1024)}MB)`);
    }

    // Check file type
    if (requireExtension) {
      const fileName = file.name.toLowerCase();
      const hasValidExtension = allowedTypes.some(type => fileName.endsWith(type.toLowerCase()));
      
      if (!hasValidExtension) {
        errors.push(`File type not supported. Allowed types: ${allowedTypes.join(', ')}`);
      }
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }

  // Get file type icon
  getFileIcon(filename) {
    const extension = filename.toLowerCase().split('.').pop();
    
    const iconMap = {
      'csv': '📊',
      'xlsx': '📈',
      'xls': '📈',
      'json': '🗂️',
      'pdf': '📄',
      'txt': '📝'
    };

    return iconMap[extension] || '📁';
  }

  // Format file size
  formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }
}

// Export singleton instance
export const fileService = new FileService();
export default fileService;