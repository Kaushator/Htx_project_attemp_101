# Path Configuration Fixes with Dynamic Detection

## Overview

This document provides comprehensive solutions for fixing hardcoded path dependencies in the HTX Trading Platform, implementing dynamic path detection, and ensuring cross-platform compatibility for WSL2 deployments.

## Current Path Issues

### Critical Problems Identified
1. **Hardcoded Username**: `/home/fake0mg/htx_project` in `launch_wsl2.bat`
2. **Static Project Paths**: No dynamic detection of project location
3. **Cross-Platform Inconsistency**: Mixed Windows/WSL path handling
4. **Performance Degradation**: Cross-filesystem operations (5-10x slower)

## Dynamic Path Detection Implementation

### 1. Enhanced Launch Script for Windows

#### Fixed `launch_wsl2_enhanced.bat`
```batch
@echo off
REM Enhanced WSL2 launcher with dynamic path detection
setlocal enabledelayedexpansion

echo 🚀 HTX Project - Enhanced WSL2 Launcher
echo ========================================

REM Get current script directory
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

REM Extract project name from current directory
for %%f in ("%SCRIPT_DIR%") do set "PROJECT_NAME=%%~nf"

REM Detect current WSL user dynamically
echo 🔍 Detecting WSL environment...
for /f "tokens=*" %%i in ('wsl whoami 2^>nul') do set "WSL_USER=%%i"

if "%WSL_USER%"=="" (
    echo ❌ WSL not accessible or not configured
    echo Please ensure WSL2 is installed and running
    exit /b 1
)

REM Define paths
set "WINDOWS_PROJECT_PATH=%SCRIPT_DIR%"
set "WSL_PROJECT_PATH=/home/%WSL_USER%/%PROJECT_NAME%"

echo 📂 Detected Configuration:
echo    Windows Project: %WINDOWS_PROJECT_PATH%
echo    WSL User: %WSL_USER%
echo    WSL Target: %WSL_PROJECT_PATH%

REM Check WSL version
wsl --list --verbose | findstr "%WSL_USER%" | findstr "2" >nul
if %ERRORLEVEL% NEQ 0 (
    echo ⚠️ WSL2 not detected. Performance may be degraded.
    echo Recommendation: wsl --set-version Ubuntu 2
    echo.
    set /p "continue=Continue anyway? (y/n): "
    if /i "!continue!" NEQ "y" exit /b 1
)

REM Check if project exists in WSL2 native filesystem
echo 🔍 Checking project location in WSL2...
wsl test -d "%WSL_PROJECT_PATH%" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo 📦 Project not found in WSL2 filesystem
    echo 🚀 Migrating project for better performance...
    echo    Source: %WINDOWS_PROJECT_PATH%
    echo    Target: %WSL_PROJECT_PATH%
    
    REM Create parent directory
    wsl mkdir -p "/home/%WSL_USER%"
    
    REM Copy project with progress indication
    echo    Copying files... (this may take several minutes)
    wsl cp -r "%WINDOWS_PROJECT_PATH%" "%WSL_PROJECT_PATH%"
    
    if %ERRORLEVEL% NEQ 0 (
        echo ❌ Failed to copy project to WSL2 filesystem
        exit /b 1
    )
    
    REM Set proper permissions
    wsl chmod -R 755 "%WSL_PROJECT_PATH%"
    wsl find "%WSL_PROJECT_PATH%" -name "*.sh" -exec chmod +x {} \;
    
    echo ✅ Project successfully migrated to WSL2 filesystem
) else (
    echo ✅ Project found in WSL2 filesystem
)

REM Launch enhanced startup script
echo 🚀 Starting HTX project in WSL2...
wsl -d Ubuntu -e bash -c "cd '%WSL_PROJECT_PATH%' && ./scripts/start_wsl2_enhanced.sh"

if %ERRORLEVEL% NEQ 0 (
    echo ❌ Failed to start project in WSL2
    exit /b 1
)

echo.
echo ✅ HTX Project started successfully!
echo 🌐 Access URLs:
echo    Frontend: http://localhost:3000
echo    Backend:  http://localhost:8004
echo    API Docs: http://localhost:8004/docs
echo.
echo 📝 Project location: %WSL_PROJECT_PATH%
pause
```

### 2. Enhanced WSL2 Startup Script

#### New `scripts/start_wsl2_enhanced.sh`
```bash
#!/usr/bin/env bash
# Enhanced WSL2 startup script with dynamic path detection

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}🚀 HTX Project - Enhanced WSL2 Startup${NC}"
echo -e "${CYAN}=====================================${NC}"

# Dynamic path detection
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PROJECT_NAME="$(basename "$PROJECT_ROOT")"

echo -e "${BLUE}📂 Project Configuration:${NC}"
echo -e "   Root: ${PROJECT_ROOT}"
echo -e "   Name: ${PROJECT_NAME}"
echo -e "   User: $(whoami)"

# Validate WSL2 environment
validate_wsl2_environment() {
    echo -e "${BLUE}🔍 Validating WSL2 environment...${NC}"
    
    # Check if running in WSL2
    if ! grep -q microsoft /proc/version 2>/dev/null; then
        echo -e "${RED}❌ Not running in WSL environment${NC}"
        return 1
    fi
    
    # Check WSL version
    if grep -q "WSL2" /proc/version 2>/dev/null; then
        echo -e "${GREEN}✅ WSL2 detected${NC}"
    else
        echo -e "${YELLOW}⚠️ WSL1 detected - performance may be degraded${NC}"
    fi
    
    # Check filesystem performance
    local test_file="/tmp/wsl_perf_test_$$"
    echo -e "${BLUE}🏃 Testing filesystem performance...${NC}"
    
    local start_time=$(date +%s.%3N)
    dd if=/dev/zero of="$test_file" bs=1M count=10 2>/dev/null
    local end_time=$(date +%s.%3N)
    local write_time=$(echo "$end_time - $start_time" | bc -l 2>/dev/null || echo "0")
    rm -f "$test_file"
    
    if [[ $(echo "$write_time > 2.0" | bc -l 2>/dev/null || echo "0") == "1" ]]; then
        echo -e "${YELLOW}⚠️ Slow filesystem detected (${write_time}s for 10MB)${NC}"
        echo -e "${YELLOW}   Consider migrating to WSL2 native filesystem${NC}"
    else
        echo -e "${GREEN}✅ Filesystem performance acceptable (${write_time}s for 10MB)${NC}"
    fi
}

# Environment setup with dynamic paths
setup_environment() {
    echo -e "${BLUE}🔧 Setting up environment...${NC}"
    
    # Determine virtual environment path
    local venv_path="$PROJECT_ROOT/.venv"
    
    # Create virtual environment if it doesn't exist
    if [[ ! -d "$venv_path" ]]; then
        echo -e "${YELLOW}📦 Creating virtual environment...${NC}"
        python3 -m venv "$venv_path"
    fi
    
    # Activate virtual environment
    source "$venv_path/bin/activate"
    echo -e "${GREEN}✅ Virtual environment activated: $venv_path${NC}"
    
    # Verify Python environment
    echo -e "${BLUE}🐍 Python environment:${NC}"
    echo -e "   Python: $(python --version)"
    echo -e "   Location: $(which python)"
    echo -e "   Virtual env: $VIRTUAL_ENV"
}

# Dynamic database path configuration
configure_database_path() {
    echo -e "${BLUE}💾 Configuring database paths...${NC}"
    
    local data_dir="$PROJECT_ROOT/data"
    local logs_dir="$PROJECT_ROOT/logs"
    
    # Create necessary directories
    mkdir -p "$data_dir" "$logs_dir"
    
    # Set environment variables for WSL2-optimized paths
    export DATABASE_URL="sqlite+aiosqlite:///$data_dir/app.db"
    export LOG_FILE="$logs_dir/htx_project_$(date +%Y%m%d).log"
    export UPLOAD_DIR="$data_dir/raw"
    export PROCESSED_DIR="$data_dir/processed"
    
    echo -e "${GREEN}✅ Database configured:${NC}"
    echo -e "   Database: $DATABASE_URL"
    echo -e "   Logs: $LOG_FILE"
    echo -e "   Upload: $UPLOAD_DIR"
    echo -e "   Processed: $PROCESSED_DIR"
    
    # Create upload directories
    mkdir -p "$UPLOAD_DIR" "$PROCESSED_DIR"
}

# Port management with dynamic detection
manage_ports() {
    echo -e "${BLUE}🔌 Managing ports...${NC}"
    
    local backend_port=8004
    local frontend_port=3000
    
    # Function to check if port is in use
    port_in_use() {
        local port=$1
        if command -v netstat >/dev/null; then
            netstat -tuln 2>/dev/null | grep -q ":$port "
        elif command -v ss >/dev/null; then
            ss -tuln 2>/dev/null | grep -q ":$port "
        else
            timeout 1 bash -c "</dev/tcp/localhost/$port" 2>/dev/null
        fi
    }
    
    # Find available ports if defaults are occupied
    find_available_port() {
        local start_port=$1
        local port=$start_port
        
        while port_in_use $port; do
            port=$((port + 1))
            if [[ $port -gt $((start_port + 100)) ]]; then
                echo "0"  # No available port found
                return 1
            fi
        done
        
        echo $port
    }
    
    # Check and adjust backend port
    if port_in_use $backend_port; then
        echo -e "${YELLOW}⚠️ Port $backend_port in use, finding alternative...${NC}"
        backend_port=$(find_available_port $backend_port)
        if [[ $backend_port == "0" ]]; then
            echo -e "${RED}❌ No available backend port found${NC}"
            return 1
        fi
        echo -e "${GREEN}✅ Using backend port: $backend_port${NC}"
    fi
    
    # Check and adjust frontend port
    if port_in_use $frontend_port; then
        echo -e "${YELLOW}⚠️ Port $frontend_port in use, finding alternative...${NC}"
        frontend_port=$(find_available_port $frontend_port)
        if [[ $frontend_port == "0" ]]; then
            echo -e "${RED}❌ No available frontend port found${NC}"
            return 1
        fi
        echo -e "${GREEN}✅ Using frontend port: $frontend_port${NC}"
    fi
    
    # Export port configuration
    export BACKEND_PORT=$backend_port
    export FRONTEND_PORT=$frontend_port
    export API_URL="http://localhost:$backend_port"
    export FRONTEND_URL="http://localhost:$frontend_port"
    
    # Update port configuration file
    cat > "$PROJECT_ROOT/.ports_config" << EOF
# HTX Project - Dynamic Port Configuration
# Generated: $(date)
BACKEND_PORT=$backend_port
FRONTEND_PORT=$frontend_port
API_URL=http://localhost:$backend_port
FRONTEND_URL=http://localhost:$frontend_port

# Environment
ENV=development
DEBUG=true
ENABLE_BACKGROUND_TASKS=true
EOF
    
    echo -e "${GREEN}✅ Port configuration updated${NC}"
}

# Process management with PID tracking
manage_processes() {
    echo -e "${BLUE}🔄 Managing processes...${NC}"
    
    local pid_dir="$PROJECT_ROOT/.pids"
    mkdir -p "$pid_dir"
    
    # Cleanup function
    cleanup_processes() {
        echo -e "${YELLOW}🧹 Cleaning up processes...${NC}"
        
        for pid_file in "$pid_dir"/*.pid; do
            [[ -f "$pid_file" ]] || continue
            
            local service_name=$(basename "$pid_file" .pid)
            local pid=$(cat "$pid_file" 2>/dev/null || echo "")
            
            if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
                echo -e "   Stopping $service_name (PID: $pid)"
                kill "$pid" 2>/dev/null || true
                
                # Wait for graceful shutdown
                local count=0
                while kill -0 "$pid" 2>/dev/null && [[ $count -lt 10 ]]; do
                    sleep 1
                    count=$((count + 1))
                done
                
                # Force kill if still running
                if kill -0 "$pid" 2>/dev/null; then
                    kill -9 "$pid" 2>/dev/null || true
                fi
            fi
            
            rm -f "$pid_file"
        done
    }
    
    # Register cleanup on exit
    trap cleanup_processes EXIT INT TERM
    
    # Stop any existing processes
    cleanup_processes
}

# Start services with health checks
start_services() {
    echo -e "${BLUE}🚀 Starting services...${NC}"
    
    local pid_dir="$PROJECT_ROOT/.pids"
    local log_dir="$PROJECT_ROOT/logs"
    mkdir -p "$log_dir"
    
    # Start backend
    echo -e "${YELLOW}🔧 Starting backend on port $BACKEND_PORT...${NC}"
    cd "$PROJECT_ROOT"
    
    # Set environment for backend
    export HOST=0.0.0.0
    export PORT=$BACKEND_PORT
    
    nohup python run_backend_wsl.py > "$log_dir/backend.log" 2>&1 &
    local backend_pid=$!
    echo $backend_pid > "$pid_dir/backend.pid"
    
    echo -e "${GREEN}✅ Backend started (PID: $backend_pid)${NC}"
    
    # Wait for backend to be ready
    echo -e "${BLUE}⏳ Waiting for backend to be ready...${NC}"
    local attempts=0
    while [[ $attempts -lt 30 ]]; do
        if curl -s "http://localhost:$BACKEND_PORT/api/v1/health" >/dev/null 2>&1; then
            echo -e "${GREEN}✅ Backend is healthy${NC}"
            break
        fi
        sleep 2
        attempts=$((attempts + 1))
    done
    
    if [[ $attempts -eq 30 ]]; then
        echo -e "${RED}❌ Backend failed to start properly${NC}"
        return 1
    fi
    
    # Start frontend
    echo -e "${YELLOW}🔧 Starting frontend on port $FRONTEND_PORT...${NC}"
    cd "$PROJECT_ROOT/frontend"
    
    # Install dependencies if needed
    if [[ ! -d "node_modules" ]]; then
        echo -e "${BLUE}📦 Installing frontend dependencies...${NC}"
        npm install --silent
    fi
    
    # Set frontend environment
    export VITE_API_URL="http://localhost:$BACKEND_PORT"
    export PORT=$FRONTEND_PORT
    
    nohup npm run dev -- --host 0.0.0.0 --port $FRONTEND_PORT > "$log_dir/frontend.log" 2>&1 &
    local frontend_pid=$!
    echo $frontend_pid > "$pid_dir/frontend.pid"
    
    echo -e "${GREEN}✅ Frontend started (PID: $frontend_pid)${NC}"
    
    cd "$PROJECT_ROOT"
}

# Health check and status report
health_check() {
    echo -e "${CYAN}🏥 System Health Check${NC}"
    echo -e "${CYAN}===================${NC}"
    
    # Check backend health
    if curl -s "http://localhost:$BACKEND_PORT/api/v1/health" | grep -q "healthy"; then
        echo -e "${GREEN}✅ Backend: Healthy${NC}"
    else
        echo -e "${RED}❌ Backend: Unhealthy${NC}"
    fi
    
    # Check frontend (simple connection test)
    if curl -s -o /dev/null -w "%{http_code}" "http://localhost:$FRONTEND_PORT" | grep -q "200"; then
        echo -e "${GREEN}✅ Frontend: Accessible${NC}"
    else
        echo -e "${YELLOW}⚠️ Frontend: Starting up...${NC}"
    fi
    
    # Display process information
    echo -e "${BLUE}📊 Process Information:${NC}"
    
    local pid_dir="$PROJECT_ROOT/.pids"
    for pid_file in "$pid_dir"/*.pid; do
        [[ -f "$pid_file" ]] || continue
        
        local service_name=$(basename "$pid_file" .pid)
        local pid=$(cat "$pid_file" 2>/dev/null || echo "")
        
        if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
            local cpu_mem=$(ps -p "$pid" -o %cpu,%mem --no-headers 2>/dev/null || echo "N/A N/A")
            echo -e "   $service_name (PID: $pid): CPU/MEM: $cpu_mem"
        fi
    done
}

# Main execution
main() {
    validate_wsl2_environment || {
        echo -e "${RED}❌ WSL2 environment validation failed${NC}"
        exit 1
    }
    
    setup_environment || {
        echo -e "${RED}❌ Environment setup failed${NC}"
        exit 1
    }
    
    configure_database_path || {
        echo -e "${RED}❌ Database configuration failed${NC}"
        exit 1
    }
    
    manage_ports || {
        echo -e "${RED}❌ Port management failed${NC}"
        exit 1
    }
    
    manage_processes || {
        echo -e "${RED}❌ Process management setup failed${NC}"
        exit 1
    }
    
    start_services || {
        echo -e "${RED}❌ Service startup failed${NC}"
        exit 1
    }
    
    # Give services time to fully start
    sleep 3
    
    health_check
    
    echo
    echo -e "${CYAN}🎉 HTX Project Started Successfully!${NC}"
    echo -e "${CYAN}==================================${NC}"
    echo -e "${GREEN}📊 Access URLs:${NC}"
    echo -e "   🌐 Frontend:  $FRONTEND_URL"
    echo -e "   ⚡ Backend:   $API_URL"
    echo -e "   📖 API Docs: $API_URL/docs"
    echo -e "   💾 Health:   $API_URL/api/v1/health"
    echo
    echo -e "${BLUE}📂 Project Location: $PROJECT_ROOT${NC}"
    echo -e "${BLUE}📊 Monitor: ./scripts/monitor_services.sh${NC}"
    echo -e "${BLUE}🛑 Stop:    ./scripts/stop_services.sh${NC}"
    echo
    echo -e "${YELLOW}💡 Services are running in the background${NC}"
    echo -e "${YELLOW}   Use Ctrl+C to stop gracefully${NC}"
    
    # Keep script running to maintain process management
    while true; do
        sleep 60
        # Optional: periodic health checks
        # health_check >/dev/null 2>&1
    done
}

# Execute main function
main "$@"
```

### 3. Service Management Scripts

#### Service Monitor Script
```bash
#!/usr/bin/env bash
# scripts/monitor_services.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PID_DIR="$PROJECT_ROOT/.pids"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔍 HTX Project Service Monitor${NC}"
echo -e "${BLUE}==============================${NC}"

# Load port configuration
if [[ -f "$PROJECT_ROOT/.ports_config" ]]; then
    source "$PROJECT_ROOT/.ports_config"
else
    BACKEND_PORT=8004
    FRONTEND_PORT=3000
fi

check_service_status() {
    local service_name=$1
    local pid_file="$PID_DIR/${service_name}.pid"
    
    if [[ ! -f "$pid_file" ]]; then
        echo -e "${RED}❌ $service_name: Not running (no PID file)${NC}"
        return 1
    fi
    
    local pid=$(cat "$pid_file" 2>/dev/null || echo "")
    
    if [[ -z "$pid" ]]; then
        echo -e "${RED}❌ $service_name: Invalid PID file${NC}"
        return 1
    fi
    
    if ! kill -0 "$pid" 2>/dev/null; then
        echo -e "${RED}❌ $service_name: Process not found (PID: $pid)${NC}"
        rm -f "$pid_file"
        return 1
    fi
    
    local cpu_mem=$(ps -p "$pid" -o %cpu,%mem --no-headers 2>/dev/null || echo "N/A N/A")
    echo -e "${GREEN}✅ $service_name: Running (PID: $pid, CPU/MEM: $cpu_mem)${NC}"
    return 0
}

check_service_health() {
    local service_name=$1
    local url=$2
    
    if curl -s -f -m 5 "$url" >/dev/null 2>&1; then
        echo -e "${GREEN}✅ $service_name: Healthy${NC}"
        return 0
    else
        echo -e "${RED}❌ $service_name: Unhealthy${NC}"
        return 1
    fi
}

# Check process status
echo -e "${BLUE}📊 Process Status:${NC}"
check_service_status "backend"
check_service_status "frontend"

echo
echo -e "${BLUE}🏥 Health Status:${NC}"
check_service_health "Backend API" "http://localhost:$BACKEND_PORT/api/v1/health"
check_service_health "Frontend" "http://localhost:$FRONTEND_PORT"

echo
echo -e "${BLUE}🌐 Service URLs:${NC}"
echo -e "   Frontend:  http://localhost:$FRONTEND_PORT"
echo -e "   Backend:   http://localhost:$BACKEND_PORT"
echo -e "   API Docs:  http://localhost:$BACKEND_PORT/docs"
echo -e "   Health:    http://localhost:$BACKEND_PORT/api/v1/health"
```

#### Service Stop Script
```bash
#!/usr/bin/env bash
# scripts/stop_services.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PID_DIR="$PROJECT_ROOT/.pids"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}🛑 Stopping HTX Project Services${NC}"
echo -e "${YELLOW}================================${NC}"

stop_service() {
    local service_name=$1
    local pid_file="$PID_DIR/${service_name}.pid"
    
    if [[ ! -f "$pid_file" ]]; then
        echo -e "${YELLOW}⚠️ $service_name: No PID file found${NC}"
        return 0
    fi
    
    local pid=$(cat "$pid_file" 2>/dev/null || echo "")
    
    if [[ -z "$pid" ]]; then
        echo -e "${YELLOW}⚠️ $service_name: Invalid PID file${NC}"
        rm -f "$pid_file"
        return 0
    fi
    
    if ! kill -0 "$pid" 2>/dev/null; then
        echo -e "${YELLOW}⚠️ $service_name: Process not running (PID: $pid)${NC}"
        rm -f "$pid_file"
        return 0
    fi
    
    echo -e "${BLUE}🛑 Stopping $service_name (PID: $pid)...${NC}"
    
    # Graceful shutdown
    kill "$pid" 2>/dev/null || true
    
    # Wait for graceful shutdown
    local count=0
    while kill -0 "$pid" 2>/dev/null && [[ $count -lt 15 ]]; do
        sleep 1
        count=$((count + 1))
        if [[ $((count % 5)) -eq 0 ]]; then
            echo -e "${YELLOW}   Waiting for graceful shutdown... ($count/15)${NC}"
        fi
    done
    
    # Force kill if still running
    if kill -0 "$pid" 2>/dev/null; then
        echo -e "${RED}   Force killing $service_name...${NC}"
        kill -9 "$pid" 2>/dev/null || true
        sleep 1
    fi
    
    # Verify stopped
    if kill -0 "$pid" 2>/dev/null; then
        echo -e "${RED}❌ Failed to stop $service_name${NC}"
        return 1
    else
        echo -e "${GREEN}✅ $service_name stopped${NC}"
        rm -f "$pid_file"
        return 0
    fi
}

# Stop all services
stop_service "frontend"
stop_service "backend"

echo
echo -e "${GREEN}✅ All services stopped${NC}"
```

## Path Configuration Validation

### Testing Script
```bash
#!/usr/bin/env bash
# scripts/test_path_configuration.sh

echo "🧪 Testing Path Configuration"
echo "============================="

# Test dynamic path detection
echo "📂 Testing path detection..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "   Script dir: $SCRIPT_DIR"
echo "   Project root: $PROJECT_ROOT"
echo "   Current user: $(whoami)"

# Test WSL environment detection
echo
echo "🔍 Testing WSL environment..."
if grep -q microsoft /proc/version 2>/dev/null; then
    echo "   ✅ Running in WSL"
    if grep -q "WSL2" /proc/version; then
        echo "   ✅ WSL2 detected"
    else
        echo "   ⚠️ WSL1 detected"
    fi
else
    echo "   ❌ Not running in WSL"
fi

# Test filesystem performance
echo
echo "🏃 Testing filesystem performance..."
test_file="/tmp/path_test_$$"
start_time=$(date +%s.%3N)
dd if=/dev/zero of="$test_file" bs=1M count=5 2>/dev/null
end_time=$(date +%s.%3N)
write_time=$(echo "$end_time - $start_time" | bc -l 2>/dev/null || echo "0")
rm -f "$test_file"

echo "   Write performance: ${write_time}s for 5MB"

if [[ $(echo "$write_time > 1.0" | bc -l 2>/dev/null || echo "0") == "1" ]]; then
    echo "   ⚠️ Performance may be degraded"
else
    echo "   ✅ Performance acceptable"
fi

# Test port availability
echo
echo "🔌 Testing port availability..."
check_port() {
    local port=$1
    if command -v netstat >/dev/null; then
        netstat -tuln 2>/dev/null | grep -q ":$port "
    else
        timeout 1 bash -c "</dev/tcp/localhost/$port" 2>/dev/null
    fi
}

for port in 8004 3000; do
    if check_port $port; then
        echo "   ⚠️ Port $port is in use"
    else
        echo "   ✅ Port $port is available"
    fi
done

echo
echo "✅ Path configuration test completed"
```

This implementation provides dynamic path detection, cross-platform compatibility, performance optimization through WSL2 filesystem migration, and robust process management for the HTX Trading Platform.