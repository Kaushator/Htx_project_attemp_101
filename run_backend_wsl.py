import os
import sys
import subprocess
import logging
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"logs/wsl2_backend_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("WSL2_Backend_Runner")

def ensure_directory_exists(dir_path):
    """Создает директорию, если она не существует"""
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        logger.info(f"Создана директория: {dir_path}")

def run_backend():
    """Запускает бэкенд в WSL2"""
    try:
        logger.info("Запуск бэкенда в WSL2...")
        
        # Создаем директорию для логов
        ensure_directory_exists("logs")
        
        # Переходим в директорию бэкенда
        os.chdir("backend")
        
        # Запускаем бэкенд
        cmd = ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8004", "--reload"]
        logger.info(f"Выполнение команды: {' '.join(cmd)}")
        
        # Запуск с перенаправлением вывода
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Вывод лога в реальном времени
        if process.stdout:
            for line in process.stdout:
                sys.stdout.write(line)
                logger.info(line.strip())
        
        process.wait()
        return process.returncode
    
    except Exception as e:
        logger.error(f"Ошибка при запуске бэкенда: {e}")
        return 1

if __name__ == "__main__":
    logger.info("===== ЗАПУСК HTX BACKEND В WSL2 =====")
    sys.exit(run_backend())
