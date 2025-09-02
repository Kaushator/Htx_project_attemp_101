import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  CircularProgress,
  Alert,
  Box
} from '@mui/material';

const OrderManagement = () => {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Mock данные для демонстрации
  const mockOrders = [
    {
      id: 1,
      symbol: 'BTCUSDT',
      side: 'buy',
      amount: 0.5,
      price: 64500,
      status: 'filled',
      timestamp: '2025-08-30T10:15:00Z'
    },
    {
      id: 2,
      symbol: 'ETHUSDT',
      side: 'sell',
      amount: 2.0,
      price: 3150,
      status: 'partial-filled',
      timestamp: '2025-08-30T11:30:00Z'
    },
    {
      id: 3,
      symbol: 'ADAUSDT',
      side: 'buy',
      amount: 1500,
      price: 0.34,
      status: 'open',
      timestamp: '2025-08-30T12:00:00Z'
    }
  ];

  useEffect(() => {
    // Симуляция загрузки данных
    setTimeout(() => {
      setOrders(mockOrders);
      setLoading(false);
    }, 1000);
  }, []);

  const getStatusColor = (status) => {
    switch (status) {
      case 'filled': return 'success';
      case 'partial-filled': return 'warning';
      case 'open': return 'info';
      case 'cancelled': return 'error';
      default: return 'default';
    }
  };

  if (loading) {
    return (
      <Container>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="50vh">
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

  return (
    <Container>
      <Typography variant="h4" gutterBottom>
        Order Management
      </Typography>
      
      <Alert severity="info" sx={{ mb: 3 }}>
        Mock данные для демонстрации функциональности
      </Alert>

      <Paper>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Order ID</TableCell>
                <TableCell>Symbol</TableCell>
                <TableCell>Side</TableCell>
                <TableCell align="right">Amount</TableCell>
                <TableCell align="right">Price</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Time</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {orders.map((order) => (
                <TableRow key={order.id}>
                  <TableCell>{order.id}</TableCell>
                  <TableCell>{order.symbol}</TableCell>
                  <TableCell>
                    <Chip 
                      label={order.side} 
                      color={order.side === 'buy' ? 'success' : 'error'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell align="right">{order.amount}</TableCell>
                  <TableCell align="right">${order.price.toLocaleString()}</TableCell>
                  <TableCell>
                    <Chip 
                      label={order.status} 
                      color={getStatusColor(order.status)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    {new Date(order.timestamp).toLocaleString()}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
    </Container>
  );
};

export default OrderManagement;
