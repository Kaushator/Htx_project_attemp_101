@echo off
REM Обновление всех зависимостей проекта в WSL2

echo Обновление зависимостей HTX Project в WSL2...
echo ======================================

REM Запуск скрипта обновления зависимостей в WSL2
wsl -d Ubuntu -e bash -c "/home/fake0mg/update_deps_wsl2.sh"

echo.
echo Обновление завершено!
echo.
