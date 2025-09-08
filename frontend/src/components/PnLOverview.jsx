import React from 'react';
import {
  Paper,
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  Divider,
  Chip
} from '@mui/material';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { TrendingUp, TrendingDown, DollarSign, Activity } from 'lucide-react';

const PnLOverview = ({ data }) => {
  if (!data || !data.charts) {
    return (
      <Paper sx={{ p: 3 }}>
        <Typography>Нет данных для отображения</Typography>
      </Paper>
    );
  }

  const { basic_pnl, charts } = data;
  const dailyPnLData = charts.daily_pnl_chart || {};

  // Prepare chart data
  const chartData = dailyPnLData.dates?.map((date, index) => ({
    date: new Date(date).toLocaleDateString('ru-RU', { 
      month: 'short', 
      day: 'numeric' 
    }),
    dailyPnL: dailyPnLData.daily_pnl?.[index] || 0,
    cumulativePnL: dailyPnLData.cumulative_pnl?.[index] || 0
  })) || [];

  // Symbol distribution data
  const symbolData = Object.entries(charts.symbol_distribution || {}).map(([symbol, count]) => ({
    symbol,
    count,
    percentage: count
  }));

  // Volume over time data
  const volumeData = charts.volume_over_time?.dates?.map((date, index) => ({
    date: new Date(date).toLocaleDateString('ru-RU', { 
      month: 'short', 
      day: 'numeric' 
    }),
    volume: charts.volume_over_time.volumes?.[index] || 0
  })) || [];

  // Colors for charts
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

  return (
    <Paper sx={{ p: 3, height: 'fit-content' }}>
      <Typography variant="h5" gutterBottom>
        PnL Overview
      </Typography>

      {/* Basic PnL Stats */}
      <Grid container spacing={2} mb={3}>
        <Grid item xs={6} md={3}>
          <Card variant="outlined">
            <CardContent sx={{ py: 2 }}>
              <Box display="flex" alignItems="center" gap={1} mb={1}>
                <DollarSign size={20} color="#1976d2" />
                <Typography variant="body2" color="text.secondary">
                  Net PnL
                </Typography>
              </Box>
              <Typography variant="h6" color={basic_pnl?.net_pnl >= 0 ? 'success.main' : 'error.main'}>
                ${(basic_pnl?.net_pnl || 0).toFixed(2)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={6} md={3}>
          <Card variant="outlined">
            <CardContent sx={{ py: 2 }}>
              <Box display="flex" alignItems="center" gap={1} mb={1}>
                <Activity size={20} color="#1976d2" />
                <Typography variant="body2" color="text.secondary">
                  Total Volume
                </Typography>
              </Box>
              <Typography variant="h6">
                ${(basic_pnl?.total_volume || 0).toFixed(2)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={6} md={3}>
          <Card variant="outlined">
            <CardContent sx={{ py: 2 }}>
              <Typography variant="body2" color="text.secondary" mb={1}>
                Total Fees
              </Typography>
              <Typography variant="h6" color="error.main">
                ${(basic_pnl?.total_fees || 0).toFixed(2)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={6} md={3}>
          <Card variant="outlined">
            <CardContent sx={{ py: 2 }}>
              <Typography variant="body2" color="text.secondary" mb={1}>
                Realized PnL
              </Typography>
              <Typography variant="h6" color={basic_pnl?.realized_pnl >= 0 ? 'success.main' : 'error.main'}>
                ${(basic_pnl?.realized_pnl || 0).toFixed(2)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Divider sx={{ my: 3 }} />

      {/* Daily PnL Chart */}
      {chartData.length > 0 && (
        <Box mb={4}>
          <Typography variant="h6" gutterBottom>
            Daily & Cumulative PnL
          </Typography>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip 
                formatter={(value, name) => [
                  `$${value.toFixed(2)}`, 
                  name === 'dailyPnL' ? 'Daily PnL' : 'Cumulative PnL'
                ]}
              />
              <Legend />
              <Bar dataKey="dailyPnL" fill="#8884d8" name="Daily PnL" />
              <Line 
                type="monotone" 
                dataKey="cumulativePnL" 
                stroke="#82ca9d" 
                strokeWidth={3}
                name="Cumulative PnL"
              />
            </LineChart>
          </ResponsiveContainer>
        </Box>
      )}

      <Grid container spacing={3}>
        {/* Symbol Distribution */}
        {symbolData.length > 0 && (
          <Grid item xs={12} md={6}>
            <Typography variant="h6" gutterBottom>
              Trading Distribution by Symbol
            </Typography>
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={symbolData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ symbol, percentage }) => `${symbol} (${percentage})`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="count"
                >
                  {symbolData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Grid>
        )}

        {/* Volume Chart */}
        {volumeData.length > 0 && (
          <Grid item xs={12} md={6}>
            <Typography variant="h6" gutterBottom>
              Trading Volume Over Time
            </Typography>
            <ResponsiveContainer width="100%" height={250}>
              <AreaChart data={volumeData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip formatter={(value) => [`${value.toFixed(2)}`, 'Volume']} />
                <Area 
                  type="monotone" 
                  dataKey="volume" 
                  stroke="#8884d8" 
                  fill="#8884d8" 
                  fillOpacity={0.6}
                />
              </AreaChart>
            </ResponsiveContainer>
          </Grid>
        )}
      </Grid>

      {/* Current Positions */}
      {basic_pnl?.current_positions && Object.keys(basic_pnl.current_positions).length > 0 && (
        <Box mt={3}>
          <Typography variant="h6" gutterBottom>
            Current Positions
          </Typography>
          <Box display="flex" flexWrap="wrap" gap={1}>
            {Object.entries(basic_pnl.current_positions).map(([symbol, position]) => (
              <Chip
                key={symbol}
                label={`${symbol}: ${position.quantity.toFixed(4)} @ $${position.avg_price.toFixed(2)}`}
                color="primary"
                variant="outlined"
                size="small"
              />
            ))}
          </Box>
        </Box>
      )}
    </Paper>
  );
};

export default PnLOverview;
