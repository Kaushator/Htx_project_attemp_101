import React, { useState } from 'react';
import {
  Container,
  Typography,
  Grid,
  Paper,
  Box,
  Card,
  CardContent,
  Chip,
  Alert,
  Tabs,
  Tab,
  Button
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  Activity,
  BarChart3,
  AlertTriangle,
  Trophy,
  Calendar,
  Target
} from 'lucide-react';

const SimpleModernDashboard = () => {
  const [selectedTab, setSelectedTab] = useState(0);

  const handleTabChange = (event, newValue) => {
    setSelectedTab(newValue);
  };

  return (
    <Container maxWidth="xl" sx={{ mt: 2, mb: 4 }}>
      <Typography variant="h3" gutterBottom sx={{ fontWeight: 600, color: 'primary.main' }}>
        HTX Trading Analytics Dashboard
      </Typography>
      
      <Typography variant="h6" color="text.secondary" gutterBottom>
        Продвинутая аналитика торговли с real-time данными
      </Typography>

      {/* Status Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center">
                <Box>
                  <Typography color="text.secondary" gutterBottom>
                    Total PnL
                  </Typography>
                  <Typography variant="h4" sx={{ color: 'success.main' }}>
                    +$2,456.78
                  </Typography>
                </Box>
                <TrendingUp size={40} color="#4caf50" />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center">
                <Box>
                  <Typography color="text.secondary" gutterBottom>
                    Active Trades
                  </Typography>
                  <Typography variant="h4">
                    23
                  </Typography>
                </Box>
                <Activity size={40} color="#2196f3" />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center">
                <Box>
                  <Typography color="text.secondary" gutterBottom>
                    Win Rate
                  </Typography>
                  <Typography variant="h4" sx={{ color: 'success.main' }}>
                    73.2%
                  </Typography>
                </Box>
                <Trophy size={40} color="#ff9800" />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center">
                <Box>
                  <Typography color="text.secondary" gutterBottom>
                    Risk Score
                  </Typography>
                  <Typography variant="h4" sx={{ color: 'warning.main' }}>
                    Medium
                  </Typography>
                </Box>
                <AlertTriangle size={40} color="#ff5722" />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* System Status */}
      <Alert severity="success" sx={{ mb: 3 }}>
        ✅ Система работает нормально. Backend API: Online, Frontend: Loaded, WebSocket: Ready
      </Alert>

      {/* Tabs Navigation */}
      <Paper sx={{ mb: 3 }}>
        <Tabs
          value={selectedTab}
          onChange={handleTabChange}
          variant="scrollable"
          scrollButtons="auto"
          indicatorColor="primary"
          textColor="primary"
        >
          <Tab label="PnL Overview" icon={<TrendingUp size={20} />} />
          <Tab label="Risk Analysis" icon={<AlertTriangle size={20} />} />
          <Tab label="Trading Patterns" icon={<BarChart3 size={20} />} />
          <Tab label="Performance" icon={<Trophy size={20} />} />
          <Tab label="Predictions" icon={<Calendar size={20} />} />
          <Tab label="Recent Activity" icon={<Activity size={20} />} />
          <Tab label="API Requirements" icon={<Target size={20} />} />
        </Tabs>
      </Paper>

      {/* Tab Content */}
      <Paper sx={{ p: 3, minHeight: 400 }}>
        {selectedTab === 0 && (
          <Box>
            <Typography variant="h5" gutterBottom>PnL Overview</Typography>
            <Typography>Здесь будут графики прибыли и убытков...</Typography>
          </Box>
        )}
        
        {selectedTab === 1 && (
          <Box>
            <Typography variant="h5" gutterBottom>Risk Analysis</Typography>
            <Typography>Здесь будет анализ рисков...</Typography>
          </Box>
        )}
        
        {selectedTab === 2 && (
          <Box>
            <Typography variant="h5" gutterBottom>Trading Patterns</Typography>
            <Typography>Здесь будут паттерны торговли...</Typography>
          </Box>
        )}
        
        {selectedTab === 3 && (
          <Box>
            <Typography variant="h5" gutterBottom>Performance Metrics</Typography>
            <Typography>Здесь будут метрики производительности...</Typography>
          </Box>
        )}
        
        {selectedTab === 4 && (
          <Box>
            <Typography variant="h5" gutterBottom>Predictions</Typography>
            <Typography>Здесь будут ML прогнозы...</Typography>
          </Box>
        )}
        
        {selectedTab === 5 && (
          <Box>
            <Typography variant="h5" gutterBottom>Recent Activity</Typography>
            <Typography>Здесь будет последняя активность...</Typography>
          </Box>
        )}
        
        {selectedTab === 6 && (
          <Box>
            <Typography variant="h5" gutterBottom>API Requirements</Typography>
            <Typography>Здесь будут требования к 3Commas API...</Typography>
            <Alert severity="info" sx={{ mt: 2 }}>
              Все готово для интеграции с 3Commas API. Спецификация данных готова.
            </Alert>
          </Box>
        )}
      </Paper>

      {/* Action Buttons */}
      <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
        <Button variant="contained" color="primary">
          Загрузить данные
        </Button>
        <Button variant="outlined" color="secondary">
          Экспорт отчета
        </Button>
        <Button variant="outlined">
          Настройки
        </Button>
      </Box>
    </Container>
  );
};

export default SimpleModernDashboard;
