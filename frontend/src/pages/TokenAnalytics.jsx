// TODO: Add implementation for /api/v1/reference/currencies endpoint
import React, { useState, useEffect } from 'react';
import {
  Box, Typography, Grid, CircularProgress, Alert, TextField,
  Card, CardContent, Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, Paper, InputAdornment, IconButton,
  Chip, Tabs, Tab, Tooltip, Badge, Switch, FormControlLabel,
  Button, Dialog, DialogTitle, DialogContent, DialogActions,
  TableSortLabel
} from '@mui/material';
import {
  Search, Refresh, FilterList, CloudUpload, Info,
  TrendingUp, TrendingDown, BarChart, Download,
  Star, StarOutline, ArrowDropUp, ArrowDropDown
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';
import axios from 'axios';
import FileUploadNew from '../components/FileUploadNew';

// Стилизованный компонент для изменения цвета на основе значения
const PriceChange = styled(Box)(({ theme, value }) => ({
  color: value > 0 ? theme.palette.success.main : value < 0 ? theme.palette.error.main : 'inherit',
  display: 'flex',
  alignItems: 'center',
}));

// Компонент для отображения объема в удобочитаемом формате
const FormatVolume = ({ volume }) => {
  if (!volume) return '0';
  if (volume >= 1e9) return `$${(volume / 1e9).toFixed(2)}B`;
  if (volume >= 1e6) return `$${(volume / 1e6).toFixed(2)}M`;
  if (volume >= 1e3) return `$${(volume / 1e3).toFixed(2)}K`;
  return `$${volume}`;
};

const TokenAnalytics = () => {
  // Состояния для работы с токенами
  const [currencies, setCurrencies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [tabValue, setTabValue] = useState(0);
  const [sortBy, setSortBy] = useState('volume24h');
  const [sortDirection, setSortDirection] = useState('desc');
  const [favorites, setFavorites] = useState([]);
  const [showUploadDialog, setShowUploadDialog] = useState(false);
  const [dataSource, setDataSource] = useState('api'); // 'api' или 'file'
  const [fileData, setFileData] = useState(null);

  // Состояние анализа
  const [analyzed, setAnalyzed] = useState(false);
  const [analysisResults, setAnalysisResults] = useState(null);

  // Загрузка данных
  useEffect(() => {
    fetchCurrencies();
    // Загрузка избранных из localStorage
    const savedFavorites = localStorage.getItem('favorite_tokens');
    if (savedFavorites) {
      setFavorites(JSON.parse(savedFavorites));
    }
  }, []);

  const fetchCurrencies = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Получение списка валют с HTX API
      const response = await axios.get('http://localhost:8000/api/v1/htx/coins');
      
      if (response.data && response.data.coins) {
        setCurrencies(response.data.coins);
      } else {
        setError('Неожиданный формат данных от API');
      }
    } catch (err) {
      console.error('Ошибка при загрузке валют:', err);
      setError(`Не удалось загрузить данные: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Обработчик загрузки файла
  const handleFileUpload = (fileResult) => {
    setDataSource('file');
    setFileData(fileResult);
    setShowUploadDialog(false);
    // TODO: После загрузки файла нужно будет сделать запрос на анализ данных
    analyzeData(fileResult.id);
  };

  // Запрос на анализ данных
  const analyzeData = async (fileId) => {
    setLoading(true);
    try {
      const response = await axios.get(`http://localhost:8000/api/v1/insights/analyze-file/${fileId}`);
      setAnalysisResults(response.data);
      setAnalyzed(true);
    } catch (err) {
      setError(`Ошибка при анализе данных: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Переключение избранных токенов
  const toggleFavorite = (symbol) => {
    const newFavorites = favorites.includes(symbol)
      ? favorites.filter(f => f !== symbol)
      : [...favorites, symbol];
    
    setFavorites(newFavorites);
    localStorage.setItem('favorite_tokens', JSON.stringify(newFavorites));
  };

  // Сортировка данных
  const handleSort = (property) => {
    const isAsc = sortBy === property && sortDirection === 'asc';
    setSortDirection(isAsc ? 'desc' : 'asc');
    setSortBy(property);
  };

  // Фильтрация и сортировка
  const filteredCurrencies = currencies
    .filter(currency => {
      // Поиск по строке
      const matchesSearch = 
        currency.symbol.toLowerCase().includes(searchTerm.toLowerCase()) || 
        currency.name?.toLowerCase().includes(searchTerm.toLowerCase());
      
      // Фильтр по вкладке
      if (tabValue === 1 && !favorites.includes(currency.symbol)) {
        return false;
      }
      
      return matchesSearch;
    })
    .sort((a, b) => {
      // Сортировка по выбранному свойству
      const factor = sortDirection === 'asc' ? 1 : -1;
      
      if (sortBy === 'symbol') {
        return factor * a.symbol.localeCompare(b.symbol);
      }
      
      if (sortBy === 'price') {
        return factor * (a.price - b.price);
      }
      
      if (sortBy === 'change24h') {
        return factor * (a.change24h - b.change24h);
      }
      
      // По умолчанию сортируем по объему
      return factor * (a.volume24h - b.volume24h);
    });

  return (
    <Box sx={{ padding: 3 }}>
      {/* Заголовок страницы */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Анализ токенов и валют
        </Typography>
        
        <Box>
          <Tooltip title="Обновить данные">
            <IconButton onClick={fetchCurrencies} disabled={loading}>
              <Refresh />
            </IconButton>
          </Tooltip>
          
          <Tooltip title="Загрузить файл для анализа">
            <IconButton onClick={() => setShowUploadDialog(true)}>
              <CloudUpload />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Карточки с сводными данными */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Всего токенов
              </Typography>
              <Typography variant="h4">
                {currencies.length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                В избранном
              </Typography>
              <Typography variant="h4">
                {favorites.length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Источник данных
              </Typography>
              <Typography variant="h6">
                {dataSource === 'api' ? 'HTX API' : 'Загруженный файл'}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Статус анализа
              </Typography>
              <Typography variant="h6" color={analyzed ? 'success.main' : 'text.secondary'}>
                {analyzed ? 'Данные проанализированы' : 'Ожидание анализа'}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Панель поиска и фильтров */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <TextField
            placeholder="Поиск по символу или названию"
            variant="outlined"
            size="small"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            sx={{ width: { xs: '100%', sm: '300px' } }}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Search />
                </InputAdornment>
              ),
              endAdornment: searchTerm && (
                <InputAdornment position="end">
                  <IconButton size="small" onClick={() => setSearchTerm('')}>
                    &times;
                  </IconButton>
                </InputAdornment>
              )
            }}
          />
          
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <FormControlLabel
              control={
                <Switch 
                  checked={dataSource === 'file'} 
                  onChange={() => setDataSource(dataSource === 'api' ? 'file' : 'api')}
                  disabled={!fileData}
                />
              }
              label="Данные из файла"
            />
          </Box>
        </Box>
        
        <Tabs value={tabValue} onChange={(e, newValue) => setTabValue(newValue)}>
          <Tab label="Все токены" />
          <Tab 
            label={
              <Badge badgeContent={favorites.length} color="primary">
                Избранное
              </Badge>
            } 
          />
        </Tabs>
      </Paper>

      {/* Сообщения об ошибках и загрузке */}
      {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}
      
      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
          <CircularProgress />
        </Box>
      ) : (
        <>
          {/* Таблица токенов */}
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell width="50px"></TableCell>
                  <TableCell>
                    <TableSortLabel
                      active={sortBy === 'symbol'}
                      direction={sortBy === 'symbol' ? sortDirection : 'asc'}
                      onClick={() => handleSort('symbol')}
                    >
                      Символ
                    </TableSortLabel>
                  </TableCell>
                  <TableCell>Название</TableCell>
                  <TableCell>
                    <TableSortLabel
                      active={sortBy === 'price'}
                      direction={sortBy === 'price' ? sortDirection : 'asc'}
                      onClick={() => handleSort('price')}
                    >
                      Цена
                    </TableSortLabel>
                  </TableCell>
                  <TableCell>
                    <TableSortLabel
                      active={sortBy === 'change24h'}
                      direction={sortBy === 'change24h' ? sortDirection : 'asc'}
                      onClick={() => handleSort('change24h')}
                    >
                      24ч %
                    </TableSortLabel>
                  </TableCell>
                  <TableCell>
                    <TableSortLabel
                      active={sortBy === 'volume24h'}
                      direction={sortBy === 'volume24h' ? sortDirection : 'asc'}
                      onClick={() => handleSort('volume24h')}
                    >
                      Объем (24ч)
                    </TableSortLabel>
                  </TableCell>
                  <TableCell>Статус</TableCell>
                  <TableCell>Торговые пары</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredCurrencies.length > 0 ? (
                  filteredCurrencies.map((currency) => (
                    <TableRow key={currency.symbol} hover>
                      <TableCell>
                        <IconButton size="small" onClick={() => toggleFavorite(currency.symbol)}>
                          {favorites.includes(currency.symbol) ? <Star color="primary" /> : <StarOutline />}
                        </IconButton>
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <Typography variant="body2" sx={{ fontWeight: 'bold', mr: 1 }}>
                            {currency.logo || '💱'} {currency.symbol}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>{currency.name}</TableCell>
                      <TableCell>${currency.price?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 6 })}</TableCell>
                      <TableCell>
                        <PriceChange value={currency.change24h}>
                          {currency.change24h > 0 ? <ArrowDropUp /> : currency.change24h < 0 ? <ArrowDropDown /> : null}
                          {currency.change24h?.toFixed(2)}%
                        </PriceChange>
                      </TableCell>
                      <TableCell>
                        <FormatVolume volume={currency.volume24h} />
                      </TableCell>
                      <TableCell>
                        <Chip 
                          label={currency.status} 
                          color={currency.status === 'trading' ? 'success' : 'default'} 
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        {currency.pairs?.map(pair => (
                          <Chip 
                            key={pair.symbol} 
                            label={pair.quote}
                            size="small"
                            variant="outlined"
                            sx={{ mr: 0.5, mb: 0.5 }}
                          />
                        ))}
                      </TableCell>
                    </TableRow>
                  ))
                ) : (
                  <TableRow>
                    <TableCell colSpan={8} align="center" sx={{ py: 3 }}>
                      {searchTerm ? 'Нет результатов по вашему запросу' : 'Нет доступных токенов'}
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
          
          {/* Пагинация (если нужна) */}
          {filteredCurrencies.length > 0 && (
            <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 2 }}>
              <Typography variant="body2" color="textSecondary">
                Показано {filteredCurrencies.length} из {currencies.length} токенов
              </Typography>
            </Box>
          )}
        </>
      )}

      {/* Диалог загрузки файла */}
      <Dialog open={showUploadDialog} onClose={() => setShowUploadDialog(false)} maxWidth="md">
        <DialogTitle>Загрузка файла для анализа</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
            Загрузите файл в формате CSV или XLSX с данными о торгах для анализа.
            Файл должен содержать столбцы: дата, символ, цена, объем.
          </Typography>
          <FileUploadNew onUpload={handleFileUpload} />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowUploadDialog(false)}>Закрыть</Button>
        </DialogActions>
      </Dialog>

      {/* Секция результатов анализа */}
      {analyzed && analysisResults && (
        <Box sx={{ mt: 4 }}>
          <Typography variant="h5" gutterBottom>
            Результаты анализа
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>
                  Ключевые метрики
                </Typography>
                {/* Здесь будут отображаться результаты анализа */}
                <Typography>
                  Данные еще в разработке...
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>
                  ML предсказания
                </Typography>
                {/* Здесь будут ML предсказания */}
                <Typography>
                  ML-анализ еще в разработке...
                </Typography>
              </Paper>
            </Grid>
          </Grid>
        </Box>
      )}
    </Box>
  );
};

export default TokenAnalytics;
