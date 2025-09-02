#!/bin/bash
# Скрипт для запуска бэкенда в WSL2

cd /home/fake0mg/htx_project/backend
source ../.venv_wsl2/bin/activate

# Запуск бэкенда
python -m uvicorn app.main:app --host 0.0.0.0 --port 8005
