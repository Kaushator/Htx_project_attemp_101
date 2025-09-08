/**
 * Real-Time Dashboard Component
 * Demonstrates WebSocket integration with live data updates
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Badge,
  IconButton,
  Tooltip,
  Switch,
  FormControlLabel,
  Stack,
  Alert,
  LinearProgress,
  Fade
} from '@mui/material';
import {
  WifiOff,
  Wifi,
  TrendingUp,
  TrendingDown,
  Refresh,
  Pause,
  PlayArrow,
  Circle
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';

import { useWebSocketData, useWebSocketAutoConnect } from '../hooks/useWebSocket';
import { WS_STATES } from '../services/websocketService';

// Styled components for better visual feedback
const ConnectionIndicator = styled(Box)(({ theme, connected }) => ({
  display: 'flex',
  alignItems: 'center',
  gap: theme.spacing(1),
  color: connected ? theme.palette.success.main : theme.palette.error.main
}));

const PriceCell = styled(TableCell)(({ theme, trend }) => ({
  color: trend > 0 ? theme.palette.success.main : 
        trend < 0 ? theme.palette.error.main : 
        theme.palette.text.primary
}));

const BlinkingCell = styled(TableCell)(({ theme, updated }) => ({
  backgroundColor: updated ? theme.palette.action.selected : 'transparent',
  transition: 'background-color 0.3s ease'
}));

const RealTimeDashboard = () => {
  const [autoConnect, setAutoConnect] = useState(true);
  const [selectedSymbols] = useState(['btcusdt', 'ethusdt', 'adausdt', 'dotusdt']);
  const [recentUpdates, setRecentUpdates] = useState(new Set());

  // WebSocket connection and data
  const { isConnected } = useWebSocketAutoConnect(autoConnect);
  const {
    connection,
    prices,
    pricesLastUpdate,
    balance,
    balanceLastUpdate,
    trades,
    tradesLastUpdate,
    systemStatus,
    send
  } = useWebSocketData({
    subscribeToPrices: true,
    subscribeToBalance: true,
    subscribeToTrades: true,
    symbols: selectedSymbols
  });

  // Track recent price updates for visual feedback
  useEffect(() => {
    if (pricesLastUpdate) {
      // Flash effect for updated prices
      const updatedSymbols = Object.keys(prices).filter(symbol => {
        const price = prices[symbol];
        return price && new Date(price.lastUpdate).getTime() > Date.now() - 2000;
      });

      setRecentUpdates(new Set(updatedSymbols));
      
      // Clear the flash effect after 2 seconds
      const timer = setTimeout(() => {
        setRecentUpdates(new Set());
      }, 2000);

      return () => clearTimeout(timer);
    }
  }, [pricesLastUpdate, prices]);

  // Format price with proper decimals
  const formatPrice = (price) => {
    if (!price) return '0.00';
    return typeof price === 'number' ? price.toFixed(4) : '0.00';
  };

  // Format percentage change
  const formatChange = (change) => {
    if (!change) return '0.00%';
    const value = typeof change === 'number' ? change : 0;
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
  };

  // Format volume
  const formatVolume = (volume) => {
    if (!volume) return '0';
    if (volume >= 1e9) return `${(volume / 1e9).toFixed(2)}B`;
    if (volume >= 1e6) return `${(volume / 1e6).toFixed(2)}M`;
    if (volume >= 1e3) return `${(volume / 1e3).toFixed(2)}K`;
    return volume.toFixed(2);
  };

  // Get connection status color and text
  const getConnectionStatus = () => {
    switch (connection.connectionState) {
      case WS_STATES.CONNECTED:
        return { color: 'success', text: 'Connected', icon: <Wifi /> };
      case WS_STATES.CONNECTING:
        return { color: 'warning', text: 'Connecting...', icon: <Circle sx={{ fontSize: 16 }} /> };
      case WS_STATES.RECONNECTING:
        return { color: 'warning', text: 'Reconnecting...', icon: <Refresh /> };
      case WS_STATES.ERROR:
        return { color: 'error', text: 'Error', icon: <WifiOff /> };
      default:
        return { color: 'error', text: 'Disconnected', icon: <WifiOff /> };
    }
  };

  const connectionStatus = getConnectionStatus();

  return (
    <Box sx={{ p: 3 }}>
      {/* Header with Connection Status */}
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4">
          Real-Time Trading Dashboard
        </Typography>
        
        <Stack direction="row" spacing={2} alignItems="center">
          <FormControlLabel
            control={
              <Switch
                checked={autoConnect}
                onChange={(e) => setAutoConnect(e.target.checked)}
              />
            }
            label="Auto Connect"
          />
          
          <ConnectionIndicator connected={isConnected}>
            {connectionStatus.icon}
            <Typography variant="body2">
              {connectionStatus.text}
            </Typography>
          </ConnectionIndicator>
        </Stack>
      </Box>

      {/* System Status Alert */}
      {!systemStatus.healthy && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          System Status: {systemStatus.message}
        </Alert>
      )}

      {/* Loading indicator when connecting */}
      {connection.connectionState === WS_STATES.CONNECTING && (
        <Fade in>
          <LinearProgress sx={{ mb: 2 }} />
        </Fade>
      )}

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Live Prices
              </Typography>
              <Typography variant="h4">
                {Object.keys(prices).length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Symbols tracked
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Account Balance
              </Typography>
              <Typography variant="h4">
                ${balance?.total_balance?.toFixed(2) || '0.00'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {balanceLastUpdate ? `Updated ${new Date(balanceLastUpdate).toLocaleTimeString()}` : 'No updates'}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Live Trades
              </Typography>
              <Typography variant="h4">
                {trades.length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Recent trades received
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Last Update
              </Typography>
              <Typography variant="h4">
                {pricesLastUpdate ? new Date(pricesLastUpdate).toLocaleTimeString() : '--:--'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Price data
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Live Price Table */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Live Price Updates
          </Typography>
          
          <TableContainer component={Paper} variant="outlined">
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Symbol</TableCell>
                  <TableCell align="right">Price</TableCell>
                  <TableCell align="right">24h Change</TableCell>
                  <TableCell align="right">Volume</TableCell>
                  <TableCell align="right">Status</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {selectedSymbols.map((symbol) => {
                  const priceData = prices[symbol];
                  const isUpdated = recentUpdates.has(symbol);
                  const trend = priceData?.change24h || 0;

                  return (
                    <TableRow key={symbol} hover>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Typography variant="body2" fontWeight="bold">
                            {symbol.toUpperCase()}
                          </Typography>
                          {isUpdated && (
                            <Chip 
                              label="LIVE" 
                              size="small" 
                              color="success" 
                              variant="outlined"
                              sx={{ animation: 'pulse 1.5s infinite' }}
                            />
                          )}
                        </Box>
                      </TableCell>

                      <BlinkingCell align="right" updated={isUpdated}>
                        <Typography variant="body2" fontWeight="bold">
                          ${formatPrice(priceData?.price)}
                        </Typography>
                      </BlinkingCell>

                      <PriceCell align="right" trend={trend}>
                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: 0.5 }}>
                          {trend > 0 ? <TrendingUp fontSize="small" /> : <TrendingDown fontSize="small" />}
                          <Typography variant="body2">
                            {formatChange(trend)}
                          </Typography>
                        </Box>
                      </PriceCell>

                      <TableCell align="right">
                        <Typography variant="body2">
                          {formatVolume(priceData?.volume24h)}
                        </Typography>
                      </TableCell>

                      <TableCell align="right">
                        <Badge
                          color={priceData ? "success" : "default"}
                          variant="dot"
                        >
                          <Typography variant="body2" color="text.secondary">
                            {priceData ? "Live" : "Waiting"}
                          </Typography>
                        </Badge>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Recent Trades */}
      {trades.length > 0 && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Recent Trades ({trades.length})
            </Typography>
            
            <TableContainer component={Paper} variant="outlined" sx={{ maxHeight: 300 }}>
              <Table size="small" stickyHeader>
                <TableHead>
                  <TableRow>
                    <TableCell>Time</TableCell>
                    <TableCell>Symbol</TableCell>
                    <TableCell align="right">Price</TableCell>
                    <TableCell align="right">Quantity</TableCell>
                    <TableCell align="right">Side</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {trades.slice(0, 20).map((trade, index) => (
                    <TableRow key={index}>
                      <TableCell>
                        <Typography variant="body2">
                          {new Date(trade.timestamp).toLocaleTimeString()}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" fontWeight="bold">
                          {trade.symbol}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="body2">
                          ${formatPrice(trade.price)}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="body2">
                          {trade.quantity}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Chip
                          label={trade.side}
                          size="small"
                          color={trade.side === 'buy' ? 'success' : 'error'}
                          variant="outlined"
                        />
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      )}

      {/* Add CSS animation for pulse effect */}
      <style jsx>{`
        @keyframes pulse {
          0% { opacity: 1; }
          50% { opacity: 0.5; }
          100% { opacity: 1; }
        }
      `}</style>
    </Box>
  );
};

export default RealTimeDashboard;