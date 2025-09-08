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
  Avatar
} from '@mui/material';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ScatterChart,
  Scatter,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { 
  Clock, 
  Calendar, 
  TrendingUp, 
  Target, 
  Activity,
  BarChart3
} from 'lucide-react';

const TradingPatterns = ({ data }) => {
  const [activeTab, setActiveTab] = useState(0);

  if (!data || !data.patterns) {
    return (
      <Paper sx={{ p: 3 }}>
        <Typography>Нет данных по торговым паттернам</Typography>
      </Paper>
    );
  }

  const { patterns } = data;

  // Prepare hourly trading pattern data
  const hourlyData = patterns.hourly_pattern ? 
    Object.entries(patterns.hourly_pattern).map(([hour, count]) => ({
      hour: `${hour}:00`,
      trades: count,
      intensity: count / Math.max(...Object.values(patterns.hourly_pattern))
    })) : [];

  // Weekly pattern data
  const weeklyData = patterns.weekly_pattern ?
    ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
      .map((day, index) => ({
        day,
        trades: patterns.weekly_pattern[index] || 0
      })) : [];

  // Symbol performance data
  const symbolData = patterns.symbol_performance ? 
    Object.entries(patterns.symbol_performance).map(([symbol, perf]) => ({
      symbol,
      winRate: (perf.win_rate * 100),
      avgProfit: perf.avg_profit,
      totalTrades: perf.total_trades,
      profitFactor: perf.profit_factor
    })) : [];

  // Trade size distribution
  const tradeSizeData = patterns.trade_size_distribution ?
    Object.entries(patterns.trade_size_distribution).map(([range, count]) => ({
      range,
      count,
      percentage: count
    })) : [];

  // Correlation data for scatter plot
  const correlationData = patterns.correlation_analysis ? 
    patterns.correlation_analysis.map((item, index) => ({
      time: index,
      volume: item.volume || 0,
      pnl: item.pnl || 0,
      volatility: item.volatility || 0
    })) : [];

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D'];

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  return (
    <Paper sx={{ p: 3, height: 'fit-content' }}>
      <Typography variant="h5" gutterBottom>
        Trading Patterns Analysis
      </Typography>

      <Tabs value={activeTab} onChange={handleTabChange} sx={{ mb: 3 }}>
        <Tab label="Temporal Patterns" />
        <Tab label="Symbol Analysis" />
        <Tab label="Trade Sizes" />
        <Tab label="Correlations" />
      </Tabs>

      {/* Temporal Patterns Tab */}
      {activeTab === 0 && (
        <Grid container spacing={3}>
          {/* Hourly Pattern */}
          <Grid item xs={12} md={6}>
            <Box mb={2}>
              <Box display="flex" alignItems="center" gap={1} mb={1}>
                <Clock size={20} />
                <Typography variant="h6">
                  Hourly Trading Activity
                </Typography>
              </Box>
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={hourlyData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="hour" />
                  <YAxis />
                  <Tooltip formatter={(value) => [value, 'Trades']} />
                  <Bar dataKey="trades" fill="#8884d8" />
                </BarChart>
              </ResponsiveContainer>
            </Box>

            {/* Peak Trading Hours */}
            {hourlyData.length > 0 && (
              <Card variant="outlined" sx={{ mt: 2 }}>
                <CardContent>
                  <Typography variant="subtitle2" gutterBottom>
                    Peak Trading Hours
                  </Typography>
                  <Box display="flex" flexWrap="wrap" gap={1}>
                    {hourlyData
                      .sort((a, b) => b.trades - a.trades)
                      .slice(0, 3)
                      .map((hour, index) => (
                        <Chip
                          key={hour.hour}
                          label={`${hour.hour} (${hour.trades} trades)`}
                          color={index === 0 ? 'primary' : 'default'}
                          size="small"
                        />
                      ))}
                  </Box>
                </CardContent>
              </Card>
            )}
          </Grid>

          {/* Weekly Pattern */}
          <Grid item xs={12} md={6}>
            <Box mb={2}>
              <Box display="flex" alignItems="center" gap={1} mb={1}>
                <Calendar size={20} />
                <Typography variant="h6">
                  Weekly Trading Distribution
                </Typography>
              </Box>
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={weeklyData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="day" angle={-45} textAnchor="end" height={80} />
                  <YAxis />
                  <Tooltip formatter={(value) => [value, 'Trades']} />
                  <Bar dataKey="trades" fill="#00C49F" />
                </BarChart>
              </ResponsiveContainer>
            </Box>

            {/* Most Active Day */}
            {weeklyData.length > 0 && (
              <Card variant="outlined" sx={{ mt: 2 }}>
                <CardContent>
                  <Typography variant="subtitle2" gutterBottom>
                    Most Active Trading Days
                  </Typography>
                  <Box display="flex" flexWrap="wrap" gap={1}>
                    {weeklyData
                      .sort((a, b) => b.trades - a.trades)
                      .slice(0, 3)
                      .map((day, index) => (
                        <Chip
                          key={day.day}
                          label={`${day.day} (${day.trades})`}
                          color={index === 0 ? 'primary' : 'default'}
                          size="small"
                        />
                      ))}
                  </Box>
                </CardContent>
              </Card>
            )}
          </Grid>
        </Grid>
      )}

      {/* Symbol Analysis Tab */}
      {activeTab === 1 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom>
              Symbol Performance Analysis
            </Typography>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Symbol</TableCell>
                    <TableCell align="right">Win Rate</TableCell>
                    <TableCell align="right">Avg Profit</TableCell>
                    <TableCell align="right">Total Trades</TableCell>
                    <TableCell align="right">Profit Factor</TableCell>
                    <TableCell>Performance</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {symbolData.map((symbol) => (
                    <TableRow key={symbol.symbol}>
                      <TableCell component="th" scope="row">
                        <Box display="flex" alignItems="center" gap={1}>
                          <Avatar sx={{ width: 24, height: 24, fontSize: 12 }}>
                            {symbol.symbol.slice(0, 2)}
                          </Avatar>
                          {symbol.symbol}
                        </Box>
                      </TableCell>
                      <TableCell align="right">
                        <Chip
                          label={`${symbol.winRate.toFixed(1)}%`}
                          color={symbol.winRate >= 50 ? 'success' : 'error'}
                          size="small"
                        />
                      </TableCell>
                      <TableCell align="right">
                        ${symbol.avgProfit.toFixed(2)}
                      </TableCell>
                      <TableCell align="right">
                        {symbol.totalTrades}
                      </TableCell>
                      <TableCell align="right">
                        {symbol.profitFactor.toFixed(2)}
                      </TableCell>
                      <TableCell>
                        {symbol.winRate >= 60 && symbol.profitFactor > 1.5 ? (
                          <Chip label="Excellent" color="success" size="small" />
                        ) : symbol.winRate >= 50 && symbol.profitFactor > 1 ? (
                          <Chip label="Good" color="primary" size="small" />
                        ) : (
                          <Chip label="Poor" color="error" size="small" />
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Grid>
        </Grid>
      )}

      {/* Trade Sizes Tab */}
      {activeTab === 2 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Typography variant="h6" gutterBottom>
              Trade Size Distribution
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={tradeSizeData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ range, percentage }) => `${range} (${percentage}%)`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="count"
                >
                  {tradeSizeData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Grid>

          <Grid item xs={12} md={6}>
            <Typography variant="h6" gutterBottom>
              Position Sizing Analysis
            </Typography>
            <Grid container spacing={2}>
              {tradeSizeData.map((item, index) => (
                <Grid item xs={6} key={item.range}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="body2" color="text.secondary">
                        {item.range}
                      </Typography>
                      <Typography variant="h6">
                        {item.count} trades
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {item.percentage}% of total
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Grid>
        </Grid>
      )}

      {/* Correlations Tab */}
      {activeTab === 3 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Typography variant="h6" gutterBottom>
              Volume vs PnL Correlation
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <ScatterChart data={correlationData}>
                <CartesianGrid />
                <XAxis dataKey="volume" name="Volume" />
                <YAxis dataKey="pnl" name="PnL" />
                <Tooltip 
                  cursor={{ strokeDasharray: '3 3' }}
                  formatter={(value, name) => [
                    name === 'volume' ? `$${value.toFixed(2)}` : `$${value.toFixed(2)}`,
                    name === 'volume' ? 'Volume' : 'PnL'
                  ]}
                />
                <Scatter dataKey="pnl" fill="#8884d8" />
              </ScatterChart>
            </ResponsiveContainer>
          </Grid>

          <Grid item xs={12} md={6}>
            <Typography variant="h6" gutterBottom>
              Volatility Impact
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={correlationData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="volatility" 
                  stroke="#8884d8" 
                  name="Volatility"
                />
              </LineChart>
            </ResponsiveContainer>
          </Grid>
        </Grid>
      )}

      {/* Pattern Insights */}
      {patterns.insights && patterns.insights.length > 0 && (
        <Box mt={3}>
          <Typography variant="h6" gutterBottom>
            Pattern Insights
          </Typography>
          <Grid container spacing={2}>
            {patterns.insights.map((insight, index) => (
              <Grid item xs={12} md={6} key={index}>
                <Card variant="outlined">
                  <CardContent>
                    <Box display="flex" alignItems="center" gap={1} mb={1}>
                      <BarChart3 size={20} color="#1976d2" />
                      <Typography variant="subtitle2">
                        {insight.title}
                      </Typography>
                    </Box>
                    <Typography variant="body2" color="text.secondary">
                      {insight.description}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>
      )}
    </Paper>
  );
};

export default TradingPatterns;
