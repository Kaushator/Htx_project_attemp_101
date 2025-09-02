#!/bin/bash
# Скрипт для запуска фронтенда в WSL2

cd /home/fake0mg/htx_project/frontend

# Проверка наличия необходимых зависимостей
echo "Проверка зависимостей..."
MISSING_DEPS=0

# Список критических зависимостей для проверки
DEPS=("react" "react-dom" "react-router-dom" "axios" "@mui/material" "react-dropzone")

for dep in "${DEPS[@]}"; do
  if ! npm list $dep >/dev/null 2>&1; then
    echo "✖ $dep не установлен. Устанавливаю..."
    npm install $dep --no-save
    MISSING_DEPS=1
  else
    echo "✓ $dep установлен"
  fi
done

# Если были отсутствующие зависимости, запускаем полную установку
if [ $MISSING_DEPS -eq 1 ]; then
  echo "Запуск полной установки зависимостей..."
  npm install
fi

# Запуск фронтенда
echo "Запуск фронтенда..."
npm run dev
