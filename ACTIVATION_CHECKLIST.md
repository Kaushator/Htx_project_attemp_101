# HTX Project Personal Activation Checklist

## 📋 Pre-Setup Checklist

### System Requirements
- [ ] **Windows 10/11** with WSL2 installed
- [ ] **Python 3.12+** available in WSL2
- [ ] **Node.js 18+** installed
- [ ] **Git** available
- [ ] **Docker** installed (optional)

### Google Cloud Platform
- [ ] **GCP Account** created
- [ ] **GCP Project** created with billing enabled
- [ ] **Required APIs** enabled:
  - [ ] Secret Manager API
  - [ ] Cloud Storage API  
  - [ ] Pub/Sub API
  - [ ] Vertex AI API (optional)
- [ ] **Service Account** created with roles:
  - [ ] Secret Manager Admin
  - [ ] Storage Admin
  - [ ] Pub/Sub Admin
- [ ] **Service Account JSON key** downloaded

### API Keys Ready
- [ ] **HTX API Key** and **Secret** obtained
- [ ] **HTX API** permissions configured (read-only recommended)
- [ ] **OpenAI API Key** obtained (optional but recommended)
- [ ] **3Commas API Keys** obtained (optional)

---

## 🚀 Activation Process

### Step 1: Clone/Download Project
- [ ] Project files downloaded to local machine
- [ ] Navigate to project directory in terminal

### Step 2: Run Activation Script
```bash
python activate_project.py
```

**Complete these during script execution:**
- [ ] Confirm prerequisites check passes
- [ ] Enter GCP Project ID
- [ ] Provide path to GCP service account JSON file
- [ ] Enter HTX API Key securely
- [ ] Enter HTX API Secret securely
- [ ] Enter HTX Sub-account UID (if applicable)
- [ ] Enter OpenAI API Key (optional)
- [ ] Enter 3Commas API credentials (optional)
- [ ] Confirm Secret Manager setup completion
- [ ] Verify dependency installation
- [ ] Review generated configuration

### Step 3: Validation
- [ ] Activation script completes successfully
- [ ] `.env` file generated
- [ ] `gcp-service-account.json` copied to project root
- [ ] Startup scripts created and executable

---

## ✅ Post-Activation Verification

### Configuration Files
- [ ] `.env` file exists and contains configuration
- [ ] `gcp-service-account.json` exists
- [ ] Log files created in `logs/` directory

### Run Validation
```bash
python validate_setup.py
```

**Verify all tests pass:**
- [ ] ✅ Environment configuration
- [ ] ✅ Dependencies installed
- [ ] ✅ Database connectivity
- [ ] ✅ GCP integration
- [ ] ✅ Secret Manager access
- [ ] ✅ File processing setup

### Test API Endpoints
```bash
python validate_setup.py --verbose
```

**Confirm endpoint availability:**
- [ ] ✅ Health check endpoints
- [ ] ✅ Core trading endpoints
- [ ] ✅ File upload endpoints
- [ ] ✅ HTX integration endpoints
- [ ] ✅ ML analytics endpoints (if enabled)
- [ ] ✅ GCP endpoints (if configured)

---

## 🌐 Launch and Access

### Start Services
**Windows PowerShell:**
```powershell
.\quick_start.ps1
```

**WSL2/Linux:**
```bash
./start_htx_dev.sh
```

### Verify Access
- [ ] **Backend API**: http://localhost:8004 responds
- [ ] **API Docs**: http://localhost:8004/docs loads
- [ ] **Frontend Dashboard**: http://localhost:3000 loads
- [ ] **Health Check**: http://localhost:8004/api/v1/health/ping returns OK

### Initial Setup in Dashboard
- [ ] Access dashboard at http://localhost:3000
- [ ] Navigate through all sections
- [ ] Test file upload functionality
- [ ] Verify HTX data sync (if configured)
- [ ] Check analytics and insights

---

## 🔒 Security Verification

### Secret Manager
- [ ] All API keys stored in Google Secret Manager
- [ ] Local `.env` file uses secure values
- [ ] No plaintext secrets in configuration files

### API Key Testing
- [ ] HTX API connection works
- [ ] OpenAI API responds (if configured)
- [ ] 3Commas integration works (if configured)

### Access Controls
- [ ] HTX API keys have minimal required permissions
- [ ] GCP service account has limited roles
- [ ] Local firewall allows only necessary ports

---

## 📊 Feature Testing

### Core Features
- [ ] **File Upload**: Can upload CSV/Excel files
- [ ] **Data Processing**: Files are parsed correctly
- [ ] **P&L Calculation**: Profit/loss metrics display
- [ ] **Cashflow Analysis**: Cash flow tracking works
- [ ] **Trading Insights**: Quick insights generate

### HTX Integration (if configured)
- [ ] **Account Balance**: Real balance displays
- [ ] **Trading History**: Live trades sync
- [ ] **Market Data**: Current prices update
- [ ] **Order Management**: Orders can be viewed

### ML Features (if enabled)
- [ ] **Risk Analysis**: Risk metrics calculate
- [ ] **Anomaly Detection**: Pattern analysis works
- [ ] **Prediction Models**: Forecasts generate
- [ ] **Trading Patterns**: Pattern recognition active

### GCP Features (if configured)
- [ ] **Cloud Storage**: File uploads to GCS
- [ ] **Pub/Sub**: Event messaging works
- [ ] **BigQuery**: Data export functions
- [ ] **Vertex AI**: ML model deployment

---

## 🛠️ Troubleshooting Completed

### Common Issues Resolved
- [ ] **Port Conflicts**: No conflicting services on 8004/3000
- [ ] **Permission Issues**: All scripts executable
- [ ] **WSL2 Integration**: Windows-WSL communication works
- [ ] **Database Setup**: SQLite database initializes
- [ ] **Environment Variables**: All required vars set

### Performance Optimization
- [ ] **Memory Usage**: Services running within limits
- [ ] **CPU Usage**: No excessive resource consumption
- [ ] **Response Times**: API responds quickly
- [ ] **File Processing**: Upload/processing performs well

---

## 📝 Documentation Review

### Setup Documentation
- [ ] Read `PERSONAL_SETUP_GUIDE.md`
- [ ] Understand troubleshooting section
- [ ] Bookmark important URLs
- [ ] Save backup of configuration

### Usage Guidelines
- [ ] Know how to start/stop services
- [ ] Understand log file locations
- [ ] Know how to update API keys
- [ ] Understand backup procedures

---

## 🎉 Activation Complete!

### Final Checklist
- [ ] ✅ **All prerequisites** met and verified
- [ ] ✅ **Activation script** completed successfully
- [ ] ✅ **Validation tests** all pass
- [ ] ✅ **Services start** without errors
- [ ] ✅ **Dashboard accessible** and functional
- [ ] ✅ **API endpoints** responding correctly
- [ ] ✅ **Security measures** implemented
- [ ] ✅ **Features tested** and working
- [ ] ✅ **Documentation** reviewed

### Next Steps
- [ ] **Upload trading data** to test analytics
- [ ] **Configure preferences** in dashboard
- [ ] **Set up automated sync** (if desired)
- [ ] **Create regular backups** of important data
- [ ] **Monitor performance** and logs

### Success Indicators
- ✅ Personal HTX Trading Platform fully operational
- ✅ Secure API key management with Google Secret Manager
- ✅ Real-time trading analytics and insights available
- ✅ Professional-grade setup for personal use

**🎊 Congratulations! Your HTX Trading Platform is ready for use!**

---

## 📞 Support Resources

### Self-Service
- **Validation**: `python validate_setup.py`
- **Logs**: Check `logs/` directory
- **Health**: http://localhost:8004/api/v1/health/status
- **Restart**: `./stop_htx_services.sh && ./start_htx_dev.sh`

### Re-activation
If issues persist, run activation again:
```bash
python activate_project.py
```

*Activation completed on: $(date)*