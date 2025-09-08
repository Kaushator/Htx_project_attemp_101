/**
 * Personalized Dashboard Component
 * Adapts layout and content based on user settings and preferences
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  CardHeader,
  Typography,
  IconButton,
  Chip,
  Button,
  Alert,
  Fab,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText
} from '@mui/material';
import {
  AccountBalance,
  TrendingUp,
  ShowChart,
  Newspaper,
  Settings,
  Visibility,
  VisibilityOff,
  DragIndicator,
  MoreVert
} from '@mui/icons-material';
import { useSettings, useDashboardLayout, useFavorites } from '../../contexts/SettingsContext';
import { SettingsButton, ThemeToggle } from '../settings/SettingsButton';
import { htxService } from '../../services/htxService';
import { useNotifications } from '../NotificationSystem';

// Widget Components
const BalanceWidget = ({ enabled, compact }) => {
  const [balance, setBalance] = useState(null);
  const [loading, setLoading] = useState(true);
  const { showError } = useNotifications();
  
  useEffect(() => {
    if (enabled) {
      htxService.getBalance()
        .then(setBalance)
        .catch(error => {
          showError('Failed to load balance');
          console.error('Balance error:', error);
        })
        .finally(() => setLoading(false));
    }
  }, [enabled, showError]);
  
  if (!enabled) return null;
  
  return (
    <Card sx={{ height: '100%' }}>
      <CardHeader 
        title=\"Account Balance\" 
        avatar={<AccountBalance />}
        titleTypographyProps={{ variant: compact ? 'subtitle1' : 'h6' }}
      />
      <CardContent>
        {loading ? (
          <Typography>Loading...</Typography>
        ) : balance ? (
          <Box>
            <Typography variant={compact ? 'h6' : 'h4'} color=\"primary\">
              ${balance.total_balance?.toFixed(2) || '0.00'}
            </Typography>
            <Typography variant=\"body2\" color=\"text.secondary\">
              Available: ${balance.available_balance?.toFixed(2) || '0.00'}
            </Typography>
            {!compact && (
              <Box sx={{ mt: 1 }}>
                {balance.currencies?.slice(0, 3).map((curr) => (
                  <Chip 
                    key={curr.currency}
                    label={`${curr.currency.toUpperCase()}: ${curr.balance}`}
                    size=\"small\"
                    sx={{ mr: 0.5, mb: 0.5 }}
                  />
                ))}
              </Box>
            )}
          </Box>
        ) : (
          <Typography color=\"error\">Failed to load balance</Typography>
        )}
      </CardContent>
    </Card>
  );
};

const PortfolioWidget = ({ enabled, compact }) => {
  const { favorites } = useFavorites();
  
  if (!enabled) return null;
  
  return (
    <Card sx={{ height: '100%' }}>
      <CardHeader 
        title=\"Portfolio\" 
        avatar={<ShowChart />}
        titleTypographyProps={{ variant: compact ? 'subtitle1' : 'h6' }}
      />
      <CardContent>
        <Typography variant={compact ? 'h6' : 'h4'} color=\"primary\">
          {favorites.tokens?.length || 0}
        </Typography>
        <Typography variant=\"body2\" color=\"text.secondary\">
          Favorite tokens
        </Typography>
        {!compact && (
          <Box sx={{ mt: 1 }}>
            {favorites.tokens?.slice(0, 5).map((token) => (
              <Chip 
                key={token}
                label={token}
                size=\"small\"
                sx={{ mr: 0.5, mb: 0.5 }}
              />
            ))}
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

const TradesWidget = ({ enabled, compact }) => {
  if (!enabled) return null;
  
  return (
    <Card sx={{ height: '100%' }}>
      <CardHeader 
        title=\"Recent Trades\" 
        avatar={<TrendingUp />}
        titleTypographyProps={{ variant: compact ? 'subtitle1' : 'h6' }}
      />
      <CardContent>
        <Typography variant=\"body2\" color=\"text.secondary\">
          No recent trades
        </Typography>
        <Button size=\"small\" sx={{ mt: 1 }}>
          View All Trades
        </Button>
      </CardContent>
    </Card>
  );
};

const ChartsWidget = ({ enabled, compact }) => {
  if (!enabled) return null;
  
  return (
    <Card sx={{ height: '100%' }}>
      <CardHeader 
        title=\"Charts\" 
        avatar={<ShowChart />}
        titleTypographyProps={{ variant: compact ? 'subtitle1' : 'h6' }}
      />
      <CardContent>
        <Box sx={{ 
          height: compact ? 200 : 300, 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          bgcolor: 'action.hover',
          borderRadius: 1
        }}>
          <Typography variant=\"body2\" color=\"text.secondary\">
            Chart placeholder
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
};

const NewsWidget = ({ enabled, compact }) => {
  if (!enabled) return null;
  
  return (
    <Card sx={{ height: '100%' }}>
      <CardHeader 
        title=\"Latest News\" 
        avatar={<Newspaper />}
        titleTypographyProps={{ variant: compact ? 'subtitle1' : 'h6' }}
      />
      <CardContent>
        <Typography variant=\"body2\" color=\"text.secondary\">
          No news available
        </Typography>
      </CardContent>
    </Card>
  );
};

// Widget factory
const createWidget = (widgetConfig, settings) => {
  const { id, enabled } = widgetConfig;
  const compact = settings.display?.compactMode || false;
  
  switch (id) {
    case 'balance':
      return <BalanceWidget enabled={enabled} compact={compact} />;
    case 'portfolio':
      return <PortfolioWidget enabled={enabled} compact={compact} />;
    case 'trades':
      return <TradesWidget enabled={enabled} compact={compact} />;
    case 'charts':
      return <ChartsWidget enabled={enabled} compact={compact} />;
    case 'news':
      return <NewsWidget enabled={enabled} compact={compact} />;
    default:
      return null;
  }
};

// Widget Configuration Menu
const WidgetMenu = ({ widgetId, enabled, onToggle, anchorEl, open, onClose }) => {
  return (
    <Menu
      anchorEl={anchorEl}
      open={open}
      onClose={onClose}
    >
      <MenuItem onClick={() => {
        onToggle(widgetId, !enabled);
        onClose();
      }}>
        <ListItemIcon>
          {enabled ? <VisibilityOff /> : <Visibility />}
        </ListItemIcon>
        <ListItemText primary={enabled ? 'Hide Widget' : 'Show Widget'} />
      </MenuItem>
    </Menu>
  );
};

const PersonalizedDashboard = () => {
  const { settings, getSettingValue } = useSettings();
  const { layout, updateWidget, enableWidget, disableWidget } = useDashboardLayout();
  const [widgetMenus, setWidgetMenus] = useState({});
  
  // Get user preferences
  const compactMode = getSettingValue('display.compactMode', false);
  const animationsEnabled = getSettingValue('display.animationsEnabled', true);
  const language = getSettingValue('language', 'en');
  
  const handleWidgetMenuOpen = (widgetId, event) => {
    setWidgetMenus(prev => ({
      ...prev,
      [widgetId]: { anchorEl: event.currentTarget, open: true }
    }));
  };
  
  const handleWidgetMenuClose = (widgetId) => {
    setWidgetMenus(prev => ({
      ...prev,
      [widgetId]: { anchorEl: null, open: false }
    }));
  };
  
  const handleWidgetToggle = (widgetId, enabled) => {
    if (enabled) {
      enableWidget(widgetId);
    } else {
      disableWidget(widgetId);
    }
  };
  
  const enabledWidgets = layout.widgets?.filter(w => w.enabled) || [];
  const disabledWidgets = layout.widgets?.filter(w => !w.enabled) || [];
  
  return (
    <Box sx={{ padding: 3 }}>
      {/* Header with personalized greeting */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant=\"h4\" component=\"h1\">
            {language === 'ru' ? 'Личный кабинет' : 
             language === 'zh' ? '个人仪表板' : 
             'Personal Dashboard'}
          </Typography>
          <Typography variant=\"body2\" color=\"text.secondary\">
            {language === 'ru' ? 'Персонализированный торговый интерфейс' :
             language === 'zh' ? '个性化交易界面' :
             'Customized for your trading preferences'}
          </Typography>
        </Box>
        
        <Box sx={{ display: 'flex', gap: 1 }}>
          <ThemeToggle />
          <SettingsButton variant=\"icon\" />
        </Box>
      </Box>
      
      {/* Settings Summary */}
      {(compactMode || disabledWidgets.length > 0) && (
        <Alert severity=\"info\" sx={{ mb: 3 }}>
          Dashboard customized: 
          {compactMode && ' Compact mode enabled.'}
          {disabledWidgets.length > 0 && ` ${disabledWidgets.length} widgets hidden.`}
          {' '}
          <Button size=\"small\" sx={{ ml: 1 }}>
            Customize Layout
          </Button>
        </Alert>
      )}
      
      {/* Enabled Widgets Grid */}
      <Grid container spacing={compactMode ? 2 : 3}>
        {enabledWidgets.map((widget) => {
          const { id, position } = widget;
          const menuState = widgetMenus[id] || { anchorEl: null, open: false };
          
          return (
            <Grid 
              key={id} 
              item 
              xs={12} 
              md={position.w === 12 ? 12 : position.w === 8 ? 8 : position.w === 6 ? 6 : 4}
            >
              <Box sx={{ position: 'relative' }}>
                {/* Widget Menu Button */}
                <IconButton
                  size=\"small\"
                  sx={{ 
                    position: 'absolute', 
                    top: 8, 
                    right: 8, 
                    zIndex: 1,
                    bgcolor: 'background.paper',
                    '&:hover': { bgcolor: 'action.hover' }
                  }}
                  onClick={(e) => handleWidgetMenuOpen(id, e)}
                >
                  <MoreVert fontSize=\"small\" />
                </IconButton>
                
                {/* Widget Content */}
                <Box sx={{ 
                  transition: animationsEnabled ? 'transform 0.2s ease-in-out' : 'none',
                  '&:hover': {
                    transform: animationsEnabled ? 'translateY(-2px)' : 'none'
                  }
                }}>
                  {createWidget(widget, settings)}
                </Box>
                
                {/* Widget Menu */}
                <WidgetMenu
                  widgetId={id}
                  enabled={widget.enabled}
                  onToggle={handleWidgetToggle}
                  anchorEl={menuState.anchorEl}
                  open={menuState.open}
                  onClose={() => handleWidgetMenuClose(id)}
                />
              </Box>
            </Grid>
          );
        })}
      </Grid>
      
      {/* Show hidden widgets section if any */}
      {disabledWidgets.length > 0 && (
        <Box sx={{ mt: 4 }}>
          <Typography variant=\"h6\" gutterBottom>
            Hidden Widgets
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            {disabledWidgets.map((widget) => (
              <Chip
                key={widget.id}
                label={widget.id.charAt(0).toUpperCase() + widget.id.slice(1)}
                onClick={() => enableWidget(widget.id)}
                icon={<Visibility />}
                variant=\"outlined\"
              />
            ))}
          </Box>
        </Box>
      )}
      
      {/* Floating Settings Button */}
      <SettingsButton 
        variant=\"fab\" 
        sx={{ 
          position: 'fixed', 
          bottom: 16, 
          right: 16 
        }} 
      />
    </Box>
  );
};

export default PersonalizedDashboard;"