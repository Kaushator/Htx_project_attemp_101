/**
 * Global Notification System
 * Provides toast notifications for errors, success, and info messages
 */

import React, { createContext, useContext, useState, useCallback } from 'react';
import {
  Snackbar,
  Alert,
  AlertTitle,
  Slide,
  IconButton,
  Stack,
  Box
} from '@mui/material';
import { Close, ErrorOutline, CheckCircle, Info, Warning } from '@mui/icons-material';

// Slide transition for notifications
function SlideTransition(props) {
  return <Slide {...props} direction="up" />;
}

// Notification context
const NotificationContext = createContext();

// Notification types
export const NOTIFICATION_TYPES = {
  SUCCESS: 'success',
  ERROR: 'error',
  WARNING: 'warning',
  INFO: 'info'
};

// Notification Provider Component
export const NotificationProvider = ({ children, maxNotifications = 3 }) => {
  const [notifications, setNotifications] = useState([]);

  // Add notification
  const addNotification = useCallback((message, type = NOTIFICATION_TYPES.INFO, options = {}) => {
    const id = `notification-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    
    const notification = {
      id,
      message,
      type,
      title: options.title,
      autoHideDuration: options.autoHideDuration || (type === NOTIFICATION_TYPES.ERROR ? 8000 : 6000),
      persist: options.persist || false,
      action: options.action,
      timestamp: new Date().toISOString()
    };

    setNotifications(prev => {
      const newNotifications = [notification, ...prev];
      // Limit number of notifications
      return newNotifications.slice(0, maxNotifications);
    });

    return id;
  }, [maxNotifications]);

  // Remove notification
  const removeNotification = useCallback((id) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  }, []);

  // Clear all notifications
  const clearNotifications = useCallback(() => {
    setNotifications([]);
  }, []);

  // Convenience methods
  const showSuccess = useCallback((message, options) => 
    addNotification(message, NOTIFICATION_TYPES.SUCCESS, options), [addNotification]);
  
  const showError = useCallback((message, options) => 
    addNotification(message, NOTIFICATION_TYPES.ERROR, options), [addNotification]);
  
  const showWarning = useCallback((message, options) => 
    addNotification(message, NOTIFICATION_TYPES.WARNING, options), [addNotification]);
  
  const showInfo = useCallback((message, options) => 
    addNotification(message, NOTIFICATION_TYPES.INFO, options), [addNotification]);

  // Handle API errors specifically
  const handleApiError = useCallback((error, customMessage) => {
    let message = customMessage || 'An error occurred';
    let title = 'Error';

    if (error?.type) {
      switch (error.type) {
        case 'NETWORK_ERROR':
          title = 'Network Error';
          message = customMessage || 'Unable to connect to server. Please check your connection.';
          break;
        case 'TIMEOUT_ERROR':
          title = 'Timeout Error';
          message = customMessage || 'Request timed out. Please try again.';
          break;
        case 'SERVER_ERROR':
          title = 'Server Error';
          message = customMessage || error.message || 'Server error occurred.';
          break;
        case 'AUTHENTICATION_ERROR':
          title = 'Authentication Error';
          message = customMessage || 'Please check your credentials and try again.';
          break;
        default:
          message = customMessage || error.message || 'An unexpected error occurred';
      }
    } else if (error?.message) {
      message = customMessage || error.message;
    }

    return showError(message, { title });
  }, [showError]);

  const contextValue = {
    notifications,
    addNotification,
    removeNotification,
    clearNotifications,
    showSuccess,
    showError,
    showWarning,
    showInfo,
    handleApiError
  };

  return (
    <NotificationContext.Provider value={contextValue}>
      {children}
      <NotificationContainer 
        notifications={notifications}
        onClose={removeNotification}
      />
    </NotificationContext.Provider>
  );
};

// Notification Container Component
const NotificationContainer = ({ notifications, onClose }) => {
  return (
    <Box
      sx={{
        position: 'fixed',
        bottom: 24,
        right: 24,
        zIndex: (theme) => theme.zIndex.snackbar,
        maxWidth: 400
      }}
    >
      <Stack spacing={2}>
        {notifications.map((notification) => (
          <NotificationItem
            key={notification.id}
            notification={notification}
            onClose={onClose}
          />
        ))}
      </Stack>
    </Box>
  );
};

// Individual Notification Item
const NotificationItem = ({ notification, onClose }) => {
  const [open, setOpen] = useState(true);

  const handleClose = (event, reason) => {
    if (reason === 'clickaway' && notification.persist) {
      return;
    }
    setOpen(false);
    setTimeout(() => onClose(notification.id), 150);
  };

  const getIcon = () => {
    switch (notification.type) {
      case NOTIFICATION_TYPES.SUCCESS:
        return <CheckCircle />;
      case NOTIFICATION_TYPES.ERROR:
        return <ErrorOutline />;
      case NOTIFICATION_TYPES.WARNING:
        return <Warning />;
      case NOTIFICATION_TYPES.INFO:
      default:
        return <Info />;
    }
  };

  return (
    <Snackbar
      open={open}
      autoHideDuration={notification.persist ? null : notification.autoHideDuration}
      onClose={handleClose}
      TransitionComponent={SlideTransition}
      sx={{ position: 'static' }}
    >
      <Alert
        severity={notification.type}
        onClose={notification.persist ? undefined : handleClose}
        icon={getIcon()}
        action={
          notification.action || (
            notification.persist && (
              <IconButton
                size="small"
                aria-label="close"
                color="inherit"
                onClick={handleClose}
              >
                <Close fontSize="small" />
              </IconButton>
            )
          )
        }
        sx={{
          minWidth: 300,
          maxWidth: 400,
          '& .MuiAlert-message': {
            wordBreak: 'break-word'
          }
        }}
      >
        {notification.title && (
          <AlertTitle>{notification.title}</AlertTitle>
        )}
        {notification.message}
      </Alert>
    </Snackbar>
  );
};

// Hook to use notifications
export const useNotifications = () => {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotifications must be used within a NotificationProvider');
  }
  return context;
};

// HOC for automatic error handling
export const withErrorHandling = (WrappedComponent) => {
  return function ErrorHandledComponent(props) {
    const { handleApiError } = useNotifications();
    
    return (
      <WrappedComponent 
        {...props} 
        onError={handleApiError}
      />
    );
  };
};

export default NotificationProvider;