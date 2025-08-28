# HTX Project WSL Setup Guide

This guide provides instructions for setting up and running the HTX Project in WSL (Windows Subsystem for Linux).

## Prerequisites

1. **WSL 2** installed with Ubuntu or similar Linux distribution
2. **Python 3.8+** installed in WSL
3. **Git** configured in WSL
4. **Node.js** (if running frontend)

## Quick Setup

### 1. Clone and Setup Environment

```bash
# Clone the repository
git clone https://github.com/Kaushator/Htx_project_attemp_101.git
cd Htx_project_attemp_101

# Run the WSL setup script
./scripts/setup_env.sh
```

### 2. Activate Environment and Start Services

```bash
# Activate virtual environment
source .venv/bin/activate

# Start the backend API
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8004
```

## Manual Setup (if setup script fails)

### 1. Create Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

### 2. Install Dependencies

```bash
# Backend dependencies
cd backend
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 3. Environment Configuration

```bash
# Copy environment template
cp backend/env.example backend/.env

# Edit with your API keys
nano backend/.env
```

### 4. Create Data Directories

```bash
mkdir -p data/{raw,processed,samples} logs
```

## Development Commands

### Code Quality

```bash
# Format code
cd backend
python -m black app/

# Check linting
python -m ruff check app/

# Run tests
pytest
```

### Database

```bash
# Initialize database
cd backend
alembic upgrade head
```

## WSL-Specific Notes

1. **File Paths**: All paths use forward slashes (`/`) instead of backslashes (`\`)
2. **Virtual Environment**: Located at `.venv/bin/activate` (not `Scripts\activate.bat`)
3. **Executable Scripts**: Make scripts executable with `chmod +x script_name.sh`
4. **Network Access**: API will be accessible at `http://localhost:8004` from Windows

## Troubleshooting

### Permission Issues
```bash
# Fix script permissions
chmod +x scripts/*.sh
```

### Python Version Issues
```bash
# Check Python version
python3 --version

# If needed, install Python 3.8+
sudo apt update
sudo apt install python3.8 python3.8-venv python3.8-dev
```

### Package Installation Issues
```bash
# Install system dependencies if needed
sudo apt install build-essential python3-dev
```

## VS Code Integration

For VS Code development in WSL:

1. Install "Remote - WSL" extension
2. Open project in WSL: `code .` from project directory
3. Select Python interpreter from `.venv/bin/python`

## Port Forwarding

WSL automatically forwards ports to Windows. Access the API from Windows at:
- `http://localhost:8004` - API server
- `http://localhost:8004/docs` - API documentation

## File Watching

For hot reload to work properly in WSL, ensure your files are stored in the WSL filesystem (`/home/username/...`) rather than the Windows filesystem (`/mnt/c/...`).