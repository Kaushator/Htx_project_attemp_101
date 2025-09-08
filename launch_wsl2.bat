@echo off
REM Скрипт запуска проекта в WSL2 из Windows

echo 🚀 HTX Project - Запуск в WSL2
echo ==============================

REM Проверка наличия WSL
wsl --status >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ WSL не установлен. Установите WSL2, следуя инструкциям:
    echo https://docs.microsoft.com/en-us/windows/wsl/install
    exit /b 1
)

REM Проверка версии WSL
wsl --list --verbose | findstr "Ubuntu" | findstr "2"
if %ERRORLEVEL% NEQ 0 (
    echo ⚠️ Ubuntu на WSL2 не найден. Рекомендуется использовать WSL2.
    echo Выполните: wsl --set-version Ubuntu 2
    echo.
    echo ❓ Продолжить, используя имеющуюся версию WSL? (y/n)
    set /p continue=
    if /i "%continue%" NEQ "y" exit /b 1
)

REM Определение пути проекта
set PROJECT_PATH=%~dp0
set PROJECT_PATH=%PROJECT_PATH:~0,-1%

REM Копирование в WSL, если указан флаг --copy
if "%1"=="--copy" (
    echo 📂 Копирование проекта в WSL...
    wsl mkdir -p ~/htx_project
    wsl cp -r "%PROJECT_PATH%/*" ~/htx_project/
    echo ✅ Файлы скопированы в ~/htx_project/
)

REM Запуск скрипта в WSL
echo 🚀 Запуск проекта в WSL2...
wsl -d Ubuntu -e bash -c "cd /home/fake0mg/htx_project && ./start_wsl2.sh"

if %ERRORLEVEL% NEQ 0 (
    echo ❌ Ошибка запуска проекта в WSL2.
    exit /b 1
)

echo.
echo ✅ Проект запущен в WSL2.
echo 🌐 Доступ к сервисам:
echo    - Backend: http://localhost:8004
echo    - Frontend: http://localhost:3000
echo    - API Docs: http://localhost:8004/docs
echo.
echo 📝 Для дополнительной информации см. docs/wsl-migration.md
