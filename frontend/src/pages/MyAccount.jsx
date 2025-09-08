import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Grid,
  Paper,
  Box,
  Card,
  CardContent,
  Button,
  Alert,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  TextField,
  MenuItem,
  Tabs,
  Tab
} from '@mui/material';
import {
  AccountBalance,
  TrendingUp,
  Refresh,
  Visibility,
  VisibilityOff
} from '@mui/icons-material';

const MyAccount = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [balance, setBalance] = useState(null);
  const [selectedPair, setSelectedPair] = useState('btcusdt');
  const [ticker, setTicker] = useState(null);
  const [klines, setKlines] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showValues, setShowValues] = useState(false);

  const popularPairs = [
    'btcusdt', 'ethusdt', 'bnbusdt', 'adausdt', 'xrpusdt', 
    'solusdt', 'dotusdt', 'linkusdt', 'ltcusdt', 'bchusdt'
  ];

  const fetchBalance = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('http://localhost:8000/api/v1/htx/balance');
      const data = await response.json();
      
      if (data.error) {
        setError(data.message || data.error);
      } else {
        setBalance(data);
      }
    } catch (err) {
      setError('Ошибка подключения к серверу');
    }
    setLoading(false);
  };

  const fetchTicker = async (symbol) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/htx/ticker/${symbol}`);
      const data = await response.json();
      
      if (!data.error) {
        setTicker(data);
      }
    } catch (err) {
      console.error('Ошибка получения тикера:', err);
    }
  };

  const fetchKlines = async (symbol, period = '1day') => {
    try {
      const response = await fetch(
        `http://localhost:8000/api/v1/htx/klines/${symbol}?period=${period}&size=50`
      );
      const data = await response.json();
      
      if (!data.error) {
        setKlines(data);
      }
    } catch (err) {
      console.error('Ошибка получения свечей:', err);
    }
  };

  useEffect(() => {
    fetchBalance();
    fetchTicker(selectedPair);
    fetchKlines(selectedPair);
  }, []);

  useEffect(() => {
    if (selectedPair) {
      fetchTicker(selectedPair);
      fetchKlines(selectedPair);
    }
  }, [selectedPair]);

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const handleRefresh = () => {
    fetchBalance();
    if (selectedPair) {
      fetchTicker(selectedPair);
      fetchKlines(selectedPair);
    }
  };

  const formatBalance = (amount) => {
    if (!showValues) return '***.**';
    return parseFloat(amount || 0).toFixed(6);
  };

  const formatPrice = (price) => {
    return parseFloat(price || 0).toFixed(6);
  };

  const renderBalanceTab = () => (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5">
          <AccountBalance sx={{ mr: 1, verticalAlign: 'middle' }} />
          Баланс аккаунта HTX
        </Typography>
        <Box>
          <Button
            startIcon={showValues ? <VisibilityOff /> : <Visibility />}
            onClick={() => setShowValues(!showValues)}
            sx={{ mr: 1 }}
          >
            {showValues ? 'Скрыть' : 'Показать'} суммы
          </Button>
          <Button
            startIcon={<Refresh />}
            onClick={handleRefresh}
            disabled={loading}
          >
            Обновить
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {loading && (
        <Box display="flex" justifyContent="center" my={4}>
          <CircularProgress />
        </Box>
      )}

      {balance && balance.data && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Валюта</TableCell>
                    <TableCell align="right">Доступно</TableCell>
                    <TableCell align="right">Заморожено</TableCell>
                    <TableCell align="right">Всего</TableCell>
                    <TableCell align="center">Статус</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {balance.data.list && balance.data.list
                    .filter(item => parseFloat(item.balance) > 0.001)
                    .map((item, index) => (
                    <TableRow key={index}>
                      <TableCell component="th" scope="row">
                        <Typography variant="subtitle1" fontWeight="bold">
                          {item.currency.toUpperCase()}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        {formatBalance(item.balance)}
                      </TableCell>
                      <TableCell align="right">
                        {formatBalance(item.frozen || 0)}
                      </TableCell>
                      <TableCell align="right">
                        <Typography fontWeight="bold">
                          {formatBalance(parseFloat(item.balance) + parseFloat(item.frozen || 0))}
                        </Typography>
                      </TableCell>
                      <TableCell align="center">
                        <Chip
                          label={item.type}
                          color={item.type === 'trade' ? 'success' : 'default'}
                          size="small"
                        />
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Grid>
        </Grid>
      )}
    </Box>
  );

  const renderMarketTab = () => (
    <Box>
      <Typography variant="h5" gutterBottom>
        <TrendingUp sx={{ mr: 1, verticalAlign: 'middle' }} />
        Рыночные данные
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <TextField
            select
            label="Торговая пара"
            value={selectedPair}
            onChange={(e) => setSelectedPair(e.target.value)}
            fullWidth
          >
            {popularPairs.map((pair) => (
              <MenuItem key={pair} value={pair}>
                {pair.toUpperCase()}
              </MenuItem>
            ))}
          </TextField>
        </Grid>

        {ticker && ticker.tick && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  {selectedPair.toUpperCase()} - Текущие данные
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={6} md={3}>
                    <Typography variant="body2" color="text.secondary">
                      Текущая цена
                    </Typography>
                    <Typography variant="h6">
                      ${formatPrice(ticker.tick.close)}
                    </Typography>
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <Typography variant="body2" color="text.secondary">
                      24ч максимум
                    </Typography>
                    <Typography variant="h6" color="error">
                      ${formatPrice(ticker.tick.high)}
                    </Typography>
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <Typography variant="body2" color="text.secondary">
                      24ч минимум
                    </Typography>
                    <Typography variant="h6" color="success.main">
                      ${formatPrice(ticker.tick.low)}
                    </Typography>
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <Typography variant="body2" color="text.secondary">
                      Объем 24ч
                    </Typography>
                    <Typography variant="h6">
                      {parseFloat(ticker.tick.vol || 0).toFixed(2)}
                    </Typography>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        )}

        {klines && klines.data && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Последние свечи (1 день)
                </Typography>
                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Время</TableCell>
                        <TableCell align="right">Открытие</TableCell>
                        <TableCell align="right">Максимум</TableCell>
                        <TableCell align="right">Минимум</TableCell>
                        <TableCell align="right">Закрытие</TableCell>
                        <TableCell align="right">Объем</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {klines.data.slice(0, 10).map((candle, index) => (
                        <TableRow key={index}>
                          <TableCell>
                            {new Date(candle.id * 1000).toLocaleDateString('ru-RU')}
                          </TableCell>
                          <TableCell align="right">${formatPrice(candle.open)}</TableCell>
                          <TableCell align="right">${formatPrice(candle.high)}</TableCell>
                          <TableCell align="right">${formatPrice(candle.low)}</TableCell>
                          <TableCell align="right">${formatPrice(candle.close)}</TableCell>
                          <TableCell align="right">{parseFloat(candle.vol).toFixed(2)}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>
          </Grid>
        )}
      </Grid>
    </Box>
  );

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Tabs value={activeTab} onChange={handleTabChange} sx={{ mb: 3 }}>
        <Tab label="Мой баланс" />
        <Tab label="Рыночные данные" />
      </Tabs>

      {activeTab === 0 && renderBalanceTab()}
      {activeTab === 1 && renderMarketTab()}
    </Container>
  );
};

export default MyAccount;
