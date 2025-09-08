#!/bin/bash
# HTX Project - Enhanced Docker Management for WSL2

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_cmd() {
    echo -e "${PURPLE}$ $1${NC}"
}

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

# Check if we're in WSL2
check_wsl() {
    if [[ -f /proc/version ]] && grep -q Microsoft /proc/version; then
        print_status "Running in WSL2 environment"
        return 0
    else
        print_error "This script should be run in WSL2"
        return 1
    fi
}

# Check if Docker is accessible
check_docker() {
    print_status "Checking Docker availability..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker command not found"
        print_warning "Please run fix_wsl_docker.sh first to set up Docker"
        return 1
    fi
    
    if ! docker info > /dev/null 2>&1; then
        print_error "Cannot connect to Docker daemon"
        print_warning "Make sure:"
        echo "  1. Docker Desktop is running on Windows"
        echo "  2. WSL2 integration is enabled in Docker Desktop settings"
        echo "  3. Your WSL2 distribution is enabled in Docker Desktop"
        return 1
    fi
    
    print_success "Docker is accessible"
    return 0
}

# Check if docker-compose is available
check_compose() {
    if command -v docker-compose > /dev/null 2>&1; then
        print_success "docker-compose is available"
        return 0
    elif docker compose version > /dev/null 2>&1; then
        print_success "docker compose (plugin) is available"
        # Create alias for compatibility
        alias docker-compose='docker compose'
        return 0
    else
        print_error "docker-compose is not available"
        return 1
    fi
}

# Setup environment
setup_environment() {
    print_header "Setting up Environment"
    
    # Create necessary directories
    mkdir -p "$PROJECT_ROOT/data"
    mkdir -p "$PROJECT_ROOT/logs" 
    mkdir -p "$PROJECT_ROOT/backend/data"
    mkdir -p "$PROJECT_ROOT/backend/logs"
    
    # Copy environment file if needed
    if [ ! -f "$PROJECT_ROOT/backend/.env" ]; then
        if [ -f "$PROJECT_ROOT/backend/.env.template" ]; then
            print_status "Creating .env from template..."
            cp "$PROJECT_ROOT/backend/.env.template" "$PROJECT_ROOT/backend/.env"
        elif [ -f "$PROJECT_ROOT/.env.template" ]; then
            cp "$PROJECT_ROOT/.env.template" "$PROJECT_ROOT/backend/.env"
        else
            print_warning "No .env template found, creating basic .env"
            create_basic_env
        fi
        print_warning "⚠️ Please update backend/.env with your API keys"
    fi
    
    print_success "Environment setup completed"
}

# Create basic .env file
create_basic_env() {
    cat > "$PROJECT_ROOT/backend/.env" << 'EOF'
# Environment Configuration
ENV=development
DEBUG=true

# Server Configuration  
API_HOST=0.0.0.0
API_PORT=8004

# Database Configuration
DATABASE_URL=sqlite+aiosqlite:///./data/app.db

# CORS Configuration
ALLOWED_HOSTS=http://localhost:3000,http://localhost:8080

# Redis Configuration  
REDIS_URL=redis://localhost:6379

# HTX API Configuration
HTX_API_KEY=your_htx_api_key_here
HTX_API_SECRET=your_htx_api_secret_here
HTX_SUBUID=your_subuid_here
HTX_BASE_URL=https://api.huobi.pro

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/htx_project.log
EOF
}

# Build containers
build_containers() {
    print_header "Building Docker Containers"
    
    cd "$PROJECT_ROOT"
    
    print_status "Building HTX Trading Platform containers..."
    print_cmd "docker-compose build --no-cache"
    
    if docker-compose build --no-cache; then
        print_success "Containers built successfully"
    else
        print_error "Failed to build containers"
        return 1
    fi
}

# Start services
start_services() {
    print_header "Starting HTX Trading Platform"
    
    cd "$PROJECT_ROOT"
    setup_environment
    
    print_status "Starting services..."
    print_cmd "docker-compose up -d"
    
    if docker-compose up -d; then
        print_success "Services started successfully"
        sleep 3
        show_status
    else
        print_error "Failed to start services"
        print_status "Checking logs..."
        docker-compose logs
        return 1
    fi
}

# Stop services
stop_services() {
    print_header "Stopping HTX Trading Platform"
    
    cd "$PROJECT_ROOT"
    
    print_status "Stopping services..."
    print_cmd "docker-compose down"
    
    if docker-compose down; then
        print_success "Services stopped successfully"
    else
        print_error "Failed to stop services"
        return 1
    fi
}

# Show service status  
show_status() {
    print_header "Service Status"
    
    cd "$PROJECT_ROOT"
    docker-compose ps
    
    echo -e "\n${BLUE}=== Service URLs ===${NC}"
    echo -e "🔗 API Documentation: ${GREEN}http://localhost:8000/docs${NC}"
    echo -e "💚 Health Check: ${GREEN}http://localhost:8000/api/v1/health${NC}" 
    echo -e "🌐 Frontend: ${GREEN}http://localhost:3000${NC}"
    echo -e "📊 Redis: ${GREEN}redis://localhost:6379${NC}"
    
    echo -e "\n${BLUE}=== Quick Test Commands ===${NC}"
    echo "curl http://localhost:8000/api/v1/health"
    echo "curl http://localhost:8000/docs"
}

# Show logs
show_logs() {
    print_header "Service Logs"
    
    cd "$PROJECT_ROOT"
    
    if [ -n "$1" ]; then
        print_status "Showing logs for service: $1"
        docker-compose logs -f "$1"
    else
        print_status "Showing logs for all services"
        docker-compose logs -f
    fi
}

# Clean up
cleanup() {
    print_header "Cleaning Up Docker Resources"
    
    cd "$PROJECT_ROOT"
    
    print_warning "This will remove all containers, networks, and volumes"
    read -p "Are you sure? (y/N): " confirm
    
    if [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]]; then
        print_status "Stopping and removing containers..."
        docker-compose down -v --remove-orphans
        
        print_status "Removing unused Docker resources..."
        docker system prune -f
        
        print_success "Cleanup completed"
    else
        print_status "Cleanup cancelled"
    fi
}

# Restart service
restart_service() {
    if [ -z "$1" ]; then
        print_error "Please specify a service name (api, redis)"
        return 1
    fi
    
    print_header "Restarting Service: $1"
    
    cd "$PROJECT_ROOT"
    
    if docker-compose restart "$1"; then
        print_success "Service $1 restarted successfully"
    else
        print_error "Failed to restart service $1"
        return 1
    fi
}

# Execute command in container
exec_command() {
    if [ -z "$1" ]; then
        print_error "Please specify a service name"
        return 1
    fi
    
    service="$1"
    shift
    command="$@"
    
    if [ -z "$command" ]; then
        command="/bin/bash"
    fi
    
    print_header "Executing in $service: $command"
    
    cd "$PROJECT_ROOT"
    docker-compose exec "$service" $command
}

# Show help
show_help() {
    cat << 'EOF'
HTX Trading Platform - Docker Management Script

USAGE:
    ./docker-manage-wsl2.sh [COMMAND] [OPTIONS]

COMMANDS:
    build           Build all containers
    start           Start all services
    stop            Stop all services  
    restart [svc]   Restart service (or all if no service specified)
    status          Show service status
    logs [svc]      Show logs (all services or specific service)
    exec <svc> [cmd] Execute command in service container
    cleanup         Remove all containers and volumes
    help            Show this help message

EXAMPLES:
    ./docker-manage-wsl2.sh build
    ./docker-manage-wsl2.sh start
    ./docker-manage-wsl2.sh logs api
    ./docker-manage-wsl2.sh exec api /bin/bash
    ./docker-manage-wsl2.sh restart redis

PREREQUISITES:
    - WSL2 with Ubuntu
    - Docker Desktop running with WSL2 integration enabled
    - Run ./fix_wsl_docker.sh first if you encounter issues

EOF
}

# Main script logic
main() {
    if ! check_wsl; then
        exit 1
    fi
    
    case "${1:-help}" in
        "build")
            check_docker && check_compose && build_containers
            ;;
        "start")
            check_docker && check_compose && start_services
            ;;
        "stop")
            check_docker && check_compose && stop_services
            ;;
        "restart")
            check_docker && check_compose
            if [ -n "$2" ]; then
                restart_service "$2"
            else
                stop_services && start_services
            fi
            ;;
        "status")
            check_docker && check_compose && show_status
            ;;
        "logs")
            check_docker && check_compose && show_logs "$2"
            ;;
        "exec")
            check_docker && check_compose
            shift
            exec_command "$@"
            ;;
        "cleanup")
            check_docker && check_compose && cleanup
            ;;
        "help"|"--help"|"-h")
            show_help
            ;;
        *)
            print_error "Unknown command: $1"
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"