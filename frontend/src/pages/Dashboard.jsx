import React, { useRef } from 'react';
import { Container, Typography, Grid, Paper } from '@mui/material';
import TradingOverview from '../components/TradingOverview';
import AccountSummary from '../components/AccountSummary';
import FileUpload from '../components/FileUpload';

const Dashboard = () => {
  const tradingRef = useRef();
  // Можно добавить другие рефы для других компонентов, если потребуется

  const handleUpload = () => {
    if (tradingRef.current && tradingRef.current.reload) {
      tradingRef.current.reload();
    }
    // Аналогично можно обновлять другие компоненты
  };

  return (
    <Container>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      <FileUpload onUpload={handleUpload} />
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper elevation={3}>
            <TradingOverview ref={tradingRef} />
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper elevation={3}>
            <AccountSummary />
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Dashboard;
