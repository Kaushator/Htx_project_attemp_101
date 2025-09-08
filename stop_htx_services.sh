#!/bin/bash
# HTX Project - Service Stopper
# Gracefully stop HTX Trading Platform services

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Project paths
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_DIR="$PROJECT_ROOT/.pids"

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

stop_service() {
    local service_name="$1"
    local pid_file="$PID_DIR/${service_name}.pid"
    
    if [[ ! -f "$pid_file" ]]; then
        print_warning "$service_name PID file not found"
        return 0
    fi
    
    local pid=$(cat "$pid_file")
    
    if ! kill -0 "$pid" 2>/dev/null; then
        print_warning "$service_name process (PID: $pid) not running"
        rm -f "$pid_file"
        return 0
    fi
    
    print_status "Stopping $service_name (PID: $pid)..."
    
    # Try graceful shutdown first
    kill -TERM "$pid"
    
    # Wait for graceful shutdown
    local attempts=0
    local max_attempts=10
    
    while [[ $attempts -lt $max_attempts ]]; do
        if ! kill -0 "$pid" 2>/dev/null; then
            print_success "$service_name stopped gracefully"
            rm -f "$pid_file"
            return 0
        fi
        
        sleep 1
        ((attempts++))
    done
    
    # Force kill if still running
    print_warning "Force killing $service_name..."
    kill -KILL "$pid" 2>/dev/null
    
    if ! kill -0 "$pid" 2>/dev/null; then
        print_success "$service_name force stopped"
        rm -f "$pid_file"
        return 0
    else
        print_error "Failed to stop $service_name"
        return 1
    fi
}

stop_port_processes() {
    local port="$1"
    local service_name="$2"
    
    print_status "Checking for processes on port $port..."
    
    local pids=$(lsof -Pi :$port -sTCP:LISTEN -t 2>/dev/null)
    
    if [[ -z "$pids" ]]; then
        print_success "No processes found on port $port"
        return 0
    fi
    
    print_status "Found processes on port $port: $pids"
    
    for pid in $pids; do
        local process_info=$(ps -p $pid -o comm= 2>/dev/null || echo "unknown")
        print_status "Killing $service_name process: $pid ($process_info)"
        
        # Try graceful shutdown
        kill -TERM $pid 2>/dev/null
        sleep 2
        
        # Force kill if still running
        if kill -0 $pid 2>/dev/null; then
            kill -KILL $pid 2>/dev/null
        fi
        
        if ! kill -0 $pid 2>/dev/null; then
            print_success "Process $pid stopped"
        else
            print_error "Failed to stop process $pid"
        fi
    done
}

cleanup_resources() {
    print_status "Cleaning up resources..."
    
    # Remove PID directory if empty
    if [[ -d "$PID_DIR" ]] && [[ -z "$(ls -A "$PID_DIR")" ]]; then
        rmdir "$PID_DIR"
        print_success "PID directory cleaned up"
    fi
    
    # Clean up any temporary files
    local temp_files=("$PROJECT_ROOT"/*.tmp "$PROJECT_ROOT"/*.lock)
    for file in "${temp_files[@]}"; do
        if [[ -f "$file" ]]; then
            rm -f "$file"
            print_success "Removed temporary file: $(basename "$file")"
        fi
    done
}

show_help() {
    echo "HTX Project Service Stopper"
    echo ""
    echo "Usage: $0 [OPTIONS] [SERVICE]"
    echo ""
    echo "Services:"
    echo "  all        Stop all services (default)"
    echo "  backend    Stop only backend"
    echo "  frontend   Stop only frontend"
    echo "  ports      Kill processes on HTX ports"
    echo ""
    echo "Options:"
    echo "  --force    Force kill all processes immediately"
    echo "  --clean    Clean up resources after stopping"
    echo "  --help     Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                # Stop all services"
    echo "  $0 backend        # Stop only backend"
    echo "  $0 --force all    # Force stop all services"
}

main() {
    local service="all"
    local force_kill=false
    local cleanup=false
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --force)
                force_kill=true
                shift
                ;;
            --clean)
                cleanup=true
                shift
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            all|backend|frontend|ports)
                service="$1"
                shift
                ;;
            *)
                print_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    echo -e "${BLUE}${BOLD}"
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║                HTX SERVICE STOPPER                       ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    print_status "Stopping HTX Trading Platform services..."
    
    case "$service" in
        "backend")
            stop_service "backend"
            if [[ "$force_kill" == true ]]; then
                stop_port_processes "8004" "backend"
            fi
            ;;
        "frontend")
            stop_service "frontend"
            if [[ "$force_kill" == true ]]; then
                stop_port_processes "3000" "frontend"
            fi
            ;;
        "ports")
            stop_port_processes "8004" "backend"
            stop_port_processes "3000" "frontend"
            ;;
        "all"|*)
            stop_service "backend"
            stop_service "frontend"
            
            if [[ "$force_kill" == true ]]; then
                stop_port_processes "8004" "backend"
                stop_port_processes "3000" "frontend"
            fi
            ;;
    esac
    
    if [[ "$cleanup" == true ]]; then
        cleanup_resources
    fi
    
    print_success "Service stopping completed"
}

# Run main function
main "$@"