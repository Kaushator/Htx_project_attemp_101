/**
 * Export Utilities for CSV and PDF Export
 * Comprehensive data export functionality with formatting and customization
 */

// CSV Export Utilities
export const csvUtils = {
  // Convert array of objects to CSV string
  arrayToCSV: (data, options = {}) => {
    if (!data || data.length === 0) return '';
    
    const {
      includeHeaders = true,
      delimiter = ',',
      excludeFields = [],
      fieldMapping = {},
      dateFormat = 'YYYY-MM-DD HH:mm:ss',
      numberFormat = (num) => num
    } = options;
    
    // Get all unique keys from all objects
    const allKeys = [...new Set(data.flatMap(Object.keys))]
      .filter(key => !excludeFields.includes(key));
    
    // Apply field mapping
    const headers = allKeys.map(key => fieldMapping[key] || key);
    
    // Helper function to escape CSV values
    const escapeCSV = (value) => {
      if (value === null || value === undefined) return '';
      
      // Convert to string
      let str = String(value);
      
      // Format dates
      if (value instanceof Date) {
        str = value.toISOString().replace('T', ' ').substring(0, 19);
      }
      
      // Format numbers
      if (typeof value === 'number') {
        str = numberFormat(value).toString();
      }
      
      // Escape quotes and wrap in quotes if contains delimiter or quotes
      if (str.includes(delimiter) || str.includes('\"') || str.includes('\n')) {
        str = '\"' + str.replace(/\"/g, '\"\"') + '\"';
      }
      
      return str;
    };
    
    const rows = [];
    
    // Add headers if requested
    if (includeHeaders) {
      rows.push(headers.join(delimiter));
    }
    
    // Add data rows
    data.forEach(item => {
      const row = allKeys.map(key => escapeCSV(item[key]));
      rows.push(row.join(delimiter));
    });
    
    return rows.join('\n');
  },
  
  // Download CSV file
  downloadCSV: (data, filename, options = {}) => {
    const csv = csvUtils.arrayToCSV(data, options);
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    
    if (link.download !== undefined) {
      const url = URL.createObjectURL(blob);
      link.setAttribute('href', url);
      link.setAttribute('download', filename);
      link.style.visibility = 'hidden';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    }
  }
};

// PDF Export Utilities (using jsPDF)
export const pdfUtils = {
  // Create PDF document with data table
  createPDF: async (data, options = {}) => {
    // Dynamic import to avoid bundle size issues
    const { jsPDF } = await import('jspdf');
    await import('jspdf-autotable');
    
    const {
      title = 'Data Export',
      subtitle = '',
      orientation = 'landscape',
      pageSize = 'a4',
      fontSize = 10,
      includeTimestamp = true,
      tableOptions = {},
      headerStyle = {},
      bodyStyle = {},
      excludeFields = [],
      fieldMapping = {},
      numberFormat = (num) => num.toLocaleString(),
      dateFormat = (date) => new Date(date).toLocaleDateString()
    } = options;
    
    const doc = new jsPDF({
      orientation,
      unit: 'mm',
      format: pageSize
    });
    
    // Set font
    doc.setFontSize(16);
    doc.text(title, 14, 22);
    
    if (subtitle) {
      doc.setFontSize(12);
      doc.text(subtitle, 14, 32);
    }
    
    if (includeTimestamp) {
      doc.setFontSize(8);
      const timestamp = `Generated on: ${new Date().toLocaleString()}`;
      doc.text(timestamp, 14, includeTimestamp ? (subtitle ? 42 : 32) : 0);
    }
    
    if (data && data.length > 0) {
      // Prepare table data
      const allKeys = [...new Set(data.flatMap(Object.keys))]
        .filter(key => !excludeFields.includes(key));
      
      const headers = allKeys.map(key => fieldMapping[key] || key);
      
      const rows = data.map(item => 
        allKeys.map(key => {
          let value = item[key];
          
          if (value === null || value === undefined) return '';
          
          // Format dates
          if (value instanceof Date || (typeof value === 'string' && !isNaN(Date.parse(value)))) {
            return dateFormat(value);
          }
          
          // Format numbers
          if (typeof value === 'number') {
            return numberFormat(value);
          }
          
          return String(value);
        })
      );
      
      // Add table
      doc.autoTable({
        head: [headers],
        body: rows,
        startY: includeTimestamp ? (subtitle ? 52 : 42) : (subtitle ? 42 : 32),
        styles: {
          fontSize: fontSize,
          cellPadding: 2,
          ...bodyStyle
        },
        headStyles: {
          fillColor: [71, 85, 119],
          textColor: 255,
          fontStyle: 'bold',
          ...headerStyle
        },
        alternateRowStyles: {
          fillColor: [245, 245, 245]
        },
        margin: { top: 10, right: 14, bottom: 10, left: 14 },
        ...tableOptions
      });
    }
    
    return doc;
  },
  
  // Download PDF file
  downloadPDF: async (data, filename, options = {}) => {
    const doc = await pdfUtils.createPDF(data, options);
    doc.save(filename);
  },
  
  // Create advanced PDF with charts and statistics
  createAdvancedPDF: async (data, charts = [], stats = {}, options = {}) => {
    const doc = await pdfUtils.createPDF(data, {
      ...options,
      title: options.title || 'Advanced Trading Report'
    });
    
    // Add statistics section if provided
    if (Object.keys(stats).length > 0) {
      doc.addPage();
      doc.setFontSize(14);
      doc.text('Statistics Summary', 14, 22);
      
      let yPosition = 35;
      Object.entries(stats).forEach(([key, value]) => {
        doc.setFontSize(10);
        doc.text(`${key}: ${value}`, 14, yPosition);
        yPosition += 7;
      });
    }
    
    // Add charts if provided (would need chart image data)
    charts.forEach((chart, index) => {
      if (chart.imageData) {
        doc.addPage();
        doc.setFontSize(14);
        doc.text(chart.title || `Chart ${index + 1}`, 14, 22);
        doc.addImage(chart.imageData, 'PNG', 14, 30, 180, 100);
      }
    });
    
    return doc;
  }
};

// General Export Utilities
export const exportUtils = {
  // Prepare data for export with common transformations
  prepareDataForExport: (data, options = {}) => {
    const {
      flattenObjects = true,
      formatNumbers = true,
      formatDates = true,
      removeNulls = false,
      customTransforms = {}
    } = options;
    
    return data.map(item => {
      let transformed = { ...item };
      
      // Apply custom transforms
      Object.entries(customTransforms).forEach(([field, transformer]) => {
        if (transformed[field] !== undefined) {
          transformed[field] = transformer(transformed[field]);
        }
      });
      
      // Flatten nested objects
      if (flattenObjects) {
        const flattened = {};
        
        const flatten = (obj, prefix = '') => {
          Object.entries(obj).forEach(([key, value]) => {
            const newKey = prefix ? `${prefix}.${key}` : key;
            
            if (value && typeof value === 'object' && !Array.isArray(value) && !(value instanceof Date)) {
              flatten(value, newKey);
            } else {
              flattened[newKey] = value;
            }
          });
        };
        
        flatten(transformed);
        transformed = flattened;
      }
      
      // Format numbers
      if (formatNumbers) {
        Object.entries(transformed).forEach(([key, value]) => {
          if (typeof value === 'number') {
            if (key.toLowerCase().includes('price') || key.toLowerCase().includes('amount')) {
              transformed[key] = Number(value.toFixed(4));
            } else if (key.toLowerCase().includes('percentage') || key.toLowerCase().includes('change')) {
              transformed[key] = Number(value.toFixed(2));
            }
          }
        });
      }
      
      // Format dates
      if (formatDates) {
        Object.entries(transformed).forEach(([key, value]) => {
          if (value instanceof Date) {
            transformed[key] = value.toISOString();
          } else if (typeof value === 'string' && !isNaN(Date.parse(value)) && value.match(/\\d{4}-\\d{2}-\\d{2}/)) {
            transformed[key] = new Date(value).toISOString();
          }
        });
      }
      
      // Remove null/undefined values
      if (removeNulls) {
        Object.entries(transformed).forEach(([key, value]) => {
          if (value === null || value === undefined) {
            delete transformed[key];
          }
        });
      }
      
      return transformed;
    });
  },
  
  // Generate filename with timestamp
  generateFilename: (prefix = 'export', extension = 'csv') => {
    const timestamp = new Date().toISOString()
      .replace(/[:.]/g, '-')
      .substring(0, 19);
    return `${prefix}_${timestamp}.${extension}`;
  },
  
  // Export data in multiple formats
  exportMultipleFormats: async (data, baseFilename, options = {}) => {
    const preparedData = exportUtils.prepareDataForExport(data, options.dataPrep);
    const results = {};
    
    // CSV Export
    if (options.csv !== false) {
      const csvFilename = `${baseFilename}.csv`;
      csvUtils.downloadCSV(preparedData, csvFilename, options.csv);
      results.csv = csvFilename;
    }
    
    // PDF Export
    if (options.pdf !== false) {
      const pdfFilename = `${baseFilename}.pdf`;
      await pdfUtils.downloadPDF(preparedData, pdfFilename, options.pdf);
      results.pdf = pdfFilename;
    }
    
    // JSON Export
    if (options.json) {
      const jsonFilename = `${baseFilename}.json`;
      const jsonStr = JSON.stringify(preparedData, null, 2);
      const blob = new Blob([jsonStr], { type: 'application/json' });
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = jsonFilename;
      link.click();
      URL.revokeObjectURL(link.href);
      results.json = jsonFilename;
    }
    
    return results;
  },
  
  // Get export statistics
  getExportStats: (data) => {
    if (!data || data.length === 0) {
      return {
        totalRecords: 0,
        fields: [],
        dataTypes: {},
        estimatedFileSize: '0 KB'
      };
    }
    
    const allKeys = [...new Set(data.flatMap(Object.keys))];
    const dataTypes = {};
    
    allKeys.forEach(key => {
      const values = data.map(item => item[key]).filter(v => v !== null && v !== undefined);
      if (values.length > 0) {
        const firstValue = values[0];
        if (typeof firstValue === 'number') {
          dataTypes[key] = 'number';
        } else if (firstValue instanceof Date) {
          dataTypes[key] = 'date';
        } else if (typeof firstValue === 'boolean') {
          dataTypes[key] = 'boolean';
        } else {
          dataTypes[key] = 'string';
        }
      }
    });
    
    // Estimate file size (rough calculation)
    const jsonSize = JSON.stringify(data).length;
    const estimatedCSVSize = jsonSize * 0.8; // CSV is usually smaller
    
    const formatSize = (bytes) => {
      if (bytes < 1024) return `${bytes} B`;
      if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
      return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
    };
    
    return {
      totalRecords: data.length,
      fields: allKeys,
      dataTypes,
      estimatedFileSize: formatSize(estimatedCSVSize)
    };
  }
};

// Default export for easy importing
export default {
  csv: csvUtils,
  pdf: pdfUtils,
  utils: exportUtils
};