#!/bin/bash
# Fix WSL2 and Docker Issues for HTX Project

set -e

echo "🔧 HTX Project - WSL2 & Docker Fix Script"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Step 1: Fix WSL environment
print_header "Step 1: Fixing WSL Environment"

# Check if we're in WSL
if [[ ! -f /proc/version ]] || ! grep -q Microsoft /proc/version; then
    print_error "This script must be run inside WSL2"
    print_warning "Please open WSL2 terminal and run this script"
    exit 1
fi

print_status "Running in WSL environment"

# Update system packages
print_status "Updating system packages..."
sudo apt update
sudo apt install -y curl wget unzip software-properties-common

# Install Python and build tools
print_status "Installing Python and development tools..."
sudo apt install -y python3 python3-pip python3-venv python3-dev
sudo apt install -y build-essential

# Install Node.js (for frontend if needed)
print_status "Installing Node.js..."
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Step 2: Fix Docker in WSL2
print_header "Step 2: Setting up Docker for WSL2"

# Check if Docker Desktop is running on Windows
if command -v docker.exe &> /dev/null; then
    print_status "Docker Desktop detected on Windows"
    
    # Create symbolic links for Docker commands
    if [ ! -L /usr/local/bin/docker ]; then
        sudo ln -sf /mnt/c/Program\ Files/Docker/Docker/resources/bin/docker.exe /usr/local/bin/docker
    fi
    
    if [ ! -L /usr/local/bin/docker-compose ]; then
        sudo ln -sf /mnt/c/Program\ Files/Docker/Docker/resources/bin/docker-compose.exe /usr/local/bin/docker-compose
    fi
    
    print_status "Docker commands linked successfully"
else
    print_warning "Docker Desktop not found. Please install Docker Desktop for Windows"
    print_warning "Download from: https://www.docker.com/products/docker-desktop"
fi

# Step 3: Set up project environment
print_header "Step 3: Setting up HTX Project Environment"

# Get project root directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

print_status "Project root: $PROJECT_ROOT"

# Create necessary directories
mkdir -p "$PROJECT_ROOT/data"
mkdir -p "$PROJECT_ROOT/logs"
mkdir -p "$PROJECT_ROOT/backend/data"
mkdir -p "$PROJECT_ROOT/backend/logs"

# Set up Python virtual environment
if [ ! -d "$PROJECT_ROOT/.venv_wsl2" ]; then
    print_status "Creating Python virtual environment..."
    python3 -m venv "$PROJECT_ROOT/.venv_wsl2"
fi

# Activate virtual environment
source "$PROJECT_ROOT/.venv_wsl2/bin/activate"

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
if [ -f "$PROJECT_ROOT/backend/requirements.txt" ]; then
    print_status "Installing Python dependencies..."
    pip install -r "$PROJECT_ROOT/backend/requirements.txt"
else
    print_status "Installing basic dependencies..."
    pip install fastapi uvicorn sqlalchemy aiofiles python-multipart
    pip install pandas numpy redis aiohttp
fi

# Step 4: Fix environment configuration
print_header "Step 4: Configuring Environment"

# Create .env file if it doesn't exist
if [ ! -f "$PROJECT_ROOT/backend/.env" ]; then
    if [ -f "$PROJECT_ROOT/backend/.env.template" ]; then
        print_status "Creating .env from template..."
        cp "$PROJECT_ROOT/backend/.env.template" "$PROJECT_ROOT/backend/.env"
    elif [ -f "$PROJECT_ROOT/.env.template" ]; then
        cp "$PROJECT_ROOT/.env.template" "$PROJECT_ROOT/backend/.env"
    else
        print_status "Creating basic .env file..."
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

# HTX API Configuration (add your keys)
HTX_API_KEY=
HTX_API_SECRET=
HTX_SUBUID=
HTX_BASE_URL=https://api.huobi.pro

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/htx_project.log
EOF
    fi
    print_status "Environment file created"
fi

# Make scripts executable
print_status "Making scripts executable..."
find "$PROJECT_ROOT" -name "*.sh" -type f -exec chmod +x {} \;

# Step 5: Test the setup
print_header "Step 5: Testing Setup"

# Test Python environment
print_status "Testing Python environment..."
python3 -c "
import sys
print(f'Python version: {sys.version}')

try:
    import fastapi
    print('✅ FastAPI available')
except ImportError:
    print('❌ FastAPI not available')

try:
    import sqlalchemy
    print('✅ SQLAlchemy available')
except ImportError:
    print('❌ SQLAlchemy not available')
"

# Test Docker connection
if command -v docker &> /dev/null; then
    print_status "Testing Docker connection..."
    if docker info &> /dev/null; then
        print_status "✅ Docker is accessible from WSL2"
    else
        print_warning "❌ Docker is not accessible. Make sure Docker Desktop is running and WSL2 integration is enabled"
    fi
else
    print_warning "Docker command not found"
fi

# Final instructions
print_header "Setup Complete!"
print_status "✅ WSL2 environment configured"
print_status "✅ Python virtual environment created"
print_status "✅ Basic dependencies installed"
print_status "✅ Environment files configured"

echo -e "\n${BLUE}Next Steps:${NC}"
echo "1. Make sure Docker Desktop is running on Windows"
echo "2. Enable WSL2 integration in Docker Desktop settings"
echo "3. Add your HTX API keys to backend/.env file"
echo "4. Run the project with: ./start_wsl2.sh"

echo -e "\n${BLUE}Quick Test Commands:${NC}"
echo "# Test backend:"
echo "cd $PROJECT_ROOT && source .venv_wsl2/bin/activate && cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8004"
echo ""
echo "# Test Docker:"
echo "docker run hello-world"

print_status "Fix script completed successfully!"