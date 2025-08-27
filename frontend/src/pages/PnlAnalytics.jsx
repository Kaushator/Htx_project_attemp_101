import React from 'react';
import { Container, Typography, Paper } from '@mui/material';
import PnlChart from '../components/PnlChart';

const PnlAnalytics = () => {
  return (
    <Container>
      <Typography variant="h4" gutterBottom>
        PnL Аналитика
      </Typography>
      <Paper elevation={3} style={{ padding: '16px' }}>
        <PnlChart />
      </Paper>
    </Container>
  );
};

export default PnlAnalytics;
