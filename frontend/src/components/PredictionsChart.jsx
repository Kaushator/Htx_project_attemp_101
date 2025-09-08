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
  FormControl,
  Select,
  MenuItem,
  InputLabel,
  Alert,
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
  ComposedChart,
  ReferenceLine
} from 'recharts';
import { 
  TrendingUp, 
  Brain, 
  Target, 
  AlertCircle,
  Calendar,
  Zap
} from 'lucide-react';

const PredictionsChart = ({ data }) => {
  const [activeTab, setActiveTab] = useState(0);
  const [selectedHorizon, setSelectedHorizon] = useState('1d');

  if (!data || !data.predictions) {
    return (
      <Paper sx={{ p: 3 }}>
        <Typography>Нет данных для прогнозирования</Typography>
      </Paper>
    );
  }

  const { predictions } = data;

  // Prepare prediction data
  const predictionData = predictions.price_predictions ? 
    predictions.price_predictions.map((pred, index) => ({
      period: index + 1,
      predicted: pred.predicted_price,
      confidence_lower: pred.confidence_interval?.lower,
      confidence_upper: pred.confidence_interval?.upper,
      actual: pred.actual_price,
      date: pred.date
    })) : [];

  // Risk prediction data
  const riskPredData = predictions.risk_predictions ?
    predictions.risk_predictions.map((risk, index) => ({
      period: index + 1,
      risk_score: risk.risk_score * 100,
      volatility: risk.predicted_volatility * 100,
      var_95: Math.abs(risk.var_95)
    })) : [];

  // Performance metrics
  const modelMetrics = predictions.model_performance || {};

  // Feature importance data
  const featureData = predictions.feature_importance ? 
    Object.entries(predictions.feature_importance)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 8)
      .map(([feature, importance]) => ({
        feature: feature.replace(/_/g, ' ').toUpperCase(),
        importance: importance * 100
      })) : [];

  // Market regime predictions
  const regimeData = predictions.market_regime ? 
    Object.entries(predictions.market_regime).map(([regime, probability]) => ({
      regime: regime.charAt(0).toUpperCase() + regime.slice(1),
      probability: probability * 100
    })) : [];

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return 'success';
    if (confidence >= 0.6) return 'warning';
    return 'error';
  };

  const getAccuracyColor = (accuracy) => {
    if (accuracy >= 0.8) return 'success.main';
    if (accuracy >= 0.6) return 'warning.main';
    return 'error.main';
  };

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  return (
    <Paper sx={{ p: 3, height: 'fit-content' }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5">
          ML Predictions & Forecasting
        </Typography>
        
        <FormControl size="small" sx={{ minWidth: 120 }}>
          <InputLabel>Time Horizon</InputLabel>
          <Select
            value={selectedHorizon}
            label="Time Horizon"
            onChange={(e) => setSelectedHorizon(e.target.value)}
          >
            <MenuItem value="1h">1 Hour</MenuItem>
            <MenuItem value="1d">1 Day</MenuItem>
            <MenuItem value="1w">1 Week</MenuItem>
            <MenuItem value="1m">1 Month</MenuItem>
          </Select>
        </FormControl>
      </Box>

      {/* Model Performance Overview */}
      <Grid container spacing={2} mb={3}>
        <Grid item xs={6} md={3}>
          <Card variant="outlined">
            <CardContent sx={{ py: 2 }}>
              <Box display="flex" alignItems="center" gap={1} mb={1}>
                <Target size={20} color="#1976d2" />
                <Typography variant="body2" color="text.secondary">
                  Accuracy
                </Typography>
              </Box>
              <Typography 
                variant="h6" 
                color={getAccuracyColor(modelMetrics.accuracy || 0)}
              >
                {((modelMetrics.accuracy || 0) * 100).toFixed(1)}%
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={6} md={3}>
          <Card variant="outlined">
            <CardContent sx={{ py: 2 }}>
              <Box display="flex" alignItems="center" gap={1} mb={1}>
                <Brain size={20} color="#9c27b0" />
                <Typography variant="body2" color="text.secondary">
                  Model Score
                </Typography>
              </Box>
              <Typography variant="h6">
                {(modelMetrics.r2_score || 0).toFixed(3)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={6} md={3}>
          <Card variant="outlined">
            <CardContent sx={{ py: 2 }}>
              <Box display="flex" alignItems="center" gap={1} mb={1}>
                <AlertCircle size={20} color="#ff9800" />
                <Typography variant="body2" color="text.secondary">
                  RMSE
                </Typography>
              </Box>
              <Typography variant="h6">
                {(modelMetrics.rmse || 0).toFixed(4)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={6} md={3}>
          <Card variant="outlined">
            <CardContent sx={{ py: 2 }}>
              <Box display="flex" alignItems="center" gap={1} mb={1}>
                <Zap size={20} color="#4caf50" />
                <Typography variant="body2" color="text.secondary">
                  Confidence
                </Typography>
              </Box>
              <Chip
                label={`${((predictions.overall_confidence || 0) * 100).toFixed(1)}%`}
                color={getConfidenceColor(predictions.overall_confidence || 0)}
                size="small"
              />
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Tabs value={activeTab} onChange={handleTabChange} sx={{ mb: 3 }}>
        <Tab label="Price Predictions" />
        <Tab label="Risk Forecasts" />
        <Tab label="Feature Importance" />
        <Tab label="Market Regime" />
      </Tabs>

      {/* Price Predictions Tab */}
      {activeTab === 0 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Box mb={2}>
              <Typography variant="h6" gutterBottom>
                Price Prediction with Confidence Intervals
              </Typography>
              <ResponsiveContainer width="100%" height={350}>
                <ComposedChart data={predictionData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="period" 
                    label={{ value: 'Time Periods', position: 'insideBottom', offset: -5 }}
                  />
                  <YAxis label={{ value: 'Price', angle: -90, position: 'insideLeft' }} />
                  <Tooltip 
                    formatter={(value, name) => [
                      `$${value?.toFixed(2) || 'N/A'}`, 
                      name === 'predicted' ? 'Predicted' : 
                      name === 'actual' ? 'Actual' :
                      name === 'confidence_lower' ? 'Lower CI' : 'Upper CI'
                    ]}
                  />
                  <Legend />
                  
                  {/* Confidence interval area */}
                  <Area
                    dataKey="confidence_upper"
                    stackId="confidence"
                    stroke="none"
                    fill="#e3f2fd"
                    fillOpacity={0.3}
                  />
                  <Area
                    dataKey="confidence_lower"
                    stackId="confidence"
                    stroke="none"
                    fill="#ffffff"
                    fillOpacity={1}
                  />
                  
                  {/* Actual and predicted lines */}
                  <Line 
                    type="monotone" 
                    dataKey="actual" 
                    stroke="#4caf50" 
                    strokeWidth={2}
                    dot={{ r: 4 }}
                    name="Actual Price"
                  />
                  <Line 
                    type="monotone" 
                    dataKey="predicted" 
                    stroke="#2196f3" 
                    strokeWidth={2}
                    strokeDasharray="5 5"
                    dot={{ r: 4 }}
                    name="Predicted Price"
                  />
                </ComposedChart>
              </ResponsiveContainer>
            </Box>

            {/* Prediction Summary */}
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="subtitle2" gutterBottom>
                      Next Period Prediction
                    </Typography>
                    <Typography variant="h5" color="primary">
                      ${(predictionData[predictionData.length - 1]?.predicted || 0).toFixed(2)}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Confidence: {((predictions.overall_confidence || 0) * 100).toFixed(1)}%
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="subtitle2" gutterBottom>
                      Prediction Trend
                    </Typography>
                    <Box display="flex" alignItems="center" gap={1}>
                      <TrendingUp 
                        size={24} 
                        color={predictionData.length > 1 && 
                          predictionData[predictionData.length - 1]?.predicted > 
                          predictionData[predictionData.length - 2]?.predicted ? 
                          '#4caf50' : '#f44336'
                        } 
                      />
                      <Typography variant="h6">
                        {predictionData.length > 1 && 
                          predictionData[predictionData.length - 1]?.predicted > 
                          predictionData[predictionData.length - 2]?.predicted ? 
                          'Bullish' : 'Bearish'
                        }
                      </Typography>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </Grid>
        </Grid>
      )}

      {/* Risk Forecasts Tab */}
      {activeTab === 1 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom>
              Risk Metrics Forecast
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <ComposedChart data={riskPredData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="period" />
                <YAxis yAxisId="left" orientation="left" />
                <YAxis yAxisId="right" orientation="right" />
                <Tooltip />
                <Legend />
                
                <Bar yAxisId="left" dataKey="risk_score" fill="#ff9800" name="Risk Score %" />
                <Line 
                  yAxisId="right" 
                  type="monotone" 
                  dataKey="volatility" 
                  stroke="#f44336" 
                  strokeWidth={2}
                  name="Volatility %"
                />
                <Line 
                  yAxisId="right" 
                  type="monotone" 
                  dataKey="var_95" 
                  stroke="#9c27b0" 
                  strokeWidth={2}
                  name="VaR 95%"
                />
              </ComposedChart>
            </ResponsiveContainer>
          </Grid>

          {/* Risk Alerts */}
          {riskPredData.some(d => d.risk_score > 70) && (
            <Grid item xs={12}>
              <Alert severity="warning">
                <Typography variant="subtitle2">Risk Alert</Typography>
                High risk periods detected in forecast. Consider reducing position sizes.
              </Alert>
            </Grid>
          )}
        </Grid>
      )}

      {/* Feature Importance Tab */}
      {activeTab === 2 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Typography variant="h6" gutterBottom>
              Model Feature Importance
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={featureData} layout="horizontal">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" domain={[0, 100]} />
                <YAxis dataKey="feature" type="category" width={100} />
                <Tooltip formatter={(value) => [`${value.toFixed(1)}%`, 'Importance']} />
                <Bar dataKey="importance" fill="#8884d8" />
              </BarChart>
            </ResponsiveContainer>
          </Grid>

          <Grid item xs={12} md={4}>
            <Typography variant="h6" gutterBottom>
              Top Predictors
            </Typography>
            {featureData.slice(0, 5).map((feature, index) => (
              <Card key={feature.feature} variant="outlined" sx={{ mb: 1 }}>
                <CardContent sx={{ py: 1 }}>
                  <Box display="flex" justifyContent="space-between" alignItems="center">
                    <Typography variant="body2">
                      {feature.feature}
                    </Typography>
                    <Box display="flex" alignItems="center" gap={1}>
                      <LinearProgress
                        variant="determinate"
                        value={feature.importance}
                        sx={{ width: 60, height: 6 }}
                      />
                      <Typography variant="caption">
                        {feature.importance.toFixed(1)}%
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            ))}
          </Grid>
        </Grid>
      )}

      {/* Market Regime Tab */}
      {activeTab === 3 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Typography variant="h6" gutterBottom>
              Market Regime Probabilities
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={regimeData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="regime" />
                <YAxis domain={[0, 100]} />
                <Tooltip formatter={(value) => [`${value.toFixed(1)}%`, 'Probability']} />
                <Bar dataKey="probability" fill="#00C49F" />
              </BarChart>
            </ResponsiveContainer>
          </Grid>

          <Grid item xs={12} md={6}>
            <Typography variant="h6" gutterBottom>
              Current Market State
            </Typography>
            <Grid container spacing={2}>
              {regimeData.map((regime) => (
                <Grid item xs={6} key={regime.regime}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="body2" color="text.secondary">
                        {regime.regime}
                      </Typography>
                      <Typography variant="h5">
                        {regime.probability.toFixed(1)}%
                      </Typography>
                      <LinearProgress
                        variant="determinate"
                        value={regime.probability}
                        color={regime.probability > 50 ? 'primary' : 'default'}
                        sx={{ mt: 1 }}
                      />
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>

            {/* Regime Interpretation */}
            <Box mt={2}>
              <Typography variant="subtitle2" gutterBottom>
                Regime Interpretation
              </Typography>
              {regimeData.map((regime) => (
                <Box key={regime.regime} mb={1}>
                  <Typography variant="body2" color="text.secondary">
                    <strong>{regime.regime}:</strong> {
                      regime.regime.toLowerCase() === 'trending' ? 
                        'Strong directional movement expected' :
                      regime.regime.toLowerCase() === 'ranging' ?
                        'Sideways movement, mean reversion likely' :
                      regime.regime.toLowerCase() === 'volatile' ?
                        'High volatility, increased risk' :
                        'Stable market conditions'
                    }
                  </Typography>
                </Box>
              ))}
            </Box>
          </Grid>
        </Grid>
      )}

      {/* Model Information */}
      <Box mt={3}>
        <Typography variant="h6" gutterBottom>
          Model Information
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="subtitle2" gutterBottom>
                  Algorithm
                </Typography>
                <Chip 
                  label={predictions.model_type || 'Random Forest'} 
                  color="primary" 
                  size="small"
                />
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  Last trained: {predictions.last_trained || 'Recently'}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="subtitle2" gutterBottom>
                  Data Quality
                </Typography>
                <LinearProgress
                  variant="determinate"
                  value={(predictions.data_quality || 0.85) * 100}
                  color="success"
                  sx={{ mb: 1 }}
                />
                <Typography variant="body2" color="text.secondary">
                  {((predictions.data_quality || 0.85) * 100).toFixed(1)}% data completeness
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
    </Paper>
  );
};

export default PredictionsChart;
