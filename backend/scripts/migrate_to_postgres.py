"""
Скрипт для миграции данных из SQLite в PostgreSQL
Использует SQLAlchemy для переноса данных между базами
"""

import os
import sys
import asyncio
from pathlib import Path
import sqlite3
import csv
from datetime import datetime

# Добавляем корень проекта в sys.path
root_dir = Path(__file__).resolve().parents[2]
sys.path.append(str(root_dir))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import inspect
from app.core.config import settings


# URL для PostgreSQL (изменяется в переменных окружения)
PG_URL = os.environ.get(
    "PG_DATABASE_URL", 
    "postgresql+asyncpg://htx:htx@localhost:5432/htx"
)

# Исходная БД SQLite (нормализованный путь)
SQLITE_PATH = settings.DATABASE_URL.replace('sqlite+aiosqlite:///', '')
SQLITE_FILE = Path(SQLITE_PATH).resolve()

# Пути для резервного копирования
BACKUP_DIR = root_dir / "data" / "backup"
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")


async def verify_connections():
    """Проверка подключений к обеим БД"""
    print(f"Проверка подключения к SQLite: {SQLITE_FILE}")
    
    if not SQLITE_FILE.exists():
        print(f"ОШИБКА: SQLite файл не найден: {SQLITE_FILE}")
        return False
    
    # Проверка SQLite
    try:
        conn = sqlite3.connect(str(SQLITE_FILE))
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"SQLite: найдено {len(tables)} таблиц")
        for table in tables:
            print(f"  - {table[0]}")
        conn.close()
    except Exception as e:
        print(f"ОШИБКА подключения к SQLite: {e}")
        return False
    
    # Проверка PostgreSQL
    print(f"\nПроверка подключения к PostgreSQL: {PG_URL.split('@')[1]}")
    try:
        pg_engine = create_async_engine(PG_URL, echo=False)
        async with pg_engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            await conn.commit()
            if result.scalar_one() == 1:
                print("PostgreSQL: подключение успешно")
            
        await pg_engine.dispose()
        return True
    except Exception as e:
        print(f"ОШИБКА подключения к PostgreSQL: {e}")
        return False


async def create_postgres_tables():
    """Создание структуры таблиц в PostgreSQL"""
    from app.models.base import Base
    
    print("\nСоздание таблиц в PostgreSQL...")
    pg_engine = create_async_engine(PG_URL, echo=False)
    
    try:
        async with pg_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("Таблицы PostgreSQL созданы успешно")
    except Exception as e:
        print(f"ОШИБКА создания таблиц: {e}")
        return False
    finally:
        await pg_engine.dispose()
    
    return True


async def backup_sqlite_data():
    """Резервное копирование данных из SQLite в CSV"""
    print(f"\nСоздание резервных копий в {BACKUP_DIR}")
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    try:
        conn = sqlite3.connect(str(SQLITE_FILE))
        cursor = conn.cursor()
        
        # Получаем список таблиц
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = table[0]
            backup_file = BACKUP_DIR / f"{table_name}_{TIMESTAMP}.csv"
            
            print(f"  Резервное копирование {table_name} → {backup_file.name}")
            
            # Получаем данные и заголовки
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            headers = [desc[0] for desc in cursor.description]
            
            # Записываем в CSV
            with open(backup_file, 'w', newline='', encoding='utf-8') as f:
                csv_writer = csv.writer(f)
                csv_writer.writerow(headers)
                csv_writer.writerows(rows)
            
            print(f"    Сохранено {len(rows)} записей")
        
        conn.close()
        return True
    except Exception as e:
        print(f"ОШИБКА резервного копирования: {e}")
        return False


async def migrate_data():
    """Мигрирует данные из SQLite в PostgreSQL"""
    
    print("\nМиграция данных из SQLite в PostgreSQL...")
    
    # Подключаемся к PostgreSQL
    pg_engine = create_async_engine(PG_URL, echo=False)
    sqlite_conn = None
    
    try:
        # Получаем список таблиц из SQLite
        sqlite_conn = sqlite3.connect(str(SQLITE_FILE))
        cursor = sqlite_conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        # Получаем инспектор PostgreSQL для проверки структуры
        async with pg_engine.begin() as conn:
            insp = inspect(pg_engine)
            
            for table in tables:
                table_name = table[0]
                print(f"Обработка таблицы {table_name}...")
                
                # Проверяем, существует ли таблица в PostgreSQL
                pg_tables = await conn.run_sync(lambda sync_conn: insp.get_table_names(connection=sync_conn))
                if table_name not in pg_tables:
                    print(f"  Таблица {table_name} не найдена в PostgreSQL, пропускаем")
                    continue
                
                # Получаем данные из SQLite
                cursor.execute(f"SELECT * FROM {table_name}")
                rows = cursor.fetchall()
                if not rows:
                    print(f"  Таблица {table_name} пуста, пропускаем")
                    continue
                
                # Получаем заголовки
                headers = [desc[0] for desc in cursor.description]
                
                # Вставляем в PostgreSQL
                columns = ", ".join(headers)
                placeholders = ", ".join([f":{i}" for i in range(len(headers))])
                
                stmt = text(f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})")
                
                row_count = 0
                for row in rows:
                    # Преобразуем кортеж в словарь с номерными ключами
                    row_dict = {str(i): val for i, val in enumerate(row)}
                    await conn.execute(stmt, row_dict)
                    row_count += 1
                
                print(f"  Перенесено {row_count} записей в {table_name}")
        
        print("\nМиграция данных завершена успешно")
        return True
    except Exception as e:
        print(f"ОШИБКА миграции данных: {e}")
        return False
    finally:
        if sqlite_conn:
            sqlite_conn.close()
        await pg_engine.dispose()


async def main():
    """Главная функция миграции"""
    print("=" * 60)
    print("МИГРАЦИЯ SQLITE → POSTGRESQL")
    print("=" * 60)
    
    # Проверяем подключения
    if not await verify_connections():
        print("\nПРЕРЫВАНИЕ: Ошибка подключения к базам данных")
        return False
    
    # Создаем резервные копии
    print("\n" + "=" * 60)
    if not await backup_sqlite_data():
        print("\nПРЕРЫВАНИЕ: Ошибка резервного копирования")
        return False
    
    # Создаем таблицы в PostgreSQL
    print("\n" + "=" * 60)
    if not await create_postgres_tables():
        print("\nПРЕРЫВАНИЕ: Ошибка создания таблиц в PostgreSQL")
        return False
    
    # Мигрируем данные
    print("\n" + "=" * 60)
    if not await migrate_data():
        print("\nПРЕРЫВАНИЕ: Ошибка миграции данных")
        return False
    
    print("\n" + "=" * 60)
    print("МИГРАЦИЯ УСПЕШНО ЗАВЕРШЕНА!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    # Проверяем переменную окружения для PostgreSQL
    if "PG_DATABASE_URL" not in os.environ:
        print("ВНИМАНИЕ: Переменная PG_DATABASE_URL не установлена")
        print(f"Будет использован URL по умолчанию: {PG_URL}")
        answer = input("Продолжить? (y/n): ")
        if answer.lower() != "y":
            sys.exit(1)
    
    asyncio.run(main())
