#!/bin/bash
# Скрипт для обновления всех зависимостей проекта в WSL2

echo "===== Обновление зависимостей HTX Project в WSL2 ====="
echo ""

# Путь к проекту
PROJECT_PATH="/home/fake0mg/htx_project"

# Обновление зависимостей бэкенда
echo "📦 Обновление зависимостей бэкенда..."
cd "$PROJECT_PATH"
source .venv_wsl2/bin/activate

# Проверка наличия requirements.txt
if [ -f "requirements.txt" ]; then
  pip install -r requirements.txt --upgrade
else
  echo "❌ Файл requirements.txt не найден в корне проекта"
  # Проверяем в папке backend
  if [ -f "backend/requirements.txt" ]; then
    echo "📄 Найден backend/requirements.txt, используем его..."
    pip install -r backend/requirements.txt --upgrade
  fi
fi

# Установка дополнительных пакетов для ML и аналитики
echo "📊 Установка пакетов для ML и аналитики..."
pip install scikit-learn pandas numpy matplotlib seaborn --upgrade

# Обновление зависимостей фронтенда
echo ""
echo "🖥️ Обновление зависимостей фронтенда..."
cd "$PROJECT_PATH/frontend"
npm install
npm update

echo ""
echo "✅ Все зависимости успешно обновлены!"
echo ""
echo "🔎 Информация о версиях:"
echo "Python: $(python --version)"
echo "Node: $(node --version)"
echo "NPM: $(npm --version)"
