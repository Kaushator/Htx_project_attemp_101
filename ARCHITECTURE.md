# HTX Trading Platform - Technical Architecture

## 🏗️ System Architecture Overview

HTX Trading Platform is built on a modern, scalable architecture designed for real-time trading analytics and data processing.

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   External APIs │
│   (React)       │    │   (FastAPI)     │    │                 │
│   Port: 3000    │◄──►│   Port: 8004    │◄──►│   HTX API       │
│                 │    │                 │    │   3Commas API   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   WebSocket     │    │   Database      │    │   File Storage  │
│   Real-time     │    │   SQLite/       │    │   CSV/Excel     │
│   Updates       │    │   PostgreSQL    │    │   Processing    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

---

## 🔧 Backend Architecture (FastAPI)

### Application Structure
```
backend/app/
├── main.py                      # FastAPI application entry point
├── core/                        # Core configuration
│   ├── config.py               # Pydantic settings management
│   ├── logging.py              # Structured logging setup
│   └── security.py             # Authentication & authorization
├── api/                         # API layer
│   └── v1/                     # API version 1
│       ├── router.py           # Main API router
│       └── endpoints/          # Individual endpoint modules
│           ├── health.py       # Health check endpoints
│           ├── files.py        # File upload/processing
│           ├── trades.py       # Trading data endpoints
│           ├── cashflow.py     # Cash flow analysis
│           ├── pnl.py          # P&L analytics
│           └── websocket.py    # WebSocket connections
├── models/                      # SQLAlchemy ORM models
│   ├── base.py                 # Base model class
│   ├── trade.py                # Trade data model
│   ├── file.py                 # File metadata model
│   └── user.py                 # User management model
├── schemas/                     # Pydantic request/response schemas
│   ├── trade.py                # Trade data schemas
│   ├── file.py                 # File operation schemas
│   └── pnl.py                  # P&L analysis schemas
├── services/                    # Business logic layer
│   ├── htx_client_real.py      # HTX API integration
│   ├── parser_csv.py           # CSV/Excel processing
│   ├── pnl_analyzer.py         # P&L calculation engine
│   ├── risk_calculator.py      # Risk metrics calculation
│   └── threecommas.py          # 3Commas API integration
├── db/                          # Database configuration
│   ├── session.py              # Async database sessions
│   ├── base.py                 # Database base configuration
│   └── init_db.py              # Database initialization
└── workers/                     # Background task processing
    ├── file_processor.py       # Async file processing
    └── data_sync.py            # External API synchronization
```

### Key Design Patterns

#### 1. Dependency Injection
```python
# Example: Database session injection
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session

@router.get("/trades/")
async def get_trades(db: AsyncSession = Depends(get_db)):
    return await trade_service.get_all(db)
```

#### 2. Repository Pattern
```python
class TradeRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, trade_data: TradeCreate) -> Trade:
        # Database operations
        pass
```

#### 3. Service Layer
```python
class PnLService:
    def __init__(self, trade_repo: TradeRepository):
        self.trade_repo = trade_repo
    
    async def calculate_pnl(self, period: str) -> PnLAnalysis:
        # Business logic
        pass
```

---

## 🎨 Frontend Architecture (React)

### Component Structure
```
frontend/src/
├── main.jsx                     # React application entry
├── App.jsx                      # Main application component
├── components/                  # Reusable components
│   ├── common/                  # Generic UI components
│   │   ├── Button.jsx
│   │   ├── Modal.jsx
│   │   └── LoadingSpinner.jsx
│   ├── forms/                   # Form components
│   │   ├── FileUpload.jsx       # Drag & drop file upload
│   │   └── TradeForm.jsx        # Trade data entry
│   ├── charts/                  # Data visualization
│   │   ├── PnLChart.jsx         # P&L time series
│   │   ├── PerformanceChart.jsx # Performance metrics
│   │   └── RiskChart.jsx        # Risk analysis charts
│   └── dashboard/               # Dashboard-specific components
│       ├── WebSocketStatus.jsx  # Real-time connection status
│       ├── MetricCard.jsx       # KPI display cards
│       └── DataTable.jsx        # Sortable data tables
├── pages/                       # Page-level components
│   ├── Dashboard.jsx            # Main dashboard page
│   ├── UltraSimpleDashboard.jsx # Simplified dashboard
│   ├── PnlAnalytics.jsx         # P&L analysis page
│   ├── RiskAnalysis.jsx         # Risk metrics page
│   ├── TransactionHistory.jsx   # Transaction listing
│   └── Settings.jsx             # Configuration page
├── hooks/                       # Custom React hooks
│   ├── useWebSocket.js          # WebSocket connection hook
│   ├── useHTXData.js           # HTX API data fetching
│   └── useFileUpload.js         # File upload management
├── services/                    # API integration
│   ├── api.js                   # Axios configuration
│   ├── htxService.js           # HTX API wrapper
│   └── fileService.js           # File operations
├── utils/                       # Utility functions
│   ├── dateHelpers.js           # Date/time utilities
│   ├── formatters.js            # Data formatting
│   └── validators.js            # Input validation
└── styles/                      # Styling
    ├── globals.css              # Global styles
    └── components/              # Component-specific styles
```

### State Management Strategy
- **Local State**: React hooks (useState, useReducer)
- **Server State**: React Query for API caching
- **WebSocket State**: Custom hooks for real-time data
- **Global State**: Context API for user preferences

---

## 🗄️ Database Design

### Entity Relationship Diagram
```
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│    Users    │       │    Files    │       │   Trades    │
├─────────────┤       ├─────────────┤       ├─────────────┤
│ id (PK)     │       │ id (PK)     │       │ id (PK)     │
│ username    │       │ filename    │       │ symbol      │
│ email       │◄─────┤│ user_id (FK)│       │ price       │
│ created_at  │      │ │ file_path   │       │ quantity    │
└─────────────┘      │ │ status      │       │ side        │
                     │ │ created_at  │       │ timestamp   │
                     │ └─────────────┘       │ file_id (FK)│
                     │                       │ pnl         │
                     │ ┌─────────────┐       │ fees        │
                     └►│ CashFlows   │       └─────────────┘
                       ├─────────────┤               │
                       │ id (PK)     │               │
                       │ amount      │               │
                       │ currency    │               │
                       │ type        │               │
                       │ trade_id(FK)│◄──────────────┘
                       │ created_at  │
                       └─────────────┘
```

### Database Models

#### Trade Model
```python
class Trade(Base):
    __tablename__ = "trades"
    
    id = Column(UUID, primary_key=True, default=uuid4)
    symbol = Column(String, nullable=False)
    side = Column(Enum(TradeSide), nullable=False)  # BUY/SELL
    price = Column(Numeric(18, 8), nullable=False)
    quantity = Column(Numeric(18, 8), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    file_id = Column(UUID, ForeignKey("files.id"))
    
    # Calculated fields
    value = Column(Numeric(18, 8))  # price * quantity
    fees = Column(Numeric(18, 8))
    pnl = Column(Numeric(18, 8))
    
    # Relationships
    file = relationship("File", back_populates="trades")
    cashflows = relationship("CashFlow", back_populates="trade")
```

#### File Model
```python
class File(Base):
    __tablename__ = "files"
    
    id = Column(UUID, primary_key=True, default=uuid4)
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer)
    mime_type = Column(String)
    status = Column(Enum(FileStatus), default=FileStatus.UPLOADED)
    
    # Processing info
    processed_at = Column(DateTime)
    error_message = Column(Text)
    records_processed = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    trades = relationship("Trade", back_populates="file", cascade="all, delete-orphan")
```

---

## 🔌 API Integration Layer

### HTX API Client
```python
class HTXClient:
    """Real HTX API client with proper authentication"""
    
    def __init__(self, access_key: str, secret_key: str):
        self.access_key = access_key
        self.secret_key = secret_key
        self.base_url = "https://api.huobi.pro"
    
    def _sign(self, method: str, url: str, params: dict) -> str:
        """Generate HMAC-SHA256 signature for HTX API"""
        # Implementation details...
    
    async def get_account_balance(self) -> dict:
        """Get account balance"""
        # Authenticated API call
    
    async def get_ticker(self, symbol: str) -> dict:
        """Get price ticker for symbol"""
        # Public API call
    
    async def get_order_history(self, symbol: str = None) -> List[dict]:
        """Get trading history"""
        # Authenticated API call
```

### WebSocket Manager
```python
class WebSocketManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        self.connections: List[WebSocket] = []
        self.htx_client = HTXClient()
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.append(websocket)
    
    async def broadcast_update(self, message: dict):
        for connection in self.connections:
            await connection.send_json(message)
    
    async def start_price_stream(self):
        """Stream real-time price updates"""
        while True:
            # Fetch latest prices and broadcast
            await asyncio.sleep(1)
```

---

## 📊 Data Processing Pipeline

### File Processing Workflow
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Upload    │───►│   Validate  │───►│    Parse    │───►│    Store    │
│   File      │    │   Format    │    │   Content   │    │   Database  │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │                   │
       ▼                   ▼                   ▼                   ▼
 File Storage       Format Check        CSV/Excel         Trade Records
 (temp location)    Size Limits         Processing        + Metadata
```

### CSV Processing Engine
```python
class CSVParser:
    """Processes CSV files and extracts trade data"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.required_columns = ['symbol', 'side', 'price', 'quantity', 'timestamp']
    
    async def validate(self) -> bool:
        """Validate CSV structure and content"""
        # Check headers, data types, required fields
    
    async def parse(self) -> List[TradeCreate]:
        """Parse CSV and return trade objects"""
        df = pd.read_csv(self.file_path)
        # Data cleaning and transformation
        return [TradeCreate(**row) for row in df.to_dict('records')]
    
    async def process_async(self, db: AsyncSession) -> ProcessingResult:
        """Full async processing pipeline"""
        # Validate → Parse → Store → Calculate metrics
```

---

## 🔄 Real-Time Architecture

### WebSocket Communication Flow
```
Frontend                Backend               External APIs
   │                      │                      │
   │ ── Connect WS ────►  │                      │
   │ ◄── Accept ────────  │                      │
   │                      │                      │
   │                      │ ── Poll HTX API ──► │
   │                      │ ◄── Price Data ──── │
   │ ◄── Broadcast ─────  │                      │
   │                      │                      │
   │ ── Request Update ─► │                      │
   │ ◄── Response ──────  │                      │
```

### Event-Driven Updates
```python
class EventManager:
    """Manages real-time events and notifications"""
    
    async def on_price_update(self, symbol: str, price: float):
        """Handle price update events"""
        event = {
            "type": "price_update",
            "symbol": symbol,
            "price": price,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.websocket_manager.broadcast_update(event)
    
    async def on_trade_processed(self, trade_id: str):
        """Handle trade processing completion"""
        event = {
            "type": "trade_processed",
            "trade_id": trade_id,
            "message": "Trade successfully processed"
        }
        await self.websocket_manager.broadcast_update(event)
```

---

## 🔒 Security Architecture

### Authentication Strategy
- **API Keys**: HTX and 3Commas API authentication
- **File Security**: Temporary file storage with cleanup
- **Input Validation**: Pydantic schemas for all inputs
- **Rate Limiting**: API request throttling
- **CORS**: Controlled cross-origin access

### Data Protection
```python
class SecurityConfig:
    """Security configuration and utilities"""
    
    @staticmethod
    def encrypt_api_key(key: str) -> str:
        """Encrypt sensitive API keys"""
        from cryptography.fernet import Fernet
        # Encryption implementation
    
    @staticmethod
    def validate_file_upload(file: UploadFile) -> bool:
        """Validate uploaded file security"""
        # File type, size, and content validation
```

---

## 📈 Performance Optimization

### Database Optimization
- **Async Operations**: All database calls are asynchronous
- **Connection Pooling**: SQLAlchemy async pool management
- **Query Optimization**: Efficient joins and aggregations
- **Indexing Strategy**: Optimized indexes for trade queries

### API Performance
- **Caching**: Redis integration for frequently accessed data
- **Background Tasks**: Async processing for file uploads
- **Request Batching**: Bulk operations for large datasets
- **Connection Reuse**: HTTP client connection pooling

### Frontend Optimization
- **Code Splitting**: Lazy loading of dashboard components
- **Memoization**: React.memo for expensive components
- **Virtual Scrolling**: Efficient rendering of large data sets
- **WebSocket Throttling**: Controlled update frequency

---

## 🚀 Deployment Architecture

### WSL Development Environment
```bash
# Project structure optimized for WSL
/mnt/e/Htx_project_attemp_101/
├── .venv_wsl/              # Linux-compatible virtual environment
├── backend/                # Python backend application
├── frontend/               # Node.js frontend application
├── scripts/                # Deployment and utility scripts
│   ├── wsl_setup.sh       # Environment setup
│   ├── full_restart.sh    # Complete restart with health checks
│   └── test_performance.py # Performance testing
└── logs/                   # Application logs
```

### Production Considerations
- **Container Strategy**: Docker support for consistent deployment
- **Load Balancing**: Multiple backend instances
- **Database Migration**: PostgreSQL for production
- **Monitoring**: Comprehensive logging and metrics
- **Backup Strategy**: Automated data backup and recovery

---

## 🔧 Development Tools Integration

### Testing Framework
```python
# pytest configuration for async testing
@pytest.mark.asyncio
async def test_htx_api_integration():
    """Test HTX API client functionality"""
    client = HTXClient(test_access_key, test_secret_key)
    balance = await client.get_account_balance()
    assert balance is not None

# Frontend testing with React Testing Library
test('dashboard renders correctly', () => {
    render(<Dashboard />);
    expect(screen.getByText('HTX Trading Platform')).toBeInTheDocument();
});
```

### Code Quality Tools
- **Backend**: Black, isort, flake8, mypy
- **Frontend**: ESLint, Prettier, TypeScript
- **Database**: Alembic migrations
- **API**: Automated OpenAPI documentation

---

This architecture provides a robust, scalable foundation for the HTX Trading Platform, with clear separation of concerns, comprehensive testing, and production-ready deployment capabilities.
