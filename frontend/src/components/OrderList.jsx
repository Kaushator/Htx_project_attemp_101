import React from 'react';
import { Typography, List, ListItem, ListItemText, Button } from '@mui/material';

const OrderList = () => {
  // Mock data for now
  const orders = [
    { id: 1, symbol: 'BTC/USD', amount: 0.2, price: 31000, status: 'open' },
    { id: 2, symbol: 'ETH/USD', amount: 1.5, price: 2100, status: 'open' },
  ];

  return (
    <div>
      <Typography variant="h6" gutterBottom>
        Open Orders
      </Typography>
      <List>
        {orders.map((order) => (
          <ListItem key={order.id} secondaryAction={
            <Button variant="outlined" color="secondary" size="small">Cancel</Button>
          }>
            <ListItemText
              primary={`${order.symbol} - ${order.amount} @ $${order.price}`}
              secondary={`Status: ${order.status}`}
            />
          </ListItem>
        ))}
      </List>
    </div>
  );
};

export default OrderList;
