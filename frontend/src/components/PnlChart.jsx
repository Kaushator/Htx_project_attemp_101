import React, { useEffect, useState } from 'react';
import { Typography } from '@mui/material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

// Пример запроса к API (замените URL на ваш реальный эндпоинт)
const fetchPnlData = async () => {
  try {
    const response = await fetch('http://localhost:8000/api/v1/pnl');
    if (!response.ok) throw new Error('Ошибка загрузки данных');
    return await response.json();
  } catch (e) {
    return [];
  }
};

const PnlChart = () => {
  const [data, setData] = useState([]);

  useEffect(() => {
    fetchPnlData().then(setData);
  }, []);

  return (
    <div>
      <Typography variant="h6" gutterBottom>
        PnL по дням
      </Typography>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data} margin={{ top: 20, right: 30, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey="pnl" stroke="#1976d2" strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default PnlChart;
