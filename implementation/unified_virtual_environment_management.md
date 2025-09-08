# HTX Trading Platform - Unified Virtual Environment Management

## Overview
This document outlines the strategy for consolidating multiple conflicting virtual environments (`.venv_wsl/`, `.venv_wsl2/`, `.venv/`) into a single unified `.venv` environment that works consistently across Windows and WSL2.

## Current Environment Issues

### Identified Problems
1. **Multiple Virtual Environments**:
   - `.venv/` - Windows-specific environment
   - `.venv_wsl/` - Legacy WSL environment  
   - `.venv_wsl2/` - Current WSL2 environment
   - Causes dependency conflicts and version mismatches

2. **Inconsistent Activation Patterns**:
   - Different activation scripts across platforms
   - Hardcoded environment paths in scripts
   - Manual environment switching required

3. **Dependency Synchronization Issues**:
   - Package versions drift between environments
   - Missing dependencies in some environments
   - Redundant package installations

## Unified Environment Strategy

### 1. Single Virtual Environment Approach

#### Target Structure
```
htx_project/
├── .venv/                    # Single unified environment
│   ├── bin/                  # Linux/WSL executables
│   ├── Scripts/              # Windows executables
│   ├── lib/                  # Python packages
│   └── pyvenv.cfg           # Environment configuration
├── requirements/             # Dependency management
│   ├── base.txt             # Core dependencies
│   ├── dev.txt              # Development dependencies
│   ├── prod.txt             # Production dependencies
│   └── wsl2.txt             # WSL2-specific dependencies
└── scripts/
    ├── activate_env.sh      # Universal activation script
    └── activate_env.bat     # Windows activation script
```

### 2. Environment Detection and Activation

#### Universal Activation Script (`scripts/activate_env.sh`)
```bash
#!/bin/bash
# Universal virtual environment activation for HTX Project

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="$PROJECT_ROOT/.venv"

# Environment detection
detect_environment() {
    if grep -q "microsoft" /proc/version 2>/dev/null; then
        if grep -q "WSL2" /proc/version 2>/dev/null; then
            echo "WSL2"
        else
            echo "WSL1"
        fi
    elif [[ "$OS" == "Windows_NT" ]]; then
        echo "Windows"
    else
        echo "Linux"
    fi
}

# Create unified virtual environment
create_unified_venv() {
    local env_type="$1"
    
    echo "🔧 Creating unified virtual environment for $env_type..."
    
    # Remove old environments
    rm -rf "$PROJECT_ROOT/.venv_wsl" "$PROJECT_ROOT/.venv_wsl2" 2>/dev/null || true
    
    # Create new unified environment
    if [ ! -d "$VENV_DIR" ]; then
        python3 -m venv "$VENV_DIR"
    fi
    
    # Install dependencies based on environment
    source "$VENV_DIR/bin/activate"
    pip install --upgrade pip
    
    case "$env_type" in
        "WSL2"|"WSL1")
            pip install -r "$PROJECT_ROOT/requirements/base.txt"
            pip install -r "$PROJECT_ROOT/requirements/wsl2.txt"
            ;;
        "Windows")
            pip install -r "$PROJECT_ROOT/requirements/base.txt"
            pip install -r "$PROJECT_ROOT/requirements/dev.txt"
            ;;
        "Linux")
            pip install -r "$PROJECT_ROOT/requirements/base.txt"
            pip install -r "$PROJECT_ROOT/requirements/prod.txt"
            ;;
    esac
    
    echo "✅ Unified virtual environment created successfully"
}

# Activate virtual environment
activate_venv() {
    if [ ! -d "$VENV_DIR" ]; then
        echo "⚠️ Virtual environment not found. Creating..."
        create_unified_venv "$(detect_environment)"
    fi
    
    source "$VENV_DIR/bin/activate"
    echo "✅ Virtual environment activated: $VIRTUAL_ENV"
    
    # Verify critical packages
    python -c "
import sys
required_packages = ['fastapi', 'sqlalchemy', 'pandas', 'scikit-learn']
missing = []
for pkg in required_packages:
    try:
        __import__(pkg)
    except ImportError:
        missing.append(pkg)

if missing:
    print(f'⚠️ Missing packages: {missing}')
    print('Run: pip install -r requirements/base.txt')
    sys.exit(1)
else:
    print('✅ All critical packages available')
"
}

# Main execution
main() {
    echo "🚀 HTX Project - Virtual Environment Manager"
    echo "Environment: $(detect_environment)"
    echo "Project Root: $PROJECT_ROOT"
    
    activate_venv
}

# Allow sourcing this script
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
```

#### Windows Activation Script (`scripts/activate_env.bat`)
```batch
@echo off
REM Universal virtual environment activation for HTX Project (Windows)

setlocal enabledelayedexpansion

set "PROJECT_ROOT=%~dp0.."
set "VENV_DIR=%PROJECT_ROOT%\.venv"

echo 🚀 HTX Project - Virtual Environment Manager
echo Environment: Windows
echo Project Root: %PROJECT_ROOT%

REM Check if virtual environment exists
if not exist "%VENV_DIR%" (
    echo ⚠️ Virtual environment not found. Creating...
    call :create_unified_venv
)

REM Activate virtual environment
if exist "%VENV_DIR%\Scripts\activate.bat" (
    call "%VENV_DIR%\Scripts\activate.bat"
    echo ✅ Virtual environment activated: %VIRTUAL_ENV%
) else (
    echo ❌ Failed to activate virtual environment
    exit /b 1
)

REM Verify critical packages
python -c "
import sys
required_packages = ['fastapi', 'sqlalchemy', 'pandas', 'scikit-learn']
missing = []
for pkg in required_packages:
    try:
        __import__(pkg)
    except ImportError:
        missing.append(pkg)

if missing:
    print(f'⚠️ Missing packages: {missing}')
    print('Run: pip install -r requirements/base.txt')
    sys.exit(1)
else:
    print('✅ All critical packages available')
"

goto :eof

:create_unified_venv
echo 🔧 Creating unified virtual environment for Windows...

REM Remove old environments
if exist "%PROJECT_ROOT%\.venv_wsl" rmdir /s /q "%PROJECT_ROOT%\.venv_wsl" 2>nul
if exist "%PROJECT_ROOT%\.venv_wsl2" rmdir /s /q "%PROJECT_ROOT%\.venv_wsl2" 2>nul

REM Create new unified environment
python -m venv "%VENV_DIR%"

REM Install dependencies
call "%VENV_DIR%\Scripts\activate.bat"
pip install --upgrade pip
pip install -r "%PROJECT_ROOT%\requirements\base.txt"
pip install -r "%PROJECT_ROOT%\requirements\dev.txt"

echo ✅ Unified virtual environment created successfully
goto :eof
```

### 3. Dependency Management System

#### Base Dependencies (`requirements/base.txt`)
```
# Core application dependencies
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
alembic==1.12.1
pandas==2.1.3
numpy==1.25.2
scikit-learn==1.3.2
aiohttp==3.9.1
pydantic==2.5.0
python-multipart==0.0.6
jinja2==3.1.2
python-dotenv==1.0.0
```

#### Development Dependencies (`requirements/dev.txt`)
```
# Development and testing dependencies
-r base.txt
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
black==23.11.0
flake8==6.1.0
mypy==1.7.1
pre-commit==3.5.0
ipython==8.17.2
jupyter==1.0.0
httpx==0.25.2
```

#### Production Dependencies (`requirements/prod.txt`)
```
# Production-specific dependencies
-r base.txt
gunicorn==21.2.0
psycopg2-binary==2.9.9
redis==5.0.1
celery==5.3.4
sentry-sdk==1.38.0
```

#### WSL2-Specific Dependencies (`requirements/wsl2.txt`)
```
# WSL2-specific optimizations and tools
-r base.txt
psutil==5.9.6
python-magic==0.4.27
watchdog==3.0.0
```

### 4. Migration Strategy

#### Migration Script (`scripts/migrate_environments.sh`)
```bash
#!/bin/bash
# Migration script to consolidate virtual environments

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKUP_DIR="$PROJECT_ROOT/backup_envs_$(date +%Y%m%d_%H%M%S)"

echo "🔄 HTX Project - Virtual Environment Migration"
echo "============================================="

# Backup existing environments
backup_environments() {
    echo "📦 Backing up existing environments..."
    mkdir -p "$BACKUP_DIR"
    
    for env_dir in ".venv" ".venv_wsl" ".venv_wsl2"; do
        if [ -d "$PROJECT_ROOT/$env_dir" ]; then
            echo "   Backing up $env_dir..."
            cp -r "$PROJECT_ROOT/$env_dir" "$BACKUP_DIR/"
        fi
    done
    
    echo "✅ Backup completed: $BACKUP_DIR"
}

# Extract package lists from existing environments
extract_package_lists() {
    echo "📋 Extracting package lists..."
    
    for env_dir in ".venv" ".venv_wsl" ".venv_wsl2"; do
        env_path="$PROJECT_ROOT/$env_dir"
        if [ -d "$env_path" ]; then
            echo "   Extracting from $env_dir..."
            
            # Try to activate and get package list
            if [ -f "$env_path/bin/activate" ]; then
                source "$env_path/bin/activate"
                pip freeze > "$BACKUP_DIR/${env_dir}_packages.txt"
                deactivate
            elif [ -f "$env_path/Scripts/activate.bat" ]; then
                echo "   Windows environment detected for $env_dir"
                # Windows environment - list will be extracted differently
            fi
        fi
    done
}

# Create unified requirements
create_unified_requirements() {
    echo "📝 Creating unified requirements..."
    
    # Combine all package lists and deduplicate
    if [ -f "$BACKUP_DIR/.venv_packages.txt" ] || [ -f "$BACKUP_DIR/.venv_wsl_packages.txt" ] || [ -f "$BACKUP_DIR/.venv_wsl2_packages.txt" ]; then
        cat "$BACKUP_DIR"/*_packages.txt 2>/dev/null | sort | uniq > "$BACKUP_DIR/all_packages.txt"
        echo "✅ Combined package list created: $BACKUP_DIR/all_packages.txt"
    fi
}

# Remove old environments
cleanup_old_environments() {
    echo "🧹 Cleaning up old environments..."
    
    read -p "Remove old virtual environments? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$PROJECT_ROOT/.venv_wsl" "$PROJECT_ROOT/.venv_wsl2"
        echo "✅ Old environments removed"
    else
        echo "⚠️ Old environments preserved"
    fi
}

# Create new unified environment
create_unified_environment() {
    echo "🔧 Creating unified environment..."
    
    # Use the activation script to create the environment
    source "$PROJECT_ROOT/scripts/activate_env.sh"
    
    echo "✅ Unified environment created and activated"
}

# Main migration process
main() {
    backup_environments
    extract_package_lists
    create_unified_requirements
    cleanup_old_environments
    create_unified_environment
    
    echo ""
    echo "🎉 Migration completed successfully!"
    echo "📁 Backup location: $BACKUP_DIR"
    echo "🚀 New environment: $PROJECT_ROOT/.venv"
    echo ""
    echo "Next steps:"
    echo "1. Test the new environment: source scripts/activate_env.sh"
    echo "2. Update your IDE/editor settings to use .venv"
    echo "3. Run tests to verify everything works"
}

main "$@"
```

### 5. IDE Integration

#### VS Code Settings (`.vscode/settings.json`)
```json
{
    "python.defaultInterpreterPath": "./.venv/bin/python",
    "python.terminal.activateEnvironment": true,
    "python.envFile": "${workspaceFolder}/.env",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestPath": "./.venv/bin/pytest",
    "files.exclude": {
        "**/.venv_wsl": true,
        "**/.venv_wsl2": true,
        "**/backup_envs_*": true
    }
}
```

### 6. Updated Launch Scripts

#### Enhanced WSL2 Start Script (`start_wsl2_unified.sh`)
```bash
#!/usr/bin/env bash
# Enhanced WSL2 startup script with unified environment

set -eo pipefail

# Source the unified environment activation
source "$(dirname "$0")/scripts/activate_env.sh"

echo "🚀 HTX Project - WSL2 Unified Launch"
echo "===================================="

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Load environment configuration
if [ -f "$PROJECT_ROOT/.env" ]; then
    source "$PROJECT_ROOT/.env"
fi

# Stop existing processes safely
echo -e "${YELLOW}Stopping existing processes...${NC}"
pkill -f "uvicorn.*htx" || true
pkill -f "node.*htx" || true
sleep 2

# Start backend
echo -e "${GREEN}Starting backend...${NC}"
cd "$PROJECT_ROOT"
python run_backend_wsl.py &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Start frontend
echo -e "${GREEN}Starting frontend...${NC}"
cd "$PROJECT_ROOT/frontend"
npm install --silent
npm run dev &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"

cd "$PROJECT_ROOT"

# Health checks
echo -e "${BLUE}Performing health checks...${NC}"
sleep 5

# Backend health check
for i in {1..10}; do
    if curl -s http://localhost:8004/api/v1/health >/dev/null 2>&1; then
        echo -e "${GREEN}✓ Backend healthy: http://localhost:8004${NC}"
        break
    elif [ $i -eq 10 ]; then
        echo -e "${RED}✗ Backend health check failed${NC}"
    else
        echo -e "${YELLOW}⏳ Waiting for backend... ($i/10)${NC}"
        sleep 2
    fi
done

# Frontend health check
for i in {1..10}; do
    if curl -s http://localhost:3000 >/dev/null 2>&1; then
        echo -e "${GREEN}✓ Frontend healthy: http://localhost:3000${NC}"
        break
    elif [ $i -eq 10 ]; then
        echo -e "${RED}✗ Frontend health check failed${NC}"
    else
        echo -e "${YELLOW}⏳ Waiting for frontend... ($i/10)${NC}"
        sleep 2
    fi
done

echo -e "${GREEN}🎉 HTX Project launched successfully!${NC}"
echo -e "${BLUE}Services:${NC}"
echo -e "  📊 Backend:  http://localhost:8004"
echo -e "  🌐 Frontend: http://localhost:3000"
echo -e "  📖 API Docs: http://localhost:8004/docs"
```

### 7. Testing and Validation

#### Environment Test Script (`scripts/test_unified_env.py`)
```python
#!/usr/bin/env python3
"""
Test script to validate unified virtual environment setup
"""

import sys
import subprocess
import importlib
from pathlib import Path

def test_environment_activation():
    """Test that the environment is properly activated"""
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Virtual environment is active")
        print(f"   Environment path: {sys.prefix}")
        return True
    else:
        print("❌ Virtual environment is not active")
        return False

def test_required_packages():
    """Test that all required packages are installed"""
    required_packages = [
        'fastapi',
        'sqlalchemy', 
        'pandas',
        'scikit-learn',
        'aiohttp',
        'pydantic',
        'uvicorn'
    ]
    
    success = True
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package} is available")
        except ImportError:
            print(f"❌ {package} is missing")
            success = False
    
    return success

def test_project_structure():
    """Test that project structure is correct"""
    project_root = Path(__file__).parent.parent
    required_paths = [
        project_root / '.venv',
        project_root / 'requirements',
        project_root / 'scripts' / 'activate_env.sh',
        project_root / 'backend',
        project_root / 'frontend'
    ]
    
    success = True
    for path in required_paths:
        if path.exists():
            print(f"✅ {path.name} exists")
        else:
            print(f"❌ {path.name} is missing")
            success = False
    
    return success

def test_environment_commands():
    """Test that environment commands work"""
    try:
        # Test Python version
        result = subprocess.run([sys.executable, '--version'], 
                              capture_output=True, text=True)
        print(f"✅ Python version: {result.stdout.strip()}")
        
        # Test pip
        result = subprocess.run([sys.executable, '-m', 'pip', '--version'], 
                              capture_output=True, text=True)
        print(f"✅ Pip version: {result.stdout.strip()}")
        
        return True
    except Exception as e:
        print(f"❌ Command test failed: {e}")
        return False

def main():
    """Run all environment tests"""
    print("🧪 HTX Project - Unified Environment Test")
    print("==========================================")
    
    tests = [
        ("Environment Activation", test_environment_activation),
        ("Required Packages", test_required_packages),
        ("Project Structure", test_project_structure),
        ("Environment Commands", test_environment_commands)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 Testing: {test_name}")
        results.append(test_func())
    
    print(f"\n📊 Test Results:")
    passed = sum(results)
    total = len(results)
    print(f"   Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Environment is ready.")
        return 0
    else:
        print("⚠️ Some tests failed. Check configuration.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

## Implementation Timeline

### Phase 1: Preparation (Day 1)
- [ ] Create backup of existing environments
- [ ] Create new directory structure for requirements
- [ ] Test environment detection logic

### Phase 2: Migration (Day 2)
- [ ] Run migration script
- [ ] Create unified `.venv` environment
- [ ] Update all launch scripts
- [ ] Test basic functionality

### Phase 3: Validation (Day 3)
- [ ] Run comprehensive tests
- [ ] Update IDE configurations
- [ ] Verify all services work with new environment
- [ ] Update documentation

### Phase 4: Cleanup (Day 4)
- [ ] Remove old environment directories
- [ ] Update CI/CD configurations
- [ ] Train team on new activation process

## Benefits of Unified Environment

1. **Consistency**: Single environment across all platforms
2. **Simplified Management**: One set of dependencies to maintain
3. **Better Performance**: No environment switching overhead
4. **Easier Troubleshooting**: Single environment to debug
5. **IDE Integration**: Better tooling support
6. **Team Collaboration**: Consistent setup for all developers

## Rollback Plan

If issues occur during migration:

1. **Immediate Rollback**:
   ```bash
   # Restore from backup
   cp -r backup_envs_YYYYMMDD_HHMMSS/.venv_wsl2 ./.venv_wsl2
   source .venv_wsl2/bin/activate
   ```

2. **Gradual Migration**:
   - Keep old environments temporarily
   - Test unified environment in parallel
   - Switch over when confidence is high

3. **Emergency Scripts**:
   - Quick restore scripts
   - Environment validation checks
   - Service restart procedures

This unified virtual environment management system will eliminate the current conflicts and provide a solid foundation for consistent development across Windows and WSL2 environments.