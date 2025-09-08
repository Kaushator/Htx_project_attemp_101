import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { AppBar, Toolbar, Typography, Button, Container } from '@mui/material';
import UltraSimpleDashboard from './pages/UltraSimpleDashboard';
import SimpleOrderManagement from './pages/SimpleOrderManagement';
import TransactionHistory from './pages/TransactionHistory';
import PnlAnalytics from './pages/PnlAnalytics';
import EnhancedTokenAnalytics from './pages/EnhancedTokenAnalytics';
import ChartsShowcase from './pages/ChartsShowcase';
import ExportDemo from './pages/ExportDemo';
import SecretManagerDashboard from './pages/SecretManagerDashboard';
import PersonalizedDashboard from './pages/PersonalizedDashboard';
import RealTimeDashboard from './components/RealTimeDashboard';
import ErrorBoundary from './components/ErrorBoundary';
import { NotificationProvider } from './components/NotificationSystem';
import { SettingsProvider } from './contexts/SettingsContext';
import GlobalLoading from './components/GlobalLoading';

const App = () => {
  return (
    <ErrorBoundary>
      <SettingsProvider>
        <NotificationProvider>
          <Router>
            <GlobalLoading variant="bar" />
          <AppBar position="static">
            <Toolbar>
              <Typography variant="h6" sx={{ flexGrow: 1 }}>
                HTX Trading Platform
              </Typography>
              <Button color="inherit" component={Link} to="/">Главная</Button>
              <Button color="inherit" component={Link} to="/realtime">Real-Time</Button>
              <Button color="inherit" component={Link} to="/personalized">Personal</Button>
              <Button color="inherit" component={Link} to="/analytics">Analytics</Button>
              <Button color="inherit" component={Link} to="/charts">Charts</Button>
              <Button color="inherit" component={Link} to="/export">Export Demo</Button>
              <Button color="inherit" component={Link} to="/secrets">Secrets</Button>
              <Button color="inherit" component={Link} to="/orders">Ордеры</Button>
              <Button color="inherit" component={Link} to="/transactions">Транзакции</Button>
              <Button color="inherit" component={Link} to="/pnl">PnL</Button>
            </Toolbar>
          </AppBar>
          <Container sx={{ mt: 4 }}>
            <ErrorBoundary>
              <Routes>
                <Route path="/" element={<UltraSimpleDashboard />} />
                <Route path="/realtime" element={<RealTimeDashboard />} />
                <Route path="/personalized" element={<PersonalizedDashboard />} />
                <Route path="/analytics" element={<EnhancedTokenAnalytics />} />
                <Route path="/charts" element={<ChartsShowcase />} />
                <Route path="/export" element={<ExportDemo />} />
                <Route path="/secrets" element={<SecretManagerDashboard />} />
                <Route path="/orders" element={<SimpleOrderManagement />} />
                <Route path="/transactions" element={<TransactionHistory />} />
                <Route path="/pnl" element={<PnlAnalytics />} />
              </Routes>
            </ErrorBoundary>
          </Container>
        </Router>
      </NotificationProvider>
    </SettingsProvider>
  </ErrorBoundary>
  );
};

export default App;
