/**
 * Secret Manager Dashboard
 * Manage and monitor API keys stored in Google Secret Manager
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  CardHeader,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
  Grid,
  LinearProgress,
  Tooltip,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText
} from '@mui/material';
import {
  Security,
  Add,
  Edit,
  Delete,
  Refresh,
  Visibility,
  VisibilityOff,
  CheckCircle,
  Warning,
  Error,
  MoreVert,
  History,
  CloudUpload
} from '@mui/icons-material';
import { useNotifications } from '../NotificationSystem';
import SecretManagerWizard from './SecretManagerWizard';

const SecretManagerDashboard = () => {
  const [secrets, setSecrets] = useState([]);
  const [loading, setLoading] = useState(false);
  const [wizardOpen, setWizardOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [selectedSecret, setSelectedSecret] = useState(null);
  const [newSecretValue, setNewSecretValue] = useState('');
  const [connectionStatus, setConnectionStatus] = useState('unknown');
  const [menuAnchorEl, setMenuAnchorEl] = useState(null);
  const [menuSecretId, setMenuSecretId] = useState(null);
  
  const { showSuccess, showError, showWarning } = useNotifications();

  // Mock secret data - in real implementation, this would come from backend API
  const mockSecrets = [
    {
      id: 'htx-api-key',
      name: 'HTX API Key',
      description: 'HTX exchange API access key',
      status: 'active',
      lastUpdated: '2024-01-15T10:30:00Z',
      required: true,
      hasValue: true
    },
    {
      id: 'htx-api-secret',
      name: 'HTX API Secret',
      description: 'HTX exchange API secret key',
      status: 'active',
      lastUpdated: '2024-01-15T10:30:00Z',
      required: true,
      hasValue: true
    },
    {
      id: 'htx-subuid',
      name: 'HTX Sub-Account UID',
      description: 'HTX sub-account user ID',
      status: 'inactive',
      lastUpdated: null,
      required: false,
      hasValue: false
    },
    {
      id: 'openai-api-key',
      name: 'OpenAI API Key',
      description: 'OpenAI API key for ML services',
      status: 'active',
      lastUpdated: '2024-01-10T14:20:00Z',
      required: false,
      hasValue: true
    },
    {
      id: 'threecommas-api-key',
      name: '3Commas API Key',
      description: '3Commas API key for bot integration',
      status: 'warning',
      lastUpdated: '2023-12-20T09:15:00Z',
      required: false,
      hasValue: true
    }
  ];

  useEffect(() => {
    loadSecrets();
    checkConnectionStatus();
  }, []);

  const loadSecrets = async () => {
    setLoading(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      setSecrets(mockSecrets);
      showSuccess('Secrets loaded successfully');
    } catch (error) {
      showError('Failed to load secrets: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const checkConnectionStatus = async () => {
    try {
      // Simulate connection check
      await new Promise(resolve => setTimeout(resolve, 500));
      setConnectionStatus('connected');
    } catch (error) {
      setConnectionStatus('error');
    }
  };

  const handleMenuOpen = (event, secretId) => {
    setMenuAnchorEl(event.currentTarget);
    setMenuSecretId(secretId);
  };

  const handleMenuClose = () => {
    setMenuAnchorEl(null);
    setMenuSecretId(null);
  };

  const handleEditSecret = (secret) => {
    setSelectedSecret(secret);
    setNewSecretValue('');
    setEditDialogOpen(true);
    handleMenuClose();
  };

  const handleUpdateSecret = async () => {
    if (!newSecretValue.trim()) {
      showWarning('Please enter a value for the secret');
      return;
    }

    try {
      // Simulate API call to update secret
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setSecrets(prev => prev.map(secret => 
        secret.id === selectedSecret.id
          ? { ...secret, lastUpdated: new Date().toISOString(), hasValue: true, status: 'active' }
          : secret
      ));
      
      showSuccess(`Secret ${selectedSecret.name} updated successfully`);
      setEditDialogOpen(false);
      setSelectedSecret(null);
      setNewSecretValue('');
    } catch (error) {
      showError('Failed to update secret: ' + error.message);
    }
  };

  const handleDeleteSecret = async (secretId) => {
    if (!window.confirm('Are you sure you want to delete this secret?')) {
      return;
    }

    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 500));
      
      setSecrets(prev => prev.map(secret => 
        secret.id === secretId
          ? { ...secret, hasValue: false, status: 'inactive', lastUpdated: null }
          : secret
      ));
      
      showSuccess('Secret deleted successfully');
      handleMenuClose();
    } catch (error) {
      showError('Failed to delete secret: ' + error.message);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'success';
      case 'warning': return 'warning';
      case 'inactive': return 'default';
      case 'error': return 'error';
      default: return 'default';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'active': return <CheckCircle />;
      case 'warning': return <Warning />;
      case 'error': return <Error />;
      default: return null;
    }
  };

  const getConnectionStatusChip = () => {
    switch (connectionStatus) {
      case 'connected':
        return <Chip icon={<CheckCircle />} label="Connected" color="success" size="small" />;
      case 'error':
        return <Chip icon={<Error />} label="Connection Error" color="error" size="small" />;
      default:
        return <Chip label="Checking..." color="default" size="small" />;
    }
  };

  const requiredSecretsCount = secrets.filter(s => s.required && s.hasValue).length;
  const totalRequiredSecrets = secrets.filter(s => s.required).length;
  const optionalSecretsCount = secrets.filter(s => !s.required && s.hasValue).length;

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" component="h1" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Security />
            Secret Manager
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Manage API keys securely with Google Secret Manager
          </Typography>
        </Box>
        
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={loadSecrets}
            disabled={loading}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<CloudUpload />}
            onClick={() => setWizardOpen(true)}
          >
            Setup Wizard
          </Button>
        </Box>
      </Box>

      {/* Status Overview */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Connection Status</Typography>
              {getConnectionStatusChip()}
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Required Keys</Typography>
              <Typography variant="h4" color={requiredSecretsCount === totalRequiredSecrets ? 'success.main' : 'error.main'}>
                {requiredSecretsCount}/{totalRequiredSecrets}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Optional Keys</Typography>
              <Typography variant="h4" color="info.main">
                {optionalSecretsCount}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Total Secrets</Typography>
              <Typography variant="h4">
                {secrets.length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Secrets Table */}
      <Card>
        <CardHeader 
          title="API Key Configuration"
          action={
            <Button
              startIcon={<Add />}
              onClick={() => setWizardOpen(true)}
            >
              Add Secret
            </Button>
          }
        />
        <CardContent sx={{ p: 0 }}>
          {loading && <LinearProgress />}
          
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Name</TableCell>
                  <TableCell>Description</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Required</TableCell>
                  <TableCell>Last Updated</TableCell>
                  <TableCell align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {secrets.map((secret) => (
                  <TableRow key={secret.id} hover>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {getStatusIcon(secret.status)}
                        <Typography variant="body2" fontWeight="medium">
                          {secret.name}
                        </Typography>
                      </Box>
                    </TableCell>
                    
                    <TableCell>
                      <Typography variant="body2" color="text.secondary">
                        {secret.description}
                      </Typography>
                    </TableCell>
                    
                    <TableCell>
                      <Chip 
                        label={secret.status} 
                        color={getStatusColor(secret.status)} 
                        size="small" 
                      />
                    </TableCell>
                    
                    <TableCell>
                      {secret.required ? (
                        <Chip label="Required" color="error" size="small" />
                      ) : (
                        <Chip label="Optional" color="default" size="small" />
                      )}
                    </TableCell>
                    
                    <TableCell>
                      {secret.lastUpdated ? (
                        <Typography variant="body2">
                          {new Date(secret.lastUpdated).toLocaleDateString()}
                        </Typography>
                      ) : (
                        <Typography variant="body2" color="text.secondary">
                          Never
                        </Typography>
                      )}
                    </TableCell>
                    
                    <TableCell align="right">
                      <IconButton
                        size="small"
                        onClick={(e) => handleMenuOpen(e, secret.id)}
                      >
                        <MoreVert />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Action Menu */}
      <Menu
        anchorEl={menuAnchorEl}
        open={Boolean(menuAnchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={() => {
          const secret = secrets.find(s => s.id === menuSecretId);
          handleEditSecret(secret);
        }}>
          <ListItemIcon>
            <Edit fontSize="small" />
          </ListItemIcon>
          <ListItemText>Edit Secret</ListItemText>
        </MenuItem>
        
        <MenuItem onClick={() => handleDeleteSecret(menuSecretId)}>
          <ListItemIcon>
            <Delete fontSize="small" />
          </ListItemIcon>
          <ListItemText>Delete Secret</ListItemText>
        </MenuItem>
      </Menu>

      {/* Edit Secret Dialog */}
      <Dialog open={editDialogOpen} onClose={() => setEditDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          Edit Secret: {selectedSecret?.name}
        </DialogTitle>
        <DialogContent>
          <Alert severity="warning" sx={{ mb: 2 }}>
            This will update the secret value in Google Secret Manager. The change will take effect immediately.
          </Alert>
          
          <TextField
            fullWidth
            label="New Secret Value"
            type="password"
            value={newSecretValue}
            onChange={(e) => setNewSecretValue(e.target.value)}
            placeholder="Enter new secret value"
            sx={{ mt: 2 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleUpdateSecret} variant="contained">
            Update Secret
          </Button>
        </DialogActions>
      </Dialog>

      {/* Setup Wizard */}
      <SecretManagerWizard
        open={wizardOpen}
        onClose={() => setWizardOpen(false)}
        onComplete={() => {
          loadSecrets();
          checkConnectionStatus();
        }}
      />
    </Box>
  );
};

export default SecretManagerDashboard;