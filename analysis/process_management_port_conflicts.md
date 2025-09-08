# Process Management and Port Conflict Issues Analysis

## Critical Process Management Problems

### 1. Aggressive System-Wide Process Termination

**Current Implementation Pattern:**
```bash
# From start_wsl2.sh (lines 21-23)
pkill -f uvicorn || true
pkill -f node || true  
pkill -f "python.*run_backend_wsl.py" || true

# From full_restart.sh (lines 70-72)
pkill -f uvicorn || true
pkill -f node || true
pkill -f python.*mcp || true

# From start_app.sh (lines 16-17)
pkill -f uvicorn
pkill -f vite
```

**Critical Issues Identified:**

1. **System-Wide Impact**: 
   - Kills ALL uvicorn processes on the system
   - Terminates ALL node processes, affecting other projects
   - No discrimination between HTX project and other applications

2. **No Graceful Shutdown**:
   - Uses SIGTERM without grace period
   - No attempt to save application state
   - Database connections may be left open
   - File operations may be corrupted

3. **Race Conditions**:
   - No verification that processes actually stopped
   - New processes may start before old ones are fully terminated
   - Service dependencies not considered during shutdown

4. **Security and Reliability Risks**:
   - May interfere with production services on same machine
   - Development environment conflicts with other projects
   - System administrator privileges implications

### 2. Missing Process Identification and Tracking

**Current Process Management Lacks:**

```bash
# No PID file management
# No process ownership validation
# No graceful shutdown procedures
# No process health monitoring
```

**Impact Assessment:**
- **Critical**: Production environment interference
- **High**: Development workflow disruption
- **Medium**: System stability concerns
- **Medium**: Data integrity risks

### 3. Process Startup Race Conditions

**Problematic Startup Sequence:**
```bash
# From start_wsl2.sh
python run_backend_wsl.py &
BACKEND_PID=$!

cd frontend
timeout 10 npm run dev &
FRONTEND_PID=$!

# Fixed delay without health checks
sleep 5

# Health check that may fail due to timing
if curl -s http://localhost:8004/api/v1/health | grep -q "healthy"; then
    echo "✓ Backend working"
else
    echo "✗ Backend not responding"
fi
```

**Issues:**
- Fixed 5-second delay may be insufficient
- No validation that processes actually started
- PID variables captured but never used for management
- Timeout on npm may kill frontend before it starts

## Port Configuration Conflicts

### 1. Docker vs Direct Execution Port Mismatch

**Docker Configuration (`docker-compose.yml`):**
```yaml
services:
  api:
    ports:
      - "8000:8000"
    command: ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**WSL2 Scripts Configuration:**
```bash
# .ports_config
BACKEND_PORT=8004
FRONTEND_PORT=3000
API_URL=http://localhost:8004

# Used consistently across scripts
curl -s http://localhost:8004/api/v1/health
```

**Conflict Analysis:**
- Docker uses port 8000
- WSL2 scripts use port 8004  
- No coordination between deployment methods
- Documentation may reference wrong ports
- Load balancer/proxy configuration confusion

### 2. Port Availability Validation Missing

**Current Scripts Assume Ports Are Free:**
```bash
# No port conflict detection before starting services
python run_backend_wsl.py &  # May fail if 8004 is occupied
npm run dev &  # May fail if 3000 is occupied
```

**Missing Validations:**
- No check if ports 8004/3000 are already in use
- No alternative port selection
- No error handling for port conflicts
- No cleanup of processes using conflicting ports

### 3. Cross-Platform Port Access Issues

**WSL2 Network Configuration Challenges:**
- Windows firewall may block WSL2 port access
- WSL2 IP address changes between reboots
- Port forwarding rules may not persist
- Different behavior between WSL2 and native Linux

## Service Dependency Management Problems

### 1. No Service Startup Order

**Current Implementation:**
```bash
# Services started in parallel without dependencies
python run_backend_wsl.py &
npm run dev &

# No validation that backend is ready before frontend starts
```

**Missing Dependencies:**
- Frontend should wait for backend API to be available
- Database initialization should complete before backend starts
- Health checks should validate all dependencies

### 2. No Health Check Integration

**Current Health Check Issues:**
```bash
# Basic curl check without retry logic
if curl -s http://localhost:8004/api/v1/health | grep -q "healthy"; then
    echo "✓ Backend working"
else
    echo "✗ Backend not responding"
fi
```

**Problems:**
- Single attempt without retries
- No timeout configuration
- No detailed error reporting
- No integration with process management

## Solutions Design

### 1. PID-Based Process Management

**Enhanced Process Management Template:**
```bash
#!/bin/bash
# Enhanced process management system

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_DIR="$PROJECT_ROOT/.pids"
LOG_DIR="$PROJECT_ROOT/logs"

# Create directories if they don't exist
mkdir -p "$PID_DIR" "$LOG_DIR"

# Process management functions
start_service() {
    local service_name=$1
    local command=$2
    local port=$3
    local pid_file="$PID_DIR/${service_name}.pid"
    local log_file="$LOG_DIR/${service_name}.log"
    
    # Check if service is already running
    if [ -f "$pid_file" ] && kill -0 "$(cat "$pid_file")" 2>/dev/null; then
        echo "⚠️ $service_name is already running (PID: $(cat "$pid_file"))"
        return 1
    fi
    
    # Check port availability
    if [ -n "$port" ] && check_port_used "$port"; then
        echo "❌ Port $port is already in use"
        return 1
    fi
    
    # Start service
    echo "🚀 Starting $service_name..."
    nohup $command > "$log_file" 2>&1 &
    local pid=$!
    echo $pid > "$pid_file"
    
    # Validate service started
    if kill -0 $pid 2>/dev/null; then
        echo "✅ $service_name started successfully (PID: $pid)"
        return 0
    else
        echo "❌ Failed to start $service_name"
        rm -f "$pid_file"
        return 1
    fi
}

stop_service() {
    local service_name=$1
    local pid_file="$PID_DIR/${service_name}.pid"
    
    if [ ! -f "$pid_file" ]; then
        echo "⚠️ $service_name is not running (no PID file)"
        return 1
    fi
    
    local pid=$(cat "$pid_file")
    
    if ! kill -0 $pid 2>/dev/null; then
        echo "⚠️ $service_name process (PID: $pid) is not running"
        rm -f "$pid_file"
        return 1
    fi
    
    # Graceful shutdown
    echo "🛑 Stopping $service_name (PID: $pid)..."
    kill $pid
    
    # Wait for graceful shutdown (up to 10 seconds)
    local count=0
    while kill -0 $pid 2>/dev/null && [ $count -lt 10 ]; do
        sleep 1
        count=$((count + 1))
    done
    
    # Force kill if still running
    if kill -0 $pid 2>/dev/null; then
        echo "⚠️ Force killing $service_name..."
        kill -9 $pid
    fi
    
    rm -f "$pid_file"
    echo "✅ $service_name stopped"
}

check_port_used() {
    local port=$1
    if command -v netstat >/dev/null; then
        netstat -tuln | grep -q ":$port "
    elif command -v ss >/dev/null; then
        ss -tuln | grep -q ":$port "
    else
        # Fallback: try to bind to port
        timeout 1 bash -c "</dev/tcp/localhost/$port" 2>/dev/null
    fi
}

get_service_status() {
    local service_name=$1
    local pid_file="$PID_DIR/${service_name}.pid"
    
    if [ ! -f "$pid_file" ]; then
        echo "stopped"
        return 1
    fi
    
    local pid=$(cat "$pid_file")
    if kill -0 $pid 2>/dev/null; then
        echo "running"
        return 0
    else
        echo "dead"
        rm -f "$pid_file"
        return 1
    fi
}

# Cleanup function for script exit
cleanup_all() {
    echo "🧹 Cleaning up all services..."
    for pid_file in "$PID_DIR"/*.pid; do
        [ -f "$pid_file" ] || continue
        local service=$(basename "$pid_file" .pid)
        stop_service "$service"
    done
}

# Register cleanup on script exit
trap cleanup_all EXIT INT TERM
```

### 2. Port Configuration Management

**Unified Port Configuration:**
```bash
#!/bin/bash
# Port management system

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PORTS_CONFIG="$PROJECT_ROOT/.ports_config"

# Default port configuration
DEFAULT_BACKEND_PORT=8004
DEFAULT_FRONTEND_PORT=3000

# Load port configuration
load_port_config() {
    if [ -f "$PORTS_CONFIG" ]; then
        source "$PORTS_CONFIG"
    fi
    
    # Use defaults if not set
    BACKEND_PORT=${BACKEND_PORT:-$DEFAULT_BACKEND_PORT}
    FRONTEND_PORT=${FRONTEND_PORT:-$DEFAULT_FRONTEND_PORT}
    API_URL=${API_URL:-"http://localhost:$BACKEND_PORT"}
    FRONTEND_URL=${FRONTEND_URL:-"http://localhost:$FRONTEND_PORT"}
}

# Find available port if default is occupied
find_available_port() {
    local start_port=$1
    local port=$start_port
    
    while check_port_used $port; do
        port=$((port + 1))
        if [ $port -gt $((start_port + 100)) ]; then
            echo "❌ No available ports found after $start_port"
            return 1
        fi
    done
    
    echo $port
}

# Update port configuration
update_port_config() {
    local backend_port=$1
    local frontend_port=$2
    
    cat > "$PORTS_CONFIG" << EOF
# HTX Project - Port Configuration
BACKEND_PORT=$backend_port
FRONTEND_PORT=$frontend_port
API_URL=http://localhost:$backend_port
FRONTEND_URL=http://localhost:$frontend_port

# Environment
ENV=development
DEBUG=true
ENABLE_BACKGROUND_TASKS=true
EOF
    
    echo "✅ Port configuration updated: Backend=$backend_port, Frontend=$frontend_port"
}
```

### 3. Health Check and Service Monitoring

**Comprehensive Health Check System:**
```bash
#!/bin/bash
# Health check and monitoring system

wait_for_service() {
    local service_name=$1
    local url=$2
    local max_attempts=${3:-30}
    local delay=${4:-2}
    
    echo "⏳ Waiting for $service_name at $url..."
    
    local attempt=1
    while [ $attempt -le $max_attempts ]; do
        if curl -s -f -m 5 "$url" >/dev/null 2>&1; then
            echo "✅ $service_name is healthy"
            return 0
        fi
        
        echo "⏳ Attempt $attempt/$max_attempts - $service_name not ready..."
        sleep $delay
        attempt=$((attempt + 1))
    done
    
    echo "❌ $service_name failed to become healthy after $max_attempts attempts"
    return 1
}

check_service_health() {
    local service_name=$1
    local url=$2
    
    if curl -s -f -m 5 "$url" >/dev/null 2>&1; then
        echo "✅ $service_name: healthy"
        return 0
    else
        echo "❌ $service_name: unhealthy"
        return 1
    fi
}

monitor_services() {
    local backend_url="$API_URL/api/v1/health"
    local frontend_url="$FRONTEND_URL"
    
    echo "🔍 Service Health Monitor"
    echo "========================"
    
    # Check backend
    if get_service_status "backend" >/dev/null; then
        check_service_health "Backend" "$backend_url"
    else
        echo "❌ Backend: not running"
    fi
    
    # Check frontend  
    if get_service_status "frontend" >/dev/null; then
        check_service_health "Frontend" "$frontend_url"
    else
        echo "❌ Frontend: not running"
    fi
    
    # Display process information
    echo ""
    echo "📊 Process Information:"
    for pid_file in "$PID_DIR"/*.pid; do
        [ -f "$pid_file" ] || continue
        local service=$(basename "$pid_file" .pid)
        local pid=$(cat "$pid_file")
        if kill -0 $pid 2>/dev/null; then
            local cpu_mem=$(ps -p $pid -o %cpu,%mem --no-headers 2>/dev/null || echo "N/A")
            echo "   $service (PID: $pid): CPU/MEM: $cpu_mem"
        fi
    done
}
```

### 4. Enhanced Startup Script

**Safe Service Startup Implementation:**
```bash
#!/bin/bash
# Enhanced startup script with proper process management

source "$(dirname "$0")/process_management.sh"
source "$(dirname "$0")/port_management.sh"

# Load configuration
load_port_config

echo "🚀 HTX Project - Enhanced Startup"
echo "=================================="

# Validate environment
if [ ! -f "$PROJECT_ROOT/.venv/bin/activate" ]; then
    echo "❌ Virtual environment not found. Please run setup first."
    exit 1
fi

source "$PROJECT_ROOT/.venv/bin/activate"

# Stop any existing services
echo "🛑 Stopping existing services..."
stop_service "frontend" 2>/dev/null || true
stop_service "backend" 2>/dev/null || true

# Find available ports if defaults are occupied
if check_port_used $BACKEND_PORT; then
    BACKEND_PORT=$(find_available_port $BACKEND_PORT)
    echo "⚠️ Using alternative backend port: $BACKEND_PORT"
fi

if check_port_used $FRONTEND_PORT; then
    FRONTEND_PORT=$(find_available_port $FRONTEND_PORT)
    echo "⚠️ Using alternative frontend port: $FRONTEND_PORT"
fi

# Update configuration if ports changed
if [ $BACKEND_PORT -ne $DEFAULT_BACKEND_PORT ] || [ $FRONTEND_PORT -ne $DEFAULT_FRONTEND_PORT ]; then
    update_port_config $BACKEND_PORT $FRONTEND_PORT
    load_port_config  # Reload updated config
fi

# Start backend
echo "🚀 Starting backend on port $BACKEND_PORT..."
if start_service "backend" "python run_backend_wsl.py" $BACKEND_PORT; then
    # Wait for backend to be healthy
    if wait_for_service "Backend" "$API_URL/api/v1/health" 30 2; then
        echo "✅ Backend is ready"
    else
        echo "❌ Backend failed health check"
        stop_service "backend"
        exit 1
    fi
else
    echo "❌ Failed to start backend"
    exit 1
fi

# Start frontend
echo "🚀 Starting frontend on port $FRONTEND_PORT..."
cd "$PROJECT_ROOT/frontend"
if start_service "frontend" "npm run dev" $FRONTEND_PORT; then
    # Wait for frontend to be ready
    if wait_for_service "Frontend" "$FRONTEND_URL" 60 2; then
        echo "✅ Frontend is ready"
    else
        echo "⚠️ Frontend may still be starting..."
    fi
else
    echo "❌ Failed to start frontend"
    stop_service "backend"
    exit 1
fi

cd "$PROJECT_ROOT"

echo ""
echo "🎉 HTX Project Started Successfully!"
echo "=================================="
echo "📊 Services:"
echo "   Backend:  $API_URL"
echo "   Frontend: $FRONTEND_URL"
echo "   API Docs: $API_URL/docs"
echo ""
echo "🔍 Monitor: ./scripts/monitor_services.sh"
echo "🛑 Stop:    ./scripts/stop_services.sh"
```

## Testing Strategy for Process Management

### Test Cases:

1. **Process Isolation Test**:
   - Start HTX services
   - Start other uvicorn/node processes  
   - Stop HTX services
   - Verify other processes still running

2. **Port Conflict Resolution**:
   - Occupy default ports with other services
   - Start HTX project
   - Verify alternative ports are used
   - Verify services function correctly

3. **Graceful Shutdown Test**:
   - Start all services
   - Trigger shutdown
   - Verify processes stop cleanly
   - Verify no orphaned processes

4. **Service Health Monitoring**:
   - Start services
   - Kill backend process manually
   - Verify health check detects failure
   - Test recovery procedures

### Validation Criteria:

- ✅ No system-wide process termination
- ✅ PID-based process management works
- ✅ Port conflicts are automatically resolved
- ✅ Health checks validate service readiness
- ✅ Graceful shutdown leaves no orphaned processes
- ✅ Service dependencies are respected
- ✅ Monitoring provides accurate service status