import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Grid,
  Paper,
  Box,
  Button,
  Alert,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow
} from '@mui/material';
import FileUpload from '../components/FileUpload';

const UltraSimpleDashboard = () => {
  const [status, setStatus] = useState('ready');
  const [balanceData, setBalanceData] = useState(null);
  const [tradesData, setTradesData] = useState([]);
  const [dbTradesData, setDbTradesData] = useState([]);
  const [loading, setLoading] = useState(false);

  const testBackend = async () => {
    setStatus('testing');
    setLoading(true);
    try {
      // Тест health check
      const healthResponse = await fetch('http://localhost:8000/api/v1/health');
      if (!healthResponse.ok) throw new Error('Health check failed');
      
      // Загружаем данные баланса HTX
      const balanceResponse = await fetch('http://localhost:8000/api/v1/htx/balance');
      if (balanceResponse.ok) {
        const balance = await balanceResponse.json();
        setBalanceData(balance);
      }
      
      // Загружаем данные трейдов HTX
      const tradesResponse = await fetch('http://localhost:8000/api/v1/htx/trades');
      if (tradesResponse.ok) {
        const trades = await tradesResponse.json();
        setTradesData(trades.data || []);
      }
      
      // Загружаем данные из БД (загруженные CSV)
      const dbTradesResponse = await fetch('http://localhost:8000/api/v1/trades?limit=10');
      if (dbTradesResponse.ok) {
        const dbTrades = await dbTradesResponse.json();
        setDbTradesData(dbTrades.trades || []);
      }
      
      setStatus('success');
    } catch (error) {
      setStatus('error');
      console.error('Backend test failed:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    testBackend();
  }, []);

  return (
    <Container maxWidth="lg" sx={{ mt: 4 }}>
      <Typography variant="h3" gutterBottom align="center">
        🚀 HTX Trading Platform
      </Typography>
      
      <Alert severity="info" sx={{ mb: 3 }}>
        <strong>Персональная конфигурация:</strong> Backend:8000 | Frontend:3000
      </Alert>

      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                System Status
              </Typography>
              <Box sx={{ mb: 2 }}>
                <Chip 
                  label={status.toUpperCase()} 
                  color={status === 'success' ? 'success' : status === 'error' ? 'error' : 'primary'}
                />
                {loading && <CircularProgress size={20} sx={{ ml: 1 }} />}
              </Box>
              <Button 
                variant="contained" 
                onClick={testBackend}
                disabled={loading}
                fullWidth
              >
                {loading ? 'Loading...' : 'Refresh Data'}
              </Button>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Account Balance
              </Typography>
              {balanceData ? (
                <Box>
                  <Typography variant="body1">
                    <strong>Total:</strong> ${balanceData.total_balance?.toLocaleString()} 
                    <Chip size="small" label={balanceData.source} sx={{ ml: 1 }} />
                  </Typography>
                  <Typography variant="body2">
                    Available: ${balanceData.available_balance?.toLocaleString()}
                  </Typography>
                  <Typography variant="body2">
                    Frozen: ${balanceData.frozen_balance?.toLocaleString()}
                  </Typography>
                  {balanceData.currencies && (
                    <Typography variant="body2" color="primary">
                      Currencies: {balanceData.currencies.length} types
                    </Typography>
                  )}
                  {balanceData.error && (
                    <Typography variant="caption" color="warning.main">
                      Note: {balanceData.error}
                    </Typography>
                  )}
                </Box>
              ) : (
                <Typography color="text.secondary">
                  No data available
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Quick Links
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                <Button variant="outlined" href="http://localhost:8000/docs" target="_blank">
                  API Docs
                </Button>
                <Button variant="outlined" href="/orders">
                  Orders
                </Button>
                <Button variant="outlined" href="/pnl">
                  P&L Analytics
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                📁 Upload Trading Data (CSV/Excel)
              </Typography>
              <FileUpload onUpload={testBackend} />
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                Поддерживаемые форматы: CSV, XLSX, XLS. Максимальный размер: 50MB
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                📊 HTX Live Data
                <Chip size="small" label="Real-time" color="success" sx={{ ml: 1 }} />
              </Typography>
              {tradesData.length > 0 ? (
                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Symbol</TableCell>
                        <TableCell>Side</TableCell>
                        <TableCell align="right">Amount</TableCell>
                        <TableCell align="right">Price</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {tradesData.slice(0, 3).map((trade, index) => (
                        <TableRow key={index}>
                          <TableCell>{trade.symbol}</TableCell>
                          <TableCell>
                            <Chip 
                              label={trade.side} 
                              color={trade.side === 'buy' ? 'success' : 'error'}
                              size="small"
                            />
                          </TableCell>
                          <TableCell align="right">{trade.amount}</TableCell>
                          <TableCell align="right">${trade.price?.toLocaleString()}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              ) : (
                <Typography color="text.secondary">
                  No HTX data available
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                💾 Uploaded CSV Data
                <Chip size="small" label={`${dbTradesData.length} records`} sx={{ ml: 1 }} />
              </Typography>
              {dbTradesData.length > 0 ? (
                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Symbol</TableCell>
                        <TableCell>Side</TableCell>
                        <TableCell align="right">Quantity</TableCell>
                        <TableCell align="right">Price</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {dbTradesData.slice(0, 3).map((trade) => (
                        <TableRow key={trade.id}>
                          <TableCell>{trade.symbol}</TableCell>
                          <TableCell>
                            <Chip 
                              label={trade.side} 
                              color={trade.side === 'buy' ? 'success' : 'error'}
                              size="small"
                            />
                          </TableCell>
                          <TableCell align="right">{trade.quantity}</TableCell>
                          <TableCell align="right">${trade.price}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              ) : (
                <Typography color="text.secondary">
                  No uploaded data. Upload a CSV file to see data here.
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Trades (Combined)
              </Typography>
              {tradesData.length > 0 ? (
                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Symbol</TableCell>
                        <TableCell>Side</TableCell>
                        <TableCell align="right">Amount</TableCell>
                        <TableCell align="right">Price</TableCell>
                        <TableCell align="right">P&L</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {tradesData.map((trade) => (
                        <TableRow key={trade.id}>
                          <TableCell>{trade.symbol}</TableCell>
                          <TableCell>
                            <Chip 
                              label={trade.side} 
                              color={trade.side === 'buy' ? 'success' : 'error'}
                              size="small"
                            />
                          </TableCell>
                          <TableCell align="right">{trade.amount}</TableCell>
                          <TableCell align="right">${trade.price?.toLocaleString()}</TableCell>
                          <TableCell align="right" sx={{ color: trade.pnl > 0 ? 'success.main' : 'error.main' }}>
                            ${trade.pnl}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              ) : (
                <Typography color="text.secondary">
                  No trades data available
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h5" gutterBottom>
              🎯 Project Status: READY FOR DEMO
            </Typography>
            <Typography variant="body1" paragraph>
              Этот проект настроен для работы ТОЛЬКО на вашем ПК с фиксированными портами.
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Typography variant="h6">✅ Working Features:</Typography>
                <ul>
                  <li>FastAPI backend on port 8000</li>
                  <li>React frontend on port 3000</li>
                  <li>Health check endpoint</li>
                  <li>Mock trading data</li>
                  <li>SQLite database</li>
                </ul>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="h6">🚀 Quick Start:</Typography>
                <ol>
                  <li>Run quick_start.bat</li>
                  <li>Wait 10 seconds</li>
                  <li>Browser opens automatically</li>
                  <li>Test backend connection</li>
                </ol>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default UltraSimpleDashboard;
