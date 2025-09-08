@echo off
REM HTX Trading Platform - Docker Management Script for Windows

setlocal enabledelayedexpansion

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running. Please start Docker Desktop.
    exit /b 1
)

REM Check if docker-compose is available
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] docker-compose is not available
    exit /b 1
)

if \"%1\"==\"\" goto usage
if \"%1\"==\"build\" goto build
if \"%1\"==\"start\" goto start
if \"%1\"==\"stop\" goto stop
if \"%1\"==\"restart\" goto restart
if \"%1\"==\"status\" goto status
if \"%1\"==\"logs\" goto logs
if \"%1\"==\"cleanup\" goto cleanup
if \"%1\"==\"full-setup\" goto full_setup
goto usage

:build
echo [INFO] Building Docker containers...
docker-compose build --no-cache
if errorlevel 1 (
    echo [ERROR] Failed to build containers
    exit /b 1
)
echo [INFO] ✅ Containers built successfully
goto end

:start
echo [INFO] Starting HTX Trading Platform...

REM Create necessary directories
if not exist \"data\" mkdir data
if not exist \"logs\" mkdir logs

REM Copy environment file if it doesn't exist
if not exist \"backend\\.env\" (
    echo [WARNING] No .env file found, copying from .env.docker template
    copy \"backend\\.env.docker\" \"backend\\.env\"
    echo [WARNING] ⚠️  Please update backend\\.env with your API keys before production use
)

docker-compose up -d
if errorlevel 1 (
    echo [ERROR] Failed to start services
    exit /b 1
)
echo [INFO] ✅ Services started successfully
goto status

:stop
echo [INFO] Stopping HTX Trading Platform...
docker-compose down
if errorlevel 1 (
    echo [ERROR] Failed to stop services
    exit /b 1
)
echo [INFO] ✅ Services stopped successfully
goto end

:restart
echo [INFO] Restarting HTX Trading Platform...
docker-compose down
docker-compose up -d
if errorlevel 1 (
    echo [ERROR] Failed to restart services
    exit /b 1
)
echo [INFO] ✅ Services restarted successfully
goto status

:status
echo === Service Status ===
docker-compose ps
echo.
echo === Service URLs ===
echo 🔗 API Documentation: http://localhost:8000/docs
echo 💚 Health Check: http://localhost:8000/api/v1/health
echo 🌐 Frontend: http://localhost:3000
echo 📊 Redis: redis://localhost:6379
goto end

:logs
echo [INFO] Showing service logs...
if \"%2\"==\"\" (
    docker-compose logs -f
) else (
    docker-compose logs -f %2
)
goto end

:cleanup
echo [WARNING] This will remove all containers, networks, and volumes
set /p confirm=\"Are you sure? (y/N): \"
if /i \"!confirm!\"==\"y\" (
    echo [INFO] Cleaning up Docker resources...
    docker-compose down -v --remove-orphans
    docker system prune -f
    echo [INFO] ✅ Cleanup completed
) else (
    echo [INFO] Cleanup cancelled
)
goto end

:full_setup
echo [INFO] Starting full setup...
call :build
if errorlevel 1 goto end
call :start
goto end

:usage
echo HTX Trading Platform - Docker Management Script
echo.
echo Usage: %0 {command} [options]
echo.
echo Commands:
echo   build          Build all Docker containers
echo   start          Start all services
echo   stop           Stop all services
echo   restart        Restart all services
echo   status         Show service status and URLs
echo   logs [svc]     Show logs for all services or specific service
echo   cleanup        Remove all containers and volumes
echo   full-setup     Build and start everything
echo.
echo Examples:
echo   %0 full-setup     # Complete setup and start
echo   %0 logs api       # Show API logs
echo   %0 status         # Show service status
echo.
goto end

:end
endlocal