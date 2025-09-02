/**
 * Settings Dialog Component
 * Comprehensive user settings management interface
 */

import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Tabs,
  Tab,
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  FormControl,
  FormControlLabel,
  FormLabel,
  RadioGroup,
  Radio,
  Switch,
  Select,
  MenuItem,
  TextField,
  InputLabel,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction
} from '@mui/material';
import {
  Settings,
  Palette,
  TrendingUp,
  Notifications,
  Close,
  GetApp,
  CloudUpload,
  RestoreFromTrash
} from '@mui/icons-material';
import { useSettings, useTheme, useDisplaySettings, useTradingSettings } from '../../contexts/SettingsContext';

// Tab Panel Component
const TabPanel = ({ children, value, index, ...other }) => {
  return (
    <div
      role=\"tabpanel\"
      hidden={value !== index}
      id={`settings-tabpanel-${index}`}
      aria-labelledby={`settings-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
};

const SettingsDialog = ({ open, onClose }) => {
  const [tabValue, setTabValue] = useState(0);
  
  const {
    settings,
    resetSettings,
    exportSettings,
    importSettings,
    getSettingValue,
    setSettingValue
  } = useSettings();
  
  const { theme, setTheme } = useTheme();
  const { display, updateDisplay } = useDisplaySettings();
  const { trading, updateTrading } = useTradingSettings();
  
  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };
  
  const handleImportFile = async (event) => {
    const file = event.target.files[0];
    if (file) {
      try {
        await importSettings(file);
        event.target.value = ''; // Reset file input
      } catch (error) {
        console.error('Import failed:', error);
      }
    }
  };
  
  const handleReset = () => {
    if (window.confirm('Are you sure you want to reset all settings to defaults?')) {
      resetSettings();
    }
  };
  
  const tabs = [
    { label: 'General', icon: <Settings /> },
    { label: 'Appearance', icon: <Palette /> },
    { label: 'Trading', icon: <TrendingUp /> },
    { label: 'Notifications', icon: <Notifications /> }
  ];
  
  return (
    <Dialog 
      open={open} 
      onClose={onClose} 
      maxWidth=\"md\" 
      fullWidth
      PaperProps={{ sx: { height: '80vh' } }}
    >
      <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Settings />
        User Settings
        <Box sx={{ flexGrow: 1 }} />
        <IconButton onClick={onClose} size=\"small\">
          <Close />
        </IconButton>
      </DialogTitle>
      
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={tabValue} onChange={handleTabChange} variant=\"fullWidth\">
          {tabs.map((tab, index) => (
            <Tab 
              key={index}
              label={tab.label} 
              icon={tab.icon} 
              iconPosition=\"start\"
            />
          ))}
        </Tabs>
      </Box>
      
      <DialogContent sx={{ p: 0, overflow: 'auto' }}>
        {/* General Settings */}
        <TabPanel value={tabValue} index={0}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant=\"h6\" gutterBottom>Language & Region</Typography>
                  
                  <FormControl fullWidth margin=\"normal\">
                    <InputLabel>Language</InputLabel>
                    <Select
                      value={getSettingValue('language', 'en')}
                      onChange={(e) => setSettingValue('language', e.target.value)}
                      label=\"Language\"
                    >
                      <MenuItem value=\"en\">English</MenuItem>
                      <MenuItem value=\"ru\">Русский</MenuItem>
                      <MenuItem value=\"zh\">中文</MenuItem>
                    </Select>
                  </FormControl>
                  
                  <FormControl fullWidth margin=\"normal\">
                    <InputLabel>Currency</InputLabel>
                    <Select
                      value={getSettingValue('currency', 'USD')}
                      onChange={(e) => setSettingValue('currency', e.target.value)}
                      label=\"Currency\"
                    >
                      <MenuItem value=\"USD\">USD - US Dollar</MenuItem>
                      <MenuItem value=\"EUR\">EUR - Euro</MenuItem>
                      <MenuItem value=\"BTC\">BTC - Bitcoin</MenuItem>
                      <MenuItem value=\"USDT\">USDT - Tether</MenuItem>
                    </Select>
                  </FormControl>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant=\"h6\" gutterBottom>Data Management</Typography>
                  
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
                    <Button
                      variant=\"outlined\"
                      startIcon={<GetApp />}
                      onClick={exportSettings}
                      fullWidth
                    >
                      Export Settings
                    </Button>
                    
                    <Button
                      variant=\"outlined\"
                      component=\"label\"
                      startIcon={<CloudUpload />}
                      fullWidth
                    >
                      Import Settings
                      <input
                        type=\"file\"
                        accept=\".json\"
                        hidden
                        onChange={handleImportFile}
                      />
                    </Button>
                    
                    <Button
                      variant=\"outlined\"
                      color=\"warning\"
                      startIcon={<RestoreFromTrash />}
                      onClick={handleReset}
                      fullWidth
                    >
                      Reset to Defaults
                    </Button>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>
        
        {/* Appearance Settings */}
        <TabPanel value={tabValue} index={1}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant=\"h6\" gutterBottom>Theme</Typography>
                  
                  <FormControl component=\"fieldset\" margin=\"normal\">
                    <FormLabel component=\"legend\">Color Theme</FormLabel>
                    <RadioGroup
                      value={theme}
                      onChange={(e) => setTheme(e.target.value)}
                    >
                      <FormControlLabel value=\"light\" control={<Radio />} label=\"Light\" />
                      <FormControlLabel value=\"dark\" control={<Radio />} label=\"Dark\" />
                      <FormControlLabel value=\"auto\" control={<Radio />} label=\"Auto (System)\" />
                    </RadioGroup>
                  </FormControl>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant=\"h6\" gutterBottom>Display Options</Typography>
                  
                  <FormControlLabel
                    control={
                      <Switch
                        checked={display.compactMode}
                        onChange={(e) => updateDisplay({ compactMode: e.target.checked })}
                      />
                    }
                    label=\"Compact Mode\"
                  />
                  
                  <FormControlLabel
                    control={
                      <Switch
                        checked={display.animationsEnabled}
                        onChange={(e) => updateDisplay({ animationsEnabled: e.target.checked })}
                      />
                    }
                    label=\"Enable Animations\"
                  />
                  
                  <FormControlLabel
                    control={
                      <Switch
                        checked={display.showTooltips}
                        onChange={(e) => updateDisplay({ showTooltips: e.target.checked })}
                      />
                    }
                    label=\"Show Tooltips\"
                  />
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>
        
        {/* Trading Settings */}
        <TabPanel value={tabValue} index={2}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant=\"h6\" gutterBottom>Default Settings</Typography>
                  
                  <FormControl fullWidth margin=\"normal\">
                    <InputLabel>Default Exchange</InputLabel>
                    <Select
                      value={trading.defaultExchange}
                      onChange={(e) => updateTrading({ defaultExchange: e.target.value })}
                      label=\"Default Exchange\"
                    >
                      <MenuItem value=\"HTX\">HTX (Huobi)</MenuItem>
                      <MenuItem value=\"Binance\">Binance</MenuItem>
                      <MenuItem value=\"Coinbase\">Coinbase</MenuItem>
                    </Select>
                  </FormControl>
                  
                  <TextField
                    fullWidth
                    margin=\"normal\"
                    label=\"Default Trading Pair\"
                    value={trading.defaultTradingPair}
                    onChange={(e) => updateTrading({ defaultTradingPair: e.target.value })}
                  />
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant=\"h6\" gutterBottom>Preferences</Typography>
                  
                  <FormControlLabel
                    control={
                      <Switch
                        checked={trading.confirmOrders}
                        onChange={(e) => updateTrading({ confirmOrders: e.target.checked })}
                      />
                    }
                    label=\"Confirm Orders\"
                  />
                  
                  <FormControlLabel
                    control={
                      <Switch
                        checked={trading.autoRefresh}
                        onChange={(e) => updateTrading({ autoRefresh: e.target.checked })}
                      />
                    }
                    label=\"Auto Refresh\"
                  />
                  
                  <FormControlLabel
                    control={
                      <Switch
                        checked={trading.soundNotifications}
                        onChange={(e) => updateTrading({ soundNotifications: e.target.checked })}
                      />
                    }
                    label=\"Sound Notifications\"
                  />
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>
        
        {/* Notifications */}
        <TabPanel value={tabValue} index={3}>
          <Card>
            <CardContent>
              <Typography variant=\"h6\" gutterBottom>Notification Settings</Typography>
              
              <List>
                <ListItem>
                  <ListItemText primary=\"Price Alerts\" />
                  <ListItemSecondaryAction>
                    <Switch
                      checked={getSettingValue('notifications.priceAlerts', true)}
                      onChange={(e) => setSettingValue('notifications.priceAlerts', e.target.checked)}
                    />
                  </ListItemSecondaryAction>
                </ListItem>
                
                <ListItem>
                  <ListItemText primary=\"Order Updates\" />
                  <ListItemSecondaryAction>
                    <Switch
                      checked={getSettingValue('notifications.orderUpdates', true)}
                      onChange={(e) => setSettingValue('notifications.orderUpdates', e.target.checked)}
                    />
                  </ListItemSecondaryAction>
                </ListItem>
                
                <ListItem>
                  <ListItemText primary=\"Browser Notifications\" />
                  <ListItemSecondaryAction>
                    <Switch
                      checked={getSettingValue('notifications.browser', true)}
                      onChange={(e) => setSettingValue('notifications.browser', e.target.checked)}
                    />
                  </ListItemSecondaryAction>
                </ListItem>
                
                <ListItem>
                  <ListItemText primary=\"System Updates\" />
                  <ListItemSecondaryAction>
                    <Switch
                      checked={getSettingValue('notifications.systemUpdates', true)}
                      onChange={(e) => setSettingValue('notifications.systemUpdates', e.target.checked)}
                    />
                  </ListItemSecondaryAction>
                </ListItem>
              </List>
            </CardContent>
          </Card>
        </TabPanel>
      </DialogContent>
      
      <DialogActions>
        <Button onClick={onClose}>
          Close
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default SettingsDialog;"