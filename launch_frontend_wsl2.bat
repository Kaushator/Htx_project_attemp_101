@echo off
REM Запуск фронтенда в WSL2

echo Запуск фронтенда HTX в WSL2...
echo ===========================

REM Запуск фронтенда в WSL2
start powershell -NoExit -Command "wsl -d Ubuntu -e bash -c '/home/fake0mg/start_wsl2_frontend.sh'"

REM Ждем, пока сервер запустится
timeout /t 5 /nobreak > nul

echo.
echo Фронтенд запущен. Доступен по адресу:
echo   - http://localhost:3000
echo.
