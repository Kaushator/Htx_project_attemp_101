#!/usr/bin/env python
"""
Скрипт для тестирования производительности ML-компонентов в WSL2
Измеряет время выполнения основных ML-операций для бенчмаркинга
"""

import requests
import time
import json
import sys
import os
import logging
import argparse
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"logs/ml_benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ML_Benchmark")

# Конфигурация
BASE_URL = "http://localhost:8004/api/v1"
DEFAULT_TESTS = ["risk_metrics", "market_sentiment", "experiment_plan", "similarity_search"]
ITERATIONS = 3

def ensure_directory_exists(dir_path):
    """Создает директорию, если она не существует"""
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        logger.info(f"Создана директория: {dir_path}")

def check_backend_health():
    """Проверяет доступность бэкенда"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200 and response.json().get("status") == "healthy":
            return True
        return False
    except Exception as e:
        logger.error(f"Ошибка при проверке доступности бэкенда: {e}")
        return False

def run_risk_metrics_test():
    """Тестирование эндпоинта метрик риска"""
    url = f"{BASE_URL}/ml/risk-metrics"
    params = {"symbol": "BTC", "days_lookback": 30}
    
    start_time = time.time()
    response = requests.get(url, params=params)
    end_time = time.time()
    
    if response.status_code != 200:
        logger.error(f"Ошибка при тестировании метрик риска: {response.status_code}")
        logger.error(response.text)
        return None
    
    return end_time - start_time

def run_market_sentiment_test():
    """Тестирование эндпоинта анализа рыночных настроений"""
    url = f"{BASE_URL}/ml/analysis/market-sentiment"
    data = {"symbol": "BTC", "period": "daily"}
    
    start_time = time.time()
    response = requests.post(url, json=data)
    end_time = time.time()
    
    if response.status_code != 200:
        logger.error(f"Ошибка при тестировании анализа настроений: {response.status_code}")
        logger.error(response.text)
        return None
    
    return end_time - start_time

def run_experiment_plan_test():
    """Тестирование эндпоинта планирования экспериментов"""
    url = f"{BASE_URL}/ml/plan"
    data = {
        "experiment_description": "Анализ волатильности Solana",
        "available_data": {"symbols": ["SOL"], "timeframe": "1h", "period": "30d"},
        "constraints": {"execution_time": "fast"}
    }
    
    start_time = time.time()
    response = requests.post(url, json=data)
    end_time = time.time()
    
    if response.status_code != 200:
        logger.error(f"Ошибка при тестировании планирования экспериментов: {response.status_code}")
        logger.error(response.text)
        return None
    
    return end_time - start_time

def run_similarity_search_test():
    """Тестирование эндпоинта поиска по сходству"""
    url = f"{BASE_URL}/ml/similarity-search"
    data = {
        "query_text": "резкое падение цены",
        "collection": "market_events",
        "top_k": 5
    }
    
    start_time = time.time()
    response = requests.post(url, json=data)
    end_time = time.time()
    
    if response.status_code != 200:
        logger.error(f"Ошибка при тестировании поиска по сходству: {response.status_code}")
        logger.error(response.text)
        return None
    
    return end_time - start_time

def run_benchmark(tests=None):
    """Запускает бенчмарк для выбранных тестов"""
    if tests is None:
        tests = DEFAULT_TESTS
    
    if not check_backend_health():
        logger.error("Бэкенд недоступен. Запустите его перед запуском бенчмарка.")
        return False
    
    test_functions = {
        "risk_metrics": run_risk_metrics_test,
        "market_sentiment": run_market_sentiment_test,
        "experiment_plan": run_experiment_plan_test,
        "similarity_search": run_similarity_search_test
    }
    
    results = {}
    
    for test_name in tests:
        if test_name not in test_functions:
            logger.warning(f"Неизвестный тест: {test_name}. Пропускаем.")
            continue
            
        logger.info(f"Запуск теста: {test_name}")
        test_function = test_functions[test_name]
        
        # Прогрев
        logger.info("Прогрев...")
        _ = test_function()
        
        # Измерения
        durations = []
        for i in range(ITERATIONS):
            logger.info(f"Итерация {i+1}/{ITERATIONS}")
            duration = test_function()
            if duration is not None:
                durations.append(duration)
                logger.info(f"Время выполнения: {duration:.4f} сек")
        
        if durations:
            avg_duration = sum(durations) / len(durations)
            results[test_name] = {
                "avg_duration": avg_duration,
                "min_duration": min(durations),
                "max_duration": max(durations),
                "iterations": len(durations)
            }
            logger.info(f"Среднее время выполнения: {avg_duration:.4f} сек")
        else:
            logger.error(f"Не удалось получить измерения для теста {test_name}")
            results[test_name] = {"error": "No measurements"}
    
    # Сохранение результатов
    ensure_directory_exists("logs")
    results_path = f"logs/ml_benchmark_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(results_path, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "tests": results
        }, f, indent=2)
    
    logger.info(f"Результаты бенчмарка сохранены в {results_path}")
    
    # Вывод сводки
    print("\n=========== ML Benchmark Results ===========")
    print(f"{'Test':<20} {'Avg (sec)':<10} {'Min (sec)':<10} {'Max (sec)':<10}")
    print("-" * 55)
    
    for test_name, data in results.items():
        if "avg_duration" in data:
            print(f"{test_name:<20} {data['avg_duration']:<10.4f} {data['min_duration']:<10.4f} {data['max_duration']:<10.4f}")
        else:
            print(f"{test_name:<20} {'ERROR':<10} {'ERROR':<10} {'ERROR':<10}")
    
    print("=" * 55)
    
    return True

def main():
    parser = argparse.ArgumentParser(description="Бенчмарк ML-компонентов в HTX проекте")
    parser.add_argument("-t", "--tests", nargs="+", choices=DEFAULT_TESTS,
                      help=f"Список тестов для запуска. Доступные тесты: {', '.join(DEFAULT_TESTS)}")
    args = parser.parse_args()
    
    logger.info("===== Запуск бенчмарка ML-компонентов =====")
    ensure_directory_exists("logs")
    
    success = run_benchmark(args.tests)
    
    if success:
        logger.info("Бенчмарк успешно завершен")
        return 0
    else:
        logger.error("Бенчмарк завершен с ошибками")
        return 1

if __name__ == "__main__":
    sys.exit(main())
