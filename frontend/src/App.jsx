import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { AppBar, Toolbar, Typography, Button, Container } from '@mui/material';
import Dashboard from './pages/Dashboard';
import OrderManagement from './pages/OrderManagement';
import TransactionHistory from './pages/TransactionHistory';
import PnlAnalytics from './pages/PnlAnalytics';

const App = () => {
  return (
    <Router>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            HTX Trading Platform
          </Typography>
          <Button color="inherit" component={Link} to="/">Главная</Button>
          <Button color="inherit" component={Link} to="/orders">Ордеры</Button>
          <Button color="inherit" component={Link} to="/transactions">Транзакции</Button>
          <Button color="inherit" component={Link} to="/pnl">PnL</Button>
        </Toolbar>
      </AppBar>
      <Container sx={{ mt: 4 }}>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/orders" element={<OrderManagement />} />
          <Route path="/transactions" element={<TransactionHistory />} />
          <Route path="/pnl" element={<PnlAnalytics />} />
        </Routes>
      </Container>
    </Router>
  );
};

export default App;
