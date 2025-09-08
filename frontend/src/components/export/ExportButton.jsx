/**
 * Export Button Component
 * Easy-to-use export button that can be integrated into any page
 */

import React, { useState } from 'react';
import {
  Button,
  IconButton,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Tooltip,
  Fab,
  SpeedDial,
  SpeedDialAction,
  SpeedDialIcon
} from '@mui/material';
import {
  GetApp,
  TableChart,
  PictureAsPdf,
  Code,
  MoreVert,
  Settings
} from '@mui/icons-material';
import ExportDialog from './ExportDialog';
import exportUtils from '../../utils/exportUtils';
import { useNotifications } from '../NotificationSystem';

// Quick Export Button - exports immediately without dialog
const QuickExportButton = ({ 
  data, 
  format = 'csv', 
  filename, 
  variant = 'outlined',
  size = 'medium',
  ...props 
}) => {
  const [exporting, setExporting] = useState(false);
  const { showSuccess, showError } = useNotifications();
  
  const handleQuickExport = async () => {
    if (!data || data.length === 0) {
      showError('No data available to export');
      return;
    }
    
    setExporting(true);
    
    try {
      const exportFilename = filename || exportUtils.utils.generateFilename('export', format);
      const preparedData = exportUtils.utils.prepareDataForExport(data);
      
      switch (format) {
        case 'csv':
          exportUtils.csv.downloadCSV(preparedData, exportFilename);
          break;
        case 'pdf':
          await exportUtils.pdf.downloadPDF(preparedData, exportFilename);
          break;
        case 'json':
          const jsonStr = JSON.stringify(preparedData, null, 2);
          const blob = new Blob([jsonStr], { type: 'application/json' });
          const link = document.createElement('a');
          link.href = URL.createObjectURL(blob);
          link.download = exportFilename;
          link.click();
          URL.revokeObjectURL(link.href);
          break;
        default:
          throw new Error('Unsupported format');
      }
      
      showSuccess(`Data exported as ${format.toUpperCase()}`);
    } catch (error) {
      showError(`Export failed: ${error.message}`);
    } finally {
      setExporting(false);
    }
  };
  
  const getIcon = () => {
    switch (format) {
      case 'csv': return <TableChart />;
      case 'pdf': return <PictureAsPdf />;
      case 'json': return <Code />;
      default: return <GetApp />;
    }
  };
  
  return (
    <Button
      variant={variant}
      size={size}
      startIcon={getIcon()}
      onClick={handleQuickExport}
      disabled={exporting || !data || data.length === 0}
      {...props}
    >
      Export {format.toUpperCase()}
    </Button>
  );
};

// Multi-Format Export Button with dropdown
const MultiExportButton = ({ 
  data, 
  filename, 
  formats = ['csv', 'pdf', 'json'],
  variant = 'outlined',
  size = 'medium',
  ...props 
}) => {
  const [anchorEl, setAnchorEl] = useState(null);
  const [exporting, setExporting] = useState(false);
  const { showSuccess, showError } = useNotifications();
  
  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
  };
  
  const handleClose = () => {
    setAnchorEl(null);
  };
  
  const handleExport = async (format) => {
    handleClose();
    
    if (!data || data.length === 0) {
      showError('No data available to export');
      return;
    }
    
    setExporting(true);
    
    try {
      const exportFilename = filename || exportUtils.utils.generateFilename('export', format);
      const preparedData = exportUtils.utils.prepareDataForExport(data);
      
      switch (format) {
        case 'csv':
          exportUtils.csv.downloadCSV(preparedData, exportFilename);
          break;
        case 'pdf':
          await exportUtils.pdf.downloadPDF(preparedData, exportFilename);
          break;
        case 'json':
          const jsonStr = JSON.stringify(preparedData, null, 2);
          const blob = new Blob([jsonStr], { type: 'application/json' });
          const link = document.createElement('a');
          link.href = URL.createObjectURL(blob);
          link.download = exportFilename;
          link.click();
          URL.revokeObjectURL(link.href);
          break;
        default:
          throw new Error('Unsupported format');
      }
      
      showSuccess(`Data exported as ${format.toUpperCase()}`);
    } catch (error) {
      showError(`Export failed: ${error.message}`);
    } finally {
      setExporting(false);
    }
  };
  
  const getFormatIcon = (format) => {
    switch (format) {
      case 'csv': return <TableChart />;
      case 'pdf': return <PictureAsPdf />;
      case 'json': return <Code />;
      default: return <GetApp />;
    }
  };
  
  return (
    <>
      <Button
        variant={variant}
        size={size}
        startIcon={<GetApp />}
        endIcon={<MoreVert />}
        onClick={handleClick}
        disabled={exporting || !data || data.length === 0}
        {...props}
      >
        Export
      </Button>
      
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleClose}
      >
        {formats.map(format => (
          <MenuItem key={format} onClick={() => handleExport(format)}>
            <ListItemIcon>
              {getFormatIcon(format)}
            </ListItemIcon>
            <ListItemText primary={`Export as ${format.toUpperCase()}`} />
          </MenuItem>
        ))}
      </Menu>
    </>
  );
};

// Advanced Export Button with dialog
const AdvancedExportButton = ({ 
  data, 
  title = 'Export Data',
  filename,
  variant = 'outlined',
  size = 'medium',
  ...props 
}) => {
  const [dialogOpen, setDialogOpen] = useState(false);
  
  return (
    <>
      <Button
        variant={variant}
        size={size}
        startIcon={<Settings />}
        onClick={() => setDialogOpen(true)}
        disabled={!data || data.length === 0}
        {...props}
      >
        Advanced Export
      </Button>
      
      <ExportDialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        data={data}
        title={title}
        defaultFilename={filename}
      />
    </>
  );
};

// Speed Dial Export (Floating Action Button)
const SpeedDialExport = ({ 
  data, 
  formats = ['csv', 'pdf', 'json'],
  position = { bottom: 16, right: 16 },
  ...props 
}) => {
  const [open, setOpen] = useState(false);
  const [exporting, setExporting] = useState(false);
  const { showSuccess, showError } = useNotifications();
  
  const handleExport = async (format) => {
    if (!data || data.length === 0) {
      showError('No data available to export');
      return;
    }
    
    setExporting(true);
    setOpen(false);
    
    try {
      const exportFilename = exportUtils.utils.generateFilename('export', format);
      const preparedData = exportUtils.utils.prepareDataForExport(data);
      
      switch (format) {
        case 'csv':
          exportUtils.csv.downloadCSV(preparedData, exportFilename);
          break;
        case 'pdf':
          await exportUtils.pdf.downloadPDF(preparedData, exportFilename);
          break;
        case 'json':
          const jsonStr = JSON.stringify(preparedData, null, 2);
          const blob = new Blob([jsonStr], { type: 'application/json' });
          const link = document.createElement('a');
          link.href = URL.createObjectURL(blob);
          link.download = exportFilename;
          link.click();
          URL.revokeObjectURL(link.href);
          break;
        default:
          throw new Error('Unsupported format');
      }
      
      showSuccess(`Data exported as ${format.toUpperCase()}`);
    } catch (error) {
      showError(`Export failed: ${error.message}`);
    } finally {
      setExporting(false);
    }
  };
  
  const getFormatIcon = (format) => {
    switch (format) {
      case 'csv': return <TableChart />;
      case 'pdf': return <PictureAsPdf />;
      case 'json': return <Code />;
      default: return <GetApp />;
    }
  };
  
  return (
    <SpeedDial
      ariaLabel=\"Export Data\"
      sx={{ position: 'fixed', ...position }}
      icon={<SpeedDialIcon />}
      onClose={() => setOpen(false)}
      onOpen={() => setOpen(true)}
      open={open}
      disabled={exporting || !data || data.length === 0}
      {...props}
    >
      {formats.map(format => (
        <SpeedDialAction
          key={format}
          icon={getFormatIcon(format)}
          tooltipTitle={`Export ${format.toUpperCase()}`}
          onClick={() => handleExport(format)}
        />
      ))}
    </SpeedDial>
  );
};

// Main Export Button Component with different modes
const ExportButton = ({ 
  mode = 'quick', // 'quick', 'multi', 'advanced', 'speedDial'
  ...props 
}) => {
  switch (mode) {
    case 'multi':
      return <MultiExportButton {...props} />;
    case 'advanced':
      return <AdvancedExportButton {...props} />;
    case 'speedDial':
      return <SpeedDialExport {...props} />;
    default:
      return <QuickExportButton {...props} />;
  }
};

// Export all components
export {
  QuickExportButton,
  MultiExportButton,
  AdvancedExportButton,
  SpeedDialExport,
  ExportDialog
};

export default ExportButton;