/**
 * Global Error Boundary Component
 * Catches and handles React errors throughout the application
 */

import React, { Component } from 'react';
import {
  Box,
  Alert,
  AlertTitle,
  Button,
  Typography,
  Card,
  CardContent,
  Stack,
  Chip,
  IconButton,
  Collapse
} from '@mui/material';
import {
  ErrorOutline,
  Refresh,
  ExpandMore,
  ExpandLess,
  BugReport
} from '@mui/icons-material';

class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      showDetails: false,
      errorId: null
    };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI
    return {
      hasError: true,
      errorId: `error-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
    };
  }

  componentDidCatch(error, errorInfo) {
    // Log error to console and potentially to error reporting service
    console.error('🔥 Error Boundary caught an error:', error, errorInfo);
    
    this.setState({
      error,
      errorInfo
    });

    // Report to error monitoring service if available
    if (window.gtag) {
      window.gtag('event', 'exception', {
        description: error.toString(),
        fatal: false
      });
    }
  }

  handleRetry = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
      showDetails: false,
      errorId: null
    });
  };

  handleReload = () => {
    window.location.reload();
  };

  toggleDetails = () => {
    this.setState(prev => ({ showDetails: !prev.showDetails }));
  };

  render() {
    if (this.state.hasError) {
      const { error, errorInfo, showDetails, errorId } = this.state;
      const { fallback, title = "Something went wrong" } = this.props;

      // Use custom fallback if provided
      if (fallback) {
        return fallback(error, errorInfo, this.handleRetry);
      }

      return (
        <Box
          sx={{
            minHeight: '200px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            p: 3
          }}
        >
          <Card sx={{ maxWidth: 600, width: '100%' }}>
            <CardContent>
              <Stack spacing={3}>
                {/* Error Header */}
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <ErrorOutline color="error" sx={{ fontSize: 40 }} />
                  <Box>
                    <Typography variant="h5" color="error" gutterBottom>
                      {title}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Error ID: {errorId}
                    </Typography>
                  </Box>
                </Box>

                {/* Error Message */}
                <Alert severity="error">
                  <AlertTitle>Application Error</AlertTitle>
                  {error?.message || 'An unexpected error occurred'}
                </Alert>

                {/* Action Buttons */}
                <Stack direction="row" spacing={2} sx={{ justifyContent: 'center' }}>
                  <Button
                    variant="contained"
                    startIcon={<Refresh />}
                    onClick={this.handleRetry}
                    color="primary"
                  >
                    Try Again
                  </Button>
                  <Button
                    variant="outlined"
                    onClick={this.handleReload}
                    color="secondary"
                  >
                    Reload Page
                  </Button>
                </Stack>

                {/* Development Details */}
                {process.env.NODE_ENV === 'development' && (
                  <>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Chip
                        icon={<BugReport />}
                        label="Development Mode"
                        size="small"
                        color="warning"
                        variant="outlined"
                      />
                      <IconButton
                        size="small"
                        onClick={this.toggleDetails}
                        aria-label="toggle error details"
                      >
                        {showDetails ? <ExpandLess /> : <ExpandMore />}
                      </IconButton>
                      <Typography variant="body2" color="text.secondary">
                        Error Details
                      </Typography>
                    </Box>

                    <Collapse in={showDetails}>
                      <Card variant="outlined" sx={{ bgcolor: 'grey.50' }}>
                        <CardContent>
                          <Typography variant="subtitle2" gutterBottom>
                            Error Stack:
                          </Typography>
                          <Typography
                            variant="body2"
                            component="pre"
                            sx={{
                              fontSize: '0.75rem',
                              fontFamily: 'monospace',
                              whiteSpace: 'pre-wrap',
                              overflow: 'auto',
                              maxHeight: '200px',
                              bgcolor: 'background.paper',
                              p: 1,
                              border: '1px solid',
                              borderColor: 'divider',
                              borderRadius: 1
                            }}
                          >
                            {error?.stack}
                          </Typography>
                          
                          {errorInfo?.componentStack && (
                            <>
                              <Typography variant="subtitle2" sx={{ mt: 2 }} gutterBottom>
                                Component Stack:
                              </Typography>
                              <Typography
                                variant="body2"
                                component="pre"
                                sx={{
                                  fontSize: '0.75rem',
                                  fontFamily: 'monospace',
                                  whiteSpace: 'pre-wrap',
                                  overflow: 'auto',
                                  maxHeight: '200px',
                                  bgcolor: 'background.paper',
                                  p: 1,
                                  border: '1px solid',
                                  borderColor: 'divider',
                                  borderRadius: 1
                                }}
                              >
                                {errorInfo.componentStack}
                              </Typography>
                            </>
                          )}
                        </CardContent>
                      </Card>
                    </Collapse>
                  </>
                )}
              </Stack>
            </CardContent>
          </Card>
        </Box>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;