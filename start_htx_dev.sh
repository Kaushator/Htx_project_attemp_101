#!/bin/bash
# HTX Project - Personal Development Environment Launcher
# Optimized for Windows with WSL2

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Project paths
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

# Configuration
BACKEND_PORT=8004
FRONTEND_PORT=3000
BACKEND_HOST="0.0.0.0"

# Logging
LOG_DIR="$PROJECT_ROOT/logs"
mkdir -p "$LOG_DIR"

print_header() {
    echo -e "${CYAN}${BOLD}"
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║                  HTX TRADING PLATFORM                   ║"
    echo "║               Personal Development Environment            ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_status() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $1"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

check_prerequisites() {
    print_status "Checking prerequisites..."
    
    local missing=0
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 not found"
        missing=1
    else
        local python_version=$(python3 --version | cut -d' ' -f2)
        print_success "Python $python_version found"
    fi
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        print_warning "Node.js not found (frontend will not start)"
    else
        local node_version=$(node --version)
        print_success "Node.js $node_version found"
    fi
    
    # Check required directories
    if [[ ! -d "$BACKEND_DIR" ]]; then
        print_error "Backend directory not found: $BACKEND_DIR"
        missing=1
    fi
    
    if [[ ! -d "$FRONTEND_DIR" ]]; then
        print_warning "Frontend directory not found: $FRONTEND_DIR"
    fi
    
    # Check environment file
    if [[ ! -f "$PROJECT_ROOT/.env" ]]; then
        print_warning ".env file not found. Run activate_project.py first."
    else
        print_success "Environment configuration found"
    fi
    
    if [[ $missing -eq 1 ]]; then
        print_error "Missing prerequisites. Please install required components."
        exit 1
    fi
}

setup_environment() {
    print_status "Setting up environment..."
    
    # Set Python path
    export PYTHONPATH="$BACKEND_DIR:$PYTHONPATH"
    
    # Set GCP credentials if available
    if [[ -f "$PROJECT_ROOT/gcp-service-account.json" ]]; then
        export GOOGLE_APPLICATION_CREDENTIALS="$PROJECT_ROOT/gcp-service-account.json"
        print_success "GCP credentials configured"
    fi
    
    # Load environment variables
    if [[ -f "$PROJECT_ROOT/.env" ]]; then
        set -a
        source "$PROJECT_ROOT/.env"
        set +a
        print_success "Environment variables loaded"
    fi
}

install_dependencies() {
    if [[ "$1" == "--skip-deps" ]]; then
        print_status "Skipping dependency installation"
        return
    fi
    
    print_status "Installing/updating dependencies..."
    
    # Backend dependencies
    if [[ -f "$BACKEND_DIR/requirements.txt" ]]; then
        print_status "Installing backend dependencies..."
        cd "$BACKEND_DIR"
        if python3 -m pip install -r requirements.txt > "$LOG_DIR/pip_install.log" 2>&1; then
            print_success "Backend dependencies installed"
        else
            print_warning "Backend dependency installation had issues (check $LOG_DIR/pip_install.log)"
        fi
        cd "$PROJECT_ROOT"
    fi
    
    # Frontend dependencies
    if [[ -f "$FRONTEND_DIR/package.json" ]] && command -v npm &> /dev/null; then
        print_status "Installing frontend dependencies..."
        cd "$FRONTEND_DIR"
        if npm install > "$LOG_DIR/npm_install.log" 2>&1; then
            print_success "Frontend dependencies installed"
        else
            print_warning "Frontend dependency installation had issues (check $LOG_DIR/npm_install.log)"
        fi
        cd "$PROJECT_ROOT"
    fi
}

check_ports() {
    print_status "Checking port availability..."
    
    # Check backend port
    if lsof -Pi :$BACKEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_warning "Port $BACKEND_PORT is already in use"
        local pid=$(lsof -Pi :$BACKEND_PORT -sTCP:LISTEN -t)
        print_status "Process using port $BACKEND_PORT: PID $pid"
        
        read -p "Kill existing process? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            kill -9 $pid
            print_success "Killed process $pid"
            sleep 2
        else
            print_error "Cannot start backend on port $BACKEND_PORT"
            exit 1
        fi
    else
        print_success "Port $BACKEND_PORT is available"
    fi
    
    # Check frontend port
    if lsof -Pi :$FRONTEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_warning "Port $FRONTEND_PORT is already in use"
        local pid=$(lsof -Pi :$FRONTEND_PORT -sTCP:LISTEN -t)
        print_status "Process using port $FRONTEND_PORT: PID $pid"
    else
        print_success "Port $FRONTEND_PORT is available"
    fi
}

start_backend() {
    print_status "Starting HTX backend server..."
    
    cd "$BACKEND_DIR"
    
    # Create PID file directory
    mkdir -p "$PROJECT_ROOT/.pids"
    
    # Start backend with proper logging
    python3 -m uvicorn app.main:app \
        --host "$BACKEND_HOST" \
        --port "$BACKEND_PORT" \
        --reload \
        --log-level info \
        --access-log \
        > "$LOG_DIR/backend.log" 2>&1 &
    
    local backend_pid=$!
    echo $backend_pid > "$PROJECT_ROOT/.pids/backend.pid"
    
    # Wait for backend to start
    local attempts=0
    local max_attempts=30
    
    while [[ $attempts -lt $max_attempts ]]; do
        if curl -s "http://localhost:$BACKEND_PORT/" > /dev/null 2>&1; then
            print_success "Backend server started (PID: $backend_pid)"
            print_status "Backend API: http://localhost:$BACKEND_PORT"
            print_status "API Documentation: http://localhost:$BACKEND_PORT/docs"
            return 0
        fi
        
        sleep 1
        ((attempts++))
        
        if [[ $((attempts % 5)) -eq 0 ]]; then
            print_status "Waiting for backend... ($attempts/$max_attempts)"
        fi
    done
    
    print_error "Backend failed to start within ${max_attempts} seconds"
    print_status "Check backend logs: $LOG_DIR/backend.log"
    return 1
}

start_frontend() {
    if [[ ! -d "$FRONTEND_DIR" ]] || ! command -v npm &> /dev/null; then
        print_warning "Frontend cannot be started (Node.js or frontend directory missing)"
        return 1
    fi
    
    print_status "Starting HTX frontend development server..."
    
    cd "$FRONTEND_DIR"
    
    # Create PID file directory
    mkdir -p "$PROJECT_ROOT/.pids"
    
    # Start frontend
    npm run dev > "$LOG_DIR/frontend.log" 2>&1 &
    
    local frontend_pid=$!
    echo $frontend_pid > "$PROJECT_ROOT/.pids/frontend.pid"
    
    # Wait for frontend to start
    local attempts=0
    local max_attempts=30
    
    while [[ $attempts -lt $max_attempts ]]; do
        if curl -s "http://localhost:$FRONTEND_PORT/" > /dev/null 2>&1; then
            print_success "Frontend server started (PID: $frontend_pid)"
            print_status "Frontend URL: http://localhost:$FRONTEND_PORT"
            return 0
        fi
        
        sleep 1
        ((attempts++))
        
        if [[ $((attempts % 5)) -eq 0 ]]; then
            print_status "Waiting for frontend... ($attempts/$max_attempts)"
        fi
    done
    
    print_warning "Frontend may still be starting (check $LOG_DIR/frontend.log)"
    return 0
}

start_services() {
    local start_mode="$1"
    
    case "$start_mode" in
        "backend")
            start_backend
            ;;
        "frontend")
            start_frontend
            ;;
        "full"|*)
            start_backend
            if [[ $? -eq 0 ]]; then
                start_frontend
            else
                print_error "Backend failed to start, skipping frontend"
                return 1
            fi
            ;;
    esac
}

cleanup() {
    print_status "Shutting down services..."
    
    # Kill backend
    if [[ -f "$PROJECT_ROOT/.pids/backend.pid" ]]; then
        local backend_pid=$(cat "$PROJECT_ROOT/.pids/backend.pid")
        if kill -0 $backend_pid 2>/dev/null; then
            kill -TERM $backend_pid
            print_success "Backend server stopped"
        fi
        rm -f "$PROJECT_ROOT/.pids/backend.pid"
    fi
    
    # Kill frontend
    if [[ -f "$PROJECT_ROOT/.pids/frontend.pid" ]]; then
        local frontend_pid=$(cat "$PROJECT_ROOT/.pids/frontend.pid")
        if kill -0 $frontend_pid 2>/dev/null; then
            kill -TERM $frontend_pid
            print_success "Frontend server stopped"
        fi
        rm -f "$PROJECT_ROOT/.pids/frontend.pid"
    fi
    
    print_status "Cleanup completed"
}

show_help() {
    echo "HTX Project Development Environment Launcher"
    echo ""
    echo "Usage: $0 [OPTIONS] [MODE]"
    echo ""
    echo "Modes:"
    echo "  full       Start both backend and frontend (default)"
    echo "  backend    Start only backend"
    echo "  frontend   Start only frontend"
    echo ""
    echo "Options:"
    echo "  --skip-deps    Skip dependency installation"
    echo "  --no-check     Skip prerequisite checks"
    echo "  --help         Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                    # Start full environment"
    echo "  $0 backend            # Start only backend"
    echo "  $0 --skip-deps full   # Start full, skip deps"
}

main() {
    local start_mode="full"
    local skip_deps=false
    local skip_checks=false
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-deps)
                skip_deps=true
                shift
                ;;
            --no-check)
                skip_checks=true
                shift
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            backend|frontend|full)
                start_mode="$1"
                shift
                ;;
            *)
                print_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # Set up signal handlers
    trap cleanup EXIT INT TERM
    
    print_header
    
    # Check prerequisites
    if [[ "$skip_checks" != true ]]; then
        check_prerequisites
    fi
    
    # Setup environment
    setup_environment
    
    # Install dependencies
    if [[ "$skip_deps" != true ]]; then
        install_dependencies
    fi
    
    # Check ports
    check_ports
    
    # Start services
    start_services "$start_mode"
    
    # Show status
    echo ""
    print_success "HTX Trading Platform is running!"
    echo ""
    echo -e "${BOLD}🌐 Access URLs:${NC}"
    if [[ "$start_mode" == "full" ]] || [[ "$start_mode" == "frontend" ]]; then
        echo -e "${CYAN}   📊 Dashboard:${NC}    http://localhost:$FRONTEND_PORT"
    fi
    if [[ "$start_mode" == "full" ]] || [[ "$start_mode" == "backend" ]]; then
        echo -e "${CYAN}   📡 API:${NC}          http://localhost:$BACKEND_PORT"
        echo -e "${CYAN}   📚 API Docs:${NC}     http://localhost:$BACKEND_PORT/docs"
    fi
    echo ""
    echo -e "${BOLD}📝 Logs:${NC}"
    echo -e "${CYAN}   Backend:${NC}       $LOG_DIR/backend.log"
    if [[ "$start_mode" == "full" ]] || [[ "$start_mode" == "frontend" ]]; then
        echo -e "${CYAN}   Frontend:${NC}      $LOG_DIR/frontend.log"
    fi
    echo ""
    echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
    
    # Wait for user interrupt
    while true; do
        sleep 1
    done
}

# Run main function
main "$@"