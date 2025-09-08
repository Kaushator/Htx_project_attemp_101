/**
 * Settings Button Component
 * Quick access to user settings from anywhere in the app
 */

import React, { useState } from 'react';
import {
  IconButton,
  Button,
  Tooltip,
  Fab,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText
} from '@mui/material';
import {
  Settings,
  Palette,
  Person,
  Download,
  Upload,
  RestoreFromTrash
} from '@mui/icons-material';
import SettingsDialog from './SettingsDialog';
import { useSettings } from '../../contexts/SettingsContext';

// Simple Settings Button
export const SettingsButton = ({ variant = 'icon', size = 'medium', ...props }) => {
  const [dialogOpen, setDialogOpen] = useState(false);
  
  const ButtonComponent = variant === 'fab' ? Fab : 
                         variant === 'button' ? Button : IconButton;
  
  const buttonProps = {
    onClick: () => setDialogOpen(true),
    size,
    ...props
  };
  
  if (variant === 'button') {
    buttonProps.startIcon = <Settings />;
    buttonProps.children = 'Settings';
  } else if (variant === 'fab') {
    buttonProps.children = <Settings />;
  } else {
    buttonProps.children = <Settings />;
  }
  
  return (
    <>
      <Tooltip title=\"Settings\">
        <ButtonComponent {...buttonProps} />
      </Tooltip>
      
      <SettingsDialog 
        open={dialogOpen} 
        onClose={() => setDialogOpen(false)} 
      />
    </>
  );
};

// Advanced Settings Menu
export const SettingsMenu = ({ anchorEl, open, onClose }) => {
  const [dialogOpen, setDialogOpen] = useState(false);
  const { exportSettings, resetSettings } = useSettings();
  
  const handleMenuItemClick = (action) => {
    onClose();
    
    switch (action) {
      case 'settings':
        setDialogOpen(true);
        break;
      case 'export':
        exportSettings();
        break;
      case 'reset':
        if (window.confirm('Are you sure you want to reset all settings?')) {
          resetSettings();
        }
        break;
      default:
        break;
    }
  };
  
  return (
    <>
      <Menu
        anchorEl={anchorEl}
        open={open}
        onClose={onClose}
        PaperProps={{
          sx: { minWidth: 200 }
        }}
      >
        <MenuItem onClick={() => handleMenuItemClick('settings')}>
          <ListItemIcon>
            <Settings />
          </ListItemIcon>
          <ListItemText primary=\"All Settings\" />
        </MenuItem>
        
        <MenuItem onClick={() => handleMenuItemClick('export')}>
          <ListItemIcon>
            <Download />
          </ListItemIcon>
          <ListItemText primary=\"Export Settings\" />
        </MenuItem>
        
        <MenuItem onClick={() => handleMenuItemClick('reset')}>
          <ListItemIcon>
            <RestoreFromTrash />
          </ListItemIcon>
          <ListItemText primary=\"Reset Settings\" />
        </MenuItem>
      </Menu>
      
      <SettingsDialog 
        open={dialogOpen} 
        onClose={() => setDialogOpen(false)} 
      />
    </>
  );
};

// Quick Theme Toggle
export const ThemeToggle = () => {
  const { getSettingValue, setSettingValue } = useSettings();
  const currentTheme = getSettingValue('theme', 'light');
  
  const toggleTheme = () => {
    const nextTheme = currentTheme === 'light' ? 'dark' : 'light';
    setSettingValue('theme', nextTheme);
  };
  
  return (
    <Tooltip title={`Switch to ${currentTheme === 'light' ? 'dark' : 'light'} theme`}>
      <IconButton onClick={toggleTheme}>
        <Palette />
      </IconButton>
    </Tooltip>
  );
};

export default SettingsButton;"