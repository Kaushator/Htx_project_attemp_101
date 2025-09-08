import React, { useRef, useState } from 'react';
import { Box, Typography, Button, CircularProgress, Alert } from '@mui/material';

const FileUpload = ({ onUpload }) => {
  const fileInput = useRef();
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);
  const [error, setError] = useState(null);

  const handleUpload = async (e) => {
    e.preventDefault();
    setMessage(null);
    setError(null);
    const file = fileInput.current.files[0];
    if (!file) return;
    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);
    try {
      const res = await fetch('http://localhost:8000/api/v1/files/upload', {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      if (res.ok) {
        setMessage(data.message || 'Файл успешно загружен!');
        if (onUpload) onUpload();
      } else {
        setError(data.detail || 'Ошибка загрузки файла');
      }
    } catch (err) {
      setError('Ошибка соединения с сервером');
    }
    setLoading(false);
  };

  return (
    <Box sx={{ my: 2 }}>
      <Typography variant="h6" gutterBottom>
        Загрузка файла (CSV/XLSX)
      </Typography>
      <form onSubmit={handleUpload}>
        <input type="file" ref={fileInput} accept=".csv,.xlsx,.xls" style={{ marginBottom: 8 }} />
        <Button type="submit" variant="contained" disabled={loading}>
          Загрузить
        </Button>
      </form>
      {loading && <CircularProgress sx={{ mt: 2 }} />}
      {message && <Alert severity="success" sx={{ mt: 2 }}>{message}</Alert>}
      {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}
    </Box>
  );
};

export default FileUpload;
