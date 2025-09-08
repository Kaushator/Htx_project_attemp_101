import React, { useState, useCallback } from 'react';
import {
  Box, Typography, Button, CircularProgress, Alert,
  Card, CardContent, Paper, LinearProgress,
  List, ListItem, ListItemText, ListItemIcon,
  Chip, IconButton, Tooltip
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  InsertDriveFile as FileIcon,
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
  Refresh as RefreshIcon,
  Delete as DeleteIcon
} from '@mui/icons-material';
import { useDropzone } from 'react-dropzone';

const FileUpload = ({ onUpload }) => {
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [error, setError] = useState(null);
  const [message, setMessage] = useState(null);

  const onDrop = useCallback(async (acceptedFiles) => {
    const file = acceptedFiles[0];
    if (!file) return;

    // Validate file type
    const allowedTypes = [
      'text/csv',
      'application/vnd.ms-excel',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    ];
    
    if (!allowedTypes.includes(file.type) && !file.name.endsWith('.csv')) {
      setError('Поддерживаются только CSV и Excel файлы');
      return;
    }

    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      setError('Файл не должен превышать 10MB');
      return;
    }

    setUploading(true);
    setError(null);
    setMessage(null);
    setUploadProgress(0);

    try {
      const formData = new FormData();
      formData.append('file', file);

      // Simulate upload progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return prev;
          }
          return prev + 10;
        });
      }, 200);

      const response = await fetch('http://127.0.0.1:8000/api/v1/files/upload', {
        method: 'POST',
        body: formData,
      });

      clearInterval(progressInterval);
      setUploadProgress(100);

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Upload failed');
      }

      const result = await response.json();
      
      // Add to uploaded files list
      const newFile = {
        id: Date.now(),
        name: file.name,
        size: file.size,
        status: 'processed',
        uploadTime: new Date(),
        recordsCount: result.records_processed || 0,
        message: result.message
      };

      setUploadedFiles(prev => [newFile, ...prev]);
      setMessage(`Файл успешно загружен! Обработано записей: ${result.records_processed || 0}`);
      
      // Call success callback
      if (onUpload) {
        onUpload(newFile);
      }

    } catch (error) {
      console.error('Upload error:', error);
      setError(error.message || 'Ошибка при загрузке файла');
    } finally {
      setUploading(false);
      setTimeout(() => {
        setUploadProgress(0);
      }, 1000);
    }
  }, [onUpload]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.ms-excel': ['.xls'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx']
    },
    multiple: false,
    disabled: uploading
  });

  const removeFile = (fileId) => {
    setUploadedFiles(prev => prev.filter(f => f.id !== fileId));
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (date) => {
    return new Date(date).toLocaleString('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        Загрузка торговых данных
      </Typography>
      
      {/* Upload Area */}
      <Card 
        variant="outlined" 
        sx={{ 
          mb: 3,
          border: isDragActive ? '2px dashed #1976d2' : '2px dashed #ccc',
          bgcolor: isDragActive ? 'action.hover' : 'background.paper',
          cursor: uploading ? 'not-allowed' : 'pointer',
          transition: 'all 0.2s ease'
        }}
      >
        <CardContent {...getRootProps()}>
          <input {...getInputProps()} />
          <Box 
            display="flex" 
            flexDirection="column" 
            alignItems="center" 
            py={4}
            sx={{ opacity: uploading ? 0.5 : 1 }}
          >
            <UploadIcon sx={{ fontSize: 48, color: isDragActive ? 'primary.main' : 'text.secondary' }} />
            <Typography variant="h6" mt={2} mb={1}>
              {isDragActive ? 'Отпустите файл здесь' : 'Перетащите файл сюда'}
            </Typography>
            <Typography variant="body2" color="text.secondary" mb={2}>
              или нажмите для выбора файла
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Поддерживаются CSV и Excel файлы (до 10MB)
            </Typography>
            
            {!uploading && (
              <Button variant="contained" sx={{ mt: 2 }} disabled={uploading}>
                Выбрать файл
              </Button>
            )}
          </Box>
        </CardContent>
      </Card>

      {/* Upload Progress */}
      {uploading && (
        <Box mb={3}>
          <Typography variant="body2" mb={1}>
            Загрузка файла... {uploadProgress}%
          </Typography>
          <LinearProgress 
            variant="determinate" 
            value={uploadProgress} 
            sx={{ height: 8, borderRadius: 4 }}
          />
        </Box>
      )}

      {/* Success Message */}
      {message && (
        <Alert severity="success" sx={{ mb: 3 }} onClose={() => setMessage(null)}>
          {message}
        </Alert>
      )}

      {/* Error Message */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Uploaded Files List */}
      {uploadedFiles.length > 0 && (
        <Box>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6">
              Загруженные файлы ({uploadedFiles.length})
            </Typography>
            <Button
              size="small"
              startIcon={<RefreshIcon />}
              onClick={() => window.location.reload()}
            >
              Обновить данные
            </Button>
          </Box>
          
          <List>
            {uploadedFiles.map((file, index) => (
              <ListItem
                key={file.id}
                secondaryAction={
                  <IconButton 
                    edge="end" 
                    onClick={() => removeFile(file.id)}
                    size="small"
                  >
                    <DeleteIcon />
                  </IconButton>
                }
              >
                <ListItemIcon>
                  {file.status === 'processed' ? (
                    <SuccessIcon color="success" />
                  ) : (
                    <ErrorIcon color="error" />
                  )}
                </ListItemIcon>
                <ListItemText
                  primary={
                    <Box display="flex" alignItems="center" gap={1}>
                      <Typography variant="body1">
                        {file.name}
                      </Typography>
                      <Chip
                        label={file.status === 'processed' ? 'Обработан' : 'Ошибка'}
                        color={file.status === 'processed' ? 'success' : 'error'}
                        size="small"
                      />
                    </Box>
                  }
                  secondary={
                    <Box>
                      <Typography variant="caption" display="block">
                        Размер: {formatFileSize(file.size)} • 
                        Записей: {file.recordsCount} • 
                        Время: {formatDate(file.uploadTime)}
                      </Typography>
                      {file.message && (
                        <Typography variant="caption" color="text.secondary">
                          {file.message}
                        </Typography>
                      )}
                    </Box>
                  }
                />
              </ListItem>
            ))}
          </List>
        </Box>
      )}

      {/* Instructions */}
      <Box mt={3}>
        <Typography variant="subtitle2" gutterBottom>
          Поддерживаемые форматы данных:
        </Typography>
        <Typography variant="body2" color="text.secondary">
          • CSV файлы с торговыми данными (timestamp, symbol, side, quantity, price, fee)
          <br />
          • Excel файлы с аналогичной структурой
          <br />
          • Экспорты с бирж HTX, Binance, OKX
          <br />
          • 3Commas отчеты (планируется)
        </Typography>
      </Box>
    </Paper>
  );
};

export default FileUpload;
