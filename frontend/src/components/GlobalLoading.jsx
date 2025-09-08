/**
 * Global Loading Component
 * Provides loading states and progress indicators
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  LinearProgress,
  CircularProgress,
  Backdrop,
  Typography,
  Fade,
  Paper,
  Stack,
  Button
} from '@mui/material';
import { loadingManager } from '../services/apiClient.js';

// Loading backdrop for full-screen loading
export const LoadingBackdrop = ({ open, message = "Loading...", variant = "circular" }) => {
  return (
    <Backdrop
      sx={{
        color: '#fff',
        zIndex: (theme) => theme.zIndex.drawer + 1,
        bgcolor: 'rgba(0, 0, 0, 0.7)'
      }}
      open={open}
    >
      <Paper
        elevation={3}
        sx={{
          p: 4,
          borderRadius: 2,
          bgcolor: 'background.paper',
          color: 'text.primary',
          minWidth: 200,
          textAlign: 'center'
        }}
      >
        <Stack spacing={3} alignItems="center">
          {variant === "circular" ? (
            <CircularProgress size={40} />
          ) : (
            <Box sx={{ width: '100%', minWidth: 200 }}>
              <LinearProgress />
            </Box>
          )}
          <Typography variant="body1">{message}</Typography>
        </Stack>
      </Paper>
    </Backdrop>
  );
};

// Loading bar that appears at the top of the page
export const LoadingBar = ({ show }) => {
  return (
    <Fade in={show}>
      <Box
        sx={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          zIndex: (theme) => theme.zIndex.appBar + 1,
          height: 4
        }}
      >
        <LinearProgress 
          sx={{
            height: '100%',
            '& .MuiLinearProgress-bar': {
              transition: 'transform 0.4s cubic-bezier(0.4, 0, 0.2, 1)'
            }
          }}
        />
      </Box>
    </Fade>
  );
};

// Inline loading component for specific sections
export const InlineLoading = ({ 
  loading, 
  children, 
  skeleton = null, 
  message = "Loading...",
  minHeight = 100,
  variant = "circular"
}) => {
  if (loading) {
    if (skeleton) {
      return skeleton;
    }

    return (
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight,
          p: 3
        }}
      >
        <Stack spacing={2} alignItems="center">
          {variant === "circular" ? (
            <CircularProgress size={32} />
          ) : (
            <Box sx={{ width: 200 }}>
              <LinearProgress />
            </Box>
          )}
          <Typography variant="body2" color="text.secondary">
            {message}
          </Typography>
        </Stack>
      </Box>
    );
  }

  return children;
};

// Button with loading state
export const LoadingButton = ({ 
  loading, 
  children, 
  loadingText = "Loading...",
  variant = "contained",
  ...props 
}) => {
  return (
    <Button
      {...props}
      variant={variant}
      disabled={loading || props.disabled}
      startIcon={loading ? <CircularProgress size={16} /> : props.startIcon}
    >
      {loading ? loadingText : children}
    </Button>
  );
};

// Global loading hook
export const useGlobalLoading = () => {
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const unsubscribe = loadingManager.addListener(setIsLoading);
    return unsubscribe;
  }, []);

  return isLoading;
};

// Specific request loading hook
export const useRequestLoading = (requestId) => {
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const checkLoading = () => {
      setIsLoading(loadingManager.isLoading(requestId));
    };

    const unsubscribe = loadingManager.addListener(checkLoading);
    checkLoading(); // Check initial state

    return unsubscribe;
  }, [requestId]);

  return isLoading;
};

// Main global loading component
export const GlobalLoading = ({ variant = "bar" }) => {
  const isLoading = useGlobalLoading();

  if (variant === "bar") {
    return <LoadingBar show={isLoading} />;
  }

  return (
    <LoadingBackdrop 
      open={isLoading} 
      message="Processing request..." 
      variant={variant}
    />
  );
};

export default GlobalLoading;