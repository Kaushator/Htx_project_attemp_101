# HTX Trading Analytics Platform - Architecture

## Systems Overview

The HTX Trading Analytics Platform is a modern, scalable solution for cryptocurrency trading analysis, built with async Python backend and React frontend. The architecture emphasizes performance, maintainability, and extensibility across multiple trading exchanges.

### Design Principles
- **Async-First**: All I/O operations use async/await patterns
- **Separation of Concerns**: Clear module boundaries between API, services, and data layers
- **Testability**: Dependency injection and interface-based design
- **Performance**: Sub-10-second time-to-insight for uploaded data
- **Security**: Encrypted secrets, input validation, rate limiting

## Module Boundaries

```
┌─────────────────────────────────────────────────────────────────┐
│                    HTX Analytics Platform                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ ┌─────────────────┐   HTTP/JSON   ┌─────────────────┐          │
│ │  React Frontend │ ◄────────────► │ FastAPI Backend │          │
│ │  (TailwindCSS)  │                │   (Python 3.8+) │          │
│ └─────────────────┘                └─────────────────┘          │
│                                             │                   │
│                                             ▼                   │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │                API Layer (v1)                               │ │
│ │ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐            │ │
│ │ │   Health    │ │   Files     │ │   Trades    │            │ │
│ │ │ Endpoints   │ │ Endpoints   │ │ Endpoints   │            │ │
│ │ └─────────────┘ └─────────────┘ └─────────────┘            │ │
│ │ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐            │ │
│ │ │  Cashflow   │ │     PnL     │ │Integration  │            │ │
│ │ │ Endpoints   │ │ Endpoints   │ │ Endpoints   │            │ │
│ │ └─────────────┘ └─────────────┘ └─────────────┘            │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                             │                   │
│                                             ▼                   │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │                Service Layer                                │ │
│ │ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐            │ │
│ │ │   Parser    │ │PnL Analytics│ │   HTX API   │            │ │
│ │ │  Service    │ │   Service   │ │   Client    │            │ │
│ │ └─────────────┘ └─────────────┘ └─────────────┘            │ │
│ │ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐            │ │
│ │ │ 3Commas     │ │   Cache     │ │Background   │            │ │
│ │ │  Service    │ │  Service    │ │  Workers    │            │ │
│ │ └─────────────┘ └─────────────┘ └─────────────┘            │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                             │                   │
│                                             ▼                   │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │                Data Layer                                   │ │
│ │ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐            │ │
│ │ │SQLAlchemy   │ │   Models    │ │  Schemas    │            │ │
│ │ │   ORM       │ │ (Database)  │ │ (Pydantic)  │            │ │
│ │ └─────────────┘ └─────────────┘ └─────────────┘            │ │
│ │ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐            │ │
│ │ │ SQLite/PG   │ │   Redis     │ │   File      │            │ │
│ │ │  Database   │ │   Cache     │ │   Storage   │            │ │
│ │ └─────────────┘ └─────────────┘ └─────────────┘            │ │
│ └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow Architecture

### 1. File Upload & Processing Pipeline
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Upload    │───►│ Validation  │───►│   Parser    │───►│  Database   │
│ CSV/Excel   │    │ Size/Format │    │ Normalize   │    │   Storage   │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
       │                    │                │                    │
       ▼                    ▼                ▼                    ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Quick scan  │    │Schema detect│    │Column map   │    │Async insert │
│ for preview │    │& validation │    │& transform  │    │with batching│
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

### 2. Analytics Computation Flow
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Request   │───►│   Cache     │───►│   Service   │───►│   Response  │
│ PnL/Stats   │    │   Check     │    │ Computation │    │  JSON/API   │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                            │                │                    │
                            ▼                ▼                    ▼
                   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
                   │Cache miss   │    │FIFO PnL calc│    │Cache result │
                   │Load from DB │    │Risk metrics │    │Set TTL      │
                   └─────────────┘    └─────────────┘    └─────────────┘
```

### 3. External API Integration Flow
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Scheduler  │───►│   Client    │───►│   Parser    │───►│  Database   │
│ Cron/Manual │    │HTX/3Commas  │    │ Normalize   │    │ Upsert/Sync │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
       │                    │                │                    │
       ▼                    ▼                ▼                    ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│Background   │    │Rate limited │    │Incremental  │    │Notify cache │
│task queue   │    │HTTP requests│    │sync by date │    │invalidation │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

## Backend Application Structure

```
backend/
├── app/
│   ├── main.py                    # FastAPI app factory & CORS setup
│   ├── core/
│   │   ├── config.py             # Pydantic settings with env vars
│   │   ├── logging.py            # Structured logging configuration
│   │   └── security.py           # JWT, encryption, rate limiting
│   ├── api/
│   │   └── v1/
│   │       ├── api.py            # API router aggregation
│   │       └── endpoints/
│   │           ├── health.py     # Health checks & system status
│   │           ├── files.py      # File upload & processing
│   │           ├── trades.py     # Trade history & filtering
│   │           ├── cashflow.py   # Deposits, withdrawals, transfers
│   │           ├── pnl.py        # PnL calculations & analytics
│   │           └── integrations.py # HTX & 3Commas endpoints
│   ├── models/
│   │   ├── base.py               # SQLAlchemy base class
│   │   ├── trade.py              # Trade model with relationships
│   │   ├── cashflow.py           # Deposit, withdrawal, transfer models
│   │   └── user.py               # User settings & preferences
│   ├── schemas/
│   │   ├── base.py               # Base Pydantic schemas
│   │   ├── trade.py              # Trade request/response schemas
│   │   ├── cashflow.py           # Cashflow schemas
│   │   └── pnl.py                # PnL calculation schemas
│   ├── services/
│   │   ├── __init__.py
│   │   ├── parser_csv.py         # CSV/Excel parsing logic
│   │   ├── pnl.py                # FIFO PnL & risk calculations
│   │   ├── htx_client.py         # HTX API integration
│   │   ├── threecommas.py        # 3Commas API integration
│   │   ├── db_service.py         # Database operations & queries
│   │   └── cache_service.py      # Redis caching layer
│   ├── db/
│   │   ├── base.py               # Database session management
│   │   ├── init_db.py            # Database initialization
│   │   └── deps.py               # Dependency injection
│   └── workers/
│       ├── __init__.py
│       ├── file_processor.py     # Background file processing
│       └── sync_worker.py        # Scheduled API synchronization
├── alembic/                      # Database migrations
├── tests/                        # Test suite
├── requirements.txt              # Production dependencies
├── requirements-dev.txt          # Development dependencies
└── Dockerfile                    # Container configuration
```

## Key Architectural Decisions

### 1. Async-First Design
**Decision**: Use FastAPI with async/await throughout the stack
**Rationale**: 
- I/O bound operations (file parsing, DB queries, API calls) benefit from async
- Better resource utilization and response times
- Native support for background tasks

**Trade-offs**: 
- More complex debugging compared to sync code
- Requires async-compatible libraries

### 2. Dual Database Support
**Decision**: Support both SQLite (development) and PostgreSQL (production)
**Rationale**:
- SQLite for rapid local development and testing
- PostgreSQL for production scalability and advanced features
- Seamless migration via SQLAlchemy abstractions

**Trade-offs**:
- Feature parity considerations (e.g., JSON columns)
- Different performance characteristics

### 3. Service Layer Abstraction
**Decision**: Separate business logic into dedicated service classes
**Rationale**:
- Testability through dependency injection
- Reusability across API endpoints
- Clear separation of concerns

**Implementation**:
```python
# services/pnl.py
class PnLService:
    def __init__(self, db_service: DBService, cache_service: CacheService):
        self.db = db_service
        self.cache = cache_service
    
    async def calculate_portfolio_pnl(self, user_id: int) -> PnLReport:
        # Implementation with caching and DB access
```

### 4. File Processing Strategy
**Decision**: Two-phase processing (quick preview + background processing)
**Rationale**:
- Meets 10-second time-to-insight requirement
- User gets immediate feedback while detailed processing continues
- Scalable for large files

**Implementation**:
```python
# Phase 1: Quick scan (< 2 seconds)
preview = await parser.quick_scan(file)
return {"preview": preview, "job_id": background_job.id}

# Phase 2: Background processing
await background_worker.process_full_file(file, job_id)
```

### 5. External API Integration
**Decision**: Abstract exchange APIs behind common interfaces
**Rationale**:
- Enables multi-exchange support
- Easier testing with mock implementations
- Consistent error handling

**Implementation**:
```python
class ExchangeClient(ABC):
    @abstractmethod
    async def get_trades(self, symbol: str, since: datetime) -> List[Trade]:
        pass

class HTXClient(ExchangeClient):
    # HTX-specific implementation
```

### 6. Caching Strategy
**Decision**: Multi-level caching with Redis
**Rationale**:
- Reduce database load for repeated queries
- Cache expensive calculations (PnL, aggregations)
- Configurable TTL based on data volatility

**Layers**:
- Application cache (in-memory for request duration)
- Redis cache (shared across instances)
- Database query result cache

### 7. Error Handling & Monitoring
**Decision**: Structured logging with correlation IDs
**Rationale**:
- Traceable requests across service boundaries
- JSON logging for log aggregation systems
- Performance metrics collection

**Implementation**:
```python
# Structured logging with context
logger.info(
    "pnl_calculation_completed",
    extra={
        "user_id": user_id,
        "duration_ms": duration,
        "trades_processed": trade_count,
        "correlation_id": correlation_id
    }
)
```

## Database Design

### Schema Overview
```sql
-- Core trading data
trades (id, symbol, side, amount, price, fee, timestamp, user_id)
deposits (id, currency, amount, timestamp, user_id)
withdrawals (id, currency, amount, fee, timestamp, user_id)
transfers (id, from_currency, to_currency, amount, rate, timestamp, user_id)

-- User management
users (id, username, settings, created_at)

-- File processing tracking
file_uploads (id, filename, status, created_at, user_id)
processing_jobs (id, file_id, status, progress, created_at)

-- Caching & performance
cached_calculations (key, value, expires_at)
```

### Indexing Strategy
```sql
-- Performance indexes
CREATE INDEX idx_trades_user_timestamp ON trades(user_id, timestamp);
CREATE INDEX idx_trades_symbol ON trades(symbol);
CREATE INDEX idx_cashflow_user_timestamp ON deposits(user_id, timestamp);

-- Partial indexes for common queries
CREATE INDEX idx_trades_recent ON trades(timestamp) 
  WHERE timestamp > NOW() - INTERVAL '30 days';
```

## Security Architecture

### 1. API Key Management
```python
# Encrypted storage with Fernet
class Settings:
    htx_api_key: str = Field(..., env="HTX_API_KEY")
    encryption_key: str = Field(..., env="ENCRYPTION_KEY")
    
    @property
    def decrypted_htx_key(self) -> str:
        return self.fernet.decrypt(self.htx_api_key.encode()).decode()
```

### 2. Input Validation
- File size limits (configurable)
- File type validation (CSV, Excel)
- Schema validation for uploaded data
- SQL injection prevention via ORM

### 3. Rate Limiting
```python
# Per-endpoint rate limits
@limiter.limit("100/minute")
async def upload_file(file: UploadFile):
    pass
```

## Deployment Architecture

### Development Environment
```yaml
# docker-compose.yml
services:
  backend:
    build: ./backend
    ports: ["8004:8004"]
    environment:
      - DATABASE_URL=sqlite:///./dev.db
  
  frontend:
    build: ./frontend
    ports: ["3000:3000"]
```

### Production Environment
```yaml
services:
  backend:
    image: htx-backend:latest
    environment:
      - DATABASE_URL=postgresql+asyncpg://...
      - REDIS_URL=redis://redis:6379
  
  redis:
    image: redis:7-alpine
  
  postgres:
    image: postgres:15
```

## Performance Considerations

### Target Metrics
- **Time-to-Insight**: ≤ 10 seconds from upload to preview
- **API Response Time**: ≤ 200ms for cached endpoints, ≤ 2s for calculations
- **Throughput**: 1000+ trades processed per analysis
- **Concurrent Users**: 50+ users with acceptable response times

### Optimization Techniques
1. **Database Query Optimization**
   - Proper indexing strategy
   - Query result caching
   - Pagination for large datasets

2. **Async Processing**
   - Background workers for heavy computations
   - Non-blocking I/O operations
   - Connection pooling

3. **Caching Strategy**
   - Multi-level caching (app, Redis, DB)
   - Cache warming for common queries
   - Intelligent cache invalidation

4. **File Processing Optimization**
   - Streaming for large files
   - Chunk-based processing
   - Early validation and feedback

## Testing Strategy

### Unit Tests
- Service layer business logic
- PnL calculation algorithms
- Data parsing and validation
- API endpoint functionality

### Integration Tests
- Database operations
- External API integrations
- File upload and processing workflows
- End-to-end user scenarios

### Performance Tests
- Load testing for API endpoints
- File processing performance
- Database query performance
- Cache effectiveness

## Future Enhancements

### Planned Architecture Evolution

1. **Microservices Migration**
   - Extract file processing to dedicated service
   - Separate analytics computation service
   - API gateway for routing and authentication

2. **Event-Driven Architecture**
   - Message queues for async communication
   - Event sourcing for audit trails
   - CQRS for read/write separation

3. **Multi-Exchange Support**
   - Plugin architecture for exchange connectors
   - Unified data models across exchanges
   - Exchange-specific configuration management

4. **Real-time Features**
   - WebSocket connections for live updates
   - Stream processing for real-time analytics
   - Live portfolio tracking

5. **Advanced Analytics**
   - Machine learning pipeline integration
   - Time-series forecasting
   - Risk assessment automation
   - Portfolio optimization algorithms

---

This architecture provides a solid foundation for the HTX Trading Analytics Platform while maintaining flexibility for future enhancements and scaling requirements.