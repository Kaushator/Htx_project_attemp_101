/**
 * WebSocket Service for Real-time Data Updates
 * Provides real-time connectivity with the HTX Trading Platform backend
 */

import { buildWsUrl } from '../config/apiConfig.js';

// WebSocket connection states
export const WS_STATES = {
  CONNECTING: 'CONNECTING',
  CONNECTED: 'CONNECTED',
  DISCONNECTED: 'DISCONNECTED',
  ERROR: 'ERROR',
  RECONNECTING: 'RECONNECTING'
};

// Event types
export const WS_EVENTS = {
  PRICE_UPDATE: 'price_update',
  BALANCE_UPDATE: 'balance_update',
  TRADE_UPDATE: 'trade_update',
  SYSTEM_STATUS: 'system_status',
  ERROR: 'error',
  CONNECTION_STATE: 'connection_state'
};

class WebSocketService {
  constructor() {
    this.ws = null;
    this.url = buildWsUrl();
    this.listeners = new Map();
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 10;
    this.reconnectDelay = 1000;
    this.heartbeatInterval = null;
    this.connectionState = WS_STATES.DISCONNECTED;
    this.subscriptions = new Set();
    
    // Bind methods
    this.connect = this.connect.bind(this);
    this.disconnect = this.disconnect.bind(this);
    this.send = this.send.bind(this);
    this.subscribe = this.subscribe.bind(this);
    this.unsubscribe = this.unsubscribe.bind(this);
  }

  // Connect to WebSocket server
  connect() {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      console.log('WebSocket already connected');
      return;
    }

    this.setState(WS_STATES.CONNECTING);
    console.log(`🔌 Connecting to WebSocket: ${this.url}`);

    try {
      this.ws = new WebSocket(this.url);
      this.setupEventHandlers();
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      this.setState(WS_STATES.ERROR);
      this.handleReconnect();
    }
  }

  // Setup WebSocket event handlers
  setupEventHandlers() {
    if (!this.ws) return;

    this.ws.onopen = (event) => {
      console.log('✅ WebSocket connected');
      this.setState(WS_STATES.CONNECTED);
      this.reconnectAttempts = 0;
      this.startHeartbeat();
      this.resubscribeAll();
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        this.handleMessage(data);
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    this.ws.onclose = (event) => {
      console.log('🔌 WebSocket disconnected:', event.code, event.reason);
      this.setState(WS_STATES.DISCONNECTED);
      this.stopHeartbeat();
      
      // Reconnect unless it was a clean close
      if (event.code !== 1000) {
        this.handleReconnect();
      }
    };

    this.ws.onerror = (event) => {
      console.error('❌ WebSocket error:', event);
      this.setState(WS_STATES.ERROR);
    };
  }

  // Handle incoming messages
  handleMessage(data) {
    const { type, payload, timestamp } = data;
    
    console.log('📨 WebSocket message:', type, payload);
    
    // Emit to all listeners for this event type
    if (this.listeners.has(type)) {
      this.listeners.get(type).forEach(callback => {
        try {
          callback(payload, timestamp);
        } catch (error) {
          console.error(`Error in WebSocket listener for ${type}:`, error);
        }
      });
    }

    // Emit to global listeners
    if (this.listeners.has('*')) {
      this.listeners.get('*').forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error('Error in global WebSocket listener:', error);
        }
      });
    }
  }

  // Send message to server
  send(type, payload = {}) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      const message = {
        type,
        payload,
        timestamp: new Date().toISOString()
      };
      
      this.ws.send(JSON.stringify(message));
      console.log('📤 Sent WebSocket message:', type, payload);
    } else {
      console.warn('WebSocket not connected, cannot send message:', type);
    }
  }

  // Subscribe to a data type
  subscribe(type, params = {}) {
    this.subscriptions.add({ type, params });
    
    if (this.connectionState === WS_STATES.CONNECTED) {
      this.send('subscribe', { type, params });
    }
  }

  // Unsubscribe from a data type
  unsubscribe(type) {
    this.subscriptions = new Set(
      Array.from(this.subscriptions).filter(sub => sub.type !== type)
    );
    
    if (this.connectionState === WS_STATES.CONNECTED) {
      this.send('unsubscribe', { type });
    }
  }

  // Resubscribe to all subscriptions (after reconnect)
  resubscribeAll() {
    Array.from(this.subscriptions).forEach(({ type, params }) => {
      this.send('subscribe', { type, params });
    });
  }

  // Add event listener
  addEventListener(type, callback) {
    if (!this.listeners.has(type)) {
      this.listeners.set(type, new Set());
    }
    
    this.listeners.get(type).add(callback);
    
    // Return unsubscribe function
    return () => {
      this.removeEventListener(type, callback);
    };
  }

  // Remove event listener
  removeEventListener(type, callback) {
    if (this.listeners.has(type)) {
      this.listeners.get(type).delete(callback);
      
      // Clean up empty listener sets
      if (this.listeners.get(type).size === 0) {
        this.listeners.delete(type);
      }
    }
  }

  // Set connection state and notify listeners
  setState(newState) {
    if (this.connectionState !== newState) {
      const previousState = this.connectionState;
      this.connectionState = newState;
      
      console.log(`🔄 WebSocket state: ${previousState} → ${newState}`);
      
      // Notify state change listeners
      this.handleMessage({
        type: WS_EVENTS.CONNECTION_STATE,
        payload: { state: newState, previousState },
        timestamp: new Date().toISOString()
      });
    }
  }

  // Handle reconnection logic
  handleReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached');
      this.setState(WS_STATES.ERROR);
      return;
    }

    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
    
    console.log(`🔄 Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
    this.setState(WS_STATES.RECONNECTING);
    
    setTimeout(() => {
      if (this.connectionState !== WS_STATES.CONNECTED) {
        this.connect();
      }
    }, delay);
  }

  // Start heartbeat to keep connection alive
  startHeartbeat() {
    this.stopHeartbeat(); // Clear any existing heartbeat
    
    this.heartbeatInterval = setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.send('ping');
      }
    }, 30000); // Ping every 30 seconds
  }

  // Stop heartbeat
  stopHeartbeat() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  // Disconnect from WebSocket
  disconnect() {
    console.log('🔌 Disconnecting WebSocket');
    
    this.stopHeartbeat();
    this.subscriptions.clear();
    
    if (this.ws) {
      this.ws.close(1000, 'Client disconnect');
      this.ws = null;
    }
    
    this.setState(WS_STATES.DISCONNECTED);
  }

  // Get current state
  getState() {
    return this.connectionState;
  }

  // Check if connected
  isConnected() {
    return this.connectionState === WS_STATES.CONNECTED;
  }

  // Get connection statistics
  getStats() {
    return {
      state: this.connectionState,
      reconnectAttempts: this.reconnectAttempts,
      subscriptions: Array.from(this.subscriptions),
      listeners: Array.from(this.listeners.keys())
    };
  }
}

// Create singleton instance
export const wsService = new WebSocketService();

// Export for use in other modules
export default wsService;