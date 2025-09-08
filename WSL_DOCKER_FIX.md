# WSL2 & Docker Fix Guide for HTX Project

This guide helps resolve WSL2 and Docker connectivity issues.

## Quick Fix

### Option 1: Automatic Fix (Recommended)

1. **From Windows Command Prompt:**
```cmd
cd e:\Htx_project_attemp_101
fix_wsl_docker.bat
```

2. **Or from WSL2 terminal:**
```bash
cd /mnt/e/Htx_project_attemp_101
chmod +x fix_wsl_docker.sh
./fix_wsl_docker.sh
```

### Option 2: Manual Steps

#### Step 1: Fix WSL2 Environment
```bash
# Open WSL2 terminal and update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y curl wget python3 python3-pip python3-venv build-essential

# Install Node.js (if needed for frontend)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
```

#### Step 2: Fix Docker Integration
```bash
# Make sure Docker Desktop is running on Windows
# Enable WSL2 integration in Docker Desktop:
# Settings > Resources > WSL Integration > Enable integration with your distribution

# Test Docker connection
docker --version
docker info
```

#### Step 3: Set up Project Environment
```bash
cd /mnt/e/Htx_project_attemp_101

# Create virtual environment
python3 -m venv .venv_wsl2
source .venv_wsl2/bin/activate

# Install dependencies
pip install --upgrade pip
pip install fastapi uvicorn sqlalchemy aiofiles python-multipart
pip install pandas numpy redis aiohttp

# Create environment file
cp .env.template backend/.env
# Edit backend/.env with your API keys

# Make scripts executable
chmod +x *.sh
```

## Running the Project

### Using Docker (Recommended)
```bash
# Start services
./docker-manage-wsl2.sh start

# Check status
./docker-manage-wsl2.sh status

# View logs
./docker-manage-wsl2.sh logs

# Stop services
./docker-manage-wsl2.sh stop
```

### Using Direct Python (Alternative)
```bash
# Activate virtual environment
source .venv_wsl2/bin/activate

# Start backend
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8004 --reload
```

## Troubleshooting

### Common Issues

1. **"bash: not found" error**
   - Run the fix script: `./fix_wsl_docker.sh`
   - Update WSL: `wsl --update`

2. **Docker not accessible**
   - Make sure Docker Desktop is running
   - Enable WSL2 integration in Docker Desktop settings
   - Restart WSL: `wsl --shutdown` then reopen

3. **Permission denied on scripts**
   ```bash
   chmod +x *.sh
   find . -name "*.sh" -exec chmod +x {} \;
   ```

4. **Python dependencies missing**
   ```bash
   source .venv_wsl2/bin/activate
   pip install --upgrade pip
   pip install -r backend/requirements.txt
   ```

### Diagnostic Tools

Run diagnostics to identify issues:
```bash
./diagnose_wsl_docker.sh
```

## Project URLs (after starting)

- 🔗 API Documentation: http://localhost:8000/docs
- 💚 Health Check: http://localhost:8000/api/v1/health
- 🌐 Frontend: http://localhost:3000
- 📊 Redis: redis://localhost:6379

## Support Commands

```bash
# Build containers
./docker-manage-wsl2.sh build

# Restart specific service
./docker-manage-wsl2.sh restart api

# Execute command in container
./docker-manage-wsl2.sh exec api /bin/bash

# Clean up everything
./docker-manage-wsl2.sh cleanup

# Show help
./docker-manage-wsl2.sh help
```