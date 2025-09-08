import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8004/api/v1';

// Custom hook for Advanced PnL Analytics
export const useAdvancedPnL = (days = 30) => {
  const [data, setData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await axios.get(
        `${API_BASE_URL}/advanced-pnl/comprehensive?days=${days}`
      );
      
      setData(response.data);
    } catch (err) {
      setError(err);
      console.error('Error fetching advanced PnL:', err);
    } finally {
      setIsLoading(false);
    }
  }, [days]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return {
    data,
    isLoading,
    error,
    refetch: fetchData
  };
};

// Hook for summary data
export const usePnLSummary = (days = 7) => {
  const [data, setData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = useCallback(async () => {
    try {
      setIsLoading(true);
      const response = await axios.get(
        `${API_BASE_URL}/advanced-pnl/summary?days=${days}`
      );
      setData(response.data);
    } catch (err) {
      setError(err);
    } finally {
      setIsLoading(false);
    }
  }, [days]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { data, isLoading, error, refetch: fetchData };
};

// Hook for health check
export const useHealthCheck = () => {
  const [isHealthy, setIsHealthy] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/health`);
        setIsHealthy(response.status === 200);
      } catch (err) {
        setIsHealthy(false);
      } finally {
        setIsLoading(false);
      }
    };

    checkHealth();
  }, []);

  return { isHealthy, isLoading };
};

// Hook for file upload
export const useFileUpload = () => {
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState(null);

  const uploadFile = async (file, onProgress) => {
    try {
      setIsUploading(true);
      setError(null);

      const formData = new FormData();
      formData.append('file', file);

      const response = await axios.post(
        `${API_BASE_URL}/files/upload`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          onUploadProgress: (progressEvent) => {
            if (onProgress) {
              const progress = Math.round(
                (progressEvent.loaded * 100) / progressEvent.total
              );
              onProgress(progress);
            }
          },
        }
      );

      return response.data;
    } catch (err) {
      setError(err);
      throw err;
    } finally {
      setIsUploading(false);
    }
  };

  return {
    uploadFile,
    isUploading,
    error
  };
};

// Hook for trades data
export const useTrades = (params = {}) => {
  const [data, setData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = useCallback(async () => {
    try {
      setIsLoading(true);
      const queryString = new URLSearchParams(params).toString();
      const response = await axios.get(
        `${API_BASE_URL}/trades?${queryString}`
      );
      setData(response.data);
    } catch (err) {
      setError(err);
    } finally {
      setIsLoading(false);
    }
  }, [params]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { data, isLoading, error, refetch: fetchData };
};

// WebSocket hook for real-time updates
export const useWebSocket = (url = 'ws://127.0.0.1:8004/ws/live') => {
  const [socket, setSocket] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [messages, setMessages] = useState([]);

  useEffect(() => {
    const ws = new WebSocket(url);
    
    ws.onopen = () => {
      setIsConnected(true);
      console.log('WebSocket connected');
    };
    
    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        setMessages(prev => [...prev.slice(-9), message]); // Keep last 10 messages
      } catch (err) {
        console.error('Error parsing WebSocket message:', err);
      }
    };
    
    ws.onclose = () => {
      setIsConnected(false);
      console.log('WebSocket disconnected');
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
    
    setSocket(ws);
    
    return () => {
      ws.close();
    };
  }, [url]);

  const sendMessage = (message) => {
    if (socket && isConnected) {
      socket.send(JSON.stringify(message));
    }
  };

  return {
    isConnected,
    messages,
    sendMessage
  };
};
