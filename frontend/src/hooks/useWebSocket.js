/**
 * React Hooks for WebSocket Integration
 * Provides easy-to-use hooks for WebSocket functionality
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { wsService, WS_STATES, WS_EVENTS } from '../services/websocketService.js';

// Hook for WebSocket connection status
export const useWebSocketConnection = () => {
  const [connectionState, setConnectionState] = useState(wsService.getState());
  const [isConnected, setIsConnected] = useState(wsService.isConnected());

  useEffect(() => {
    const unsubscribe = wsService.addEventListener(WS_EVENTS.CONNECTION_STATE, ({ state }) => {
      setConnectionState(state);
      setIsConnected(state === WS_STATES.CONNECTED);
    });

    // Set initial state
    setConnectionState(wsService.getState());
    setIsConnected(wsService.isConnected());

    return unsubscribe;
  }, []);

  const connect = useCallback(() => {
    wsService.connect();
  }, []);

  const disconnect = useCallback(() => {
    wsService.disconnect();
  }, []);

  const getStats = useCallback(() => {
    return wsService.getStats();
  }, []);

  return {
    connectionState,
    isConnected,
    connect,
    disconnect,
    getStats
  };
};

// Hook for subscribing to specific WebSocket events
export const useWebSocketSubscription = (eventType, callback, dependencies = []) => {
  const callbackRef = useRef(callback);
  
  // Update callback ref when it changes
  useEffect(() => {
    callbackRef.current = callback;
  }, [callback]);

  useEffect(() => {
    const wrappedCallback = (...args) => callbackRef.current(...args);
    const unsubscribe = wsService.addEventListener(eventType, wrappedCallback);
    
    return unsubscribe;
  }, [eventType, ...dependencies]);
};

// Hook for price updates
export const usePriceUpdates = (symbols = []) => {
  const [prices, setPrices] = useState({});
  const [lastUpdate, setLastUpdate] = useState(null);

  useWebSocketSubscription(WS_EVENTS.PRICE_UPDATE, useCallback((data) => {
    const { symbol, price, change24h, volume24h, timestamp } = data;
    
    // Only update if we're interested in this symbol (or all symbols)
    if (symbols.length === 0 || symbols.includes(symbol)) {
      setPrices(prev => ({
        ...prev,
        [symbol]: {
          price,
          change24h,
          volume24h,
          timestamp,
          lastUpdate: new Date().toISOString()
        }
      }));
      setLastUpdate(timestamp);
    }
  }, [symbols]));

  // Subscribe to price updates when symbols change
  useEffect(() => {
    if (wsService.isConnected()) {
      symbols.forEach(symbol => {
        wsService.subscribe('price_updates', { symbol });
      });
    }

    return () => {
      symbols.forEach(symbol => {
        wsService.unsubscribe('price_updates');
      });
    };
  }, [symbols]);

  return { prices, lastUpdate };
};

// Hook for balance updates
export const useBalanceUpdates = () => {
  const [balance, setBalance] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);

  useWebSocketSubscription(WS_EVENTS.BALANCE_UPDATE, useCallback((data) => {
    setBalance(data);
    setLastUpdate(new Date().toISOString());
  }, []));

  // Subscribe to balance updates
  useEffect(() => {
    if (wsService.isConnected()) {
      wsService.subscribe('balance_updates');
    }

    return () => {
      wsService.unsubscribe('balance_updates');
    };
  }, []);

  return { balance, lastUpdate };
};

// Hook for trade updates
export const useTradeUpdates = () => {
  const [trades, setTrades] = useState([]);
  const [lastUpdate, setLastUpdate] = useState(null);

  useWebSocketSubscription(WS_EVENTS.TRADE_UPDATE, useCallback((data) => {
    setTrades(prev => [data, ...prev.slice(0, 99)]); // Keep last 100 trades
    setLastUpdate(new Date().toISOString());
  }, []));

  // Subscribe to trade updates
  useEffect(() => {
    if (wsService.isConnected()) {
      wsService.subscribe('trade_updates');
    }

    return () => {
      wsService.unsubscribe('trade_updates');
    };
  }, []);

  const clearTrades = useCallback(() => {
    setTrades([]);
  }, []);

  return { trades, lastUpdate, clearTrades };
};

// Hook for system status updates
export const useSystemStatus = () => {
  const [status, setStatus] = useState({
    healthy: true,
    message: 'System operational',
    timestamp: null
  });

  useWebSocketSubscription(WS_EVENTS.SYSTEM_STATUS, useCallback((data) => {
    setStatus({
      ...data,
      timestamp: new Date().toISOString()
    });
  }, []));

  return status;
};

// Hook for sending WebSocket messages
export const useWebSocketSender = () => {
  const send = useCallback((type, payload) => {
    if (wsService.isConnected()) {
      wsService.send(type, payload);
      return true;
    } else {
      console.warn('Cannot send message: WebSocket not connected');
      return false;
    }
  }, []);

  return send;
};

// Comprehensive hook that combines multiple WebSocket features
export const useWebSocketData = ({ 
  subscribeToPrices = true, 
  subscribeToBalance = true, 
  subscribeToTrades = true,
  symbols = []
} = {}) => {
  const connection = useWebSocketConnection();
  const prices = subscribeToPrices ? usePriceUpdates(symbols) : { prices: {}, lastUpdate: null };
  const balance = subscribeToBalance ? useBalanceUpdates() : { balance: null, lastUpdate: null };
  const trades = subscribeToTrades ? useTradeUpdates() : { trades: [], lastUpdate: null, clearTrades: () => {} };
  const systemStatus = useSystemStatus();
  const send = useWebSocketSender();

  return {
    connection,
    prices: prices.prices,
    pricesLastUpdate: prices.lastUpdate,
    balance: balance.balance,
    balanceLastUpdate: balance.lastUpdate,
    trades: trades.trades,
    tradesLastUpdate: trades.lastUpdate,
    clearTrades: trades.clearTrades,
    systemStatus,
    send
  };
};

// Hook for WebSocket auto-connection management
export const useWebSocketAutoConnect = (autoConnect = true) => {
  const { isConnected, connect } = useWebSocketConnection();

  useEffect(() => {
    if (autoConnect && !isConnected) {
      // Auto-connect with a small delay to avoid connection spam
      const timer = setTimeout(() => {
        connect();
      }, 1000);

      return () => clearTimeout(timer);
    }
  }, [autoConnect, isConnected, connect]);

  // Auto-reconnect on page visibility change
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible' && autoConnect && !isConnected) {
        connect();
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => document.removeEventListener('visibilitychange', handleVisibilityChange);
  }, [autoConnect, isConnected, connect]);

  return { isConnected, connect };
};

export default useWebSocketConnection;