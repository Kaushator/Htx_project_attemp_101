import React, { useEffect, useState, forwardRef, useImperativeHandle } from 'react';
import { Typography, List, ListItem, ListItemText, CircularProgress } from '@mui/material';

const TradingOverview = forwardRef((props, ref) => {
  const [trades, setTrades] = useState([]);
  const [loading, setLoading] = useState(true);

  const loadData = () => {
    setLoading(true);
    fetch('http://localhost:8004/api/v1/trades?limit=10')
      .then((res) => res.json())
      .then((data) => {
        setTrades(data.trades || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  };

  useImperativeHandle(ref, () => ({
    reload: loadData,
  }));

  useEffect(() => {
    loadData();
  }, []);

  return (
    <div>
      <Typography variant="h6" gutterBottom>
        Trading Overview
      </Typography>
      {loading ? (
        <CircularProgress />
      ) : (
        <List>
          {trades.map((trade) => (
            <ListItem key={trade.id}>
              <ListItemText
                primary={`${trade.symbol} - $${trade.price}`}
                secondary={`Amount: ${trade.quantity} | Side: ${trade.side}`}
              />
            </ListItem>
          ))}
        </List>
      )}
    </div>
  );
});

export default TradingOverview;
