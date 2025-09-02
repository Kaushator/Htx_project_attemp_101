#!/bin/bash
# Quick fix for HTX Project dependencies in WSL2

echo "🔧 HTX Project - Quick Dependencies Fix"
echo "======================================"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m' 
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Get project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

echo -e "${BLUE}Project root: $PROJECT_ROOT${NC}"

# Check if we're in WSL
if ! grep -qEi "(Microsoft|WSL)" /proc/version &> /dev/null; then
    echo -e "${RED}❌ This script is designed for WSL2 environment${NC}"
    exit 1
fi

echo -e "${GREEN}✅ WSL2 environment detected${NC}"

# Create/activate virtual environment
VENV_DIR=".venv_wsl2"
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}Creating virtual environment: $VENV_DIR${NC}"
    python3 -m venv "$VENV_DIR"
else
    echo -e "${BLUE}Using existing virtual environment: $VENV_DIR${NC}"
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Verify Python version
PYTHON_VERSION=$(python --version 2>&1 | grep -o '[0-9]\+\.[0-9]\+')
if [[ $(echo "$PYTHON_VERSION >= 3.12" | bc 2>/dev/null || echo 0) == 1 ]]; then
    echo -e "${GREEN}✅ Python $PYTHON_VERSION (OK)${NC}"
else
    echo -e "${YELLOW}⚠️ Python $PYTHON_VERSION (3.12+ recommended)${NC}"
fi

# Upgrade pip
echo -e "${BLUE}Upgrading pip...${NC}"
python -m pip install --upgrade pip

# Install core dependencies
echo -e "${BLUE}Installing core dependencies...${NC}"
if [ -f "backend/requirements.txt" ]; then
    pip install -r backend/requirements.txt
else
    echo -e "${RED}❌ backend/requirements.txt not found${NC}"
    exit 1
fi

# Install additional development dependencies
if [ -f "backend/requirements-dev.txt" ]; then
    echo -e "${BLUE}Installing development dependencies...${NC}"
    pip install -r backend/requirements-dev.txt
fi

# Verify key imports
echo -e "${BLUE}Verifying key imports...${NC}"
python -c "
import sys
imports_to_test = [
    'fastapi', 'uvicorn', 'sqlalchemy', 'pydantic', 'pydantic_settings',
    'transformers', 'torch', 'openai', 'httpx', 'pandas', 'numpy'
]

failed = []
for module in imports_to_test:
    try:
        __import__(module)
        print(f'✅ {module}')
    except ImportError as e:
        print(f'❌ {module}: {e}')
        failed.append(module)

if failed:
    print(f'\n❌ Failed imports: {failed}')
    sys.exit(1)
else:
    print('\n✅ All key modules imported successfully!')
"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Dependencies installed and verified successfully!${NC}"
    echo -e "${YELLOW}To activate this environment:${NC}"
    echo -e "   source $PROJECT_ROOT/$VENV_DIR/bin/activate"
    echo -e "${YELLOW}To run the backend (Option 1 - Recommended):${NC}"
    echo -e "   cd backend && python run.py"
    echo -e "${YELLOW}To run the backend (Option 2 - Direct):${NC}"
    echo -e "   cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
    echo -e "${YELLOW}To run the backend (Option 3 - From project root):${NC}"
    echo -e "   bash start_backend.sh"
else
    echo -e "${RED}❌ Some dependencies failed to install${NC}"
    exit 1
fi