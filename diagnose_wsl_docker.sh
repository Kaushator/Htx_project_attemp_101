#!/bin/bash
# HTX Project - WSL2 and Docker Diagnostics

set +e  # Don't exit on errors, we want to see all issues

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo -e "\n${BLUE}=== $1 ===${NC}"
}

print_check() {
    echo -n "Checking $1... "
}

print_ok() {
    echo -e "${GREEN}✅ OK${NC}"
}

print_fail() {
    echo -e "${RED}❌ FAIL${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ WARNING${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️ $1${NC}"
}

# Start diagnostics
echo "HTX Project - WSL2 & Docker Diagnostics"
echo "========================================"

# Check WSL environment
print_header "WSL Environment"

print_check "WSL version"
if [[ -f /proc/version ]] && grep -q Microsoft /proc/version; then
    if grep -q "microsoft-standard-WSL2" /proc/version; then
        print_ok
        print_info "Running WSL2"
    else
        print_warning
        print_info "Running WSL1 (WSL2 recommended)"
    fi
else
    print_fail
    print_info "Not running in WSL"
fi

print_check "Linux distribution"
if [ -f /etc/os-release ]; then
    print_ok
    . /etc/os-release
    print_info "Distribution: $PRETTY_NAME"
else
    print_fail
    print_info "Cannot determine Linux distribution"
fi

print_check "Basic shell tools"
missing_tools=()
for tool in bash curl wget unzip; do
    if ! command -v "$tool" &> /dev/null; then
        missing_tools+=("$tool")
    fi
done

if [ ${#missing_tools[@]} -eq 0 ]; then
    print_ok
else
    print_fail
    print_info "Missing tools: ${missing_tools[*]}"
    echo "  Install with: sudo apt update && sudo apt install ${missing_tools[*]}"
fi

# Check Python environment
print_header "Python Environment"

print_check "Python 3"
if command -v python3 &> /dev/null; then
    print_ok
    python_version=$(python3 --version)
    print_info "$python_version"
else
    print_fail
    print_info "Python 3 not found"
    echo "  Install with: sudo apt install python3 python3-pip python3-venv"
fi

print_check "pip"
if command -v pip &> /dev/null || command -v pip3 &> /dev/null; then
    print_ok
else
    print_fail
    print_info "pip not found"
fi

print_check "Virtual environment"
if [ -d ".venv_wsl2" ]; then
    print_ok
    print_info "Virtual environment exists"
else
    print_warning
    print_info "Virtual environment not found"
    echo "  Create with: python3 -m venv .venv_wsl2"
fi

# Check Docker
print_header "Docker Environment"

print_check "Docker command"
if command -v docker &> /dev/null; then
    print_ok
    docker_version=$(docker --version 2>/dev/null || echo "Unknown version")
    print_info "$docker_version"
else
    print_fail
    print_info "Docker command not found"
    echo "  Install Docker Desktop for Windows and enable WSL2 integration"
fi

print_check "Docker daemon connection"
if docker info &> /dev/null; then
    print_ok
    print_info "Docker daemon accessible"
else
    print_fail
    print_info "Cannot connect to Docker daemon"
    echo "  Make sure:"
    echo "    - Docker Desktop is running"
    echo "    - WSL2 integration is enabled in Docker Desktop settings"
    echo "    - Your WSL2 distribution is enabled in Docker Desktop"
fi

print_check "docker-compose"
if command -v docker-compose &> /dev/null; then
    print_ok
    compose_version=$(docker-compose --version 2>/dev/null || echo "Unknown version")
    print_info "$compose_version"
elif docker compose version &> /dev/null; then
    print_ok
    print_info "Docker Compose plugin available"
else
    print_fail
    print_info "docker-compose not found"
fi

# Check project files
print_header "Project Structure"

print_check "Project root"
if [ -f "docker-compose.yml" ] || [ -f "Makefile" ]; then
    print_ok
    print_info "Project files found"
else
    print_warning
    print_info "May not be in project root directory"
fi

print_check "Backend directory"
if [ -d "backend" ]; then
    print_ok
else
    print_fail
    print_info "Backend directory not found"
fi

print_check "Environment file"
if [ -f "backend/.env" ]; then
    print_ok
    print_info "Environment file exists"
elif [ -f ".env.template" ] || [ -f "backend/.env.template" ]; then
    print_warning
    print_info "Template found but .env missing"
    echo "  Create with: cp .env.template backend/.env"
else
    print_fail
    print_info "No environment configuration found"
fi

print_check "Docker Compose file"
if [ -f "docker-compose.yml" ]; then
    print_ok
else
    print_fail
    print_info "docker-compose.yml not found"
fi

# Check network connectivity
print_header "Network Connectivity"

print_check "Internet connectivity"
if curl -s --max-time 5 https://www.google.com > /dev/null; then
    print_ok
else
    print_fail
    print_info "Cannot reach internet"
fi

print_check "Docker Hub connectivity"
if curl -s --max-time 5 https://hub.docker.com > /dev/null; then
    print_ok
else
    print_warning
    print_info "Cannot reach Docker Hub"
fi

# Summary and recommendations
print_header "Recommendations"

echo "Based on the diagnostics above:"
echo ""

# Check for common issues
if ! command -v docker &> /dev/null; then
    echo "🔧 Install Docker Desktop for Windows:"
    echo "   https://www.docker.com/products/docker-desktop"
    echo ""
fi

if [[ -f /proc/version ]] && grep -q Microsoft /proc/version && ! docker info &> /dev/null; then
    echo "🔧 Enable WSL2 integration in Docker Desktop:"
    echo "   1. Open Docker Desktop"
    echo "   2. Go to Settings > Resources > WSL Integration"
    echo "   3. Enable integration with your WSL2 distribution"
    echo ""
fi

if ! command -v python3 &> /dev/null; then
    echo "🔧 Install Python development environment:"
    echo "   sudo apt update"
    echo "   sudo apt install python3 python3-pip python3-venv build-essential"
    echo ""
fi

if [ ! -f "backend/.env" ]; then
    echo "🔧 Set up environment configuration:"
    echo "   cp .env.template backend/.env"
    echo "   # Edit backend/.env with your API keys"
    echo ""
fi

echo "🔧 To fix all issues automatically, run:"
echo "   ./fix_wsl_docker.sh"
echo ""

echo "🔧 To manage Docker services, use:"
echo "   ./docker-manage-wsl2.sh [command]"
echo ""

echo "Diagnostics complete!"