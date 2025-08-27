import React from 'react';
import { Typography, List, ListItem, ListItemText } from '@mui/material';

const AccountSummary = () => {
  // Mock data for now
  const accountData = {
    balance: 5000,
    openOrders: 3,
    pnl: 1200,
  };

  return (
    <div>
      <Typography variant="h6" gutterBottom>
        Account Summary
      </Typography>
      <List>
        <ListItem>
          <ListItemText primary="Balance" secondary={`$${accountData.balance}`} />
        </ListItem>
        <ListItem>
          <ListItemText primary="Open Orders" secondary={accountData.openOrders} />
        </ListItem>
        <ListItem>
          <ListItemText primary="PnL" secondary={`$${accountData.pnl}`} />
        </ListItem>
      </List>
    </div>
  );
};

export default AccountSummary;
