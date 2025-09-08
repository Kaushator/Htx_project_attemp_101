# HTX Trading Platform - Personal Setup Guide

Welcome to your personal HTX Trading Platform! This guide will walk you through the complete setup process for your personal PC with secure Google Secret Manager integration.

## 🚀 Quick Start (TL;DR)

1. **Run the activation script**: `python activate_project.py`
2. **Start the platform**: `./quick_start.ps1` (Windows) or `./start_htx_dev.sh` (WSL/Linux)
3. **Access your dashboard**: http://localhost:3000

---

## 📋 Prerequisites

### Required Software

- **Windows 10/11** with WSL2 enabled
- **Python 3.12+** (installed in WSL2)
- **Node.js 18+** (for frontend)
- **Git** (for updates)
- **Docker** (optional, for containerized deployment)

### WSL2 Setup

If you don't have WSL2 set up:

1. **Enable WSL2** (run as Administrator):
   ```powershell
   wsl --install -d Ubuntu
   ```

2. **Restart your computer** when prompted

3. **Set up Ubuntu** when it first launches

### Google Cloud Platform Account

You'll need:
- A GCP project with billing enabled
- Service Account with the following roles:
  - Secret Manager Admin
  - Storage Admin
  - Pub/Sub Admin
  - Vertex AI User (optional)

---

## 🔧 Complete Setup Process

### Step 1: Project Activation

Run the automated activation script:

```bash
python activate_project.py
```

This script will:
- ✅ Check prerequisites
- ☁️ Set up GCP project integration
- 🔐 Collect your API keys securely
- 🔒 Store secrets in Google Secret Manager
- 📦 Install all dependencies
- ⚙️ Generate configuration files
- ✅ Validate the setup

### Step 2: API Keys Required

During setup, you'll need to provide:

| Service | Required | Description |
|---------|----------|-------------|
| **HTX Exchange** | ✅ Required | API Key and Secret from HTX/Huobi |
| **OpenAI** | ⚠️ Recommended | For ML analytics and insights |
| **3Commas** | ⭕ Optional | For portfolio synchronization |
| **GCP Service Account** | ✅ Required | JSON key file for GCP services |

#### Getting HTX API Keys

1. Log in to [HTX/Huobi](https://www.htx.com)
2. Go to **Account** → **API Key Management**
3. Create a new API key with permissions:
   - Read account info
   - Read trading history
   - Read wallet balance
4. **Important**: Enable IP restrictions for security

#### Getting OpenAI API Key

1. Visit [OpenAI Platform](https://platform.openai.com)
2. Go to **API Keys** section
3. Create a new API key
4. Set usage limits to control costs

#### Setting up GCP Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project (or use existing)
3. Enable required APIs:
   - Secret Manager API
   - Cloud Storage API
   - Pub/Sub API
4. Create a Service Account:
   - Go to **IAM & Admin** → **Service Accounts**
   - Click **Create Service Account**
   - Assign roles: Secret Manager Admin, Storage Admin, Pub/Sub Admin
5. Download the JSON key file

### Step 3: Launch the Platform

#### Option A: Windows PowerShell (Recommended)

```powershell
.\quick_start.ps1
```

Available modes:
- `.\quick_start.ps1 full` - Start both backend and frontend
- `.\quick_start.ps1 backend` - Backend only
- `.\quick_start.ps1 frontend` - Frontend only

#### Option B: WSL2/Linux Direct

```bash
./start_htx_dev.sh
```

Available options:
- `./start_htx_dev.sh full` - Start both services
- `./start_htx_dev.sh backend` - Backend only
- `./start_htx_dev.sh --skip-deps` - Skip dependency check

### Step 4: Verify Setup

Run the validation script:

```bash
python validate_setup.py
```

This will test:
- ✅ Environment configuration
- ✅ Database connectivity
- ✅ API endpoints
- ✅ GCP integration
- ✅ Secret Manager access

---

## 🌐 Access URLs

Once running, access these URLs:

| Service | URL | Description |
|---------|-----|-------------|
| **Dashboard** | http://localhost:3000 | Main trading dashboard |
| **API** | http://localhost:8004 | Backend API |
| **API Docs** | http://localhost:8004/docs | Interactive API documentation |
| **Health Check** | http://localhost:8004/api/v1/health/ping | System health status |

---

## 🗂️ File Structure

After setup, your project will have:

```
HTX_Project/
├── 📁 backend/              # Python FastAPI backend
├── 📁 frontend/             # React frontend
├── 📁 logs/                 # Application logs
├── 📁 data/                 # Local data storage
├── 🔐 .env                  # Environment configuration
├── 🔑 gcp-service-account.json  # GCP credentials
├── 🚀 quick_start.ps1       # Windows launcher
├── 🚀 start_htx_dev.sh      # Linux launcher
├── 🛑 stop_htx_services.sh  # Service stopper
├── ✅ validate_setup.py     # Setup validator
└── 📋 activation_setup.log  # Setup logs
```

---

## 🔒 Security Features

### Google Secret Manager Integration

All sensitive data is stored securely:

- **HTX API Keys** → `htx-api-key`, `htx-api-secret`
- **OpenAI Key** → `openai-api-key`
- **3Commas Keys** → `threecommas-api-key`, `threecommas-api-secret`
- **Encryption Key** → `encryption-key`

### Local Encryption

As a fallback, local environment variables are encrypted using Fernet encryption.

### API Key Rotation

To rotate API keys:

1. Update the secret in Google Secret Manager
2. Restart the services
3. No code changes required!

---

## 🔧 Configuration Options

### Environment Variables

Key settings in `.env`:

```bash
# Core settings
ENV=dev
DEBUG=true
API_PORT=8004

# Database
DATABASE_URL=sqlite+aiosqlite:///./data/app.db

# GCP Integration
GCP_PROJECT_ID=your-project-id
USE_SECRET_MANAGER=true

# Feature toggles
ENABLE_ML_ENDPOINTS=true
ENABLE_GCP_ENDPOINTS=true
```

### Performance Tuning

For better performance:

```bash
# Hardware optimization
ML_DEVICE=cuda  # If you have NVIDIA GPU
LOAD_IN_4BIT=false  # Use full precision if you have RAM

# Database optimization (for high volume)
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/htx_db
```

---

## 🛠️ Troubleshooting

### Common Issues

#### 1. "WSL2 not found"

**Solution:**
```powershell
# Run as Administrator
wsl --install -d Ubuntu
# Restart computer
```

#### 2. "Port already in use"

**Solution:**
```bash
# Stop existing services
./stop_htx_services.sh

# Or kill specific processes
lsof -ti:8004 | xargs kill -9  # Backend
lsof -ti:3000 | xargs kill -9  # Frontend
```

#### 3. "Secret Manager authentication failed"

**Solution:**
- Verify your GCP service account key file exists
- Check that the key has correct permissions
- Ensure the Secret Manager API is enabled

#### 4. "HTX API connection failed"

**Solution:**
- Verify your HTX API keys are correct
- Check if IP restrictions are properly configured
- Ensure HTX account has trading permissions

#### 5. "Frontend won't start"

**Solution:**
```bash
cd frontend
npm install  # Reinstall dependencies
npm run dev  # Start manually
```

### Debug Mode

Enable detailed logging:

```bash
# Set debug mode in .env
DEBUG=true
LOG_LEVEL=DEBUG

# Run validation with verbose output
python validate_setup.py --verbose
```

### Log Files

Check these logs for issues:

- `activation_setup.log` - Setup process
- `validation_results.log` - Validation details
- `logs/backend.log` - Backend application
- `logs/frontend.log` - Frontend development server

---

## 🔄 Maintenance

### Updating Dependencies

```bash
# Backend
cd backend
pip install -r requirements.txt --upgrade

# Frontend
cd frontend
npm update
```

### Backing Up Configuration

Important files to backup:
- `.env` (environment configuration)
- `gcp-service-account.json` (GCP credentials)
- `data/app.db` (local database)

### Updating API Keys

1. **Update in Secret Manager:**
   ```bash
   gcloud secrets versions add htx-api-key --data-file=new_key.txt
   ```

2. **Or re-run activation:**
   ```bash
   python activate_project.py
   ```

---

## 📊 Using the Platform

### Uploading Trading Data

1. **Access the dashboard**: http://localhost:3000
2. **Go to File Upload** section
3. **Drag and drop** your CSV files (HTX exports)
4. **View analytics** in real-time

### Supported File Formats

- HTX trading history exports (CSV)
- Custom CSV with columns: symbol, price, quantity, datetime
- Excel files (.xlsx, .xls)

### API Integration

Connect your HTX account for real-time data:

1. **Configure API keys** (done during setup)
2. **Enable sync** in the dashboard
3. **Monitor** real-time updates

---

## 🆘 Getting Help

### Self-Help Resources

1. **Validation script**: `python validate_setup.py`
2. **API documentation**: http://localhost:8004/docs
3. **Log files**: Check `logs/` directory
4. **Health check**: http://localhost:8004/api/v1/health/status

### Advanced Configuration

For advanced users, see:
- `backend/app/core/config.py` - Configuration options
- `DEPLOYMENT.md` - Production deployment
- `DEVELOPMENT.md` - Development guidelines

### Re-running Setup

If something goes wrong, you can always re-run:

```bash
python activate_project.py
```

This will reconfigure everything safely.

---

## 🎉 Success!

Once setup is complete, you'll have:

- ✅ **Secure API key management** with Google Secret Manager
- ✅ **Real-time trading dashboard** with analytics
- ✅ **Automated data processing** for HTX files
- ✅ **ML-powered insights** and predictions
- ✅ **Professional-grade architecture** for personal use

**Start trading smarter with your personal HTX Analytics Platform!** 📈

---

*Last updated: $(date)*