import React, { useState } from 'react';
import {
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  Grid,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Code,
  Alert,
  Divider,
  Button
} from '@mui/material';
import {
  ExpandMore,
  Api,
  Database,
  TrendingUp,
  Shield,
  Activity,
  Settings,
  FileText,
  CheckCircle
} from 'lucide-react';

const DataRequirements = () => {
  const [expandedPanel, setExpandedPanel] = useState('trades');

  const handleChange = (panel) => (event, isExpanded) => {
    setExpandedPanel(isExpanded ? panel : false);
  };

  const dataStructures = {
    trades: {
      title: "Trading Data Structure",
      icon: <TrendingUp size={20} />,
      description: "Требуемая структура торговых данных от 3Commas API",
      fields: [
        { name: "id", type: "integer", description: "Уникальный ID сделки", required: true },
        { name: "bot_id", type: "integer", description: "ID торгового бота", required: true },
        { name: "pair", type: "string", description: "Торговая пара (например, BTC_USDT)", required: true },
        { name: "type", type: "string", description: "Тип сделки (buy/sell)", required: true },
        { name: "amount", type: "decimal", description: "Количество базовой валюты", required: true },
        { name: "price", type: "decimal", description: "Цена исполнения", required: true },
        { name: "total", type: "decimal", description: "Общая сумма сделки", required: true },
        { name: "fee", type: "decimal", description: "Комиссия за сделку", required: false },
        { name: "timestamp", type: "datetime", description: "Время исполнения сделки", required: true },
        { name: "status", type: "string", description: "Статус сделки (filled, partial, etc.)", required: true }
      ],
      example: {
        "id": 12345,
        "bot_id": 678,
        "pair": "BTC_USDT",
        "type": "buy",
        "amount": "0.001",
        "price": "45000.00",
        "total": "45.00",
        "fee": "0.045",
        "timestamp": "2024-01-15T10:30:00Z",
        "status": "filled"
      }
    },
    bots: {
      title: "Bot Configuration",
      icon: <Activity size={20} />,
      description: "Конфигурация торговых ботов",
      fields: [
        { name: "id", type: "integer", description: "Уникальный ID бота", required: true },
        { name: "name", type: "string", description: "Название бота", required: true },
        { name: "pair", type: "string", description: "Торговая пара", required: true },
        { name: "strategy", type: "string", description: "Стратегия торговли", required: true },
        { name: "base_order_volume", type: "decimal", description: "Объем базового ордера", required: true },
        { name: "safety_order_volume", type: "decimal", description: "Объем страховочного ордера", required: true },
        { name: "take_profit", type: "decimal", description: "Процент тейк-профита", required: true },
        { name: "max_safety_orders", type: "integer", description: "Максимум страховочных ордеров", required: true },
        { name: "safety_order_step_scale", type: "decimal", description: "Шаг увеличения страховочных ордеров", required: false },
        { name: "status", type: "string", description: "Статус бота (active, stopped, etc.)", required: true },
        { name: "created_at", type: "datetime", description: "Дата создания", required: true }
      ],
      example: {
        "id": 678,
        "name": "BTC Long Bot",
        "pair": "BTC_USDT",
        "strategy": "long",
        "base_order_volume": "10.00",
        "safety_order_volume": "20.00", 
        "take_profit": "1.5",
        "max_safety_orders": 5,
        "safety_order_step_scale": "1.2",
        "status": "active",
        "created_at": "2024-01-01T00:00:00Z"
      }
    },
    performance: {
      title: "Performance Metrics",
      icon: <Shield size={20} />,
      description: "Метрики производительности ботов",
      fields: [
        { name: "bot_id", type: "integer", description: "ID бота", required: true },
        { name: "total_profit", type: "decimal", description: "Общая прибыль", required: true },
        { name: "total_trades", type: "integer", description: "Общее количество сделок", required: true },
        { name: "successful_trades", type: "integer", description: "Успешные сделки", required: true },
        { name: "avg_profit_per_trade", type: "decimal", description: "Средняя прибыль на сделку", required: true },
        { name: "max_drawdown", type: "decimal", description: "Максимальная просадка", required: true },
        { name: "sharpe_ratio", type: "decimal", description: "Коэффициент Шарпа", required: false },
        { name: "win_rate", type: "decimal", description: "Процент прибыльных сделок", required: true },
        { name: "period_start", type: "datetime", description: "Начало периода", required: true },
        { name: "period_end", type: "datetime", description: "Конец периода", required: true }
      ],
      example: {
        "bot_id": 678,
        "total_profit": "150.75",
        "total_trades": 45,
        "successful_trades": 32,
        "avg_profit_per_trade": "3.35",
        "max_drawdown": "-5.2",
        "sharpe_ratio": "1.35",
        "win_rate": "71.11",
        "period_start": "2024-01-01T00:00:00Z",
        "period_end": "2024-01-15T23:59:59Z"
      }
    },
    positions: {
      title: "Current Positions",
      icon: <Database size={20} />,
      description: "Текущие открытые позиции",
      fields: [
        { name: "bot_id", type: "integer", description: "ID бота", required: true },
        { name: "pair", type: "string", description: "Торговая пара", required: true },
        { name: "position_type", type: "string", description: "Тип позиции (long/short)", required: true },
        { name: "entry_price", type: "decimal", description: "Цена входа", required: true },
        { name: "current_price", type: "decimal", description: "Текущая цена", required: true },
        { name: "amount", type: "decimal", description: "Количество", required: true },
        { name: "unrealized_pnl", type: "decimal", description: "Нереализованная прибыль/убыток", required: true },
        { name: "realized_pnl", type: "decimal", description: "Реализованная прибыль/убыток", required: true },
        { name: "safety_orders_count", type: "integer", description: "Количество активных страховочных ордеров", required: true },
        { name: "opened_at", type: "datetime", description: "Время открытия позиции", required: true }
      ],
      example: {
        "bot_id": 678,
        "pair": "BTC_USDT",
        "position_type": "long",
        "entry_price": "44500.00",
        "current_price": "45000.00",
        "amount": "0.002",
        "unrealized_pnl": "1.00",
        "realized_pnl": "0.00",
        "safety_orders_count": 2,
        "opened_at": "2024-01-15T09:30:00Z"
      }
    }
  };

  const apiEndpoints = [
    {
      endpoint: "/ver1/bots",
      method: "GET",
      description: "Получить список всех ботов",
      response: "Array of bot objects"
    },
    {
      endpoint: "/ver1/bots/{bot_id}/deals",
      method: "GET", 
      description: "Получить сделки конкретного бота",
      response: "Array of deal objects"
    },
    {
      endpoint: "/ver1/deals",
      method: "GET",
      description: "Получить все сделки аккаунта",
      response: "Array of deal objects"
    },
    {
      endpoint: "/ver1/accounts/{account_id}/balance",
      method: "GET",
      description: "Получить баланс аккаунта",
      response: "Balance object"
    }
  ];

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom>
        <Api size={24} style={{ marginRight: 8, verticalAlign: 'middle' }} />
        3Commas API Data Requirements
      </Typography>
      
      <Alert severity="info" sx={{ mb: 3 }}>
        <Typography variant="body2">
          Ниже представлены структуры данных, которые наше приложение ожидает получить от 3Commas API.
          Эта информация поможет понять, какие данные будут использоваться для анализа и отображения.
        </Typography>
      </Alert>

      {/* API Endpoints */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            <Settings size={20} style={{ marginRight: 8, verticalAlign: 'middle' }} />
            Required API Endpoints
          </Typography>
          <List>
            {apiEndpoints.map((endpoint, index) => (
              <ListItem key={index} divider>
                <ListItemIcon>
                  <Api size={16} />
                </ListItemIcon>
                <ListItemText
                  primary={
                    <Box display="flex" alignItems="center" gap={1}>
                      <Chip label={endpoint.method} color="primary" size="small" />
                      <Code>{endpoint.endpoint}</Code>
                    </Box>
                  }
                  secondary={`${endpoint.description} → ${endpoint.response}`}
                />
              </ListItem>
            ))}
          </List>
        </CardContent>
      </Card>

      {/* Data Structures */}
      <Typography variant="h6" gutterBottom>
        Data Structures
      </Typography>
      
      {Object.entries(dataStructures).map(([key, structure]) => (
        <Accordion
          key={key}
          expanded={expandedPanel === key}
          onChange={handleChange(key)}
          sx={{ mb: 2 }}
        >
          <AccordionSummary expandIcon={<ExpandMore />}>
            <Box display="flex" alignItems="center" gap={2}>
              {structure.icon}
              <Box>
                <Typography variant="h6">{structure.title}</Typography>
                <Typography variant="body2" color="text.secondary">
                  {structure.description}
                </Typography>
              </Box>
            </Box>
          </AccordionSummary>
          
          <AccordionDetails>
            <Grid container spacing={3}>
              {/* Fields */}
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle1" gutterBottom>
                  Required Fields
                </Typography>
                <List dense>
                  {structure.fields.map((field, index) => (
                    <ListItem key={index}>
                      <ListItemIcon>
                        {field.required ? (
                          <CheckCircle size={16} color="#4caf50" />
                        ) : (
                          <FileText size={16} color="#9e9e9e" />
                        )}
                      </ListItemIcon>
                      <ListItemText
                        primary={
                          <Box display="flex" alignItems="center" gap={1}>
                            <Typography variant="body2" fontWeight="bold">
                              {field.name}
                            </Typography>
                            <Chip 
                              label={field.type} 
                              size="small" 
                              variant="outlined"
                              color={field.required ? "primary" : "default"}
                            />
                          </Box>
                        }
                        secondary={field.description}
                      />
                    </ListItem>
                  ))}
                </List>
              </Grid>
              
              {/* Example */}
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle1" gutterBottom>
                  JSON Example
                </Typography>
                <Paper variant="outlined" sx={{ p: 2, bgcolor: 'grey.50' }}>
                  <pre style={{ 
                    fontSize: '12px', 
                    margin: 0, 
                    overflow: 'auto',
                    whiteSpace: 'pre-wrap'
                  }}>
                    {JSON.stringify(structure.example, null, 2)}
                  </pre>
                </Paper>
              </Grid>
            </Grid>
          </AccordionDetails>
        </Accordion>
      ))}

      {/* Integration Notes */}
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Integration Notes
          </Typography>
          <Box component="ul" sx={{ pl: 2 }}>
            <Typography component="li" variant="body2" sx={{ mb: 1 }}>
              Все временные метки должны быть в формате ISO 8601 (UTC)
            </Typography>
            <Typography component="li" variant="body2" sx={{ mb: 1 }}>
              Денежные значения должны быть строками для точности (избежание float проблем)
            </Typography>
            <Typography component="li" variant="body2" sx={{ mb: 1 }}>
              API должен поддерживать пагинацию для больших объемов данных
            </Typography>
            <Typography component="li" variant="body2" sx={{ mb: 1 }}>
              Желательна поддержка фильтрации по датам и торговым парам
            </Typography>
            <Typography component="li" variant="body2" sx={{ mb: 1 }}>
              WebSocket поддержка для real-time обновлений (опционально)
            </Typography>
          </Box>
        </CardContent>
      </Card>
    </Paper>
  );
};

export default DataRequirements;
