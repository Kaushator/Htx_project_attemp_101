import React, { useEffect, useState, forwardRef, useImperativeHandle } from 'react';
import { Typography, List, ListItem, ListItemText, CircularProgress } from '@mui/material';

const endpointMap = {
  deposit: '/api/v1/cashflow/deposits',
  withdrawal: '/api/v1/cashflow/withdrawals',
  transfer: '/api/v1/cashflow/transfers',
};

const TransactionList = forwardRef(({ type }, ref) => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  const loadData = () => {
    setLoading(true);
    fetch(`http://localhost:8000${endpointMap[type]}?limit=20`)
      .then((res) => res.json())
      .then((res) => {
        if (type === 'deposit') setData(res.deposits || []);
        else if (type === 'withdrawal') setData(res.withdrawals || []);
        else if (type === 'transfer') setData(res.transfers || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  };

  useImperativeHandle(ref, () => ({
    reload: loadData,
  }));

  useEffect(() => {
    loadData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [type]);

  return (
    <div>
      <Typography variant="h6" gutterBottom>
        {type.charAt(0).toUpperCase() + type.slice(1)}s
      </Typography>
      {loading ? (
        <CircularProgress />
      ) : (
        <List>
          {data.map((item, idx) => (
            <ListItem key={item.id || idx}>
              <ListItemText
                primary={`${item.amount} ${item.currency}`}
                secondary={`Date: ${item.date || item.time}${item.from_account ? ` | From: ${item.from_account}` : ''}${item.to_account ? ` | To: ${item.to_account}` : ''}`}
              />
            </ListItem>
          ))}
        </List>
      )}
    </div>
  );
});

export default TransactionList;
