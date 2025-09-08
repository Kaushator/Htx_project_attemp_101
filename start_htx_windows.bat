@echo off
REM HTX Project - Windows PowerShell Launcher
REM Optimized for Windows with WSL2 integration

setlocal EnableDelayedExpansion

REM Configuration
set PROJECT_ROOT=%~dp0
set BACKEND_PORT=8004
set FRONTEND_PORT=3000
set WSL_DISTRO=Ubuntu

REM Colors (limited support in cmd)
set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "BLUE=[94m"
set "CYAN=[96m"
set "BOLD=[1m"
set "NC=[0m"

echo.
echo %CYAN%%BOLD%=====================================================================%NC%
echo %CYAN%%BOLD%                    HTX TRADING PLATFORM                             %NC%
echo %CYAN%%BOLD%                  Windows Development Launcher                       %NC%
echo %CYAN%%BOLD%=====================================================================%NC%
echo.

REM Check if WSL2 is available
echo %BLUE%[%time%] Checking WSL2 availability...%NC%
wsl --list --quiet >nul 2>&1
if !errorlevel! neq 0 (
    echo %RED%❌ WSL2 not found. Please install WSL2 and Ubuntu.%NC%
    echo %YELLOW%   Run: wsl --install -d Ubuntu%NC%
    pause
    exit /b 1
)

REM Check if Ubuntu is installed
wsl -d %WSL_DISTRO% echo "test" >nul 2>&1
if !errorlevel! neq 0 (
    echo %RED%❌ Ubuntu WSL2 distribution not found.%NC%
    echo %YELLOW%   Available distributions:%NC%
    wsl --list
    pause
    exit /b 1
)

echo %GREEN%✅ WSL2 Ubuntu found%NC%

REM Convert Windows path to WSL path
for /f "tokens=*" %%i in ('wsl wslpath "%PROJECT_ROOT%"') do set WSL_PROJECT_ROOT=%%i

echo %BLUE%[%time%] Project path: %WSL_PROJECT_ROOT%%NC%

REM Check if start script exists in WSL
wsl -d %WSL_DISTRO% test -f "%WSL_PROJECT_ROOT%/start_htx_dev.sh"
if !errorlevel! neq 0 (
    echo %RED%❌ Start script not found in WSL: %WSL_PROJECT_ROOT%/start_htx_dev.sh%NC%
    echo %YELLOW%   Please ensure the project is properly set up.%NC%
    pause
    exit /b 1
)

REM Make script executable
echo %BLUE%[%time%] Making start script executable...%NC%
wsl -d %WSL_DISTRO% chmod +x "%WSL_PROJECT_ROOT%/start_htx_dev.sh"

REM Parse command line arguments
set "WSL_ARGS="
set "MODE=full"

:parse_args
if "%~1"=="" goto start_services
if "%~1"=="--help" goto show_help
if "%~1"=="-h" goto show_help
if "%~1"=="backend" (
    set "MODE=backend"
    set "WSL_ARGS=!WSL_ARGS! backend"
    shift
    goto parse_args
)
if "%~1"=="frontend" (
    set "MODE=frontend"
    set "WSL_ARGS=!WSL_ARGS! frontend"
    shift
    goto parse_args
)
if "%~1"=="--skip-deps" (
    set "WSL_ARGS=!WSL_ARGS! --skip-deps"
    shift
    goto parse_args
)
if "%~1"=="--no-check" (
    set "WSL_ARGS=!WSL_ARGS! --no-check"
    shift
    goto parse_args
)

REM Unknown argument
echo %RED%❌ Unknown argument: %~1%NC%
goto show_help

:start_services
echo %BLUE%[%time%] Starting HTX Trading Platform (%MODE% mode)...%NC%
echo %YELLOW%⚠️  Press Ctrl+C in the WSL terminal to stop services%NC%
echo.

REM Start the services in WSL
wsl -d %WSL_DISTRO% bash -c "cd '%WSL_PROJECT_ROOT%' && ./start_htx_dev.sh %WSL_ARGS%"

echo.
echo %BLUE%[%time%] Services stopped.%NC%
pause
exit /b 0

:show_help
echo.
echo HTX Project Windows Development Launcher
echo.
echo Usage: %~nx0 [OPTIONS] [MODE]
echo.
echo Modes:
echo   full       Start both backend and frontend (default)
echo   backend    Start only backend
echo   frontend   Start only frontend
echo.
echo Options:
echo   --skip-deps    Skip dependency installation
echo   --no-check     Skip prerequisite checks
echo   --help         Show this help message
echo.
echo Examples:
echo   %~nx0                    # Start full environment
echo   %~nx0 backend            # Start only backend
echo   %~nx0 --skip-deps full   # Start full, skip deps
echo.
echo This launcher requires WSL2 with Ubuntu installed.
echo It will run the HTX Trading Platform in the WSL2 environment.
echo.
pause
exit /b 0