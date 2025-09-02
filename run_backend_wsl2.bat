@echo off
REM Скрипт для запуска только бэкенда через WSL2

echo 🚀 HTX Project - Запуск бэкенда в WSL2
echo =======================================

REM Проверка наличия WSL
wsl --status >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ WSL не установлен. Установите WSL2, следуя инструкциям:
    echo https://docs.microsoft.com/en-us/windows/wsl/install
    exit /b 1
)

REM Определение пути проекта
set PROJECT_PATH=%~dp0
set PROJECT_PATH=%PROJECT_PATH:~0,-1%

REM Запуск скрипта в WSL
echo 🚀 Запуск бэкенда в WSL2...
wsl -d Ubuntu -e chmod +x "%PROJECT_PATH%/run_backend_simple.sh"
wsl -d Ubuntu -e "%PROJECT_PATH%/run_backend_simple.sh"
