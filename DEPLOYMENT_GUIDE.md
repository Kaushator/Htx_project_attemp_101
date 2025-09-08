# HTX Trading Platform - Deployment Guide

This guide provides comprehensive instructions for deploying the HTX Trading Platform in both development and production environments.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Development Deployment](#development-deployment)
3. [Production Deployment](#production-deployment)
4. [Environment Configuration](#environment-configuration)
5. [Service Management](#service-management)
6. [Monitoring and Maintenance](#monitoring-and-maintenance)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements
- Docker Engine 20.10 or higher
- Docker Compose 1.29 or higher
- 4GB RAM minimum (8GB recommended for production)
- 10GB free disk space
- Internet connectivity for initial setup

### Required Tools
- Git
- Docker CLI
- Docker Compose CLI
- Text editor or IDE

### HTX API Access
- HTX API Key
- HTX Secret Key
- Valid HTX account with trading permissions

## Development Deployment

### Quick Start
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd htx-trading-platform
   ```

2. Configure environment variables:
   ```bash
   cp backend/.env.docker backend/.env
   # Edit backend/.env with your HTX API credentials
   ```

3. Start the development environment:
   ```bash
   docker-compose up --build
   ```

4. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Development Environment Features
- Hot reloading for frontend development
- Debug logging enabled
- SQLite database for local development
- Single instance services

## Production Deployment

### Production Setup Steps

1. Prepare the production environment:
   ```bash
   # Clone repository
   git clone <repository-url>
   cd htx-trading-platform
   
   # Create production environment file
   cp backend/.env.docker backend/.env
   # Edit with production values
   ```

2. Configure SSL certificates (if using custom domain):
   ```bash
   mkdir -p nginx/ssl
   # Place your SSL certificate and key files in this directory
   ```

3. Update production configuration:
   ```bash
   # Edit docker-compose.prod.yml
   # Update domain names, passwords, and resource allocations
   ```

4. Initialize the database:
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml run --rm api alembic upgrade head
   ```

5. Start production services:
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
   ```

6. Verify deployment:
   ```bash
   # Check service status
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml ps
   
   # Check logs
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml logs
   ```

### Production Environment Features
- Multi-container deployment
- PostgreSQL database
- Nginx reverse proxy with SSL support
- Resource limits and scaling
- Monitoring stack (Prometheus/Grafana)
- Health checks and auto-restart

## Environment Configuration

### Backend Environment Variables
Create `backend/.env` with the following variables:

```env
# HTX API Credentials
HTX_API_KEY=your_htx_api_key
HTX_SECRET_KEY=your_htx_secret_key

# Database Configuration
DATABASE_URL=sqlite+aiosqlite:///./data/app.db
REDIS_URL=redis://redis:6379

# Application Settings
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false
LOG_LEVEL=info

# Security Settings
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Frontend Environment Variables
Frontend configuration is handled through build-time variables in `docker-compose.yml`:

```yaml
environment:
  - VITE_API_URL=http://localhost:8000  # Development
  # - VITE_API_URL=https://api.yourdomain.com  # Production
```

### Production-Specific Configuration
In `docker-compose.prod.yml`, update the following:

1. Database credentials:
   ```yaml
   environment:
     POSTGRES_PASSWORD: your_secure_password
   ```

2. Grafana admin password:
   ```yaml
   environment:
     GF_SECURITY_ADMIN_PASSWORD: your_admin_password
   ```

3. Resource allocations based on your infrastructure.

## Service Management

### Starting Services
```bash
# Development
docker-compose up -d

# Production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Stopping Services
```bash
# Development
docker-compose down

# Production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml down
```

### Restarting Services
```bash
# Restart specific service
docker-compose restart api

# Restart all services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml restart
```

### Viewing Logs
```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs api

# Follow logs in real-time
docker-compose logs -f
```

### Scaling Services
```bash
# Scale API services (production only)
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --scale api=3
```

## Monitoring and Maintenance

### Health Checks
All services include built-in health checks:
- API: `http://localhost:8000/api/v1/health`
- Frontend: `http://localhost:3000/`
- Redis: `redis-cli ping`
- Database: `pg_isready` (production)

### Monitoring Stack
The production environment includes:
- Prometheus for metrics collection
- Grafana for dashboard visualization
- Default dashboards for system and application metrics

Access Grafana at: `http://localhost:3001`
Default credentials: admin / admin_password_change_me

### Database Maintenance
Regular maintenance tasks:

1. Database backups:
   ```bash
   docker-compose exec db pg_dump -U htx htx > backup.sql
   ```

2. Database cleanup:
   ```bash
   docker-compose exec api alembic revision --autogenerate -m "Migration description"
   docker-compose exec api alembic upgrade head
   ```

### Log Management
Logs are stored in the `logs` directory:
- API logs: `logs/api/`
- Frontend logs: `logs/nginx/`
- Database logs: `logs/db/` (production)

## Troubleshooting

### Common Issues and Solutions

#### 1. Services Not Starting
```bash
# Check service status
docker-compose ps

# Check logs for specific service
docker-compose logs api

# Rebuild containers
docker-compose down
docker-compose up --build
```

#### 2. Database Connection Issues
```bash
# Check database connectivity
docker-compose exec api python -c "import asyncio; from app.db.session import database; asyncio.run(database.connect())"

# Verify database URL in .env file
```

#### 3. API Authentication Failures
```bash
# Verify HTX API credentials
docker-compose exec api python -c "from app.core.config import settings; print(settings.HTX_API_KEY[:5] + '...')"

# Check credential format and permissions
```

#### 4. Frontend Not Loading
```bash
# Check nginx configuration
docker-compose exec frontend nginx -t

# Verify API connectivity from frontend
docker-compose exec frontend curl http://api:8000/api/v1/health
```

#### 5. WebSocket Connection Issues
```bash
# Check WebSocket endpoint
curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" -H "Host: localhost:8000" -H "Origin: http://localhost:3000" http://localhost:8000/ws

# Verify nginx WebSocket configuration
```

### Performance Tuning

#### Resource Allocation
Adjust resource limits in `docker-compose.prod.yml` based on your infrastructure:
```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 2G
    reservations:
      cpus: '1.0'
      memory: 1G
```

#### Database Optimization
For high-traffic environments:
1. Increase PostgreSQL shared_buffers
2. Tune checkpoint settings
3. Optimize query indexes

#### API Scaling
For production environments:
1. Increase uvicorn workers
2. Adjust replica count
3. Optimize database connection pooling

### Security Considerations

#### Credential Management
- Never commit credentials to version control
- Use environment variables for sensitive data
- Rotate API keys regularly
- Implement proper access controls

#### Network Security
- Use HTTPS in production
- Restrict external access to necessary ports only
- Implement proper firewall rules
- Regular security updates

#### Container Security
- Keep base images updated
- Run containers as non-root users
- Implement proper file permissions
- Regular vulnerability scanning

## Backup and Recovery

### Data Backup Strategy
1. Database backups:
   ```bash
   # PostgreSQL backup (production)
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml exec db pg_dump -U htx htx > backup_$(date +%Y%m%d).sql
   
   # SQLite backup (development)
   cp data/app.db backups/app_$(date +%Y%m%d).db
   ```

2. Configuration backups:
   - Backup `.env` files
   - Backup SSL certificates
   - Backup custom configurations

### Disaster Recovery
1. Restore database from backup:
   ```bash
   # PostgreSQL restore
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml exec -T db psql -U htx htx < backup.sql
   ```

2. Rebuild and restart services:
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml down
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
   ```

## Updates and Maintenance

### Updating the Application
1. Pull the latest code:
   ```bash
   git pull origin main
   ```

2. Rebuild containers:
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml build --no-cache
   ```

3. Apply database migrations:
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml run --rm api alembic upgrade head
   ```

4. Restart services:
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml down
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
   ```

### Version Management
- Track releases with Git tags
- Maintain changelogs
- Test updates in staging environment
- Implement rollback procedures

This deployment guide ensures successful deployment and operation of the HTX Trading Platform in both development and production environments.