/**
 * User Settings Context and Hooks
 * Manages user preferences, dashboard layout, and personalization settings
 */

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { useNotifications } from '../NotificationSystem';

// Default settings structure
const defaultSettings = {
  // General preferences
  theme: 'light', // 'light', 'dark', 'auto'
  language: 'en', // 'en', 'ru', 'zh'
  timezone: 'UTC',
  currency: 'USD',
  
  // Dashboard layout
  dashboardLayout: {
    widgets: [
      { id: 'balance', enabled: true, position: { x: 0, y: 0, w: 6, h: 4 } },
      { id: 'portfolio', enabled: true, position: { x: 6, y: 0, w: 6, h: 4 } },
      { id: 'trades', enabled: true, position: { x: 0, y: 4, w: 12, h: 6 } },
      { id: 'charts', enabled: true, position: { x: 0, y: 10, w: 8, h: 8 } },
      { id: 'news', enabled: false, position: { x: 8, y: 10, w: 4, h: 8 } }
    ],
    gridSize: { cols: 12, rowHeight: 30 },
    compactType: 'vertical',
    margin: [10, 10]
  },
  
  // Trading preferences
  trading: {
    defaultExchange: 'HTX',
    defaultTradingPair: 'BTCUSDT',
    defaultOrderType: 'limit',
    riskLevel: 'medium', // 'low', 'medium', 'high'
    autoRefresh: true,
    refreshInterval: 5000, // ms
    confirmOrders: true,
    soundNotifications: false
  },
  
  // Display preferences
  display: {
    compactMode: false,
    showTooltips: true,
    animationsEnabled: true,
    highContrastMode: false,
    fontSize: 'medium', // 'small', 'medium', 'large'
    density: 'comfortable', // 'compact', 'comfortable', 'spacious'
    chartTheme: 'default',
    numberFormat: {
      decimals: 4,
      thousandsSeparator: ',',
      decimalSeparator: '.'
    }
  },
  
  // Notifications
  notifications: {
    browser: true,
    email: false,
    sms: false,
    priceAlerts: true,
    orderUpdates: true,
    newsAlerts: false,
    systemUpdates: true
  },
  
  // Privacy & Security
  privacy: {
    shareAnalytics: false,
    rememberLogin: true,
    twoFactorAuth: false,
    sessionTimeout: 3600, // seconds
    publicProfile: false
  },
  
  // Advanced
  advanced: {
    apiKeys: {},
    customCSS: '',
    debugMode: false,
    experimentalFeatures: false,
    dataExport: {
      format: 'csv',
      includeMetadata: true,
      compression: false
    }
  },
  
  // Favorites and watchlists
  favorites: {
    tokens: [],
    tradingPairs: [],
    strategies: [],
    dashboards: []
  }
};

// Settings Context
const SettingsContext = createContext({
  settings: defaultSettings,
  updateSettings: () => {},
  resetSettings: () => {},
  exportSettings: () => {},
  importSettings: () => {},
  getSettingValue: () => null,
  setSettingValue: () => {}
});

// Settings Provider Component
export const SettingsProvider = ({ children }) => {
  const [settings, setSettings] = useState(defaultSettings);
  const { showSuccess, showError } = useNotifications();
  
  // Load settings from localStorage on mount
  useEffect(() => {
    try {
      const savedSettings = localStorage.getItem('userSettings');
      if (savedSettings) {
        const parsed = JSON.parse(savedSettings);
        // Merge with defaults to ensure all keys exist
        setSettings(prev => ({ ...prev, ...parsed }));
      }
    } catch (error) {
      console.error('Failed to load settings:', error);
      showError('Failed to load user settings');
    }
  }, [showError]);
  
  // Save settings to localStorage whenever they change
  useEffect(() => {
    try {
      localStorage.setItem('userSettings', JSON.stringify(settings));
    } catch (error) {
      console.error('Failed to save settings:', error);
      showError('Failed to save settings');
    }
  }, [settings, showError]);
  
  // Update settings function
  const updateSettings = useCallback((newSettings) => {
    setSettings(prev => {
      // Deep merge for nested objects
      const merged = { ...prev };
      
      Object.keys(newSettings).forEach(key => {
        if (typeof newSettings[key] === 'object' && newSettings[key] !== null && !Array.isArray(newSettings[key])) {
          merged[key] = { ...merged[key], ...newSettings[key] };
        } else {
          merged[key] = newSettings[key];
        }
      });
      
      return merged;
    });
  }, []);
  
  // Reset to defaults
  const resetSettings = useCallback(() => {
    setSettings(defaultSettings);
    showSuccess('Settings reset to defaults');
  }, [showSuccess]);
  
  // Export settings
  const exportSettings = useCallback(() => {
    try {
      const settingsJson = JSON.stringify(settings, null, 2);
      const blob = new Blob([settingsJson], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `htx_settings_${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      
      showSuccess('Settings exported successfully');
    } catch (error) {
      showError('Failed to export settings');
    }
  }, [settings, showSuccess, showError]);
  
  // Import settings
  const importSettings = useCallback((file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      
      reader.onload = (e) => {
        try {
          const importedSettings = JSON.parse(e.target.result);
          
          // Validate imported settings structure
          if (typeof importedSettings === 'object' && importedSettings !== null) {
            updateSettings(importedSettings);
            showSuccess('Settings imported successfully');
            resolve(importedSettings);
          } else {
            throw new Error('Invalid settings format');
          }
        } catch (error) {
          showError('Failed to import settings: Invalid file format');
          reject(error);
        }
      };
      
      reader.onerror = () => {
        showError('Failed to read settings file');
        reject(new Error('File read error'));
      };
      
      reader.readAsText(file);
    });
  }, [updateSettings, showSuccess, showError]);
  
  // Get specific setting value by path
  const getSettingValue = useCallback((path, defaultValue = null) => {
    const keys = path.split('.');
    let value = settings;
    
    for (const key of keys) {
      if (value && typeof value === 'object' && key in value) {
        value = value[key];
      } else {
        return defaultValue;
      }
    }
    
    return value;
  }, [settings]);
  
  // Set specific setting value by path
  const setSettingValue = useCallback((path, value) => {
    const keys = path.split('.');
    const newSettings = { ...settings };
    let current = newSettings;
    
    // Navigate to the parent of the target key
    for (let i = 0; i < keys.length - 1; i++) {
      const key = keys[i];
      if (!(key in current) || typeof current[key] !== 'object') {
        current[key] = {};
      } else {
        current[key] = { ...current[key] };
      }
      current = current[key];
    }
    
    // Set the final value
    current[keys[keys.length - 1]] = value;
    
    setSettings(newSettings);
  }, [settings]);
  
  const contextValue = {
    settings,
    updateSettings,
    resetSettings,
    exportSettings,
    importSettings,
    getSettingValue,
    setSettingValue
  };
  
  return (
    <SettingsContext.Provider value={contextValue}>
      {children}
    </SettingsContext.Provider>
  );
};

// Settings Hook
export const useSettings = () => {
  const context = useContext(SettingsContext);
  if (!context) {
    throw new Error('useSettings must be used within a SettingsProvider');
  }
  return context;
};

// Specific hooks for common settings
export const useTheme = () => {
  const { getSettingValue, setSettingValue } = useSettings();
  return {
    theme: getSettingValue('theme', 'light'),
    setTheme: (theme) => setSettingValue('theme', theme)
  };
};

export const useDisplaySettings = () => {
  const { getSettingValue, setSettingValue } = useSettings();
  return {
    display: getSettingValue('display', defaultSettings.display),
    updateDisplay: (displaySettings) => {
      Object.entries(displaySettings).forEach(([key, value]) => {
        setSettingValue(`display.${key}`, value);
      });
    }
  };
};

export const useTradingSettings = () => {
  const { getSettingValue, setSettingValue } = useSettings();
  return {
    trading: getSettingValue('trading', defaultSettings.trading),
    updateTrading: (tradingSettings) => {
      Object.entries(tradingSettings).forEach(([key, value]) => {
        setSettingValue(`trading.${key}`, value);
      });
    }
  };
};

export const useDashboardLayout = () => {
  const { getSettingValue, setSettingValue } = useSettings();
  return {
    layout: getSettingValue('dashboardLayout', defaultSettings.dashboardLayout),
    updateLayout: (layout) => setSettingValue('dashboardLayout', layout),
    updateWidget: (widgetId, updates) => {
      const currentLayout = getSettingValue('dashboardLayout', defaultSettings.dashboardLayout);
      const updatedWidgets = currentLayout.widgets.map(widget => 
        widget.id === widgetId ? { ...widget, ...updates } : widget
      );
      setSettingValue('dashboardLayout', { ...currentLayout, widgets: updatedWidgets });
    },
    enableWidget: (widgetId) => {
      const currentLayout = getSettingValue('dashboardLayout', defaultSettings.dashboardLayout);
      const updatedWidgets = currentLayout.widgets.map(widget => 
        widget.id === widgetId ? { ...widget, enabled: true } : widget
      );
      setSettingValue('dashboardLayout', { ...currentLayout, widgets: updatedWidgets });
    },
    disableWidget: (widgetId) => {
      const currentLayout = getSettingValue('dashboardLayout', defaultSettings.dashboardLayout);
      const updatedWidgets = currentLayout.widgets.map(widget => 
        widget.id === widgetId ? { ...widget, enabled: false } : widget
      );
      setSettingValue('dashboardLayout', { ...currentLayout, widgets: updatedWidgets });
    }
  };
};

export const useFavorites = () => {
  const { getSettingValue, setSettingValue } = useSettings();
  
  const addFavorite = useCallback((type, item) => {
    const favorites = getSettingValue('favorites', defaultSettings.favorites);
    const currentList = favorites[type] || [];
    
    if (!currentList.includes(item)) {
      setSettingValue(`favorites.${type}`, [...currentList, item]);
      return true;
    }
    return false;
  }, [getSettingValue, setSettingValue]);
  
  const removeFavorite = useCallback((type, item) => {
    const favorites = getSettingValue('favorites', defaultSettings.favorites);
    const currentList = favorites[type] || [];
    const filtered = currentList.filter(fav => fav !== item);
    setSettingValue(`favorites.${type}`, filtered);
  }, [getSettingValue, setSettingValue]);
  
  const isFavorite = useCallback((type, item) => {
    const favorites = getSettingValue('favorites', defaultSettings.favorites);
    const currentList = favorites[type] || [];
    return currentList.includes(item);
  }, [getSettingValue]);
  
  return {
    favorites: getSettingValue('favorites', defaultSettings.favorites),
    addFavorite,
    removeFavorite,
    isFavorite
  };
};

export default SettingsContext;