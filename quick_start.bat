@echo off
echo ========================================
echo HTX PROJECT - БЫСТРЫЙ ЗАПУСК
echo ========================================

echo Останавливаем старые процессы...
wsl -d Ubuntu -- bash -c "pkill -f uvicorn; pkill -f node" 2>nul
timeout /t 2 /nobreak >nul

echo Запускаем Backend в WSL (порт 8004)...
start "HTX-Backend" cmd /k "wsl -d Ubuntu -- bash -c \"cd /mnt/e/Htx_project_attemp_101/backend && source ../.venv_wsl/bin/activate && python -m uvicorn app.main:app --host 0.0.0.0 --port 8004 --reload\""

echo Ждем 8 секунд...
timeout /t 8 /nobreak >nul

echo Запускаем Frontend в WSL (порт 3000)...
start "HTX-Frontend" cmd /k "wsl -d Ubuntu -- bash -c \"cd /mnt/e/Htx_project_attemp_101/frontend && npm run dev -- --host 0.0.0.0 --port 3000\""

echo ========================================
echo Backend: http://localhost:8004
echo Frontend: http://localhost:3000
echo Health Check: http://localhost:8004/api/v1/health
echo ========================================

echo Открываем браузер...
timeout /t 3 /nobreak >nul
start http://localhost:3000

pause
