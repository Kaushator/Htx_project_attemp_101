#!/usr/bin/env bash
# filepath: activate_ml.sh

set -eo pipefail

echo "🚀 HTX Project - Активация ML-функций в WSL2"
echo "=========================================="

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Переходим в корень проекта
cd "$(dirname "$0")"
PROJECT_ROOT=$(pwd)

# Проверка, что мы в WSL2
if [[ "$(uname -r)" != *"microsoft"* ]]; then
    echo -e "${RED}Этот скрипт должен выполняться только в среде WSL2${NC}"
    echo -e "${YELLOW}Используйте команду: wsl -d Ubuntu -e bash -c \"cd ~/htx_project && ./activate_ml.sh\"${NC}"
    exit 1
fi

# Проверка версии WSL
echo -e "${BLUE}Проверка версии WSL...${NC}"
WSL_VERSION=$(wsl.exe -l -v | grep -i ubuntu | awk '{print $3}')
if [[ "$WSL_VERSION" != "2" ]]; then
    echo -e "${RED}Требуется WSL2, обнаружена версия: $WSL_VERSION${NC}"
    echo -e "${YELLOW}Выполните миграцию на WSL2, следуя инструкциям в docs/wsl-migration.md${NC}"
    exit 1
fi

echo -e "${GREEN}✓ WSL2 активен${NC}"

# Активация виртуального окружения
echo -e "${BLUE}Активация виртуального окружения...${NC}"
source .venv_wsl2/bin/activate

# Установка ML-зависимостей
echo -e "${BLUE}Установка ML-зависимостей...${NC}"
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install transformers scikit-learn pandas numpy matplotlib seaborn
pip install "uvicorn[standard]" fastapi sqlalchemy

# Проверка GPU (если есть)
echo -e "${BLUE}Проверка доступности GPU...${NC}"
if command -v nvidia-smi &> /dev/null; then
    echo -e "${GREEN}✓ NVIDIA GPU обнаружена${NC}"
    nvidia-smi
    
    # Обновляем конфигурацию для использования CUDA
    echo -e "${BLUE}Настройка конфигурации для GPU...${NC}"
    GPU_CONFIG="ML_DEVICE=\"cuda\"\nLOAD_IN_4BIT=True\nTORCH_DTYPE=\"float16\""
    
    # Проверка, есть ли уже настройки GPU в .env файле
    if [ -f "backend/.env" ]; then
        if grep -q "ML_DEVICE" "backend/.env"; then
            echo -e "${YELLOW}Конфигурация GPU уже существует в .env${NC}"
        else
            echo -e "\n# ML Configuration\n$GPU_CONFIG" >> backend/.env
            echo -e "${GREEN}✓ Конфигурация GPU добавлена в .env${NC}"
        fi
    else
        echo -e "# ML Configuration\n$GPU_CONFIG" > backend/.env
        echo -e "${GREEN}✓ Создан .env файл с конфигурацией GPU${NC}"
    fi
else
    echo -e "${YELLOW}GPU не обнаружена, используем CPU для ML-функций${NC}"
    
    # Обновляем конфигурацию для использования CPU
    echo -e "${BLUE}Настройка конфигурации для CPU...${NC}"
    CPU_CONFIG="ML_DEVICE=\"cpu\"\nLOAD_IN_4BIT=False\nTORCH_DTYPE=\"float32\""
    
    # Проверка, есть ли уже настройки CPU в .env файле
    if [ -f "backend/.env" ]; then
        if grep -q "ML_DEVICE" "backend/.env"; then
            echo -e "${YELLOW}Конфигурация ML уже существует в .env${NC}"
        else
            echo -e "\n# ML Configuration\n$CPU_CONFIG" >> backend/.env
            echo -e "${GREEN}✓ Конфигурация CPU добавлена в .env${NC}"
        fi
    else
        echo -e "# ML Configuration\n$CPU_CONFIG" > backend/.env
        echo -e "${GREEN}✓ Создан .env файл с конфигурацией CPU${NC}"
    fi
fi

# Создание директории для моделей (кэш для трансформеров)
echo -e "${BLUE}Создание директории для кэша моделей...${NC}"
mkdir -p "$PROJECT_ROOT/.cache/models"
export TRANSFORMERS_CACHE="$PROJECT_ROOT/.cache/models"
echo "export TRANSFORMERS_CACHE=\"$PROJECT_ROOT/.cache/models\"" >> .venv_wsl2/bin/activate

# Запуск бэкенда для тестирования ML-компонентов
echo -e "${GREEN}ML-компоненты активированы!${NC}"
echo -e "${BLUE}Теперь вы можете запустить проект с ML-функциями:${NC}"
echo -e "${YELLOW}./start_wsl2.sh${NC}"
echo -e "${BLUE}Для тестирования ML-эндпоинтов:${NC}"
echo -e "${YELLOW}./scripts/test_ml_endpoints.sh${NC}"

echo -e "\n${GREEN}Для получения подробной информации см. docs/ml-activation-plan.md${NC}"
