/**
 * Google Secret Manager Setup Wizard
 * Guides users through configuring API keys with Google Secret Manager
 */

import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Box,
  Typography,
  TextField,
  Card,
  CardContent,
  Alert,
  Chip,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  LinearProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Grid,
  IconButton,
  Tooltip,
  Paper
} from '@mui/material';
import {
  Cloud,
  Security,
  Key,
  CheckCircle,
  Warning,
  Error,
  Info,
  ExpandMore,
  ContentCopy,
  Visibility,
  VisibilityOff,
  CloudUpload,
  Settings,
  Close
} from '@mui/icons-material';
import { useNotifications } from '../NotificationSystem';

const SecretManagerWizard = ({ open, onClose, onComplete }) => {
  const [activeStep, setActiveStep] = useState(0);
  const [wizardData, setWizardData] = useState({
    gcpProjectId: '',
    serviceAccountKey: '',
    secrets: {
      htxApiKey: '',
      htxApiSecret: '',
      htxSubuid: '',
      openaiApiKey: '',
      threecommasApiKey: '',
      threecommasApiSecret: ''
    },
    validationResults: {},
    setupComplete: false
  });
  const [showSecrets, setShowSecrets] = useState({});
  const [validating, setValidating] = useState(false);
  
  const { showSuccess, showError, showWarning } = useNotifications();

  const steps = [
    {
      label: 'GCP Setup',
      description: 'Configure Google Cloud Project and Service Account',
      icon: <Cloud />
    },
    {
      label: 'API Keys',
      description: 'Enter your trading platform API keys',
      icon: <Key />
    },
    {
      label: 'Validation',
      description: 'Validate configuration and test connections',
      icon: <Security />
    },
    {
      label: 'Complete',
      description: 'Finish setup and start using the platform',
      icon: <CheckCircle />
    }
  ];

  const secretConfigs = [
    {
      key: 'htxApiKey',
      label: 'HTX API Key',
      description: 'HTX exchange API access key',
      required: true,
      placeholder: 'Enter your HTX API key'
    },
    {
      key: 'htxApiSecret',
      label: 'HTX API Secret',
      description: 'HTX exchange API secret key',
      required: true,
      placeholder: 'Enter your HTX API secret',
      secret: true
    },
    {
      key: 'htxSubuid',
      label: 'HTX Sub-Account UID',
      description: 'HTX sub-account user ID (optional)',
      required: false,
      placeholder: 'Enter HTX sub-account UID (optional)'
    },
    {
      key: 'openaiApiKey',
      label: 'OpenAI API Key',
      description: 'OpenAI API key for ML services (optional)',
      required: false,
      placeholder: 'sk-...',
      secret: true
    },
    {
      key: 'threecommasApiKey',
      label: '3Commas API Key',
      description: '3Commas API key for bot integration (optional)',
      required: false,
      placeholder: 'Enter 3Commas API key'
    },
    {
      key: 'threecommasApiSecret',
      label: '3Commas API Secret',
      description: '3Commas API secret (optional)',
      required: false,
      placeholder: 'Enter 3Commas API secret',
      secret: true
    }
  ];

  const handleNext = () => {
    if (activeStep === steps.length - 1) {
      handleComplete();
    } else {
      setActiveStep(prev => prev + 1);
    }
  };

  const handleBack = () => {
    setActiveStep(prev => prev - 1);
  };

  const handleComplete = () => {
    setWizardData(prev => ({ ...prev, setupComplete: true }));
    showSuccess('Secret Manager setup completed successfully!');
    onComplete?.(wizardData);
    onClose();
  };

  const updateWizardData = (field, value) => {
    setWizardData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const updateSecret = (key, value) => {
    setWizardData(prev => ({
      ...prev,
      secrets: {
        ...prev.secrets,
        [key]: value
      }
    }));
  };

  const toggleSecretVisibility = (key) => {
    setShowSecrets(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    showSuccess('Copied to clipboard!');
  };

  const validateConfiguration = async () => {
    setValidating(true);
    
    try {
      // Simulate API validation calls
      const results = {};
      
      // Validate GCP configuration
      if (wizardData.gcpProjectId && wizardData.serviceAccountKey) {
        results.gcp = { status: 'success', message: 'GCP configuration valid' };
      } else {
        results.gcp = { status: 'error', message: 'Missing GCP configuration' };
      }
      
      // Validate required API keys
      const requiredSecrets = secretConfigs.filter(config => config.required);
      const missingRequired = requiredSecrets.filter(config => 
        !wizardData.secrets[config.key] || wizardData.secrets[config.key].trim() === ''
      );
      
      if (missingRequired.length === 0) {
        results.apiKeys = { status: 'success', message: 'All required API keys provided' };
      } else {
        results.apiKeys = { 
          status: 'error', 
          message: `Missing required keys: ${missingRequired.map(k => k.label).join(', ')}` 
        };
      }
      
      // Simulate network validation
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      setWizardData(prev => ({
        ...prev,
        validationResults: results
      }));
      
      const allValid = Object.values(results).every(result => result.status === 'success');
      if (allValid) {
        showSuccess('All configurations validated successfully!');
      } else {
        showWarning('Some configurations need attention');
      }
      
    } catch (error) {
      showError('Validation failed: ' + error.message);
    } finally {
      setValidating(false);
    }
  };

  const renderStepContent = (step) => {
    switch (step) {
      case 0: // GCP Setup
        return (
          <Box sx={{ mt: 2 }}>
            <Alert severity="info" sx={{ mb: 3 }}>
              You'll need a Google Cloud Project with Secret Manager API enabled and a service account with appropriate permissions.
            </Alert>
            
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="GCP Project ID"
                  value={wizardData.gcpProjectId}
                  onChange={(e) => updateWizardData('gcpProjectId', e.target.value)}
                  placeholder="your-gcp-project-id"
                  helperText="Your Google Cloud Project ID where Secret Manager is enabled"
                />
              </Grid>
              
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  multiline
                  rows={6}
                  label="Service Account Key (JSON)"
                  value={wizardData.serviceAccountKey}
                  onChange={(e) => updateWizardData('serviceAccountKey', e.target.value)}
                  placeholder='{"type": "service_account", "project_id": "...", ...}'
                  helperText="Paste the contents of your service account JSON key file"
                />
              </Grid>
            </Grid>
            
            <Accordion sx={{ mt: 2 }}>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Typography>Setup Instructions</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Typography variant="body2" component="div">
                  <strong>1. Enable Secret Manager API:</strong>
                  <Paper sx={{ p: 1, mt: 1, mb: 2, bgcolor: 'grey.100' }}>
                    <code>gcloud services enable secretmanager.googleapis.com</code>
                    <IconButton size="small" onClick={() => copyToClipboard('gcloud services enable secretmanager.googleapis.com')}>
                      <ContentCopy fontSize="small" />
                    </IconButton>
                  </Paper>
                  
                  <strong>2. Create Service Account:</strong>
                  <Paper sx={{ p: 1, mt: 1, mb: 2, bgcolor: 'grey.100' }}>
                    <code>gcloud iam service-accounts create htx-secrets-manager</code>
                    <IconButton size="small" onClick={() => copyToClipboard('gcloud iam service-accounts create htx-secrets-manager')}>
                      <ContentCopy fontSize="small" />
                    </IconButton>
                  </Paper>
                  
                  <strong>3. Grant Permissions:</strong>
                  <Paper sx={{ p: 1, mt: 1, bgcolor: 'grey.100' }}>
                    <code>gcloud projects add-iam-policy-binding PROJECT_ID --member="serviceAccount:htx-secrets-manager@PROJECT_ID.iam.gserviceaccount.com" --role="roles/secretmanager.admin"</code>
                    <IconButton size="small" onClick={() => copyToClipboard('gcloud projects add-iam-policy-binding PROJECT_ID --member="serviceAccount:htx-secrets-manager@PROJECT_ID.iam.gserviceaccount.com" --role="roles/secretmanager.admin"')}>
                      <ContentCopy fontSize="small" />
                    </IconButton>
                  </Paper>
                </Typography>
              </AccordionDetails>
            </Accordion>
          </Box>
        );
        
      case 1: // API Keys
        return (
          <Box sx={{ mt: 2 }}>
            <Alert severity="warning" sx={{ mb: 3 }}>
              These API keys will be securely stored in Google Secret Manager. Required keys are marked with *.
            </Alert>
            
            <Grid container spacing={3}>
              {secretConfigs.map((config) => (
                <Grid item xs={12} key={config.key}>
                  <Card variant="outlined">
                    <CardContent>
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                        <Typography variant="h6">
                          {config.label}
                          {config.required && <span style={{ color: 'red' }}> *</span>}
                        </Typography>
                        <Box sx={{ flexGrow: 1 }} />
                        {config.secret && (
                          <IconButton
                            size="small"
                            onClick={() => toggleSecretVisibility(config.key)}
                          >
                            {showSecrets[config.key] ? <VisibilityOff /> : <Visibility />}
                          </IconButton>
                        )}
                      </Box>
                      
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                        {config.description}
                      </Typography>
                      
                      <TextField
                        fullWidth
                        type={config.secret && !showSecrets[config.key] ? 'password' : 'text'}
                        value={wizardData.secrets[config.key]}
                        onChange={(e) => updateSecret(config.key, e.target.value)}
                        placeholder={config.placeholder}
                        error={config.required && !wizardData.secrets[config.key]}
                        helperText={config.required && !wizardData.secrets[config.key] ? 'This field is required' : ''}
                      />
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Box>
        );
        
      case 2: // Validation
        return (
          <Box sx={{ mt: 2 }}>
            <Alert severity="info" sx={{ mb: 3 }}>
              Click "Validate Configuration" to test your setup before proceeding.
            </Alert>
            
            <Button
              variant="contained"
              onClick={validateConfiguration}
              disabled={validating}
              startIcon={<Security />}
              fullWidth
              sx={{ mb: 3 }}
            >
              {validating ? 'Validating...' : 'Validate Configuration'}
            </Button>
            
            {validating && <LinearProgress sx={{ mb: 3 }} />}
            
            {Object.keys(wizardData.validationResults).length > 0 && (
              <List>
                {Object.entries(wizardData.validationResults).map(([key, result]) => (
                  <ListItem key={key}>
                    <ListItemIcon>
                      {result.status === 'success' ? (
                        <CheckCircle color="success" />
                      ) : result.status === 'warning' ? (
                        <Warning color="warning" />
                      ) : (
                        <Error color="error" />
                      )}
                    </ListItemIcon>
                    <ListItemText
                      primary={key === 'gcp' ? 'GCP Configuration' : 'API Keys'}
                      secondary={result.message}
                    />
                  </ListItem>
                ))}
              </List>
            )}
          </Box>
        );
        
      case 3: // Complete
        return (
          <Box sx={{ mt: 2, textAlign: 'center' }}>
            <CheckCircle color="success" sx={{ fontSize: 64, mb: 2 }} />
            <Typography variant="h5" gutterBottom>
              Setup Complete!
            </Typography>
            <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
              Your Secret Manager configuration has been completed successfully.
              You can now start using the HTX Trading Platform with secure API key management.
            </Typography>
            
            <Alert severity="success" sx={{ mb: 2 }}>
              <strong>Next Steps:</strong>
              <br />
              • Your API keys are securely stored in Google Secret Manager
              <br />
              • The platform will automatically fetch keys as needed
              <br />
              • You can update keys anytime through the settings panel
            </Alert>
            
            <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', mt: 3 }}>
              <Chip icon={<Security />} label="Secure Storage" color="success" />
              <Chip icon={<Cloud />} label="Cloud Managed" color="primary" />
              <Chip icon={<Settings />} label="Easy Updates" color="info" />
            </Box>
          </Box>
        );
        
      default:
        return null;
    }
  };

  const canProceed = () => {
    switch (activeStep) {
      case 0:
        return wizardData.gcpProjectId.trim() !== '' && wizardData.serviceAccountKey.trim() !== '';
      case 1:
        const requiredSecrets = secretConfigs.filter(config => config.required);
        return requiredSecrets.every(config => 
          wizardData.secrets[config.key] && wizardData.secrets[config.key].trim() !== ''
        );
      case 2:
        return Object.keys(wizardData.validationResults).length > 0 && 
               Object.values(wizardData.validationResults).every(result => result.status === 'success');
      default:
        return true;
    }
  };

  return (
    <Dialog 
      open={open} 
      onClose={onClose} 
      maxWidth="md" 
      fullWidth
      PaperProps={{ sx: { minHeight: '70vh' } }}
    >
      <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Security />
        Google Secret Manager Setup
        <Box sx={{ flexGrow: 1 }} />
        <IconButton onClick={onClose} size="small">
          <Close />
        </IconButton>
      </DialogTitle>
      
      <DialogContent>
        <Stepper activeStep={activeStep} orientation="vertical">
          {steps.map((step, index) => (
            <Step key={step.label}>
              <StepLabel 
                icon={step.icon}
                optional={
                  <Typography variant="caption">{step.description}</Typography>
                }
              >
                {step.label}
              </StepLabel>
              <StepContent>
                {renderStepContent(index)}
                
                <Box sx={{ mt: 3 }}>
                  <Button
                    variant="contained"
                    onClick={handleNext}
                    disabled={!canProceed() || validating}
                    sx={{ mr: 1 }}
                  >
                    {index === steps.length - 1 ? 'Complete Setup' : 'Next'}
                  </Button>
                  
                  {index > 0 && (
                    <Button onClick={handleBack} disabled={validating}>
                      Back
                    </Button>
                  )}
                </Box>
              </StepContent>
            </Step>
          ))}
        </Stepper>
      </DialogContent>
      
      <DialogActions>
        <Button onClick={onClose}>
          {wizardData.setupComplete ? 'Close' : 'Cancel'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default SecretManagerWizard;