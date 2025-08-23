# HTX Project - Development Run Script (PowerShell)

Write-Host "🚀 Starting HTX Project in development mode..." -ForegroundColor Green

# Check if virtual environment exists
if (-not (Test-Path ".venv")) {
    Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
}

# Activate virtual environment
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Yellow
& .venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "📥 Installing dependencies..." -ForegroundColor Yellow
pip install -r backend\requirements.txt

# Copy environment file if it doesn't exist
if (-not (Test-Path "backend\.env")) {
    Write-Host "⚙️  Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item "backend\env.example" "backend\.env"
    Write-Host "⚠️  Please update backend\.env with your API keys!" -ForegroundColor Red
}

# Create data directories
Write-Host "📁 Creating data directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path "data\raw", "data\processed", "data\samples" -Force | Out-Null

# Start the API
Write-Host "🌐 Starting FastAPI server..." -ForegroundColor Green
Set-Location backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
