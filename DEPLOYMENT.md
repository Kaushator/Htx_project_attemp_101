# HTX Trading Platform - Deployment Guide

## 🚀 Production Deployment Guide

This document provides comprehensive instructions for deploying the HTX Trading Platform to production environments.

---

## 📋 Table of Contents

1. [System Requirements](#system-requirements)
2. [Pre-deployment Checklist](#pre-deployment-checklist)
3. [WSL Deployment](#wsl-deployment)
4. [Docker Deployment](#docker-deployment)
5. [Production Configuration](#production-configuration)
6. [Monitoring & Maintenance](#monitoring--maintenance)
7. [Security Guidelines](#security-guidelines)
8. [Troubleshooting](#troubleshooting)

---

## System Requirements

### Minimum Requirements
- **OS**: Ubuntu 20.04+ or WSL 2
- **Python**: 3.12+
- **Node.js**: 18+
- **Memory**: 4GB RAM
- **Storage**: 10GB free space
- **Network**: Stable internet connection for API calls

### Recommended Requirements
- **OS**: Ubuntu 22.04 LTS
- **Python**: 3.12.3
- **Node.js**: 18.17+
- **Memory**: 8GB RAM
- **Storage**: 50GB SSD
- **Database**: PostgreSQL 14+ (for production)

### External Dependencies
- **HTX API Access**: Valid API credentials
- **3Commas API** (optional): For advanced integrations
- **SSL Certificate**: For HTTPS in production

---

## Pre-deployment Checklist

### ✅ Environment Verification
```bash
# Check system versions
python3 --version    # Should be 3.12+
node --version       # Should be 18+
npm --version        # Should be 9+

# Check WSL (if applicable)
wsl --version
```

### ✅ Repository Preparation
```bash
# Clone repository
git clone <repository-url>
cd Htx_project_attemp_101

# Verify file structure
ls -la scripts/
ls -la backend/
ls -la frontend/
```

### ✅ Dependencies Check
```bash
# Backend dependencies
cd backend && cat requirements.txt

# Frontend dependencies  
cd frontend && cat package.json
```

---

## WSL Deployment

### Quick Deployment (Recommended)
```bash
# One-command deployment with full testing
wsl -d Ubuntu -- bash -c "cd /mnt/e/Htx_project_attemp_101 && ./scripts/full_restart.sh"
```

This script will:
1. Stop all existing processes
2. Verify WSL environment
3. Install/update dependencies
4. Start backend and frontend services
5. Run comprehensive health tests
6. Provide detailed status report

### Manual Deployment Steps

#### 1. Environment Setup
```bash
cd /mnt/e/Htx_project_attemp_101

# Setup WSL environment
chmod +x scripts/wsl_setup.sh
./scripts/wsl_setup.sh

# Activate virtual environment
source .venv_wsl/bin/activate
```

#### 2. Configuration
```bash
# Copy environment template
cp backend/env.example backend/.env

# Edit configuration
nano backend/.env
```

Required environment variables:
```env
# HTX API Configuration
HTX_ACCESS_KEY=your_access_key_here
HTX_SECRET_KEY=your_secret_key_here
HTX_BASE_URL=https://api.huobi.pro

# Database Configuration
DATABASE_URL=sqlite+aiosqlite:///./data/app.db
# For PostgreSQL: postgresql+asyncpg://user:pass@localhost/dbname

# Application Configuration
DEBUG=false
LOG_LEVEL=INFO
ENABLE_BACKGROUND_TASKS=true

# Security
SECRET_KEY=your-secret-key-here
FERNET_KEY=your-fernet-encryption-key
```

#### 3. Database Setup
```bash
cd backend

# Run migrations
alembic upgrade head

# Verify database
python -c "from app.db.session import engine; print('Database OK')"
```

#### 4. Service Startup
```bash
# Start backend (production mode)
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8004 --workers 4

# Start frontend (production build)
cd frontend
npm run build
npm run preview -- --host 0.0.0.0 --port 3000
```

---

## Docker Deployment

### Docker Configuration

#### Dockerfile (Backend)
```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY backend/ .

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8004"]
```

#### Dockerfile (Frontend)
```dockerfile
FROM node:18-alpine

WORKDIR /app

# Install dependencies
COPY frontend/package*.json ./
RUN npm ci --only=production

# Copy source and build
COPY frontend/ .
RUN npm run build

# Serve with nginx
FROM nginx:alpine
COPY --from=0 /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 3000
CMD ["nginx", "-g", "daemon off;"]
```

#### Docker Compose
```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: backend/Dockerfile
    ports:
      - "8004:8004"
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:password@db:5432/htx_trading
      - HTX_ACCESS_KEY=${HTX_ACCESS_KEY}
      - HTX_SECRET_KEY=${HTX_SECRET_KEY}
    depends_on:
      - db
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs

  frontend:
    build:
      context: .
      dockerfile: frontend/Dockerfile
    ports:
      - "3000:3000"
    depends_on:
      - backend

  db:
    image: postgres:14
    environment:
      - POSTGRES_DB=htx_trading
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

#### Deployment Commands
```bash
# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f

# Scale backend
docker-compose up -d --scale backend=3

# Stop services
docker-compose down
```

---

## Production Configuration

### Backend Configuration (backend/.env)
```env
# Production Settings
DEBUG=false
LOG_LEVEL=INFO
ENABLE_BACKGROUND_TASKS=true

# Database (PostgreSQL recommended)
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/htx_trading

# Security
SECRET_KEY=your-super-secret-key-32-characters
FERNET_KEY=your-fernet-encryption-key-here

# API Configuration
HTX_ACCESS_KEY=your_production_htx_access_key
HTX_SECRET_KEY=your_production_htx_secret_key
HTX_BASE_URL=https://api.huobi.pro

# CORS Settings
ALLOWED_ORIGINS=["https://yourdomain.com", "https://www.yourdomain.com"]

# Rate Limiting
API_RATE_LIMIT=100
API_RATE_WINDOW=60

# File Upload
MAX_FILE_SIZE=10485760  # 10MB
UPLOAD_DIRECTORY=/app/data/uploads
```

### Frontend Configuration (frontend/.env.production)
```env
VITE_API_BASE_URL=https://api.yourdomain.com
VITE_WS_URL=wss://api.yourdomain.com/ws
VITE_APP_NAME=HTX Trading Platform
VITE_APP_VERSION=1.0.0
```

### Nginx Configuration
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # API
    location /api/ {
        proxy_pass http://localhost:8004;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # WebSocket
    location /ws {
        proxy_pass http://localhost:8004;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

---

## Monitoring & Maintenance

### Health Monitoring
```bash
# Automated health check script
#!/bin/bash
# health_check.sh

# Check backend health
backend_status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8004/api/v1/health)
if [ "$backend_status" != "200" ]; then
    echo "Backend unhealthy: $backend_status"
    # Restart backend service
    systemctl restart htx-backend
fi

# Check frontend
frontend_status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000)
if [ "$frontend_status" != "200" ]; then
    echo "Frontend unhealthy: $frontend_status"
    # Restart frontend service
    systemctl restart htx-frontend
fi

# Check disk space
disk_usage=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$disk_usage" -gt 85 ]; then
    echo "Disk usage high: $disk_usage%"
    # Cleanup old logs
    find /app/logs -name "*.log" -mtime +7 -delete
fi
```

### Log Management
```bash
# Log rotation configuration (/etc/logrotate.d/htx-trading)
/app/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 www-data www-data
    postrotate
        systemctl reload htx-backend
    endscript
}
```

### Backup Strategy
```bash
#!/bin/bash
# backup.sh

# Database backup
pg_dump htx_trading > /backups/htx_trading_$(date +%Y%m%d_%H%M%S).sql

# Application data backup
tar -czf /backups/htx_data_$(date +%Y%m%d_%H%M%S).tar.gz /app/data

# Cleanup old backups (keep 30 days)
find /backups -name "*.sql" -mtime +30 -delete
find /backups -name "*.tar.gz" -mtime +30 -delete
```

---

## Security Guidelines

### API Security
- **HTTPS Only**: All communication must use SSL/TLS
- **API Key Encryption**: Use Fernet encryption for storing API keys
- **Rate Limiting**: Implement request rate limiting
- **Input Validation**: Validate all input data
- **CORS Policy**: Restrict cross-origin requests

### File Upload Security
```python
# Secure file upload configuration
ALLOWED_EXTENSIONS = ['.csv', '.xlsx', '.xls']
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
UPLOAD_SCAN_ENABLED = True  # Virus scanning
```

### Database Security
- **Connection Encryption**: Use SSL for database connections
- **User Permissions**: Minimal database user privileges
- **Regular Updates**: Keep PostgreSQL updated
- **Backup Encryption**: Encrypt database backups

### System Security
```bash
# Firewall configuration
ufw allow 22/tcp     # SSH
ufw allow 80/tcp     # HTTP
ufw allow 443/tcp    # HTTPS
ufw enable

# Fail2ban configuration for SSH protection
apt-get install fail2ban
```

---

## Troubleshooting

### Common Issues

#### 1. Backend Won't Start
```bash
# Check Python environment
source .venv_wsl/bin/activate
python --version

# Check dependencies
pip install -r backend/requirements.txt

# Check database connection
python -c "from app.db.session import engine; print('DB OK')"

# Check logs
tail -f logs/backend.log
```

#### 2. Frontend Build Errors
```bash
# Clear cache and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install

# Check Node version
node --version  # Should be 18+

# Try development mode
npm run dev
```

#### 3. Database Migration Issues
```bash
# Check migration status
cd backend
alembic current

# Reset migrations (CAUTION: Data loss)
alembic downgrade base
alembic upgrade head

# Manual migration
alembic revision --autogenerate -m "description"
alembic upgrade head
```

#### 4. WebSocket Connection Problems
```bash
# Check WebSocket endpoint
curl -i -N -H "Connection: Upgrade" \
     -H "Upgrade: websocket" \
     -H "Sec-WebSocket-Key: SGVsbG8sIHdvcmxkIQ==" \
     -H "Sec-WebSocket-Version: 13" \
     http://localhost:8004/api/v1/ws

# Check nginx configuration
nginx -t && systemctl reload nginx
```

#### 5. HTX API Authentication
```bash
# Test API credentials
cd backend
python -c "
from app.services.htx_client_real import htx_client
import asyncio
result = asyncio.run(htx_client.get_account_balance())
print(result)
"
```

### Performance Optimization

#### Database Optimization
```sql
-- Create indexes for frequently queried columns
CREATE INDEX idx_trades_symbol ON trades(symbol);
CREATE INDEX idx_trades_timestamp ON trades(timestamp);
CREATE INDEX idx_trades_symbol_timestamp ON trades(symbol, timestamp);

-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM trades WHERE symbol = 'BTCUSDT';
```

#### Backend Optimization
```python
# Enable response compression
from fastapi.middleware.gzip import GZipMiddleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Connection pooling
DATABASE_URL = "postgresql+asyncpg://user:pass@localhost/db?pool_size=20&max_overflow=30"
```

#### Frontend Optimization
```javascript
// Code splitting
const PnlAnalytics = lazy(() => import('./pages/PnlAnalytics'));

// Memoization
const ExpensiveComponent = memo(({ data }) => {
    return <div>{/* Heavy computation */}</div>;
});
```

---

## Production Checklist

### Pre-Launch ✅
- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] SSL certificates installed
- [ ] Backup strategy implemented
- [ ] Monitoring setup complete
- [ ] Security audit completed
- [ ] Performance testing done
- [ ] Documentation updated

### Launch Day ✅
- [ ] Deploy to production environment
- [ ] Verify all endpoints functional
- [ ] Test HTX API integration
- [ ] Verify file upload functionality
- [ ] Test WebSocket connections
- [ ] Monitor error logs
- [ ] Performance metrics baseline
- [ ] User acceptance testing

### Post-Launch ✅
- [ ] Monitor system performance
- [ ] Review error logs daily
- [ ] Backup verification
- [ ] Security monitoring
- [ ] User feedback collection
- [ ] Performance optimization
- [ ] Regular updates and patches

---

This deployment guide ensures a robust, secure, and maintainable production environment for the HTX Trading Platform.
