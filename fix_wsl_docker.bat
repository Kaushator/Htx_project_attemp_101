@echo off
REM HTX Project - WSL2 and Docker Fix Launcher
REM This script helps fix WSL2 and Docker issues from Windows

echo ========================================
echo HTX Project - WSL2 and Docker Fix
echo ========================================
echo.

REM Check if WSL is installed
wsl --list --verbose >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] WSL is not installed or not working properly
    echo Please install WSL2 first:
    echo https://docs.microsoft.com/en-us/windows/wsl/install
    pause
    exit /b 1
)

echo [INFO] WSL detected, checking distributions...
wsl --list --verbose

echo.
echo [INFO] Attempting to fix WSL2 and Docker setup...
echo This will run the fix script inside WSL2

REM Navigate to project directory and run fix script
cd /d "%~dp0"

REM Make the script executable and run it
wsl chmod +x ./fix_wsl_docker.sh
wsl ./fix_wsl_docker.sh

if %errorlevel% equ 0 (
    echo.
    echo [SUCCESS] Fix script completed successfully!
    echo.
    echo Next steps:
    echo 1. Make sure Docker Desktop is running
    echo 2. Enable WSL2 integration in Docker Desktop settings
    echo 3. Try running: wsl ./start_wsl2.sh
) else (
    echo.
    echo [ERROR] Fix script failed. Please check the output above.
    echo.
    echo Manual steps to try:
    echo 1. Open WSL2 terminal: wsl
    echo 2. Update packages: sudo apt update ^&^& sudo apt upgrade
    echo 3. Install basic tools: sudo apt install curl wget python3 python3-pip
    echo 4. Run fix script: ./fix_wsl_docker.sh
)

echo.
pause