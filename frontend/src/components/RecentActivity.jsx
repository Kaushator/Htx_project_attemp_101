import React, { useState } from 'react';
import {
  Paper,
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Avatar,
  Tabs,
  Tab,
  IconButton,
  Tooltip,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Divider
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Activity,
  Clock,
  DollarSign,
  FileText,
  AlertTriangle,
  CheckCircle,
  RefreshCw,
  Upload
} from 'lucide-react';

const RecentActivity = ({ data }) => {
  const [activeTab, setActiveTab] = useState(0);

  if (!data) {
    return (
      <Paper sx={{ p: 3 }}>
        <Typography>Нет данных о последней активности</Typography>
      </Paper>
    );
  }

  // Recent trades
  const recentTrades = data.recent_trades || [];
  
  // Recent files uploaded
  const recentFiles = data.recent_files || [];
  
  // System activities
  const systemActivity = data.system_activity || [];
  
  // Alerts and notifications
  const alerts = data.alerts || [];

  const getTradeIcon = (side) => {
    return side?.toLowerCase() === 'buy' ? TrendingUp : TrendingDown;
  };

  const getTradeColor = (pnl) => {
    if (pnl > 0) return 'success.main';
    if (pnl < 0) return 'error.main';
    return 'text.primary';
  };

  const getActivityIcon = (type) => {
    switch (type?.toLowerCase()) {
      case 'trade': return Activity;
      case 'upload': return Upload;
      case 'analysis': return FileText;
      case 'alert': return AlertTriangle;
      case 'sync': return RefreshCw;
      default: return CheckCircle;
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('ru-RU', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(amount);
  };

  const formatDateTime = (dateString) => {
    return new Date(dateString).toLocaleString('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  return (
    <Paper sx={{ p: 3, height: 'fit-content' }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5">
          Recent Activity
        </Typography>
        <Tooltip title="Refresh">
          <IconButton size="small">
            <RefreshCw size={20} />
          </IconButton>
        </Tooltip>
      </Box>

      <Tabs value={activeTab} onChange={handleTabChange} sx={{ mb: 3 }}>
        <Tab label="Recent Trades" />
        <Tab label="File Activity" />
        <Tab label="System Events" />
        <Tab label="Alerts" />
      </Tabs>

      {/* Recent Trades Tab */}
      {activeTab === 0 && (
        <Box>
          {recentTrades.length > 0 ? (
            <TableContainer sx={{ maxHeight: 400 }}>
              <Table stickyHeader size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Time</TableCell>
                    <TableCell>Symbol</TableCell>
                    <TableCell>Side</TableCell>
                    <TableCell align="right">Quantity</TableCell>
                    <TableCell align="right">Price</TableCell>
                    <TableCell align="right">PnL</TableCell>
                    <TableCell>Status</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {recentTrades.slice(0, 20).map((trade, index) => {
                    const TradeIcon = getTradeIcon(trade.side);
                    return (
                      <TableRow key={trade.id || index} hover>
                        <TableCell>
                          <Typography variant="caption">
                            {formatDateTime(trade.timestamp)}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Box display="flex" alignItems="center" gap={1}>
                            <Avatar sx={{ width: 20, height: 20, fontSize: 10 }}>
                              {trade.symbol?.slice(0, 2)}
                            </Avatar>
                            <Typography variant="body2">
                              {trade.symbol}
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Box display="flex" alignItems="center" gap={1}>
                            <TradeIcon 
                              size={16} 
                              color={trade.side?.toLowerCase() === 'buy' ? '#4caf50' : '#f44336'}
                            />
                            <Chip
                              label={trade.side}
                              color={trade.side?.toLowerCase() === 'buy' ? 'success' : 'error'}
                              size="small"
                              variant="outlined"
                            />
                          </Box>
                        </TableCell>
                        <TableCell align="right">
                          {trade.quantity?.toFixed(4)}
                        </TableCell>
                        <TableCell align="right">
                          {formatCurrency(trade.price || 0)}
                        </TableCell>
                        <TableCell align="right">
                          <Typography color={getTradeColor(trade.pnl || 0)}>
                            {formatCurrency(trade.pnl || 0)}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={trade.status || 'Completed'}
                            color={trade.status === 'Completed' ? 'success' : 'warning'}
                            size="small"
                          />
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </TableContainer>
          ) : (
            <Box textAlign="center" py={4}>
              <Activity size={48} color="#ccc" />
              <Typography variant="body2" color="text.secondary" mt={2}>
                No recent trades
              </Typography>
            </Box>
          )}
        </Box>
      )}

      {/* File Activity Tab */}
      {activeTab === 1 && (
        <Box>
          {recentFiles.length > 0 ? (
            <List>
              {recentFiles.map((file, index) => (
                <React.Fragment key={file.id || index}>
                  <ListItem>
                    <ListItemAvatar>
                      <Avatar sx={{ bgcolor: 'primary.main' }}>
                        <FileText size={20} />
                      </Avatar>
                    </ListItemAvatar>
                    <ListItemText
                      primary={
                        <Box display="flex" justifyContent="space-between" alignItems="center">
                          <Typography variant="body2">
                            {file.filename || `File ${index + 1}`}
                          </Typography>
                          <Chip
                            label={file.status || 'Processed'}
                            color={file.status === 'Processed' ? 'success' : 'warning'}
                            size="small"
                          />
                        </Box>
                      }
                      secondary={
                        <Box>
                          <Typography variant="caption" color="text.secondary">
                            Uploaded: {formatDateTime(file.upload_time || new Date())}
                          </Typography>
                          <br />
                          <Typography variant="caption">
                            {file.records_count || 0} records • {file.file_size || 'Unknown size'}
                          </Typography>
                        </Box>
                      }
                    />
                  </ListItem>
                  {index < recentFiles.length - 1 && <Divider />}
                </React.Fragment>
              ))}
            </List>
          ) : (
            <Box textAlign="center" py={4}>
              <Upload size={48} color="#ccc" />
              <Typography variant="body2" color="text.secondary" mt={2}>
                No recent file uploads
              </Typography>
            </Box>
          )}
        </Box>
      )}

      {/* System Events Tab */}
      {activeTab === 2 && (
        <Box>
          {systemActivity.length > 0 ? (
            <List>
              {systemActivity.map((activity, index) => {
                const ActivityIcon = getActivityIcon(activity.type);
                return (
                  <React.Fragment key={activity.id || index}>
                    <ListItem>
                      <ListItemAvatar>
                        <Avatar sx={{ bgcolor: 'info.main' }}>
                          <ActivityIcon size={20} />
                        </Avatar>
                      </ListItemAvatar>
                      <ListItemText
                        primary={
                          <Typography variant="body2">
                            {activity.message || activity.description}
                          </Typography>
                        }
                        secondary={
                          <Box display="flex" justifyContent="space-between" alignItems="center">
                            <Typography variant="caption" color="text.secondary">
                              {formatDateTime(activity.timestamp || new Date())}
                            </Typography>
                            <Chip
                              label={activity.type || 'Event'}
                              size="small"
                              variant="outlined"
                            />
                          </Box>
                        }
                      />
                    </ListItem>
                    {index < systemActivity.length - 1 && <Divider />}
                  </React.Fragment>
                );
              })}
            </List>
          ) : (
            <Box textAlign="center" py={4}>
              <Clock size={48} color="#ccc" />
              <Typography variant="body2" color="text.secondary" mt={2}>
                No recent system events
              </Typography>
            </Box>
          )}
        </Box>
      )}

      {/* Alerts Tab */}
      {activeTab === 3 && (
        <Box>
          {alerts.length > 0 ? (
            <List>
              {alerts.map((alert, index) => (
                <React.Fragment key={alert.id || index}>
                  <ListItem>
                    <ListItemAvatar>
                      <Avatar sx={{ 
                        bgcolor: alert.severity === 'error' ? 'error.main' : 
                                alert.severity === 'warning' ? 'warning.main' : 'info.main'
                      }}>
                        <AlertTriangle size={20} />
                      </Avatar>
                    </ListItemAvatar>
                    <ListItemText
                      primary={
                        <Box display="flex" justifyContent="space-between" alignItems="center">
                          <Typography variant="body2">
                            {alert.title || alert.message}
                          </Typography>
                          <Chip
                            label={alert.severity || 'info'}
                            color={
                              alert.severity === 'error' ? 'error' : 
                              alert.severity === 'warning' ? 'warning' : 'info'
                            }
                            size="small"
                          />
                        </Box>
                      }
                      secondary={
                        <Box>
                          <Typography variant="caption" color="text.secondary">
                            {formatDateTime(alert.timestamp || new Date())}
                          </Typography>
                          {alert.description && (
                            <>
                              <br />
                              <Typography variant="caption">
                                {alert.description}
                              </Typography>
                            </>
                          )}
                        </Box>
                      }
                    />
                  </ListItem>
                  {index < alerts.length - 1 && <Divider />}
                </React.Fragment>
              ))}
            </List>
          ) : (
            <Box textAlign="center" py={4}>
              <CheckCircle size={48} color="#4caf50" />
              <Typography variant="body2" color="text.secondary" mt={2}>
                No active alerts
              </Typography>
            </Box>
          )}
        </Box>
      )}

      {/* Quick Stats */}
      <Box mt={3}>
        <Typography variant="h6" gutterBottom>
          Quick Stats
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={6} md={3}>
            <Card variant="outlined">
              <CardContent sx={{ py: 2 }}>
                <Box display="flex" alignItems="center" gap={1}>
                  <Activity size={20} color="#1976d2" />
                  <Box>
                    <Typography variant="caption" color="text.secondary">
                      Today's Trades
                    </Typography>
                    <Typography variant="h6">
                      {recentTrades.filter(t => 
                        new Date(t.timestamp).toDateString() === new Date().toDateString()
                      ).length}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={6} md={3}>
            <Card variant="outlined">
              <CardContent sx={{ py: 2 }}>
                <Box display="flex" alignItems="center" gap={1}>
                  <FileText size={20} color="#4caf50" />
                  <Box>
                    <Typography variant="caption" color="text.secondary">
                      Files Processed
                    </Typography>
                    <Typography variant="h6">
                      {recentFiles.filter(f => f.status === 'Processed').length}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={6} md={3}>
            <Card variant="outlined">
              <CardContent sx={{ py: 2 }}>
                <Box display="flex" alignItems="center" gap={1}>
                  <AlertTriangle size={20} color="#ff9800" />
                  <Box>
                    <Typography variant="caption" color="text.secondary">
                      Active Alerts
                    </Typography>
                    <Typography variant="h6">
                      {alerts.filter(a => a.status === 'active').length}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={6} md={3}>
            <Card variant="outlined">
              <CardContent sx={{ py: 2 }}>
                <Box display="flex" alignItems="center" gap={1}>
                  <DollarSign size={20} color="#4caf50" />
                  <Box>
                    <Typography variant="caption" color="text.secondary">
                      Today's PnL
                    </Typography>
                    <Typography 
                      variant="h6" 
                      color={
                        recentTrades.reduce((sum, t) => sum + (t.pnl || 0), 0) >= 0 ? 
                        'success.main' : 'error.main'
                      }
                    >
                      {formatCurrency(
                        recentTrades.filter(t => 
                          new Date(t.timestamp).toDateString() === new Date().toDateString()
                        ).reduce((sum, t) => sum + (t.pnl || 0), 0)
                      )}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
    </Paper>
  );
};

export default RecentActivity;
