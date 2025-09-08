import React, { useState, useEffect } from 'react';
import {
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Alert,
  CircularProgress,
  Button,
  TextField,
  InputAdornment,
  IconButton,
  Tooltip,
  Avatar
} from '@mui/material';
import {
  Search,
  Refresh,
  TrendingUp,
  TrendingDown,
  Star,
  StarBorder,
  FilterList
} from '@mui/icons-material';
import axios from 'axios';

const HTXCoinsPage = () => {
  const [coins, setCoins] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [favorites, setFavorites] = useState([]);
  const [sortBy, setSortBy] = useState('volume');
  const [filterBy, setFilterBy] = useState('all'); // all, favorites, trading

  // Загрузка данных о монетах
  const fetchCoins = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Получаем данные через наш backend API
      const response = await axios.get('http://localhost:8000/api/v1/htx/coins');
      
      if (response.data && response.data.coins && Array.isArray(response.data.coins)) {
        // Преобразуем данные в нужный формат для отображения
        const processedCoins = response.data.coins.map(coin => ({
          symbol: coin.symbol || '',
          name: coin.name || coin.symbol || '',
          price: coin.price || 0,
          change24h: coin.change24h || 0,
          volume24h: coin.volume24h || 0,
          marketCap: (coin.price * (coin.supply || 0)) || 0,
          logo: getCoinLogo(coin.symbol),
          status: coin.state === 'online' ? 'trading' : 'suspended',
          high24h: coin.high24h || 0,
          low24h: coin.low24h || 0
        }));
        
        setCoins(processedCoins);
      } else {
        throw new Error('Неверный формат данных от API');
      }
    } catch (err) {
      console.error('Error fetching coins:', err);
      setError('Ошибка загрузки данных о монетах. Проверьте подключение к HTX API.');
      
      // Для демонстрации создадим тестовые данные
      const mockCoins = [
        {
          symbol: 'BTC',
          name: 'Bitcoin',
          price: 65432.50,
          change24h: 2.15,
          volume24h: 28567890000,
          marketCap: 1280000000000,
          logo: '🟠',
          status: 'trading',
          high24h: 65900.00,
          low24h: 64000.00
        },
        {
          symbol: 'ETH', 
          name: 'Ethereum',
          price: 3256.78,
          change24h: -1.24,
          volume24h: 15423890000,
          marketCap: 391000000000,
          logo: '🔵',
          status: 'trading',
          high24h: 3300.00,
          low24h: 3200.00
        },
        {
          symbol: 'USDT',
          name: 'Tether USD',
          price: 1.0001,
          change24h: 0.01,
          volume24h: 45678900000,
          marketCap: 118000000000,
          logo: '🟢',
          status: 'trading',
          high24h: 1.01,
          low24h: 0.99
        }
      ];
      setCoins(mockCoins);
    } finally {
      setLoading(false);
    }
  };
  
  // Функция для получения эмодзи логотипа монеты
  const getCoinLogo = (symbol) => {
    const logos = {
      'BTC': '�',
      'ETH': '🔵',
      'USDT': '🟢',
      'BNB': '🟡',
      'ADA': '🔴',
      'DOT': '🟣',
      'XRP': '⚪',
      'SOL': '🟣',
      'DOGE': '�',
      'AVAX': '🔴'
    };
    
    return logos[symbol] || '🪙';
  };

  useEffect(() => {
    fetchCoins();
    // Загружаем избранное из localStorage
    const savedFavorites = localStorage.getItem('htx_favorites');
    if (savedFavorites) {
      setFavorites(JSON.parse(savedFavorites));
    }
  }, []);

  // Функции для работы с избранным
  const toggleFavorite = (symbol) => {
    const newFavorites = favorites.includes(symbol)
      ? favorites.filter(fav => fav !== symbol)
      : [...favorites, symbol];
    
    setFavorites(newFavorites);
    localStorage.setItem('htx_favorites', JSON.stringify(newFavorites));
  };

  // Фильтрация и сортировка монет
  const filteredCoins = coins
    .filter(coin => {
      const matchesSearch = coin.symbol.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           coin.name.toLowerCase().includes(searchTerm.toLowerCase());
      
      if (filterBy === 'favorites') {
        return matchesSearch && favorites.includes(coin.symbol);
      } else if (filterBy === 'trading') {
        return matchesSearch && coin.status === 'trading';
      }
      return matchesSearch;
    })
    .sort((a, b) => {
      switch (sortBy) {
        case 'price':
          return b.price - a.price;
        case 'change':
          return b.change24h - a.change24h;
        case 'volume':
          return b.volume24h - a.volume24h;
        case 'name':
          return a.name.localeCompare(b.name);
        default:
          return 0;
      }
    });

  const formatNumber = (num) => {
    if (num >= 1e9) return (num / 1e9).toFixed(2) + 'B';
    if (num >= 1e6) return (num / 1e6).toFixed(2) + 'M';
    if (num >= 1e3) return (num / 1e3).toFixed(2) + 'K';
    return num.toFixed(2);
  };

  const formatPrice = (price) => {
    if (price < 1) return price.toFixed(6);
    if (price < 100) return price.toFixed(4);
    return price.toFixed(2);
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        HTX Монеты
      </Typography>

      {/* Статистика */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" color="primary">
                Всего монет
              </Typography>
              <Typography variant="h4">
                {coins.length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" color="success.main">
                Торгуемых
              </Typography>
              <Typography variant="h4">
                {coins.filter(c => c.status === 'trading').length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" color="warning.main">
                В избранном
              </Typography>
              <Typography variant="h4">
                {favorites.length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" color="info.main">
                Общий объем
              </Typography>
              <Typography variant="h4">
                ${formatNumber(coins.reduce((sum, coin) => sum + coin.volume24h, 0))}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Контролы поиска и фильтрации */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              placeholder="Поиск по символу или названию..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Search />
                  </InputAdornment>
                ),
              }}
            />
          </Grid>
          <Grid item xs={12} md={2}>
            <TextField
              select
              fullWidth
              label="Фильтр"
              value={filterBy}
              onChange={(e) => setFilterBy(e.target.value)}
              SelectProps={{ native: true }}
            >
              <option value="all">Все монеты</option>
              <option value="trading">Торгуемые</option>
              <option value="favorites">Избранные</option>
            </TextField>
          </Grid>
          <Grid item xs={12} md={2}>
            <TextField
              select
              fullWidth
              label="Сортировка"
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              SelectProps={{ native: true }}
            >
              <option value="volume">По объему</option>
              <option value="price">По цене</option>
              <option value="change">По изменению</option>
              <option value="name">По названию</option>
            </TextField>
          </Grid>
          <Grid item xs={12} md={2}>
            <Button
              fullWidth
              variant="outlined"
              onClick={fetchCoins}
              disabled={loading}
              startIcon={loading ? <CircularProgress size={20} /> : <Refresh />}
            >
              Обновить
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {/* Уведомления */}
      {error && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Таблица монет */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Избранное</TableCell>
              <TableCell>Монета</TableCell>
              <TableCell align="right">Цена (USD)</TableCell>
              <TableCell align="right">24ч Изменение</TableCell>
              <TableCell align="right">Объем 24ч</TableCell>
              <TableCell align="right">Рын. капитализация</TableCell>
              <TableCell>Статус</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={7} align="center">
                  <CircularProgress sx={{ my: 2 }} />
                </TableCell>
              </TableRow>
            ) : filteredCoins.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} align="center">
                  <Typography variant="body1" color="text.secondary">
                    Монеты не найдены
                  </Typography>
                </TableCell>
              </TableRow>
            ) : (
              filteredCoins.map((coin) => (
                <TableRow 
                  key={coin.symbol}
                  hover
                  sx={{ '&:hover': { backgroundColor: 'action.hover' } }}
                >
                  <TableCell>
                    <IconButton
                      onClick={() => toggleFavorite(coin.symbol)}
                      color={favorites.includes(coin.symbol) ? 'warning' : 'default'}
                    >
                      {favorites.includes(coin.symbol) ? <Star /> : <StarBorder />}
                    </IconButton>
                  </TableCell>
                  
                  <TableCell>
                    <Box display="flex" alignItems="center" gap={2}>
                      <Avatar sx={{ width: 32, height: 32, fontSize: '1.2rem' }}>
                        {coin.logo}
                      </Avatar>
                      <Box>
                        <Typography variant="body1" fontWeight="bold">
                          {coin.symbol}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {coin.name}
                        </Typography>
                      </Box>
                    </Box>
                  </TableCell>
                  
                  <TableCell align="right">
                    <Typography variant="body1" fontWeight="bold">
                      ${formatPrice(coin.price)}
                    </Typography>
                  </TableCell>
                  
                  <TableCell align="right">
                    <Box display="flex" alignItems="center" justifyContent="flex-end" gap={1}>
                      {coin.change24h > 0 ? (
                        <TrendingUp color="success" />
                      ) : (
                        <TrendingDown color="error" />
                      )}
                      <Typography 
                        variant="body1"
                        color={coin.change24h > 0 ? 'success.main' : 'error.main'}
                        fontWeight="bold"
                      >
                        {coin.change24h > 0 ? '+' : ''}{coin.change24h.toFixed(2)}%
                      </Typography>
                    </Box>
                  </TableCell>
                  
                  <TableCell align="right">
                    <Typography variant="body1">
                      ${formatNumber(coin.volume24h)}
                    </Typography>
                  </TableCell>
                  
                  <TableCell align="right">
                    <Typography variant="body1">
                      ${formatNumber(coin.marketCap)}
                    </Typography>
                  </TableCell>
                  
                  <TableCell>
                    <Chip
                      label={coin.status === 'trading' ? 'Торгуется' : 'Приостановлен'}
                      color={coin.status === 'trading' ? 'success' : 'warning'}
                      size="small"
                    />
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Информация о последнем обновлении */}
      <Box sx={{ mt: 2, textAlign: 'center' }}>
        <Typography variant="body2" color="text.secondary">
          Последнее обновление: {new Date().toLocaleString('ru-RU')}
        </Typography>
      </Box>
    </Box>
  );
};

export default HTXCoinsPage;
