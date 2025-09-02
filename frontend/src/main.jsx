import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ThemeProvider, CssBaseline, createTheme } from '@mui/material';

// Импорт страниц и компонентов
import App from './App.jsx';
import Dashboard from './pages/Dashboard.jsx';
import ModernDashboard from './pages/ModernDashboard.jsx';
import TokenAnalytics from './pages/TokenAnalytics.jsx';
import HTXCoinsPage from './pages/HTXCoinsPage.jsx';
import './index.css';

// Создание темы
const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#3f8cff',
    },
    secondary: {
      main: '#19857b',
    },
    background: {
      default: '#121212',
      paper: '#1e1e1e',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 500,
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 500,
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
        },
      },
    },
  },
});

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<App />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/modern" element={<ModernDashboard />} />
          <Route path="/tokens" element={<TokenAnalytics />} />
          <Route path="/coins" element={<HTXCoinsPage />} />
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  </React.StrictMode>,
);