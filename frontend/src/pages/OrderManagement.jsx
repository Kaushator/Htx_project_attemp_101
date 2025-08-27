import React from 'react';
import { Container, Typography, Grid, Paper, Button, TextField } from '@mui/material';
import OrderList from '../components/OrderList';

const OrderManagement = () => {
  return (
    <Container>
      <Typography variant="h4" gutterBottom>
        Order Management
      </Typography>
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper elevation={3} style={{ padding: '16px' }}>
            <Typography variant="h6">Create New Order</Typography>
            <form>
              <TextField label="Symbol" fullWidth margin="normal" />
              <TextField label="Amount" type="number" fullWidth margin="normal" />
              <TextField label="Price" type="number" fullWidth margin="normal" />
              <Button variant="contained" color="primary" fullWidth>
                Submit Order
              </Button>
            </form>
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper elevation={3}>
            <OrderList />
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default OrderManagement;
