import React, { useState } from 'react';
import {
  Paper,
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  Tabs,
  Tab,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  LinearProgress
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
  RadialBarChart,
  RadialBar,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { 
  TrendingUp, 
  Target, 
  Award, 
  Activity,
  BarChart3,
  Percent
} from 'lucide-react';

const PerformanceMetrics = ({ data }) => {
  const [activeTab, setActiveTab] = useState(0);

  if (!data || !data.performance) {
    return (
      <Paper sx={{ p: 3 }}>
        <Typography>Нет данных по производительности</Typography>
      </Paper>
    );
  }

  const { performance } = data;

  // Key performance metrics
  const kpiData = [
    {
      label: 'Total Return',
      value: (performance.total_return || 0) * 100,
      unit: '%',
      color: performance.total_return >= 0 ? 'success.main' : 'error.main',
      icon: TrendingUp
    },
    {
      label: 'Sharpe Ratio',
      value: performance.sharpe_ratio || 0,
      unit: '',
      color: performance.sharpe_ratio >= 1 ? 'success.main' : 'warning.main',
      icon: Target
    },
    {
      label: 'Win Rate',
      value: (performance.win_rate || 0) * 100,
      unit: '%',
      color: performance.win_rate >= 0.5 ? 'success.main' : 'error.main',
      icon: Award
    },
    {
      label: 'Max Drawdown',
      value: Math.abs(performance.max_drawdown || 0) * 100,
      unit: '%',
      color: 'error.main',
      icon: Activity
    }
  ];

  // Monthly performance data
  const monthlyData = performance.monthly_returns ? 
    Object.entries(performance.monthly_returns).map(([month, returns]) => ({
      month: new Date(month).toLocaleDateString('ru-RU', { 
        month: 'short', 
        year: '2-digit' 
      }),
      returns: returns * 100,
      cumulative: (performance.cumulative_returns?.[month] || 0) * 100
    })) : [];

  // Performance ratios
  const ratiosData = [
    { 
      name: 'Sharpe Ratio', 
      value: performance.sharpe_ratio || 0,
      benchmark: 1.0,
      max: 3.0
    },
    { 
      name: 'Sortino Ratio', 
      value: performance.sortino_ratio || 0,
      benchmark: 1.5,
      max: 4.0
    },
    { 
      name: 'Calmar Ratio', 
      value: performance.calmar_ratio || 0,
      benchmark: 0.5,
      max: 2.0
    },
    { 
      name: 'Information Ratio', 
      value: performance.information_ratio || 0,
      benchmark: 0.4,
      max: 1.5
    }
  ];

  // Drawdown analysis
  const drawdownData = performance.drawdown_periods ? 
    performance.drawdown_periods.map((dd, index) => ({
      period: index + 1,
      drawdown: Math.abs(dd.drawdown || 0) * 100,
      duration: dd.duration || 0,
      recovery: dd.recovery_time || 0
    })) : [];

  // Risk-adjusted returns
  const riskAdjustedData = performance.risk_buckets ? 
    Object.entries(performance.risk_buckets).map(([bucket, data]) => ({
      risk_level: bucket.replace('_', ' ').toUpperCase(),
      return: (data.return || 0) * 100,
      volatility: (data.volatility || 0) * 100,
      sharpe: data.sharpe || 0
    })) : [];

  // Performance attribution
  const attributionData = performance.attribution ? 
    Object.entries(performance.attribution).map(([factor, contribution]) => ({
      factor: factor.replace('_', ' ').toUpperCase(),
      contribution: contribution * 100
    })) : [];

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  return (
    <Paper sx={{ p: 3, height: 'fit-content' }}>
      <Typography variant="h5" gutterBottom>
        Performance Analytics
      </Typography>

      {/* Key Performance Indicators */}
      <Grid container spacing={2} mb={3}>
        {kpiData.map((kpi, index) => {
          const IconComponent = kpi.icon;
          return (
            <Grid item xs={6} md={3} key={kpi.label}>
              <Card variant="outlined">
                <CardContent sx={{ py: 2 }}>
                  <Box display="flex" alignItems="center" gap={1} mb={1}>
                    <IconComponent size={20} />
                    <Typography variant="body2" color="text.secondary">
                      {kpi.label}
                    </Typography>
                  </Box>
                  <Typography variant="h6" color={kpi.color}>
                    {kpi.value.toFixed(kpi.label === 'Sharpe Ratio' ? 3 : 1)}{kpi.unit}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          );
        })}
      </Grid>

      <Tabs value={activeTab} onChange={handleTabChange} sx={{ mb: 3 }}>
        <Tab label="Returns Analysis" />
        <Tab label="Risk Ratios" />
        <Tab label="Drawdown Analysis" />
        <Tab label="Attribution" />
      </Tabs>

      {/* Returns Analysis Tab */}
      {activeTab === 0 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom>
              Monthly Returns & Cumulative Performance
            </Typography>
            <ResponsiveContainer width="100%" height={350}>
              <AreaChart data={monthlyData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip 
                  formatter={(value, name) => [
                    `${value.toFixed(2)}%`, 
                    name === 'returns' ? 'Monthly Return' : 'Cumulative Return'
                  ]}
                />
                <Legend />
                <Bar dataKey="returns" fill="#8884d8" name="Monthly Returns" />
                <Area 
                  type="monotone" 
                  dataKey="cumulative" 
                  stroke="#82ca9d" 
                  fill="#82ca9d"
                  fillOpacity={0.3}
                  name="Cumulative Returns"
                />
              </AreaChart>
            </ResponsiveContainer>
          </Grid>

          {/* Performance Summary */}
          <Grid item xs={12} md={6}>
            <Typography variant="h6" gutterBottom>
              Return Statistics
            </Typography>
            <TableContainer>
              <Table size="small">
                <TableBody>
                  <TableRow>
                    <TableCell>Average Monthly Return</TableCell>
                    <TableCell align="right">
                      {((performance.avg_monthly_return || 0) * 100).toFixed(2)}%
                    </TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Best Month</TableCell>
                    <TableCell align="right" sx={{ color: 'success.main' }}>
                      {((performance.best_month || 0) * 100).toFixed(2)}%
                    </TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Worst Month</TableCell>
                    <TableCell align="right" sx={{ color: 'error.main' }}>
                      {((performance.worst_month || 0) * 100).toFixed(2)}%
                    </TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Volatility</TableCell>
                    <TableCell align="right">
                      {((performance.volatility || 0) * 100).toFixed(2)}%
                    </TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Positive Months</TableCell>
                    <TableCell align="right">
                      {performance.positive_months || 0} / {performance.total_months || 0}
                    </TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </TableContainer>
          </Grid>

          <Grid item xs={12} md={6}>
            <Typography variant="h6" gutterBottom>
              Risk-Adjusted Performance
            </Typography>
            {riskAdjustedData.map((item) => (
              <Card key={item.risk_level} variant="outlined" sx={{ mb: 1 }}>
                <CardContent sx={{ py: 1 }}>
                  <Box display="flex" justifyContent="space-between" alignItems="center">
                    <Typography variant="body2">
                      {item.risk_level}
                    </Typography>
                    <Box textAlign="right">
                      <Typography variant="body2">
                        Return: {item.return.toFixed(1)}%
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        Sharpe: {item.sharpe.toFixed(2)}
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            ))}
          </Grid>
        </Grid>
      )}

      {/* Risk Ratios Tab */}
      {activeTab === 1 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Typography variant="h6" gutterBottom>
              Risk-Adjusted Performance Ratios
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={ratiosData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="value" fill="#8884d8" name="Current Value" />
                <Bar dataKey="benchmark" fill="#82ca9d" name="Benchmark" />
              </BarChart>
            </ResponsiveContainer>
          </Grid>

          <Grid item xs={12} md={4}>
            <Typography variant="h6" gutterBottom>
              Ratio Analysis
            </Typography>
            {ratiosData.map((ratio) => (
              <Card key={ratio.name} variant="outlined" sx={{ mb: 2 }}>
                <CardContent>
                  <Typography variant="subtitle2" gutterBottom>
                    {ratio.name}
                  </Typography>
                  <Box display="flex" alignItems="center" gap={2} mb={1}>
                    <LinearProgress
                      variant="determinate"
                      value={(ratio.value / ratio.max) * 100}
                      color={ratio.value >= ratio.benchmark ? 'success' : 'warning'}
                      sx={{ flexGrow: 1, height: 8 }}
                    />
                    <Typography variant="body2">
                      {ratio.value.toFixed(2)}
                    </Typography>
                  </Box>
                  <Box display="flex" justifyContent="space-between">
                    <Typography variant="caption" color="text.secondary">
                      Benchmark: {ratio.benchmark}
                    </Typography>
                    <Chip
                      label={ratio.value >= ratio.benchmark ? 'Good' : 'Poor'}
                      color={ratio.value >= ratio.benchmark ? 'success' : 'error'}
                      size="small"
                    />
                  </Box>
                </CardContent>
              </Card>
            ))}
          </Grid>
        </Grid>
      )}

      {/* Drawdown Analysis Tab */}
      {activeTab === 2 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Typography variant="h6" gutterBottom>
              Drawdown Periods Analysis
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={drawdownData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="period" />
                <YAxis />
                <Tooltip 
                  formatter={(value, name) => [
                    name === 'drawdown' ? `${value.toFixed(1)}%` : `${value} days`,
                    name === 'drawdown' ? 'Max Drawdown' : 
                    name === 'duration' ? 'Duration' : 'Recovery Time'
                  ]}
                />
                <Legend />
                <Bar dataKey="drawdown" fill="#f44336" name="Max Drawdown %" />
                <Bar dataKey="duration" fill="#ff9800" name="Duration (days)" />
              </BarChart>
            </ResponsiveContainer>
          </Grid>

          <Grid item xs={12} md={4}>
            <Typography variant="h6" gutterBottom>
              Drawdown Statistics
            </Typography>
            <Card variant="outlined" sx={{ mb: 2 }}>
              <CardContent>
                <Typography variant="subtitle2" gutterBottom>
                  Current Drawdown
                </Typography>
                <Typography variant="h5" color="error.main">
                  {((performance.current_drawdown || 0) * 100).toFixed(2)}%
                </Typography>
              </CardContent>
            </Card>

            <Card variant="outlined" sx={{ mb: 2 }}>
              <CardContent>
                <Typography variant="subtitle2" gutterBottom>
                  Average Drawdown
                </Typography>
                <Typography variant="h6">
                  {((performance.avg_drawdown || 0) * 100).toFixed(2)}%
                </Typography>
              </CardContent>
            </Card>

            <Card variant="outlined">
              <CardContent>
                <Typography variant="subtitle2" gutterBottom>
                  Recovery Factor
                </Typography>
                <Typography variant="h6" color="success.main">
                  {(performance.recovery_factor || 0).toFixed(2)}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Higher is better
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Attribution Tab */}
      {activeTab === 3 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Typography variant="h6" gutterBottom>
              Performance Attribution
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={attributionData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ factor, contribution }) => 
                    `${factor}: ${contribution.toFixed(1)}%`
                  }
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="contribution"
                >
                  {attributionData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Grid>

          <Grid item xs={12} md={6}>
            <Typography variant="h6" gutterBottom>
              Factor Contributions
            </Typography>
            {attributionData.map((factor) => (
              <Card key={factor.factor} variant="outlined" sx={{ mb: 1 }}>
                <CardContent sx={{ py: 1 }}>
                  <Box display="flex" justifyContent="space-between" alignItems="center">
                    <Typography variant="body2">
                      {factor.factor}
                    </Typography>
                    <Box display="flex" alignItems="center" gap={1}>
                      <LinearProgress
                        variant="determinate"
                        value={Math.abs(factor.contribution)}
                        color={factor.contribution >= 0 ? 'success' : 'error'}
                        sx={{ width: 60, height: 6 }}
                      />
                      <Typography 
                        variant="body2"
                        color={factor.contribution >= 0 ? 'success.main' : 'error.main'}
                      >
                        {factor.contribution >= 0 ? '+' : ''}{factor.contribution.toFixed(1)}%
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            ))}
          </Grid>
        </Grid>
      )}

      {/* Performance Grade */}
      <Box mt={3}>
        <Typography variant="h6" gutterBottom>
          Overall Performance Grade
        </Typography>
        <Card variant="outlined">
          <CardContent>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} md={6}>
                <Box display="flex" alignItems="center" gap={2}>
                  <Award size={32} color="#1976d2" />
                  <Box>
                    <Typography variant="h4" color="primary">
                      {performance.performance_grade || 'B+'}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Performance Score: {(performance.performance_score || 0.75) * 100}/100
                    </Typography>
                  </Box>
                </Box>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="body2" color="text.secondary">
                  {performance.performance_comment || 
                    'Good risk-adjusted returns with manageable drawdowns. Consider optimizing trade sizing for better Sharpe ratio.'}
                </Typography>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      </Box>
    </Paper>
  );
};

export default PerformanceMetrics;
