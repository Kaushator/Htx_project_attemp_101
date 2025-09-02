#!/bin/bash
# HTX Trading Platform - Docker Management Script

set -e

# Colors for output
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
BLUE='\\033[0;34m'
NC='\\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e \"${GREEN}[INFO]${NC} $1\"
}

print_warning() {
    echo -e \"${YELLOW}[WARNING]${NC} $1\"
}

print_error() {
    echo -e \"${RED}[ERROR]${NC} $1\"
}

print_header() {
    echo -e \"${BLUE}=== $1 ===${NC}\"
}

# Check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error \"Docker is not running. Please start Docker Desktop.\"
        exit 1
    fi
    print_status \"Docker is running\"
}

# Check if docker-compose is available
check_compose() {
    if ! command -v docker-compose > /dev/null 2>&1; then
        print_error \"docker-compose is not installed or not in PATH\"
        exit 1
    fi
    print_status \"docker-compose is available\"
}

# Build containers
build_containers() {
    print_header \"Building Docker Containers\"
    print_status \"Building HTX Trading Platform containers...\"
    
    docker-compose build --no-cache
    
    if [ $? -eq 0 ]; then
        print_status \"✅ Containers built successfully\"
    else
        print_error \"❌ Failed to build containers\"
        exit 1
    fi
}

# Start services
start_services() {
    print_header \"Starting HTX Trading Platform\"
    
    # Create necessary directories
    mkdir -p data logs
    
    # Copy environment file if it doesn't exist
    if [ ! -f \"backend/.env\" ]; then
        print_warning \"No .env file found, copying from .env.docker template\"
        cp backend/.env.docker backend/.env
        print_warning \"⚠️  Please update backend/.env with your API keys before production use\"
    fi
    
    print_status \"Starting services...\"
    docker-compose up -d
    
    if [ $? -eq 0 ]; then
        print_status \"✅ Services started successfully\"
        show_status
    else
        print_error \"❌ Failed to start services\"
        exit 1
    fi
}

# Stop services
stop_services() {
    print_header \"Stopping HTX Trading Platform\"
    
    print_status \"Stopping services...\"
    docker-compose down
    
    if [ $? -eq 0 ]; then
        print_status \"✅ Services stopped successfully\"
    else
        print_error \"❌ Failed to stop services\"
        exit 1
    fi
}

# Show service status
show_status() {
    print_header \"Service Status\"
    docker-compose ps
    
    echo -e \"\n${BLUE}=== Service URLs ===${NC}\"
    echo -e \"🔗 API Documentation: ${GREEN}http://localhost:8000/docs${NC}\"
    echo -e \"💚 Health Check: ${GREEN}http://localhost:8000/api/v1/health${NC}\"
    echo -e \"🌐 Frontend: ${GREEN}http://localhost:3000${NC}\"
    echo -e \"📊 Redis: ${GREEN}redis://localhost:6379${NC}\"
}

# Show logs
show_logs() {
    print_header \"Service Logs\"
    if [ -n \"$1\" ]; then
        docker-compose logs -f \"$1\"
    else
        docker-compose logs -f
    fi
}

# Clean up containers and volumes
cleanup() {
    print_header \"Cleaning Up Docker Resources\"
    
    print_warning \"This will remove all containers, networks, and volumes\"
    read -p \"Are you sure? (y/N): \" confirm
    
    if [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]]; then
        print_status \"Stopping and removing containers...\"
        docker-compose down -v --remove-orphans
        
        print_status \"Removing unused Docker resources...\"
        docker system prune -f
        
        print_status \"✅ Cleanup completed\"
    else
        print_status \"Cleanup cancelled\"
    fi
}

# Restart specific service
restart_service() {
    if [ -z \"$1\" ]; then
        print_error \"Please specify a service name (api, redis, frontend)\"
        exit 1
    fi
    
    print_header \"Restarting Service: $1\"
    docker-compose restart \"$1\"
    
    if [ $? -eq 0 ]; then
        print_status \"✅ Service $1 restarted successfully\"
    else
        print_error \"❌ Failed to restart service $1\"
        exit 1
    fi
}

# Execute command in container
exec_command() {
    if [ -z \"$1\" ]; then
        print_error \"Please specify a service name\"
        exit 1
    fi
    
    service=\"$1\"
    shift
    command=\"$@\"
    
    if [ -z \"$command\" ]; then
        command=\"/bin/bash\"
    fi
    
    print_header \"Executing in $service: $command\"
    docker-compose exec \"$service\" $command
}

# Database operations
db_operations() {
    case \"$1\" in
        \"migrate\")
            print_header \"Running Database Migrations\"
            docker-compose exec api alembic upgrade head
            ;;
        \"reset\")
            print_header \"Resetting Database\"
            print_warning \"This will delete all data!\"
            read -p \"Are you sure? (y/N): \" confirm
            if [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]]; then
                docker-compose exec api rm -f /app/data/app.db
                docker-compose exec api alembic upgrade head
                print_status \"✅ Database reset completed\"
            fi
            ;;
        \"backup\")
            print_header \"Creating Database Backup\"
            timestamp=$(date +\"%Y%m%d_%H%M%S\")
            docker-compose exec api cp /app/data/app.db \"/app/data/backup_${timestamp}.db\"
            print_status \"✅ Database backed up to backup_${timestamp}.db\"
            ;;
        *)
            print_error \"Unknown database operation. Use: migrate, reset, backup\"
            exit 1
            ;;
    esac
}

# Main script logic
case \"$1\" in
    \"build\")
        check_docker
        check_compose
        build_containers
        ;;
    \"start\")
        check_docker
        check_compose
        start_services
        ;;
    \"stop\")
        check_docker
        check_compose
        stop_services
        ;;
    \"restart\")
        check_docker
        check_compose
        if [ -n \"$2\" ]; then
            restart_service \"$2\"
        else
            stop_services
            start_services
        fi
        ;;
    \"status\")
        check_docker
        show_status
        ;;
    \"logs\")
        check_docker
        show_logs \"$2\"
        ;;
    \"exec\")
        check_docker
        shift
        exec_command \"$@\"
        ;;
    \"db\")
        check_docker
        db_operations \"$2\"
        ;;
    \"cleanup\")
        check_docker
        cleanup
        ;;
    \"full-setup\")
        check_docker
        check_compose
        build_containers
        start_services
        ;;
    *)
        echo \"HTX Trading Platform - Docker Management Script\"
        echo \"\"
        echo \"Usage: $0 {command} [options]\"
        echo \"\"
        echo \"Commands:\"
        echo \"  build          Build all Docker containers\"
        echo \"  start          Start all services\"
        echo \"  stop           Stop all services\"
        echo \"  restart [svc]  Restart all services or specific service\"
        echo \"  status         Show service status and URLs\"
        echo \"  logs [svc]     Show logs for all services or specific service\"
        echo \"  exec <svc> [cmd] Execute command in service container\"
        echo \"  db <operation> Database operations (migrate, reset, backup)\"
        echo \"  cleanup        Remove all containers and volumes\"
        echo \"  full-setup     Build and start everything\"
        echo \"\"
        echo \"Examples:\"
        echo \"  $0 full-setup     # Complete setup and start\"
        echo \"  $0 logs api       # Show API logs\"
        echo \"  $0 exec api bash  # Open bash in API container\"
        echo \"  $0 db migrate     # Run database migrations\"
        echo \"\"
        exit 1
        ;;
esac