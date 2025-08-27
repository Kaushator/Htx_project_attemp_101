import React, { useRef } from 'react';
import { Container, Typography, Grid, Paper, Tabs, Tab, Box } from '@mui/material';
import TransactionList from '../components/TransactionList';

const TransactionHistory = () => {
  const [tab, setTab] = React.useState(0);
  const depositRef = useRef();
  const withdrawalRef = useRef();
  const transferRef = useRef();

  const handleTabChange = (event, newValue) => {
    setTab(newValue);
  };

  // Функция для обновления всех списков
  const reloadAll = () => {
    if (depositRef.current && depositRef.current.reload) depositRef.current.reload();
    if (withdrawalRef.current && withdrawalRef.current.reload) withdrawalRef.current.reload();
    if (transferRef.current && transferRef.current.reload) transferRef.current.reload();
  };

  return (
    <Container>
      <Typography variant="h4" gutterBottom>
        Transaction History
      </Typography>
      <Paper elevation={3}>
        <Tabs value={tab} onChange={handleTabChange} indicatorColor="primary" textColor="primary" centered>
          <Tab label="Deposits" />
          <Tab label="Withdrawals" />
          <Tab label="Transfers" />
        </Tabs>
        <Box p={2}>
          {tab === 0 && <TransactionList type="deposit" ref={depositRef} />}
          {tab === 1 && <TransactionList type="withdrawal" ref={withdrawalRef} />}
          {tab === 2 && <TransactionList type="transfer" ref={transferRef} />}
        </Box>
      </Paper>
    </Container>
  );
};

export default TransactionHistory;
