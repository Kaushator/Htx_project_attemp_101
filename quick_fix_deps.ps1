# HTX Project - Quick Dependencies Fix (PowerShell)
# Fix for Windows/PowerShell environment

Write-Host "🔧 HTX Project - Quick Dependencies Fix (PowerShell)" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan

# Get project root
$PROJECT_ROOT = Get-Location
Write-Host "📂 Project root: $PROJECT_ROOT" -ForegroundColor Blue

# Check Python version
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.12+ and add it to PATH" -ForegroundColor Yellow
    exit 1
}

# Create/activate virtual environment
$VENV_DIR = ".venv_wsl2"
if (!(Test-Path $VENV_DIR)) {
    Write-Host "Creating virtual environment: $VENV_DIR" -ForegroundColor Yellow
    python -m venv $VENV_DIR
} else {
    Write-Host "Using existing virtual environment: $VENV_DIR" -ForegroundColor Blue
}

# Activate virtual environment
$activateScript = "$VENV_DIR\Scripts\Activate.ps1"
if (Test-Path $activateScript) {
    Write-Host "Activating virtual environment..." -ForegroundColor Blue
    & $activateScript
} else {
    Write-Host "❌ Virtual environment activation script not found" -ForegroundColor Red
    exit 1
}

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Blue
python -m pip install --upgrade pip

# Install core dependencies
Write-Host "Installing core dependencies..." -ForegroundColor Blue
if (Test-Path "backend\requirements.txt") {
    pip install -r backend\requirements.txt
} else {
    Write-Host "❌ backend\requirements.txt not found" -ForegroundColor Red
    exit 1
}

# Install development dependencies
if (Test-Path "backend\requirements-dev.txt") {
    Write-Host "Installing development dependencies..." -ForegroundColor Blue
    pip install -r backend\requirements-dev.txt
}

# Verify key imports
Write-Host "Verifying key imports..." -ForegroundColor Blue
$testScript = @"
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
"@

$testScript | python

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Dependencies installed and verified successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "To run the backend (choose one option):" -ForegroundColor Yellow
    Write-Host "   Option 1: cd backend && python run.py" -ForegroundColor White
    Write-Host "   Option 2: cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000" -ForegroundColor White
    Write-Host "   Option 3: python run_backend_simple.py" -ForegroundColor White
} else {
    Write-Host "❌ Some dependencies failed to install" -ForegroundColor Red
    exit 1
}