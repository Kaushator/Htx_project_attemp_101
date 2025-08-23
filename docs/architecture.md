# HTX Project Architecture

## Обзор

HTX Project - это комплексное решение для анализа торговых данных с биржи HTX (Huobi), включающее:

- **Backend**: FastAPI приложение с асинхронной архитектурой
- **Frontend**: React приложение с TypeScript и TailwindCSS
- **Database**: SQLAlchemy 2.0 с поддержкой SQLite/PostgreSQL
- **Integrations**: HTX API, 3Commas API
- **File Processing**: Парсинг CSV/Excel файлов

## Архитектура Backend

### Структура приложения

```
backend/app/
├── main.py              # Точка входа FastAPI
├── core/                # Конфигурация и логирование
│   ├── config.py       # Настройки (Pydantic)
│   └── logging.py      # Логирование
├── api/v1/             # API endpoints
│   └── endpoints/      # Конкретные эндпоинты
├── models/             # SQLAlchemy модели
├── schemas/            # Pydantic схемы
├── services/           # Бизнес-логика
├── db/                 # База данных
└── workers/            # Фоновые задачи
```

### Ключевые компоненты

#### 1. FastAPI Application
- Асинхронная архитектура
- Автоматическая документация (Swagger/ReDoc)
- CORS middleware
- Глобальная обработка ошибок

#### 2. Database Layer
- SQLAlchemy 2.0 с async поддержкой
- Асинхронные сессии
- Миграции через Alembic
- Поддержка SQLite и PostgreSQL

#### 3. Services Layer
- **HTXClient**: Интеграция с HTX API
- **FileParser**: Парсинг CSV/Excel файлов
- **PnLService**: Расчет прибыли/убытков
- **CashflowService**: Управление денежными потоками
- **ThreeCommasIntegration**: Интеграция с 3Commas

#### 4. Background Tasks
- APScheduler для планирования задач
- Асинхронная обработка файлов
- Синхронизация данных с внешними API

## API Design

### RESTful Endpoints

#### Health Check
- `GET /api/v1/health` - Базовая проверка
- `GET /api/v1/health/db` - Проверка БД
- `GET /api/v1/health/full` - Полная проверка

#### Files
- `POST /api/v1/files/upload` - Загрузка файлов
- `GET /api/v1/files/list` - Список файлов
- `DELETE /api/v1/files/{filename}` - Удаление файла

#### Trades
- `GET /api/v1/trades` - Список сделок
- `GET /api/v1/trades/{id}` - Конкретная сделка
- `GET /api/v1/trades/summary` - Сводка

#### Cashflow
- `GET /api/v1/cashflow/deposits` - Депозиты
- `GET /api/v1/cashflow/withdrawals` - Выводы
- `GET /api/v1/cashflow/transfers` - Трансферы
- `GET /api/v1/cashflow/summary` - Сводка

#### PnL
- `GET /api/v1/pnl/summary` - Сводка PnL
- `GET /api/v1/pnl/daily` - Ежедневный PnL
- `GET /api/v1/pnl/symbols` - PnL по символам
- `GET /api/v1/pnl/drawdown` - Анализ просадки

## Data Models

### Основные сущности

#### Trade
- ID, дата, символ
- Сторона (buy/sell)
- Количество, цена, комиссия
- Источник данных

#### Deposit/Withdrawal
- ID, дата, валюта
- Количество, комиссия
- Транзакционный ID
- Статус

#### Transfer
- ID, дата, валюта
- Количество
- От/Куда аккаунты

## Security

### Аутентификация
- JWT токены (опционально)
- API ключи для внешних сервисов

### Валидация
- Pydantic схемы для всех входных данных
- Валидация файлов (размер, тип)
- Санитизация данных

## Performance

### Оптимизации
- Асинхронная обработка
- Connection pooling для БД
- Кэширование (Redis опционально)
- Пагинация для больших списков

### Мониторинг
- Структурированное логирование
- Health checks
- Метрики производительности

## Deployment

### Docker
- Многоэтапная сборка
- Оптимизированные образы
- Docker Compose для разработки

### Environment
- Переменные окружения
- Конфигурация через .env файлы
- Разные настройки для dev/prod

## Future Enhancements

### Планируемые улучшения
1. **Real-time данные**: WebSocket для live данных
2. **Advanced Analytics**: Машинное обучение
3. **Mobile App**: React Native приложение
4. **Multi-exchange**: Поддержка других бирж
5. **Trading Bots**: Автоматическая торговля

### Масштабирование
- Микросервисная архитектура
- Message queues (RabbitMQ/Kafka)
- Distributed caching
- Load balancing
