import React, { useState, useEffect } from 'react';
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
  CircularProgress,
  Tabs,
  Tab,
  IconButton,
  Tooltip,
  FormControl,
  Select,
  MenuItem,
  InputLabel,
  Fab
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  Activity,
  BarChart3,
  Refresh,
  Calendar,
  Target,
  AlertTriangle,
  Trophy,
  RefreshCw
} from 'lucide-react';
import { motion } from 'framer-motion';
import { useAdvancedPnL } from '../hooks/useAdvancedPnL';
import PnLOverview from '../components/PnLOverview';
import RiskMetrics from '../components/RiskMetrics';
import TradingPatterns from '../components/TradingPatterns';
import PredictionsChart from '../components/PredictionsChart';
import PerformanceMetrics from '../components/PerformanceMetrics';
import RecentActivity from '../components/RecentActivity';
import FileUpload from '../components/FileUpload';
import WebSocketStatus from '../components/WebSocketStatus';
import DataRequirements from '../components/DataRequirements';

const Dashboard = () => {
  const [selectedTab, setSelectedTab] = useState(0);
  const [timeframe, setTimeframe] = useState(30); // days
  const [realtimeData, setRealtimeData] = useState(null);
  
  const {
    data: analytics,
    isLoading,
    error,
    refetch
  } = useAdvancedPnL(timeframe);

  const handleTabChange = (event, newValue) => {
    setSelectedTab(newValue);
  };

  const handleTimeframeChange = (days) => {
    setTimeframe(days);
  };

  const handleRefresh = () => {
    refetch();
  };

  const handleWebSocketData = (data) => {
    setRealtimeData(data);
    // If the data is relevant to current view, trigger refresh
    if (data.type === 'trade_update' || data.type === 'data_update') {
      setTimeout(() => refetch(), 1000); // Small delay to allow backend to process
    }
  };

  if (error) {
    return (
      <Container>
        <Alert severity="error" sx={{ mt: 2 }}>
          Ошибка загрузки данных: {error.message}
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ py: 3 }}>
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Box>
            <Typography variant="h3" component="h1" fontWeight="bold" color="primary">
              Trading Dashboard
            </Typography>
            <Typography variant="subtitle1" color="text.secondary">
              Advanced PnL Analytics & Performance Insights
            </Typography>
          </Box>
          
          <Box display="flex" gap={1} alignItems="center">
            {/* Timeframe Selector */}
            <Box display="flex" gap={1}>
              {[7, 30, 90].map((days) => (
                <Chip
                  key={days}
                  label={`${days}д`}
                  onClick={() => handleTimeframeChange(days)}
                  color={timeframe === days ? 'primary' : 'default'}
                  variant={timeframe === days ? 'filled' : 'outlined'}
                />
              ))}
            </Box>
            
            <Tooltip title="Обновить данные">
              <IconButton onClick={handleRefresh} disabled={isLoading}>
                <Refresh className={isLoading ? 'animate-spin' : ''} />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>
      </motion.div>

      {/* Loading State */}
      {isLoading && (
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress size={60} />
          <Typography variant="h6" sx={{ ml: 2 }}>
            Загружаем аналитику...
          </Typography>
        </Box>
      )}

      {/* Main Content */}
      {!isLoading && analytics && (
        <>
          {/* Key Metrics Cards */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            <Grid container spacing={3} mb={4}>
              <Grid item xs={12} sm={6} md={3}>
                <MetricCard
                  title="Net PnL"
                  value={analytics.basic_pnl?.net_pnl || 0}
                  format="currency"
                  icon={<DollarSign />}
                  trend={analytics.basic_pnl?.net_pnl > 0 ? 'up' : 'down'}
                />
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <MetricCard
                  title="Win Rate"
                  value={(analytics.risk_metrics?.win_rate || 0) * 100}
                  format="percentage"
                  icon={<Target />}
                  trend={analytics.risk_metrics?.win_rate > 0.5 ? 'up' : 'down'}
                />
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <MetricCard
                  title="Sharpe Ratio"
                  value={analytics.risk_metrics?.sharpe_ratio || 0}
                  format="number"
                  icon={<BarChart3 />}
                  trend={analytics.risk_metrics?.sharpe_ratio > 1 ? 'up' : 'down'}
                />
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <MetricCard
                  title="Total Trades"
                  value={analytics.total_trades || 0}
                  format="number"
                  icon={<Activity />}
                />
              </Grid>
            </Grid>
          </motion.div>

          {/* File Upload */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <Grid container spacing={3}>
              <Grid item xs={12} md={8}>
                <FileUpload onUpload={refetch} />
              </Grid>
              <Grid item xs={12} md={4}>
                <WebSocketStatus onDataUpdate={handleWebSocketData} />
              </Grid>
            </Grid>
          </motion.div>

          {/* Tabs Navigation */}
          <Paper sx={{ mb: 3 }}>
            <Tabs
              value={selectedTab}
              onChange={handleTabChange}
              variant="fullWidth"
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
          <motion.div
            key={selectedTab}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3 }}
          >
            {selectedTab === 0 && (
              <PnLOverview data={analytics} />
            )}

            {selectedTab === 1 && (
              <RiskMetrics data={analytics} />
            )}

            {selectedTab === 2 && (
              <TradingPatterns data={analytics} />
            )}

            {selectedTab === 3 && (
              <PerformanceMetrics data={analytics} />
            )}

            {selectedTab === 4 && (
              <PredictionsChart data={analytics} />
            )}

            {selectedTab === 5 && (
              <RecentActivity data={analytics} />
            )}

            {selectedTab === 6 && (
              <DataRequirements />
            )}
          </motion.div>
        </>
      )}
      
      {/* Floating Refresh Button */}
      <Fab
        color="primary"
        aria-label="refresh"
        sx={{
          position: 'fixed',
          bottom: 16,
          right: 16,
        }}
        onClick={handleRefresh}
        disabled={isLoading}
      >
        <RefreshCw size={24} />
      </Fab>
    </Container>
  );
};

// MetricCard Component
const MetricCard = ({ title, value, format, icon, trend }) => {
  const formatValue = (val, fmt) => {
    if (typeof val !== 'number') return '—';
    
    switch (fmt) {
      case 'currency':
        return new Intl.NumberFormat('ru-RU', {
          style: 'currency',
          currency: 'USD'
        }).format(val);
      case 'percentage':
        return `${val.toFixed(2)}%`;
      case 'number':
        return val.toFixed(2);
      default:
        return val.toString();
    }
  };

  const getTrendColor = () => {
    if (trend === 'up') return 'success.main';
    if (trend === 'down') return 'error.main';
    return 'text.primary';
  };

  const getTrendIcon = () => {
    if (trend === 'up') return <TrendingUp size={16} />;
    if (trend === 'down') return <TrendingDown size={16} />;
    return null;
  };

  return (
    <Card elevation={2} sx={{ height: '100%' }}>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="start" mb={2}>
          <Box sx={{ color: 'primary.main' }}>
            {icon}
          </Box>
          <Box sx={{ color: getTrendColor() }}>
            {getTrendIcon()}
          </Box>
        </Box>
        
        <Typography variant="h4" component="div" sx={{ mb: 1, color: getTrendColor() }}>
          {formatValue(value, format)}
        </Typography>
        
        <Typography color="text.secondary" variant="body2">
          {title}
        </Typography>
      </CardContent>
    </Card>
  );
};

export default Dashboard;
