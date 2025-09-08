@echo off
REM Скрипт для активации ML-функций в WSL2

echo 🚀 HTX Project - Активация ML-функций в WSL2
echo ==========================================

REM Проверка WSL
echo Проверка установки WSL...
wsl -l -v >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [31mОшибка: WSL не установлен или не настроен[0m
    echo Установите WSL, следуя инструкциям: https://docs.microsoft.com/en-us/windows/wsl/install
    exit /b 1
)

REM Проверка установки Ubuntu
echo Проверка установки Ubuntu...
wsl -l -v | findstr "Ubuntu" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [31mОшибка: Ubuntu не установлен в WSL[0m
    echo Установите Ubuntu из Microsoft Store или используя команду:
    echo wsl --install -d Ubuntu
    exit /b 1
)

REM Проверка версии WSL
echo Проверка версии WSL...
wsl -l -v | findstr "Ubuntu" | findstr "2" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [31mОшибка: Требуется WSL2, но обнаружена WSL1[0m
    echo Выполните миграцию на WSL2, следуя инструкциям в docs/wsl-migration.md
    exit /b 1
)

echo [32m✓ WSL2 активен[0m

REM Запуск скрипта активации в WSL
echo Запуск скрипта активации ML в WSL2...
wsl -d Ubuntu -e bash -c "cd /home/fake0mg/htx_project && chmod +x activate_ml.sh && ./activate_ml.sh"

REM Проверка результата
if %ERRORLEVEL% NEQ 0 (
    echo [31mОшибка при выполнении скрипта активации в WSL2[0m
    exit /b 1
) else (
    echo [32mML-компоненты успешно активированы![0m
    echo [33mТеперь вы можете запустить проект с активированными ML-функциями:[0m
    echo [36mlaunсh_backend_wsl2.bat[0m
)

echo.
echo [32mДля получения подробной информации см. docs/ml-activation-plan.md[0m
echo.
