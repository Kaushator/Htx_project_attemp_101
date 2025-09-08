import React from 'react';
import {
  Paper,
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  LinearProgress,
  Chip,
  Alert,
  AlertTitle
} from '@mui/material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  BarChart,
  Bar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar
} from 'recharts';
import { Shield, AlertTriangle, TrendingUp, Target } from 'lucide-react';

const RiskMetrics = ({ data }) => {
  if (!data || !data.risk_analysis) {
    return (
      <Paper sx={{ p: 3 }}>
        <Typography>Нет данных по рискам для отображения</Typography>
      </Paper>
    );
  }

  const { risk_analysis } = data;

  // Risk score color
  const getRiskColor = (score) => {
    if (score <= 0.3) return 'success';
    if (score <= 0.6) return 'warning';
    return 'error';
  };

  // Risk level text
  const getRiskLevel = (score) => {
    if (score <= 0.3) return 'Низкий';
    if (score <= 0.6) return 'Средний';
    return 'Высокий';
  };

  // VaR data for chart
  const varData = [
    { period: '1 день', var_95: risk_analysis.var?.['1d_95'] || 0, var_99: risk_analysis.var?.['1d_99'] || 0 },
    { period: '1 неделя', var_95: risk_analysis.var?.['1w_95'] || 0, var_99: risk_analysis.var?.['1w_99'] || 0 },
    { period: '1 месяц', var_95: risk_analysis.var?.['1m_95'] || 0, var_99: risk_analysis.var?.['1m_99'] || 0 }
  ];

  // Risk metrics radar data
  const radarData = [
    {
      metric: 'Волатильность',
      value: Math.min((risk_analysis.volatility || 0) * 100, 100)
    },
    {
      metric: 'Max Drawdown',
      value: Math.abs(risk_analysis.max_drawdown || 0) * 2 // Scale for visibility
    },
    {
      metric: 'Sharpe Ratio',
      value: Math.max(0, Math.min((risk_analysis.sharpe_ratio || 0) * 20, 100))
    },
    {
      metric: 'Risk Score',
      value: (risk_analysis.risk_score || 0) * 100
    },
    {
      metric: 'VaR Impact',
      value: Math.abs(risk_analysis.var?.['1d_95'] || 0) / 10 // Scale for chart
    }
  ];

  return (
    <Paper sx={{ p: 3, height: 'fit-content' }}>
      <Typography variant="h5" gutterBottom>
        Risk Analysis
      </Typography>

      {/* Risk Score Overview */}
      <Card variant="outlined" sx={{ mb: 3 }}>
        <CardContent>
          <Box display="flex" alignItems="center" gap={2} mb={2}>
            <Shield size={24} color="#1976d2" />
            <Typography variant="h6">
              Overall Risk Score
            </Typography>
          </Box>
          
          <Box display="flex" alignItems="center" gap={2} mb={2}>
            <Box flexGrow={1}>
              <LinearProgress 
                variant="determinate" 
                value={(risk_analysis.risk_score || 0) * 100}
                color={getRiskColor(risk_analysis.risk_score || 0)}
                sx={{ height: 8, borderRadius: 4 }}
              />
            </Box>
            <Chip 
              label={getRiskLevel(risk_analysis.risk_score || 0)}
              color={getRiskColor(risk_analysis.risk_score || 0)}
              size="small"
            />
            <Typography variant="h6">
              {((risk_analysis.risk_score || 0) * 100).toFixed(1)}%
            </Typography>
          </Box>

          {risk_analysis.risk_score > 0.7 && (
            <Alert severity="error" sx={{ mt: 2 }}>
              <AlertTitle>Высокий уровень риска</AlertTitle>
              Рекомендуется пересмотреть торговую стратегию и размер позиций
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* Key Risk Metrics */}
      <Grid container spacing={2} mb={3}>
        <Grid item xs={6} md={3}>
          <Card variant="outlined">
            <CardContent sx={{ py: 2 }}>
              <Box display="flex" alignItems="center" gap={1} mb={1}>
                <TrendingUp size={20} color="#1976d2" />
                <Typography variant="body2" color="text.secondary">
                  Volatility
                </Typography>
              </Box>
              <Typography variant="h6">
                {((risk_analysis.volatility || 0) * 100).toFixed(2)}%
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={6} md={3}>
          <Card variant="outlined">
            <CardContent sx={{ py: 2 }}>
              <Box display="flex" alignItems="center" gap={1} mb={1}>
                <AlertTriangle size={20} color="#f44336" />
                <Typography variant="body2" color="text.secondary">
                  Max Drawdown
                </Typography>
              </Box>
              <Typography variant="h6" color="error.main">
                {((risk_analysis.max_drawdown || 0) * 100).toFixed(2)}%
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={6} md={3}>
          <Card variant="outlined">
            <CardContent sx={{ py: 2 }}>
              <Box display="flex" alignItems="center" gap={1} mb={1}>
                <Target size={20} color="#4caf50" />
                <Typography variant="body2" color="text.secondary">
                  Sharpe Ratio
                </Typography>
              </Box>
              <Typography 
                variant="h6" 
                color={risk_analysis.sharpe_ratio > 1 ? 'success.main' : 'text.primary'}
              >
                {(risk_analysis.sharpe_ratio || 0).toFixed(3)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={6} md={3}>
          <Card variant="outlined">
            <CardContent sx={{ py: 2 }}>
              <Typography variant="body2" color="text.secondary" mb={1}>
                Beta
              </Typography>
              <Typography variant="h6">
                {(risk_analysis.beta || 0).toFixed(3)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* VaR Chart */}
        <Grid item xs={12} md={6}>
          <Typography variant="h6" gutterBottom>
            Value at Risk (VaR)
          </Typography>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={varData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="period" />
              <YAxis />
              <Tooltip formatter={(value) => [`$${Math.abs(value).toFixed(2)}`, 'VaR']} />
              <Legend />
              <Bar dataKey="var_95" fill="#ff9800" name="VaR 95%" />
              <Bar dataKey="var_99" fill="#f44336" name="VaR 99%" />
            </BarChart>
          </ResponsiveContainer>
        </Grid>

        {/* Risk Radar Chart */}
        <Grid item xs={12} md={6}>
          <Typography variant="h6" gutterBottom>
            Risk Profile
          </Typography>
          <ResponsiveContainer width="100%" height={250}>
            <RadarChart data={radarData}>
              <PolarGrid />
              <PolarAngleAxis dataKey="metric" tick={{ fontSize: 12 }} />
              <PolarRadiusAxis 
                angle={90} 
                domain={[0, 100]} 
                tick={false}
              />
              <Radar
                name="Risk Metrics"
                dataKey="value"
                stroke="#8884d8"
                fill="#8884d8"
                fillOpacity={0.6}
              />
              <Tooltip />
            </RadarChart>
          </ResponsiveContainer>
        </Grid>
      </Grid>

      {/* Risk Recommendations */}
      {risk_analysis.recommendations && risk_analysis.recommendations.length > 0 && (
        <Box mt={3}>
          <Typography variant="h6" gutterBottom>
            Risk Management Recommendations
          </Typography>
          {risk_analysis.recommendations.map((recommendation, index) => (
            <Alert 
              key={index}
              severity="info" 
              sx={{ mb: 1 }}
            >
              {recommendation}
            </Alert>
          ))}
        </Box>
      )}

      {/* Historical VaR Performance */}
      {risk_analysis.var_breaches && (
        <Box mt={3}>
          <Typography variant="h6" gutterBottom>
            VaR Performance
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={6}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="body2" color="text.secondary">
                    VaR Breaches (95%)
                  </Typography>
                  <Typography variant="h5" color="error.main">
                    {risk_analysis.var_breaches.var_95_breaches || 0}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Expected: ≤5%
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={6}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="body2" color="text.secondary">
                    VaR Breaches (99%)
                  </Typography>
                  <Typography variant="h5" color="error.main">
                    {risk_analysis.var_breaches.var_99_breaches || 0}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Expected: ≤1%
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Box>
      )}
    </Paper>
  );
};

export default RiskMetrics;
