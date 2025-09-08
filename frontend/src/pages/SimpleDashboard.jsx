import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Grid,
  Paper,
  Box,
  Card,
  CardContent,
  CircularProgress,
  Alert,
  Button
} from '@mui/material';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

const SimpleDashboard = () => {
  const [healthStatus, setHealthStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const checkHealth = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.get(`${API_BASE_URL}/health`);
      setHealthStatus(response.data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    checkHealth();
  }, []);

  if (loading) {
    return (
      <Container>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="50vh">
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  return (
    <Container>
      <Typography variant="h4" gutterBottom>
        HTX Trading Dashboard
      </Typography>
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          Backend Error: {error}
          <Button onClick={checkHealth} sx={{ ml: 2 }}>
            Retry
          </Button>
        </Alert>
      )}

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                System Status
              </Typography>
              {healthStatus ? (
                <Box>
                  <Typography color="success.main">
                    ✅ Status: {healthStatus.status}
                  </Typography>
                  <Typography variant="body2">
                    Timestamp: {healthStatus.timestamp}
                  </Typography>
                  <Typography variant="body2">
                    Version: {healthStatus.version}
                  </Typography>
                </Box>
              ) : (
                <Typography color="error">
                  ❌ Backend not responding
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Quick Actions
              </Typography>
              <Box>
                <Button 
                  variant="outlined" 
                  onClick={checkHealth}
                  sx={{ mr: 1, mb: 1 }}
                >
                  Check Health
                </Button>
                <Button 
                  variant="outlined"
                  href="/orders"
                  sx={{ mr: 1, mb: 1 }}
                >
                  View Orders
                </Button>
                <Button 
                  variant="outlined"
                  href="/pnl"
                  sx={{ mr: 1, mb: 1 }}
                >
                  PnL Analytics
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Welcome to HTX Trading Platform
            </Typography>
            <Typography variant="body1">
              This is a simplified dashboard for testing. The system provides:
            </Typography>
            <ul>
              <li>Trading data analysis</li>
              <li>P&L calculations</li>
              <li>HTX API integration</li>
              <li>File upload and processing</li>
            </ul>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default SimpleDashboard;
