import React, { useEffect, useState, useRef } from 'react';
import {
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Switch,
  FormControlLabel,
  Alert
} from '@mui/material';
import {
  Wifi,
  WifiOff,
  Activity,
  TrendingUp,
  TrendingDown,
  AlertCircle
} from 'lucide-react';

const WebSocketStatus = ({ onDataUpdate }) => {
  const [isConnected, setIsConnected] = useState(false);
  const [isEnabled, setIsEnabled] = useState(false);
  const [lastMessage, setLastMessage] = useState(null);
  const [messages, setMessages] = useState([]);
  const [error, setError] = useState(null);
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);

  const connectWebSocket = () => {
    if (!isEnabled) return;
    
    try {
      // Connect to WebSocket endpoint
      wsRef.current = new WebSocket('ws://127.0.0.1:8000/api/v1/ws');
      
      wsRef.current.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
        setError(null);
        
        // Send subscription message
        wsRef.current.send(JSON.stringify({
          type: 'subscribe',
          channel: 'trading_updates'
        }));
      };

      wsRef.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          setLastMessage(data);
          
          // Add to messages list (keep last 10)
          setMessages(prev => [
            { ...data, timestamp: new Date() },
            ...prev.slice(0, 9)
          ]);
          
          // Call data update callback
          if (onDataUpdate && data.type === 'data_update') {
            onDataUpdate(data);
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      wsRef.current.onclose = () => {
        console.log('WebSocket disconnected');
        setIsConnected(false);
        
        // Attempt to reconnect after 3 seconds if enabled
        if (isEnabled) {
          reconnectTimeoutRef.current = setTimeout(() => {
            connectWebSocket();
          }, 3000);
        }
      };

      wsRef.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        setError('WebSocket connection error');
      };

    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      setError('Failed to connect to WebSocket');
    }
  };

  const disconnectWebSocket = () => {
    if (wsRef.current) {
      wsRef.current.close();
    }
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    setIsConnected(false);
  };

  useEffect(() => {
    if (isEnabled) {
      connectWebSocket();
    } else {
      disconnectWebSocket();
    }

    return () => {
      disconnectWebSocket();
    };
  }, [isEnabled]);

  const handleToggle = (event) => {
    setIsEnabled(event.target.checked);
  };

  const getMessageIcon = (type) => {
    switch (type) {
      case 'trade_update':
        return <Activity size={16} />;
      case 'price_update':
        return <TrendingUp size={16} />;
      case 'alert':
        return <AlertCircle size={16} />;
      default:
        return <Activity size={16} />;
    }
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString('ru-RU');
  };

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        Real-time Updates
      </Typography>

      {/* Connection Control */}
      <Card variant="outlined" sx={{ mb: 3 }}>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Box display="flex" alignItems="center" gap={2}>
              {isConnected ? (
                <Wifi size={24} color="#4caf50" />
              ) : (
                <WifiOff size={24} color="#f44336" />
              )}
              <Box>
                <Typography variant="subtitle1">
                  WebSocket Connection
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {isConnected ? 'Connected' : 'Disconnected'}
                </Typography>
              </Box>
            </Box>
            
            <FormControlLabel
              control={
                <Switch 
                  checked={isEnabled} 
                  onChange={handleToggle}
                  color="primary"
                />
              }
              label="Enable Real-time"
            />
          </Box>
          
          {error && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {error}
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* Connection Status */}
      <Box display="flex" gap={1} mb={3}>
        <Chip
          label={isConnected ? 'Online' : 'Offline'}
          color={isConnected ? 'success' : 'error'}
          size="small"
          icon={isConnected ? <Wifi size={16} /> : <WifiOff size={16} />}
        />
        {lastMessage && (
          <Chip
            label={`Last update: ${formatTimestamp(lastMessage.timestamp)}`}
            size="small"
            variant="outlined"
          />
        )}
      </Box>

      {/* Recent Messages */}
      {messages.length > 0 && (
        <Box>
          <Typography variant="subtitle2" gutterBottom>
            Recent Updates ({messages.length})
          </Typography>
          <List dense>
            {messages.map((message, index) => (
              <ListItem key={index} divider>
                <ListItemIcon>
                  {getMessageIcon(message.type)}
                </ListItemIcon>
                <ListItemText
                  primary={
                    <Box display="flex" justifyContent="space-between" alignItems="center">
                      <Typography variant="body2">
                        {message.message || message.type}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {formatTimestamp(message.timestamp)}
                      </Typography>
                    </Box>
                  }
                  secondary={
                    message.data && (
                      <Typography variant="caption">
                        {JSON.stringify(message.data).substring(0, 100)}...
                      </Typography>
                    )
                  }
                />
              </ListItem>
            ))}
          </List>
        </Box>
      )}

      {/* Instructions */}
      {!isEnabled && (
        <Box mt={3}>
          <Typography variant="body2" color="text.secondary">
            Включите real-time обновления для получения данных в реальном времени:
            <br />
            • Обновления торговых данных
            <br />
            • Изменения цен
            <br />
            • Системные уведомления
            <br />
            • Alerts и предупреждения
          </Typography>
        </Box>
      )}
    </Paper>
  );
};

export default WebSocketStatus;
