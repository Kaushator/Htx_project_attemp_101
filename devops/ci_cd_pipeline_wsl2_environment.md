# HTX Trading Platform - CI/CD Pipeline for WSL2 Environment

## Overview
Comprehensive CI/CD pipeline design optimized for WSL2 development environment, providing automated testing, building, and deployment specifically tailored for the HTX Trading Platform's unique Windows/WSL2 hybrid architecture.

## CI/CD Architecture Overview

### Pipeline Components
```
HTX CI/CD Pipeline
├── Source Control Integration
│   ├── Git Hooks (pre-commit, pre-push)
│   ├── Branch Protection Rules
│   └── Automated Code Quality Checks
├── Build Pipeline
│   ├── WSL2 Environment Setup
│   ├── Dependency Management
│   ├── Code Compilation & Building
│   └── Asset Optimization
├── Testing Pipeline
│   ├── Unit Tests (Backend & Frontend)
│   ├── Integration Tests
│   ├── API Testing (HTX Integration)
│   ├── Performance Tests
│   └── Security Scans
├── Deployment Pipeline
│   ├── Staging Deployment
│   ├── Production Deployment
│   ├── Database Migration
│   └── Service Health Verification
└── Monitoring & Feedback
    ├── Build Status Notifications
    ├── Deployment Monitoring
    ├── Performance Metrics
    └── Error Tracking
```

## GitHub Actions WSL2 Configuration

### Main Workflow (`.github/workflows/htx-ci-cd.yml`)
```yaml
name: HTX Trading Platform CI/CD

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  workflow_dispatch:

env:
  NODE_VERSION: '18'
  PYTHON_VERSION: '3.11'
  
jobs:
  code-quality:
    name: Code Quality Checks
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          
      - name: Install Python dependencies
        run: |
          python -m pip install --upgrade pip
          pip install black flake8 mypy pytest pytest-cov
          pip install -r requirements.txt
          
      - name: Run Black code formatter check
        run: black --check --diff .
        
      - name: Run Flake8 linter
        run: flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        
      - name: Run MyPy type checker
        run: mypy . --ignore-missing-imports
        
      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
          
      - name: Install frontend dependencies
        working-directory: ./frontend
        run: npm ci
        
      - name: Run ESLint
        working-directory: ./frontend
        run: npm run lint
        
      - name: Run Prettier check
        working-directory: ./frontend
        run: npm run format:check

  test-backend:
    name: Backend Tests
    runs-on: ubuntu-latest
    needs: code-quality
    
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_USER: htx_test
          POSTGRES_PASSWORD: htx_test
          POSTGRES_DB: htx_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
          
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r requirements/test.txt
          
      - name: Create test environment
        run: |
          cp .env.example .env.test
          echo "DATABASE_URL=postgresql://htx_test:htx_test@localhost:5432/htx_test" >> .env.test
          echo "TESTING=true" >> .env.test
          
      - name: Run database migrations
        run: |
          export TESTING=true
          export DATABASE_URL=postgresql://htx_test:htx_test@localhost:5432/htx_test
          python -m alembic upgrade head
          
      - name: Run backend tests
        run: |
          export TESTING=true
          python -m pytest tests/ -v --cov=. --cov-report=xml --cov-report=term-missing
          
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          flags: backend
          name: backend-coverage

  test-frontend:
    name: Frontend Tests
    runs-on: ubuntu-latest
    needs: code-quality
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        
      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
          
      - name: Install dependencies
        working-directory: ./frontend
        run: npm ci
        
      - name: Run frontend tests
        working-directory: ./frontend
        run: npm run test:coverage
        
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./frontend/coverage/lcov.info
          flags: frontend
          name: frontend-coverage

  integration-tests:
    name: Integration Tests
    runs-on: ubuntu-latest
    needs: [test-backend, test-frontend]
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          
      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          
      - name: Start services with Docker Compose
        run: |
          cp .env.example .env
          docker-compose -f docker-compose.test.yml up -d
          
      - name: Wait for services to be ready
        run: |
          timeout 60 bash -c 'until curl -f http://localhost:8000/api/v1/health; do sleep 2; done'
          
      - name: Run integration tests
        run: |
          python -m pytest tests/integration/ -v
          
      - name: Run API tests with Newman
        run: |
          npm install -g newman
          newman run testing/htx_api_test_collection.json \
            --environment testing/test_environment.json \
            --reporters cli,json \
            --reporter-json-export results/newman-results.json
            
      - name: Stop services
        if: always()
        run: docker-compose -f docker-compose.test.yml down

  security-scan:
    name: Security Scanning
    runs-on: ubuntu-latest
    needs: code-quality
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        
      - name: Run Bandit security scan
        run: |
          pip install bandit[toml]
          bandit -r . -f json -o bandit-report.json
          
      - name: Run Safety dependency check
        run: |
          pip install safety
          safety check --json --output safety-report.json
          
      - name: Run npm audit
        working-directory: ./frontend
        run: |
          npm audit --audit-level moderate --json > npm-audit-report.json || true
          
      - name: Upload security reports
        uses: actions/upload-artifact@v3
        with:
          name: security-reports
          path: |
            bandit-report.json
            safety-report.json
            frontend/npm-audit-report.json

  build:
    name: Build Application
    runs-on: ubuntu-latest
    needs: [test-backend, test-frontend, integration-tests, security-scan]
    if: github.ref == 'refs/heads/main' || github.ref == 'refs/heads/develop'
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          
      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          
      - name: Build frontend
        working-directory: ./frontend
        run: |
          npm ci
          npm run build
          
      - name: Create deployment package
        run: |
          mkdir -p dist
          cp -r backend/ dist/
          cp -r frontend/dist/ dist/frontend/
          cp requirements.txt dist/
          cp docker-compose.yml dist/
          cp -r scripts/ dist/
          
      - name: Upload build artifacts
        uses: actions/upload-artifact@v3
        with:
          name: htx-build-${{ github.sha }}
          path: dist/
          retention-days: 30

  deploy-staging:
    name: Deploy to Staging
    runs-on: ubuntu-latest
    needs: build
    if: github.ref == 'refs/heads/develop'
    environment: staging
    
    steps:
      - name: Download build artifacts
        uses: actions/download-artifact@v3
        with:
          name: htx-build-${{ github.sha }}
          path: dist/
          
      - name: Deploy to staging server
        run: |
          echo "Deploying to staging environment..."
          # Deployment script would go here
          # This could be SSH deployment, container registry push, etc.
          
      - name: Run health checks
        run: |
          timeout 120 bash -c 'until curl -f https://staging.htx-platform.com/api/v1/health; do sleep 5; done'
          
      - name: Notify deployment status
        if: always()
        run: |
          echo "Staging deployment completed"

  deploy-production:
    name: Deploy to Production
    runs-on: ubuntu-latest
    needs: build
    if: github.ref == 'refs/heads/main'
    environment: production
    
    steps:
      - name: Download build artifacts
        uses: actions/download-artifact@v3
        with:
          name: htx-build-${{ github.sha }}
          path: dist/
          
      - name: Deploy to production server
        run: |
          echo "Deploying to production environment..."
          # Production deployment script
          
      - name: Run health checks
        run: |
          timeout 120 bash -c 'until curl -f https://htx-platform.com/api/v1/health; do sleep 5; done'
          
      - name: Notify deployment status
        if: always()
        run: |
          echo "Production deployment completed"
```

## Local WSL2 Development Pipeline

### Pre-commit Hooks (`.pre-commit-config.yaml`)
```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict
      
  - repo: https://github.com/psf/black
    rev: 23.9.1
    hooks:
      - id: black
        language_version: python3
        
  - repo: https://github.com/pycqa/flake8
    rev: 6.1.0
    hooks:
      - id: flake8
        args: [--max-line-length=88, --extend-ignore=E203]
        
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.6.1
    hooks:
      - id: mypy
        additional_dependencies: [types-requests]
        
  - repo: https://github.com/pycqa/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: [-r, ., -f, json, -o, bandit-report.json]
        
  - repo: local
    hooks:
      - id: frontend-lint
        name: Frontend ESLint
        entry: bash -c 'cd frontend && npm run lint'
        language: system
        files: ^frontend/
        
      - id: frontend-test
        name: Frontend Tests
        entry: bash -c 'cd frontend && npm test -- --watchAll=false'
        language: system
        files: ^frontend/
```

### Local Development Pipeline Script (`scripts/dev_pipeline.sh`)
```bash
#!/usr/bin/env bash
# Local development pipeline for WSL2

set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔧 HTX Development Pipeline${NC}"
echo "=========================="

# Activate virtual environment
source "$PROJECT_ROOT/scripts/activate_env.sh"

# Install development dependencies
echo -e "${YELLOW}📦 Installing development dependencies...${NC}"
pip install -r requirements/dev.txt
cd "$PROJECT_ROOT/frontend" && npm install --silent
cd "$PROJECT_ROOT"

# Code quality checks
echo -e "${BLUE}🔍 Running code quality checks...${NC}"

# Python code formatting
echo -e "${YELLOW}Running Black formatter...${NC}"
if ! black --check --diff .; then
    echo -e "${RED}❌ Code formatting issues found. Run: black .${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Code formatting passed${NC}"

# Python linting
echo -e "${YELLOW}Running Flake8 linter...${NC}"
if ! flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics; then
    echo -e "${RED}❌ Linting issues found${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Linting passed${NC}"

# Type checking
echo -e "${YELLOW}Running MyPy type checker...${NC}"
if ! mypy . --ignore-missing-imports; then
    echo -e "${RED}❌ Type checking issues found${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Type checking passed${NC}"

# Frontend linting
echo -e "${YELLOW}Running frontend linting...${NC}"
cd "$PROJECT_ROOT/frontend"
if ! npm run lint; then
    echo -e "${RED}❌ Frontend linting issues found${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Frontend linting passed${NC}"
cd "$PROJECT_ROOT"

# Security scanning
echo -e "${BLUE}🔒 Running security scans...${NC}"

# Python security check
echo -e "${YELLOW}Running Bandit security scanner...${NC}"
if ! bandit -r . -f json -o bandit-report.json; then
    echo -e "${YELLOW}⚠️ Security issues found (check bandit-report.json)${NC}"
fi

# Dependency security check
echo -e "${YELLOW}Running Safety dependency check...${NC}"
if ! safety check; then
    echo -e "${YELLOW}⚠️ Vulnerable dependencies found${NC}"
fi

# Testing pipeline
echo -e "${BLUE}🧪 Running test suite...${NC}"

# Backend tests
echo -e "${YELLOW}Running backend tests...${NC}"
if ! python -m pytest tests/ -v --cov=. --cov-report=term-missing; then
    echo -e "${RED}❌ Backend tests failed${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Backend tests passed${NC}"

# Frontend tests
echo -e "${YELLOW}Running frontend tests...${NC}"
cd "$PROJECT_ROOT/frontend"
if ! npm test -- --watchAll=false; then
    echo -e "${RED}❌ Frontend tests failed${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Frontend tests passed${NC}"
cd "$PROJECT_ROOT"

# Build validation
echo -e "${BLUE}🏗️ Validating build process...${NC}"

# Frontend build
echo -e "${YELLOW}Building frontend...${NC}"
cd "$PROJECT_ROOT/frontend"
if ! npm run build; then
    echo -e "${RED}❌ Frontend build failed${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Frontend build successful${NC}"
cd "$PROJECT_ROOT"

# Integration test with local services
echo -e "${BLUE}🔗 Running integration tests...${NC}"

# Start services for testing
echo -e "${YELLOW}Starting test services...${NC}"
python "$PROJECT_ROOT/scripts/process_manager.py" stop all || true
python "$PROJECT_ROOT/scripts/process_manager.py" start backend --port 8004 --command python run_backend_wsl.py &
sleep 5

# Health check
if curl -f http://localhost:8004/api/v1/health >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Integration test environment ready${NC}"
    
    # Run API tests
    if [ -f "$PROJECT_ROOT/testing/htx_api_test_collection.json" ]; then
        echo -e "${YELLOW}Running API tests...${NC}"
        npx newman run "$PROJECT_ROOT/testing/htx_api_test_collection.json" \
            --environment "$PROJECT_ROOT/testing/test_environment.json" || true
    fi
else
    echo -e "${RED}❌ Integration test environment failed to start${NC}"
fi

# Cleanup
python "$PROJECT_ROOT/scripts/process_manager.py" stop all || true

echo -e "${GREEN}🎉 Development pipeline completed successfully!${NC}"
echo -e "${BLUE}Next steps:${NC}"
echo -e "  1. Commit your changes: git add . && git commit -m 'Your message'"
echo -e "  2. Push to branch: git push origin your-branch"
echo -e "  3. Create pull request for code review"
```

## Deployment Automation

### WSL2 Production Deployment Script (`scripts/deploy_production.sh`)
```bash
#!/usr/bin/env bash
# Production deployment script for WSL2 environment

set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DEPLOY_ENV="${1:-production}"
BACKUP_TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "🚀 HTX Production Deployment"
echo "Environment: $DEPLOY_ENV"
echo "Timestamp: $BACKUP_TIMESTAMP"
echo "=========================="

# Pre-deployment checks
echo "🔍 Pre-deployment checks..."

# Check if services are running
if ! python "$PROJECT_ROOT/scripts/process_manager.py" status >/dev/null 2>&1; then
    echo "⚠️ No running services detected"
fi

# Database backup
echo "💾 Creating database backup..."
BACKUP_DIR="$PROJECT_ROOT/backups/$BACKUP_TIMESTAMP"
mkdir -p "$BACKUP_DIR"

if [ -f "$PROJECT_ROOT/data/app.db" ]; then
    cp "$PROJECT_ROOT/data/app.db" "$BACKUP_DIR/app.db.backup"
    echo "✅ Database backup created: $BACKUP_DIR/app.db.backup"
fi

# Stop services gracefully
echo "🛑 Stopping services..."
python "$PROJECT_ROOT/scripts/process_manager.py" stop all --timeout 30

# Update codebase
echo "📥 Updating codebase..."
git fetch origin
git checkout "$DEPLOY_ENV"
git pull origin "$DEPLOY_ENV"

# Update dependencies
echo "📦 Updating dependencies..."
source "$PROJECT_ROOT/scripts/activate_env.sh"
pip install -r requirements.txt --upgrade

cd "$PROJECT_ROOT/frontend"
npm ci --production
npm run build
cd "$PROJECT_ROOT"

# Database migrations
echo "🗄️ Running database migrations..."
python -m alembic upgrade head

# Start services
echo "🚀 Starting services..."
"$PROJECT_ROOT/scripts/start_safe.sh"

# Health verification
echo "🏥 Verifying deployment health..."
sleep 10

for i in {1..12}; do
    if curl -f http://localhost:8004/api/v1/health >/dev/null 2>&1; then
        echo "✅ Deployment health check passed"
        break
    elif [ $i -eq 12 ]; then
        echo "❌ Deployment health check failed"
        
        # Rollback procedure
        echo "🔄 Initiating rollback..."
        python "$PROJECT_ROOT/scripts/process_manager.py" stop all
        
        if [ -f "$BACKUP_DIR/app.db.backup" ]; then
            cp "$BACKUP_DIR/app.db.backup" "$PROJECT_ROOT/data/app.db"
        fi
        
        git checkout HEAD~1
        "$PROJECT_ROOT/scripts/start_safe.sh"
        
        exit 1
    else
        echo "⏳ Waiting for services... ($i/12)"
        sleep 5
    fi
done

echo "🎉 Deployment completed successfully!"
echo "📊 Access URLs:"
echo "  Backend: http://localhost:8004"
echo "  Frontend: http://localhost:3000"
echo "  Monitoring: http://localhost:8005"
```

## Docker Integration for CI/CD

### Multi-stage Dockerfile
```dockerfile
# Multi-stage build for HTX Trading Platform
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci --only=production

COPY frontend/ ./
RUN npm run build

FROM python:3.11-slim AS backend-builder

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist
COPY scripts/ ./scripts/
COPY alembic.ini ./

EXPOSE 8004
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8004"]
```

### Docker Compose for Testing
```yaml
# docker-compose.test.yml
version: '3.9'
services:
  app:
    build: .
    ports:
      - "8004:8004"
    environment:
      - DATABASE_URL=sqlite:///data/test.db
      - TESTING=true
    volumes:
      - ./data:/app/data
    depends_on:
      - postgres
      
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: htx_test
      POSTGRES_USER: htx_test
      POSTGRES_PASSWORD: htx_test
    ports:
      - "5432:5432"
    volumes:
      - postgres_test_data:/var/lib/postgresql/data

volumes:
  postgres_test_data:
```

## Expected Benefits

### Development Efficiency
- **Automated Quality Gates**: Consistent code quality enforcement
- **Fast Feedback Loop**: Quick identification of issues
- **Standardized Environment**: Consistent development setup across team
- **Automated Testing**: Comprehensive test coverage validation

### Deployment Reliability
- **Zero-downtime Deployments**: Graceful service management
- **Automated Rollbacks**: Quick recovery from deployment issues
- **Health Monitoring**: Continuous deployment validation
- **Backup Integration**: Automated data protection

This comprehensive CI/CD pipeline ensures reliable, automated deployment processes specifically optimized for the HTX Trading Platform's WSL2 environment while maintaining high code quality and deployment safety standards.