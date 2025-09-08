@echo off
REM Запуск бэкенда в WSL2

echo Запуск бэкенда HTX в WSL2...
echo ==========================

REM Запуск бэкенда в WSL2
start powershell -NoExit -Command "wsl -d Ubuntu -e bash -c '/home/fake0mg/start_wsl2_backend.sh'"

REM Ждем, пока сервер запустится
timeout /t 5 /nobreak > nul

echo.
echo Бэкенд запущен. Доступен по адресу:
echo   - Windows: http://localhost:8005
echo   - WSL2:    http://172.28.245.98:8005
echo.
