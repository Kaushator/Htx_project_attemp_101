/**
 * Export Features Demo Page
 * Demonstrates all export functionality with sample data
 */

import React, { useState, useMemo } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  CardHeader,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Alert,
  Divider
} from '@mui/material';
import {
  QuickExportButton,
  MultiExportButton,
  AdvancedExportButton,
  SpeedDialExport
} from '../components/export/ExportButton';

// Generate sample trading data
const generateSampleData = () => {
  const symbols = ['BTC', 'ETH', 'USDT', 'BNB', 'ADA', 'SOL', 'XRP', 'DOT', 'DOGE', 'AVAX'];
  const data = [];
  
  for (let i = 0; i < 50; i++) {
    const symbol = symbols[Math.floor(Math.random() * symbols.length)];
    const price = Math.random() * 1000 + 1;
    const change24h = (Math.random() - 0.5) * 20;
    const volume24h = Math.random() * 10000000;
    
    data.push({
      id: i + 1,
      symbol: `${symbol}USDT`,
      name: symbol,
      price: Number(price.toFixed(4)),
      change24h: Number(change24h.toFixed(2)),
      volume24h: Number(volume24h.toFixed(0)),
      marketCap: Number((price * Math.random() * 1000000).toFixed(0)),
      timestamp: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString(),
      isActive: Math.random() > 0.3,
      exchange: ['HTX', 'Binance', 'Coinbase'][Math.floor(Math.random() * 3)],
      tradingPair: {
        base: symbol,
        quote: 'USDT',
        type: 'spot'
      },
      technicalIndicators: {
        rsi: Math.random() * 100,
        macd: (Math.random() - 0.5) * 10,
        volume_ratio: Math.random() * 5
      }
    });
  }
  
  return data;
};

const ExportDemo = () => {
  const [sampleData] = useState(generateSampleData());
  
  // Prepare different data subsets for demonstration
  const topGainers = useMemo(() => 
    sampleData.filter(item => item.change24h > 0).slice(0, 10),
    [sampleData]
  );
  
  const highVolume = useMemo(() => 
    sampleData.filter(item => item.volume24h > 5000000).slice(0, 15),
    [sampleData]
  );
  
  const activeCoins = useMemo(() => 
    sampleData.filter(item => item.isActive),
    [sampleData]
  );
  
  return (
    <Box sx={{ padding: 3 }}>
      {/* Header */}
      <Typography variant=\"h4\" component=\"h1\" gutterBottom>
        Export Features Demonstration
      </Typography>
      
      <Alert severity=\"info\" sx={{ mb: 3 }}>
        This page demonstrates all export functionality with sample trading data. 
        You can export data in CSV, PDF, and JSON formats with various customization options.
      </Alert>
      
      {/* Export Button Examples */}
      <Grid container spacing={3}>
        {/* Quick Export Buttons */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader title=\"Quick Export Buttons\" />
            <CardContent>
              <Typography variant=\"body2\" color=\"text.secondary\" paragraph>
                One-click export with default settings:
              </Typography>
              
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <QuickExportButton
                  data={sampleData}
                  format=\"csv\"
                  filename=\"sample_data\"
                  variant=\"contained\"
                  size=\"small\"
                />
                
                <QuickExportButton
                  data={topGainers}
                  format=\"pdf\"
                  filename=\"top_gainers\"
                  variant=\"contained\"
                  color=\"success\"
                  size=\"small\"
                />
                
                <QuickExportButton
                  data={activeCoins}
                  format=\"json\"
                  filename=\"active_coins\"
                  variant=\"outlined\"
                  size=\"small\"
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        {/* Multi-Format Export */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader title=\"Multi-Format Export\" />
            <CardContent>
              <Typography variant=\"body2\" color=\"text.secondary\" paragraph>
                Choose from multiple formats via dropdown:
              </Typography>
              
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <MultiExportButton
                  data={sampleData}
                  filename=\"all_trading_data\"
                  formats={['csv', 'pdf', 'json']}
                  variant=\"contained\"
                  color=\"primary\"
                />
                
                <MultiExportButton
                  data={highVolume}
                  filename=\"high_volume_coins\"
                  formats={['csv', 'pdf']}
                  variant=\"outlined\"
                  color=\"warning\"
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        {/* Advanced Export */}
        <Grid item xs={12}>
          <Card>
            <CardHeader title=\"Advanced Export with Customization\" />
            <CardContent>
              <Typography variant=\"body2\" color=\"text.secondary\" paragraph>
                Full customization dialog with field selection, format options, and data processing:
              </Typography>
              
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <AdvancedExportButton
                  data={sampleData}
                  title=\"Complete Trading Data Export\"
                  filename=\"trading_data_complete\"
                  variant=\"contained\"
                  color=\"secondary\"
                />
                
                <AdvancedExportButton
                  data={topGainers}
                  title=\"Top Gainers Export\"
                  filename=\"top_gainers_detailed\"
                  variant=\"outlined\"
                  color=\"success\"
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        {/* Data Preview Tables */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader 
              title=\"Sample Data (First 10 Records)\" 
              action={
                <Chip 
                  label={`${sampleData.length} total records`} 
                  color=\"primary\" 
                  size=\"small\" 
                />
              }
            />
            <CardContent>
              <TableContainer component={Paper} variant=\"outlined\">
                <Table size=\"small\">
                  <TableHead>
                    <TableRow>
                      <TableCell>Symbol</TableCell>
                      <TableCell align=\"right\">Price</TableCell>
                      <TableCell align=\"right\">24h Change</TableCell>
                      <TableCell align=\"right\">Volume</TableCell>
                      <TableCell>Exchange</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {sampleData.slice(0, 10).map((row) => (
                      <TableRow key={row.id}>
                        <TableCell>{row.symbol}</TableCell>
                        <TableCell align=\"right\">${row.price}</TableCell>
                        <TableCell 
                          align=\"right\" 
                          sx={{ 
                            color: row.change24h >= 0 ? 'success.main' : 'error.main' 
                          }}
                        >
                          {row.change24h >= 0 ? '+' : ''}{row.change24h}%
                        </TableCell>
                        <TableCell align=\"right\">
                          ${row.volume24h.toLocaleString()}
                        </TableCell>
                        <TableCell>
                          <Chip label={row.exchange} size=\"small\" variant=\"outlined\" />
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>
        
        {/* Top Gainers */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader 
              title=\"Top Gainers\" 
              action={
                <Chip 
                  label={`${topGainers.length} gainers`} 
                  color=\"success\" 
                  size=\"small\" 
                />
              }
            />
            <CardContent>
              <TableContainer component={Paper} variant=\"outlined\">
                <Table size=\"small\">
                  <TableHead>
                    <TableRow>
                      <TableCell>Symbol</TableCell>
                      <TableCell align=\"right\">Price</TableCell>
                      <TableCell align=\"right\">Gain %</TableCell>
                      <TableCell>Status</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {topGainers.slice(0, 8).map((row) => (
                      <TableRow key={row.id}>
                        <TableCell>{row.symbol}</TableCell>
                        <TableCell align=\"right\">${row.price}</TableCell>
                        <TableCell align=\"right\" sx={{ color: 'success.main' }}>
                          +{row.change24h}%
                        </TableCell>
                        <TableCell>
                          <Chip 
                            label={row.isActive ? 'Active' : 'Inactive'} 
                            color={row.isActive ? 'success' : 'default'} 
                            size=\"small\" 
                          />
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>
        
        {/* Export Features List */}
        <Grid item xs={12}>
          <Card>
            <CardHeader title=\"Export Features Summary\" />
            <CardContent>
              <Grid container spacing={2}>
                <Grid item xs={12} md={4}>
                  <Typography variant=\"h6\" gutterBottom>Supported Formats</Typography>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                    <Chip label=\"CSV - Comma Separated Values\" icon={<span>📊</span>} />
                    <Chip label=\"PDF - Portable Document Format\" icon={<span>📄</span>} />
                    <Chip label=\"JSON - JavaScript Object Notation\" icon={<span>⚙️</span>} />
                  </Box>
                </Grid>
                
                <Grid item xs={12} md={4}>
                  <Typography variant=\"h6\" gutterBottom>Customization Options</Typography>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                    <Chip label=\"Field Selection\" variant=\"outlined\" />
                    <Chip label=\"Field Renaming\" variant=\"outlined\" />
                    <Chip label=\"Data Formatting\" variant=\"outlined\" />
                    <Chip label=\"PDF Layout Options\" variant=\"outlined\" />
                    <Chip label=\"Statistics Inclusion\" variant=\"outlined\" />
                  </Box>
                </Grid>
                
                <Grid item xs={12} md={4}>
                  <Typography variant=\"h6\" gutterBottom>Data Processing</Typography>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                    <Chip label=\"Object Flattening\" variant=\"outlined\" />
                    <Chip label=\"Number Formatting\" variant=\"outlined\" />
                    <Chip label=\"Date Standardization\" variant=\"outlined\" />
                    <Chip label=\"Null Value Handling\" variant=\"outlined\" />
                    <Chip label=\"Custom Transforms\" variant=\"outlined\" />
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      
      {/* Speed Dial Export (Floating) */}
      <SpeedDialExport
        data={sampleData}
        formats={['csv', 'pdf', 'json']}
        position={{ bottom: 16, right: 16 }}
      />
    </Box>
  );
};

export default ExportDemo;