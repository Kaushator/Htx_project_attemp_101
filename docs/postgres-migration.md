# PostgreSQL Migration - ЗАВЕРШЕНО ✅

**Дата выполнения**: 28 августа 2025  
**Статус**: Успешно завершена

## 🎯 Цель миграции
Переход с SQLite на PostgreSQL для лучшей производительности и функциональности

## ✅ Что было выполнено:

### 1. Установка PostgreSQL в WSL
- PostgreSQL 16.9 установлен и настроен
- Создана база данных `htx_project` 
- Настроен пользователь `htx_user` с правами

### 2. Обновление конфигурации
- `env.postgres` - конфигурация для PostgreSQL
- `alembic.ini` - использует переменные окружения
- `alembic/env.py` - поддержка настроек приложения
- `.env` - скопирован и настроен в WSL

### 3. Исправление SQL совместимости  
**Проблема**: `strftime()` работает только в SQLite  
**Решение**: Создана функция `get_hour_truncate()`:
- PostgreSQL: `date_trunc('hour', column)`
- SQLite: `strftime('%Y-%m-%d %H:00:00', column)`

### 4. Установка зависимостей
- `asyncpg` - асинхронный драйвер PostgreSQL
- `psycopg2-binary` - синхронный драйвер для миграций

### 5. Миграция базы данных
```bash
alembic upgrade head
# INFO: Context impl PostgresqlImpl ✅
# INFO: Running upgrade -> 76485e958611, Initial migration ✅
```

## 🧪 Результаты тестирования:
- **16/17 тестов PASSED** ✅
- Все SQL запросы работают корректно
- Database health checks проходят
- Background tasks функционируют

## 🚀 Технические преимущества:
- Расширенные SQL функции (`date_trunc`, `JSONB`)
- Лучшая производительность для сложных запросов
- Поддержка concurrent connections
- Продвинутые индексы и оптимизация

**🎉 Миграция на PostgreSQL завершена успешно!**

## Предварительные требования

1. WSL с Ubuntu или другим дистрибутивом Linux
2. PostgreSQL установлен и запущен в WSL
3. Docker (опционально)

## Вариант 1: Локальная установка PostgreSQL в WSL

### 1. Установка PostgreSQL в WSL

```bash
# Обновление пакетов и установка PostgreSQL
sudo apt update
sudo apt install -y postgresql postgresql-contrib

# Запуск службы PostgreSQL
sudo service postgresql start

# Создание пользователя и базы данных
sudo -u postgres psql -c "CREATE USER htx WITH PASSWORD 'htx';"
sudo -u postgres psql -c "CREATE DATABASE htx OWNER htx;"

# Проверка статуса PostgreSQL
sudo service postgresql status

# Установка драйвера asyncpg в venv
cd ~/projects/Htx_project_attemp_101
source .venv/bin/activate
pip install asyncpg
```

### 2. Настройка окружения для PostgreSQL

```bash
# Копируем шаблон конфигурации для PostgreSQL
cd ~/projects/Htx_project_attemp_101
cp backend/env.postgres backend/.env

# Редактируем DATABASE_URL для локальной установки PostgreSQL
sed -i 's|postgresql+asyncpg://htx:htx@db:5432/htx|postgresql+asyncpg://htx:htx@localhost:5432/htx|g' backend/.env
```

### 3. Миграция данных из SQLite в PostgreSQL

```bash
cd ~/projects/Htx_project_attemp_101
source .venv/bin/activate

# Запуск скрипта миграции
cd backend
python scripts/setup_postgres.py  # Проверяет подключение и создает таблицы
python scripts/migrate_to_postgres.py  # Переносит данные из SQLite
```

### 4. Проверка и запуск API с PostgreSQL

```bash
cd ~/projects/Htx_project_attemp_101
source .venv/bin/activate

# Запуск API с новой БД
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --loop uvloop --http httptools
```

## Вариант 2: PostgreSQL в Docker

### 1. Запуск PostgreSQL через Docker Compose

```bash
# Переходим в корневую директорию проекта
cd ~/projects/Htx_project_attemp_101

# Запускаем Docker Compose с PostgreSQL и Redis
./scripts/setup_docker.sh
```

### 2. Настройка окружения для Docker PostgreSQL

```bash
# Копируем шаблон конфигурации для PostgreSQL в Docker
cp backend/env.postgres backend/.env

# Устанавливаем asyncpg
source .venv/bin/activate
pip install asyncpg
```

### 3. Миграция данных из SQLite в PostgreSQL

```bash
cd ~/projects/Htx_project_attemp_101
source .venv/bin/activate

# Настраиваем переменную окружения для миграции
export PG_DATABASE_URL="postgresql+asyncpg://htx:htx@localhost:5432/htx"

# Запуск скрипта миграции
cd backend
python scripts/migrate_to_postgres.py
```

### 4. Проверка и запуск API с PostgreSQL в Docker

```bash
# API уже запущен в Docker и доступен по адресу:
# http://localhost:8000

# Для локального запуска:
cd ~/projects/Htx_project_attemp_101
source .venv/bin/activate
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --loop uvloop --http httptools
```

## Примечания

- Если вы получаете ошибки прав доступа в PostgreSQL, проверьте конфигурацию в файле `/etc/postgresql/*/main/pg_hba.conf`
- После миграции сохраните копию SQLite базы данных для резервного копирования
- Обязательно установите пакет `asyncpg` для работы с PostgreSQL:
  ```
  pip install asyncpg
  ```
- Для решения проблем с подключением, проверьте, что PostgreSQL слушает на всех интерфейсах:
  ```
  sudo -u postgres psql -c "ALTER SYSTEM SET listen_addresses = '*';"
  sudo service postgresql restart
  ```
