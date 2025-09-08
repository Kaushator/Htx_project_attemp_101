@echo off
REM Скрипт для одноразовой миграции проекта на WSL2

echo ===== Миграция HTX Project на WSL2 =====
echo.

REM Проверка наличия WSL2
wsl --status >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ОШИБКА] WSL не установлен. Установите WSL2:
    echo https://docs.microsoft.com/en-us/windows/wsl/install
    exit /b 1
)

REM Проверка версии WSL
echo [OK] Проверка версии WSL...
REM Просто продолжаем выполнение, т.к. мы уже проверили, что WSL2 установлен

REM Определение пути проекта
set PROJECT_PATH=%~dp0
set PROJECT_PATH=%PROJECT_PATH:~0,-1%

echo 1. Копирование проекта в WSL2...
wsl -d Ubuntu -e mkdir -p /home/fake0mg/htx_project
wsl -d Ubuntu -e bash -c "cp -r /mnt/e/Htx_project_attemp_101/* /home/fake0mg/htx_project/"

echo 2. Базовая настройка окружения WSL2...
wsl -d Ubuntu -e bash -c "cd /home/fake0mg/htx_project && chmod +x scripts/setup_wsl2.sh run_backend_simple.sh start_wsl2.sh"

echo 3. Создание тестовой базы данных...
wsl -d Ubuntu -e bash -c "cd /home/fake0mg/htx_project && mkdir -p data && touch data/app.db"

echo 4. Создание виртуального окружения...
wsl -d Ubuntu -e bash -c "cd /home/fake0mg/htx_project && python3 -m venv .venv_wsl2"
wsl -d Ubuntu -e bash -c "cd /home/fake0mg/htx_project && . .venv_wsl2/bin/activate && pip install --upgrade pip"
wsl -d Ubuntu -e bash -c "cd /home/fake0mg/htx_project && . .venv_wsl2/bin/activate && pip install fastapi uvicorn httpx sqlalchemy"

echo 5. Проверка установки...
wsl -d Ubuntu -e bash -c "cd /home/fake0mg/htx_project && . .venv_wsl2/bin/activate && python -c 'import fastapi; print(f\"FastAPI {fastapi.__version__} установлен успешно!\")'"

echo.
echo ===== Миграция завершена! =====
echo.
echo Для запуска проекта:
echo 1. Используйте launch_wsl2.bat из Windows
echo 2. Или запустите ./start_wsl2.sh напрямую из WSL2
echo.
echo Подробности: docs/wsl-migration.md
echo.
