# HTX Project - PowerShell Quick Start Script
# Optimized for Windows with WSL2

param(
    [string]$Mode = "full",
    [switch]$SkipDeps,
    [switch]$NoCheck,
    [switch]$Help
)

# Configuration
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackendPort = 8004
$FrontendPort = 3000
$WSLDistro = "Ubuntu"

# Colors for output
$Colors = @{
    Red    = "`e[91m"
    Green  = "`e[92m"
    Yellow = "`e[93m"
    Blue   = "`e[94m"
    Cyan   = "`e[96m"
    Bold   = "`e[1m"
    Reset  = "`e[0m"
}

function Write-ColoredOutput {
    param(
        [string]$Message,
        [string]$Color = "Reset"
    )
    Write-Host "$($Colors[$Color])$Message$($Colors.Reset)"
}

function Write-Header {
    Write-Host ""
    Write-ColoredOutput "=====================================================================" "Cyan"
    Write-ColoredOutput "                    HTX TRADING PLATFORM                             " "Cyan"
    Write-ColoredOutput "                  PowerShell Quick Start                            " "Cyan"
    Write-ColoredOutput "=====================================================================" "Cyan"
    Write-Host ""
}

function Write-Status {
    param([string]$Message)
    Write-ColoredOutput "[$(Get-Date -Format 'HH:mm:ss')] $Message" "Blue"
}

function Write-Success {
    param([string]$Message)
    Write-ColoredOutput "✅ $Message" "Green"
}

function Write-Warning {
    param([string]$Message)
    Write-ColoredOutput "⚠️  $Message" "Yellow"
}

function Write-Error {
    param([string]$Message)
    Write-ColoredOutput "❌ $Message" "Red"
}

function Show-Help {
    Write-Host "HTX Project PowerShell Quick Start"
    Write-Host ""
    Write-Host "Usage: .\quick_start.ps1 [OPTIONS] [MODE]"
    Write-Host ""
    Write-Host "Modes:"
    Write-Host "  full       Start both backend and frontend (default)"
    Write-Host "  backend    Start only backend"
    Write-Host "  frontend   Start only frontend"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -SkipDeps     Skip dependency installation"
    Write-Host "  -NoCheck      Skip prerequisite checks"
    Write-Host "  -Help         Show this help message"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\quick_start.ps1                    # Start full environment"
    Write-Host "  .\quick_start.ps1 backend            # Start only backend"
    Write-Host "  .\quick_start.ps1 -SkipDeps full     # Start full, skip deps"
    Write-Host ""
    Write-Host "This script requires WSL2 with Ubuntu installed."
    Write-Host "It will run the HTX Trading Platform in the WSL2 environment."
}

function Test-WSL2 {
    Write-Status "Checking WSL2 availability..."
    
    try {
        $wslList = wsl --list --quiet 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-Error "WSL2 not found. Please install WSL2 and Ubuntu."
            Write-Warning "Run: wsl --install -d Ubuntu"
            return $false
        }
        
        # Check if Ubuntu is installed
        $testResult = wsl -d $WSLDistro echo "test" 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Ubuntu WSL2 distribution not found."
            Write-Warning "Available distributions:"
            wsl --list
            return $false
        }
        
        Write-Success "WSL2 Ubuntu found"
        return $true
    }
    catch {
        Write-Error "Error checking WSL2: $_"
        return $false
    }
}

function Get-WSLPath {
    param([string]$WindowsPath)
    
    try {
        $wslPath = wsl wslpath "$WindowsPath" 2>$null
        if ($LASTEXITCODE -eq 0) {
            return $wslPath.Trim()
        }
    }
    catch {
        Write-Warning "Could not convert Windows path to WSL path"
    }
    
    # Fallback: manual conversion
    $wslPath = $WindowsPath -replace '^([A-Z]):', '/mnt/$1'.ToLower()
    $wslPath = $wslPath -replace '\\', '/'
    return $wslPath
}

function Test-StartScript {
    param([string]$WSLProjectRoot)
    
    Write-Status "Checking start script in WSL..."
    
    $scriptPath = "$WSLProjectRoot/start_htx_dev.sh"
    $testResult = wsl -d $WSLDistro test -f "$scriptPath" 2>$null
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Start script not found in WSL: $scriptPath"
        Write-Warning "Please ensure the project is properly set up."
        return $false
    }
    
    # Make script executable
    Write-Status "Making start script executable..."
    wsl -d $WSLDistro chmod +x "$scriptPath" 2>$null
    
    Write-Success "Start script is ready"
    return $true
}

function Start-Services {
    param(
        [string]$WSLProjectRoot,
        [string]$StartMode,
        [bool]$SkipDependencies,
        [bool]$SkipChecks
    )
    
    Write-Status "Starting HTX Trading Platform ($StartMode mode)..."
    Write-Warning "Press Ctrl+C in the WSL terminal to stop services"
    Write-Host ""
    
    # Build WSL arguments
    $wslArgs = @()
    
    if ($SkipDependencies) {
        $wslArgs += "--skip-deps"
    }
    
    if ($SkipChecks) {
        $wslArgs += "--no-check"
    }
    
    $wslArgs += $StartMode
    
    $argsString = $wslArgs -join " "
    
    try {
        # Start services in WSL
        wsl -d $WSLDistro bash -c "cd '$WSLProjectRoot' && ./start_htx_dev.sh $argsString"
        
        Write-Host ""
        Write-Status "Services stopped."
    }
    catch {
        Write-Error "Error starting services: $_"
    }
}

function Test-PortAvailability {
    param([int]$Port)
    
    try {
        $connection = Test-NetConnection -ComputerName localhost -Port $Port -InformationLevel Quiet -WarningAction SilentlyContinue
        return -not $connection
    }
    catch {
        return $true  # Assume available if test fails
    }
}

function Show-PortStatus {
    Write-Status "Checking port availability..."
    
    if (-not (Test-PortAvailability -Port $BackendPort)) {
        Write-Warning "Port $BackendPort is already in use"
        $response = Read-Host "Would you like to continue anyway? (y/N)"
        if ($response -notmatch '^[Yy]$') {
            return $false
        }
    } else {
        Write-Success "Port $BackendPort is available"
    }
    
    if (-not (Test-PortAvailability -Port $FrontendPort)) {
        Write-Warning "Port $FrontendPort is already in use"
    } else {
        Write-Success "Port $FrontendPort is available"
    }
    
    return $true
}

function Main {
    if ($Help) {
        Show-Help
        return
    }
    
    Write-Header
    
    # Validate mode
    if ($Mode -notin @("full", "backend", "frontend")) {
        Write-Error "Invalid mode: $Mode"
        Show-Help
        return
    }
    
    # Check WSL2
    if (-not (Test-WSL2)) {
        return
    }
    
    # Convert project path to WSL
    $wslProjectRoot = Get-WSLPath -WindowsPath $ProjectRoot
    Write-Status "Project path: $wslProjectRoot"
    
    # Check start script
    if (-not (Test-StartScript -WSLProjectRoot $wslProjectRoot)) {
        return
    }
    
    # Check ports (if not skipping checks)
    if (-not $NoCheck) {
        if (-not (Show-PortStatus)) {
            return
        }
    }
    
    # Start services
    Start-Services -WSLProjectRoot $wslProjectRoot -StartMode $Mode -SkipDependencies $SkipDeps -SkipChecks $NoCheck
}

# Run main function
Main