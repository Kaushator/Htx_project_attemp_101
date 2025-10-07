# Installation Guide

Get the HTX Trading Platform running in your development environment.

## 🎯 Prerequisites

### System Requirements
- **OS**: Windows 10/11 with WSL 2 (Ubuntu)
- **Python**: 3.12+
- **Node.js**: 18+
- **Memory**: 16GB RAM (32GB for ML)
- **Storage**: 10GB (200GB+ for local LLMs)

### Required Software
- WSL 2 with Ubuntu
- Docker Desktop
- Git
- Make

## 🔧 WSL 2 Setup

```powershell
# Enable WSL 2 (PowerShell as Admin)
wsl --install
wsl --set-default-version 2
wsl --install -d Ubuntu
```

```bash
# Update Ubuntu
sudo apt update && sudo apt upgrade -y
sudo apt install -y make build-essential git curl wget
```

## 🐍 Python Setup

```bash
# Install Python 3.12
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.12 python3.12-venv python3.12-dev
```

## 📦 Node.js Setup

```bash
# Install Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

## 📁 Project Setup

```bash
# Clone repository
git clone https://github.com/your-username/Htx_project_attemp_101.git
cd Htx_project_attemp_101

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Quick setup
make install
```

## 🚀 Start Development

```bash
# Start all services
make dev

# Or start individually:
make backend-dev    # Backend on :8004
make frontend-dev   # Frontend on :3000
```

## 🐳 Docker Setup

```bash
# Build and run with Docker
make docker-build
make docker-run

# Services available:
# - Frontend: http://localhost:3000
# - Backend: http://localhost:8004
# - API Docs: http://localhost:8004/docs
```

## 🤖 ML Features

### CPU-Only (Default)
```bash
# Already included in requirements.txt
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

### GPU Support (NVIDIA)
```bash
# Install CUDA support
pip install torch --index-url https://download.pytorch.org/whl/cu118

# Set environment
export ML_DEVICE=cuda
export LOAD_IN_4BIT=true
```

### OpenAI Integration
```bash
# Set API key in .env
OPENAI_API_KEY=your_openai_key_here
```

## 🧪 Testing

```bash
# Run all tests
make test

# Backend only
make test-backend

# Frontend only  
make test-frontend

# With coverage
make test-coverage
```

## 🔧 Troubleshooting

### Common Issues
1. **WSL 2 not working**: Ensure virtualization enabled in BIOS
2. **Python version**: Use `python3.12` explicitly
3. **Node.js issues**: Clear npm cache with `npm cache clean --force`
4. **Docker permission**: Add user to docker group
5. **GPU not detected**: Install NVIDIA drivers and CUDA toolkit

### Useful Commands
```bash
# Check WSL version
wsl --list --verbose

# Check Python version
python3.12 --version

# Check Docker
docker --version

# Check GPU
nvidia-smi  # If available
```

## 📚 Next Steps

1. **[API Documentation](../api/overview.md)** - Learn the API
2. **[ML Features](../ml/overview.md)** - Explore AI capabilities
3. **[Configuration](configuration.md)** - Advanced settings
4. **[Troubleshooting](../troubleshooting/common-issues.md)** - Common issues
