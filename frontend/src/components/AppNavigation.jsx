import React from 'react';
import { Box, Container, Typography, Paper, Tab, Tabs, Button, AppBar, Toolbar, IconButton, Drawer, List, ListItem, ListItemIcon, ListItemText, Divider } from '@mui/material';
import { Link, useLocation } from 'react-router-dom';
import { Menu as MenuIcon, Dashboard as DashboardIcon, TrendingUp as TrendingUpIcon, Analytics as AnalyticsIcon, Settings as SettingsIcon, Logout as LogoutIcon, CurrencyBitcoin as CoinIcon, BarChart as ChartIcon } from '@mui/icons-material';

const AppNavigation = ({ children }) => {
  const [mobileOpen, setMobileOpen] = React.useState(false);
  const location = useLocation();
  const drawerWidth = 240;

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const menuItems = [
    { text: 'Главная', path: '/', icon: <DashboardIcon /> },
    { text: 'Современная панель', path: '/modern', icon: <AnalyticsIcon /> },
    { text: 'Анализ токенов', path: '/tokens', icon: <ChartIcon /> },
    { text: 'Монеты HTX', path: '/coins', icon: <CoinIcon /> },
  ];

  const drawer = (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ p: 2, display: 'flex', alignItems: 'center' }}>
        <TrendingUpIcon sx={{ fontSize: 30, mr: 1, color: 'primary.main' }} />
        <Typography variant="h5" component="h1" fontWeight="bold">HTX Project</Typography>
      </Box>
      <Divider />
      <List sx={{ flexGrow: 1 }}>
        {menuItems.map((item) => (
          <ListItem 
            button 
            key={item.text} 
            component={Link} 
            to={item.path}
            selected={location.pathname === item.path}
            sx={{
              '&.Mui-selected': {
                backgroundColor: 'rgba(63, 140, 255, 0.1)',
                borderRight: '3px solid',
                borderColor: 'primary.main'
              }
            }}
          >
            <ListItemIcon sx={{ 
              color: location.pathname === item.path ? 'primary.main' : 'text.secondary' 
            }}>
              {item.icon}
            </ListItemIcon>
            <ListItemText 
              primary={item.text} 
              sx={{ 
                color: location.pathname === item.path ? 'primary.main' : 'text.primary' 
              }}
            />
          </ListItem>
        ))}
      </List>
      <Divider />
      <List>
        <ListItem button>
          <ListItemIcon>
            <SettingsIcon />
          </ListItemIcon>
          <ListItemText primary="Настройки" />
        </ListItem>
        <ListItem button>
          <ListItemIcon>
            <LogoutIcon />
          </ListItemIcon>
          <ListItemText primary="Выйти" />
        </ListItem>
      </List>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', backgroundColor: 'background.default' }}>
      <AppBar 
        position="fixed" 
        sx={{ 
          zIndex: (theme) => theme.zIndex.drawer + 1,
          boxShadow: 2,
          backgroundColor: 'background.paper',
          color: 'text.primary'
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { sm: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" component="div" sx={{ display: { xs: 'none', sm: 'block' } }}>
            HTX Trading Analytics
          </Typography>
          <Box sx={{ flexGrow: 1 }} />
          <Button 
            variant="contained" 
            color="primary" 
            component={Link} 
            to="/tokens"
          >
            Новый анализ
          </Button>
        </Toolbar>
      </AppBar>
      
      <Box
        component="nav"
        sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
      >
        {/* Мобильная версия */}
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{ keepMounted: true }}
          sx={{
            display: { xs: 'block', sm: 'none' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
        >
          {drawer}
        </Drawer>
        
        {/* Десктопная версия */}
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>
      
      <Box
        component="main"
        sx={{ 
          flexGrow: 1, 
          p: 3, 
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          ml: { sm: `${drawerWidth}px` },
          mt: '64px'  // Высота AppBar
        }}
      >
        {children}
      </Box>
    </Box>
  );
};

export default AppNavigation;
