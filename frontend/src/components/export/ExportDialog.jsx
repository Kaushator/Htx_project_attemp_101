/**
 * Export Dialog Component
 * Provides user-friendly interface for data export with format options
 */

import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  FormControl,
  FormControlLabel,
  FormGroup,
  Checkbox,
  Radio,
  RadioGroup,
  FormLabel,
  TextField,
  Grid,
  Box,
  Typography,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Chip,
  Alert,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Switch
} from '@mui/material';
import {
  GetApp,
  ExpandMore,
  Description,
  PictureAsPdf,
  TableChart,
  Code,
  Settings,
  Info,
  CheckCircle
} from '@mui/icons-material';
import { useNotifications } from '../NotificationSystem';
import exportUtils from '../../utils/exportUtils';

const ExportDialog = ({ 
  open, 
  onClose, 
  data = [], 
  title = 'Export Data',
  defaultFilename = 'export'
}) => {
  const [exportOptions, setExportOptions] = useState({
    format: 'csv', // 'csv', 'pdf', 'json'
    filename: defaultFilename,
    
    // CSV options
    includeHeaders: true,
    delimiter: ',',
    
    // PDF options
    orientation: 'landscape',
    pageSize: 'a4',
    includeTimestamp: true,
    includeStats: false,
    
    // Data processing options
    excludeFields: [],
    flattenObjects: true,
    formatNumbers: true,
    formatDates: true,
    removeNulls: false,
    
    // Field mapping
    fieldMapping: {}
  });
  
  const [exporting, setExporting] = useState(false);
  const [exportStats, setExportStats] = useState(null);
  const [availableFields, setAvailableFields] = useState([]);
  
  const { showSuccess, showError } = useNotifications();
  
  // Calculate export statistics when data changes
  useEffect(() => {
    if (data && data.length > 0) {
      const stats = exportUtils.utils.getExportStats(data);
      setExportStats(stats);
      setAvailableFields(stats.fields);
    }
  }, [data]);
  
  const handleFormatChange = (event) => {
    setExportOptions(prev => ({
      ...prev,
      format: event.target.value
    }));
  };
  
  const handleOptionChange = (key, value) => {
    setExportOptions(prev => ({
      ...prev,
      [key]: value
    }));
  };
  
  const handleFieldExclusion = (field, excluded) => {
    setExportOptions(prev => ({
      ...prev,
      excludeFields: excluded 
        ? [...prev.excludeFields, field]
        : prev.excludeFields.filter(f => f !== field)
    }));
  };
  
  const handleFieldMapping = (field, mappedName) => {
    setExportOptions(prev => ({
      ...prev,
      fieldMapping: {
        ...prev.fieldMapping,
        [field]: mappedName
      }
    }));
  };
  
  const handleExport = async () => {
    if (!data || data.length === 0) {
      showError('No data available to export');
      return;
    }
    
    setExporting(true);
    
    try {
      const filename = exportOptions.filename || exportUtils.utils.generateFilename('export');
      
      // Prepare data with options
      const preparedData = exportUtils.utils.prepareDataForExport(data, {
        flattenObjects: exportOptions.flattenObjects,
        formatNumbers: exportOptions.formatNumbers,
        formatDates: exportOptions.formatDates,
        removeNulls: exportOptions.removeNulls
      });
      
      switch (exportOptions.format) {
        case 'csv':
          exportUtils.csv.downloadCSV(preparedData, `${filename}.csv`, {
            includeHeaders: exportOptions.includeHeaders,
            delimiter: exportOptions.delimiter,
            excludeFields: exportOptions.excludeFields,
            fieldMapping: exportOptions.fieldMapping
          });
          break;
          
        case 'pdf':
          const pdfOptions = {
            title: title,
            subtitle: `${data.length} records exported`,
            orientation: exportOptions.orientation,
            pageSize: exportOptions.pageSize,
            includeTimestamp: exportOptions.includeTimestamp,
            excludeFields: exportOptions.excludeFields,
            fieldMapping: exportOptions.fieldMapping
          };
          
          // Add statistics if requested
          if (exportOptions.includeStats && exportStats) {
            const stats = {
              'Total Records': exportStats.totalRecords,
              'Total Fields': exportStats.fields.length,
              'Export Date': new Date().toLocaleString(),
              'File Size (est.)': exportStats.estimatedFileSize
            };
            
            await exportUtils.pdf.createAdvancedPDF(
              preparedData, 
              [], 
              stats, 
              pdfOptions
            ).then(doc => doc.save(`${filename}.pdf`));
          } else {
            await exportUtils.pdf.downloadPDF(preparedData, `${filename}.pdf`, pdfOptions);
          }
          break;
          
        case 'json':
          const jsonStr = JSON.stringify(preparedData, null, 2);
          const blob = new Blob([jsonStr], { type: 'application/json' });
          const link = document.createElement('a');
          link.href = URL.createObjectURL(blob);
          link.download = `${filename}.json`;
          link.click();
          URL.revokeObjectURL(link.href);
          break;
          
        default:
          throw new Error('Unsupported export format');
      }
      
      showSuccess(`Data exported successfully as ${exportOptions.format.toUpperCase()}`);
      onClose();
      
    } catch (error) {
      console.error('Export failed:', error);
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
      default: return <Description />;
    }
  };
  
  return (
    <Dialog 
      open={open} 
      onClose={onClose} 
      maxWidth=\"md\" 
      fullWidth
      PaperProps={{ sx: { minHeight: '60vh' } }}
    >
      <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <GetApp />
        {title}
      </DialogTitle>
      
      <DialogContent>
        {exporting && (
          <Box sx={{ mb: 2 }}>
            <LinearProgress />
            <Typography variant=\"body2\" color=\"text.secondary\" sx={{ mt: 1 }}>
              Exporting data...
            </Typography>
          </Box>
        )}
        
        {/* Export Statistics */}
        {exportStats && (
          <Alert severity=\"info\" sx={{ mb: 3 }}>
            <Typography variant=\"body2\">
              Ready to export <strong>{exportStats.totalRecords} records</strong> with{' '}
              <strong>{exportStats.fields.length} fields</strong>. 
              Estimated file size: <strong>{exportStats.estimatedFileSize}</strong>
            </Typography>
          </Alert>
        )}
        
        <Grid container spacing={3}>
          {/* Format Selection */}
          <Grid item xs={12}>
            <FormControl component=\"fieldset\">
              <FormLabel component=\"legend\" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Settings />
                Export Format
              </FormLabel>
              <RadioGroup
                value={exportOptions.format}
                onChange={handleFormatChange}
                row
                sx={{ mt: 1 }}
              >
                <FormControlLabel 
                  value=\"csv\" 
                  control={<Radio />} 
                  label={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <TableChart /> CSV
                    </Box>
                  } 
                />
                <FormControlLabel 
                  value=\"pdf\" 
                  control={<Radio />} 
                  label={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <PictureAsPdf /> PDF
                    </Box>
                  } 
                />
                <FormControlLabel 
                  value=\"json\" 
                  control={<Radio />} 
                  label={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Code /> JSON
                    </Box>
                  } 
                />
              </RadioGroup>
            </FormControl>
          </Grid>
          
          {/* Filename */}
          <Grid item xs={12}>
            <TextField
              fullWidth
              label=\"Filename\"
              value={exportOptions.filename}
              onChange={(e) => handleOptionChange('filename', e.target.value)}
              helperText={`File will be saved as: ${exportOptions.filename}.${exportOptions.format}`}
            />
          </Grid>
          
          {/* Format-specific options */}
          <Grid item xs={12}>
            <Accordion>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Typography>Format Options</Typography>
              </AccordionSummary>
              <AccordionDetails>
                {exportOptions.format === 'csv' && (
                  <Grid container spacing={2}>
                    <Grid item xs={12}>
                      <FormControlLabel
                        control={
                          <Switch
                            checked={exportOptions.includeHeaders}
                            onChange={(e) => handleOptionChange('includeHeaders', e.target.checked)}
                          />
                        }
                        label=\"Include Headers\"
                      />
                    </Grid>
                    <Grid item xs={6}>
                      <TextField
                        fullWidth
                        label=\"Delimiter\"
                        value={exportOptions.delimiter}
                        onChange={(e) => handleOptionChange('delimiter', e.target.value)}
                      />
                    </Grid>
                  </Grid>
                )}
                
                {exportOptions.format === 'pdf' && (
                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <FormControl fullWidth>
                        <FormLabel>Page Orientation</FormLabel>
                        <RadioGroup
                          value={exportOptions.orientation}
                          onChange={(e) => handleOptionChange('orientation', e.target.value)}
                        >
                          <FormControlLabel value=\"landscape\" control={<Radio />} label=\"Landscape\" />
                          <FormControlLabel value=\"portrait\" control={<Radio />} label=\"Portrait\" />
                        </RadioGroup>
                      </FormControl>
                    </Grid>
                    <Grid item xs={6}>
                      <FormControl fullWidth>
                        <FormLabel>Page Size</FormLabel>
                        <RadioGroup
                          value={exportOptions.pageSize}
                          onChange={(e) => handleOptionChange('pageSize', e.target.value)}
                        >
                          <FormControlLabel value=\"a4\" control={<Radio />} label=\"A4\" />
                          <FormControlLabel value=\"letter\" control={<Radio />} label=\"Letter\" />
                          <FormControlLabel value=\"legal\" control={<Radio />} label=\"Legal\" />
                        </RadioGroup>
                      </FormControl>
                    </Grid>
                    <Grid item xs={12}>
                      <FormGroup>
                        <FormControlLabel
                          control={
                            <Checkbox
                              checked={exportOptions.includeTimestamp}
                              onChange={(e) => handleOptionChange('includeTimestamp', e.target.checked)}
                            />
                          }
                          label=\"Include Timestamp\"
                        />
                        <FormControlLabel
                          control={
                            <Checkbox
                              checked={exportOptions.includeStats}
                              onChange={(e) => handleOptionChange('includeStats', e.target.checked)}
                            />
                          }
                          label=\"Include Statistics Page\"
                        />
                      </FormGroup>
                    </Grid>
                  </Grid>
                )}
              </AccordionDetails>
            </Accordion>
          </Grid>
          
          {/* Data Processing Options */}
          <Grid item xs={12}>
            <Accordion>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Typography>Data Processing Options</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <FormGroup>
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={exportOptions.flattenObjects}
                        onChange={(e) => handleOptionChange('flattenObjects', e.target.checked)}
                      />
                    }
                    label=\"Flatten Nested Objects\"
                  />
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={exportOptions.formatNumbers}
                        onChange={(e) => handleOptionChange('formatNumbers', e.target.checked)}
                      />
                    }
                    label=\"Format Numbers\"
                  />
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={exportOptions.formatDates}
                        onChange={(e) => handleOptionChange('formatDates', e.target.checked)}
                      />
                    }
                    label=\"Format Dates\"
                  />
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={exportOptions.removeNulls}
                        onChange={(e) => handleOptionChange('removeNulls', e.target.checked)}
                      />
                    }
                    label=\"Remove Null Values\"
                  />
                </FormGroup>
              </AccordionDetails>
            </Accordion>
          </Grid>
          
          {/* Field Selection */}
          {availableFields.length > 0 && (
            <Grid item xs={12}>
              <Accordion>
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Typography>
                    Field Selection 
                    <Chip 
                      label={`${availableFields.length - exportOptions.excludeFields.length} selected`} 
                      size=\"small\" 
                      sx={{ ml: 1 }} 
                    />
                  </Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <List dense>
                    {availableFields.map(field => (
                      <ListItem key={field}>
                        <ListItemIcon>
                          <Checkbox
                            checked={!exportOptions.excludeFields.includes(field)}
                            onChange={(e) => handleFieldExclusion(field, !e.target.checked)}
                          />
                        </ListItemIcon>
                        <ListItemText 
                          primary={field}
                          secondary={
                            <TextField
                              size=\"small\"
                              placeholder={`Rename \"${field}\"...`}
                              value={exportOptions.fieldMapping[field] || ''}
                              onChange={(e) => handleFieldMapping(field, e.target.value)}
                              sx={{ mt: 0.5 }}
                            />
                          }
                        />
                      </ListItem>
                    ))}
                  </List>
                </AccordionDetails>
              </Accordion>
            </Grid>
          )}
        </Grid>
      </DialogContent>
      
      <DialogActions>
        <Button onClick={onClose} disabled={exporting}>
          Cancel
        </Button>
        <Button 
          onClick={handleExport} 
          variant=\"contained\" 
          disabled={exporting || !data || data.length === 0}
          startIcon={getFormatIcon(exportOptions.format)}
        >
          Export {exportOptions.format.toUpperCase()}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default ExportDialog;