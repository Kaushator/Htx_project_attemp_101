@echo off
REM Простой скрипт для запуска бэкенда на WSL2

echo Запуск бэкенда HTX в WSL2...
echo ==========================

REM Проверка наличия WSL
wsl --status >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ОШИБКА] WSL не установлен
    exit /b 1
)

REM Запуск бэкенда в WSL2
echo Запуск бэкенда...
wsl -d Ubuntu -e bash -c "cd /home/fake0mg/htx_project/backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8004"

echo.
echo Бэкенд запущен. Доступен по адресу: http://localhost:8004
echo Для остановки нажмите Ctrl+C
