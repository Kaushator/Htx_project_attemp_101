# HTX Trading Analysis Project

Комплексный инструмент для анализа торговых данных с биржи HTX (Huobi), включающий загрузку CSV/Excel файлов, расчет PnL и интеграцию с 3Commas.

## 🚀 Быстрый старт

### Локальный запуск

```bash
# 1. Клонировать репозиторий
git clone <repository-url>
cd htx_project

# 2. Запустить скрипт разработки
# Windows:
.\scripts\run_dev.ps1

# Linux/Mac:
chmod +x scripts/run_dev.sh
./scripts/run_dev.sh
```

### Docker запуск

```bash
# 1. Скопировать переменные окружения
cp backend/env.example backend/.env

# 2. Запустить с Docker Compose
docker-compose up --build
```

## 📁 Структура проекта

```
htx_project/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── main.py         # Точка входа FastAPI
│   │   ├── core/           # Конфигурация и логирование
│   │   ├── api/v1/         # API endpoints
│   │   ├── models/         # SQLAlchemy модели
│   │   ├── schemas/        # Pydantic схемы
│   │   ├── services/       # Бизнес-логика
│   │   ├── db/            # База данных
│   │   └── workers/       # Фоновые задачи
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/               # React frontend (опционально)
├── data/                  # Данные
│   ├── raw/              # Исходные файлы
│   ├── processed/        # Обработанные данные
│   └── samples/          # Примеры файлов
├── docs/                 # Документация
├── scripts/              # Скрипты запуска
└── docker-compose.yml
```

## 🔧 Конфигурация

### Переменные окружения

Скопируйте `backend/env.example` в `backend/.env` и настройте:

```ini
# API настройки
API_HOST=0.0.0.0
API_PORT=8000

# База данных
DATABASE_URL=sqlite+aiosqlite:///./data/app.db

# HTX API
HTX_API_KEY=your_api_key
HTX_API_SECRET=your_api_secret

# 3Commas API (опционально)
THREECOMMAS_API_KEY=your_api_key
THREECOMMAS_API_SECRET=your_api_secret
```

## 📊 API Endpoints

### Health Check
- `GET /api/v1/health` - Проверка состояния API
- `GET /api/v1/health/db` - Проверка базы данных

### Files
- `POST /api/v1/files/upload` - Загрузка CSV/XLSX файлов
- `GET /api/v1/files/list` - Список загруженных файлов

### Trades
- `GET /api/v1/trades` - Список сделок
- `GET /api/v1/trades/summary` - Сводка по сделкам

### Cashflow
- `GET /api/v1/cashflow/deposits` - Депозиты
- `GET /api/v1/cashflow/withdrawals` - Выводы
- `GET /api/v1/cashflow/transfers` - Трансферы

### PnL
- `GET /api/v1/pnl/summary` - Сводка PnL
- `GET /api/v1/pnl/daily` - Ежедневный PnL
- `GET /api/v1/pnl/drawdown` - Анализ просадки

## 🔍 Документация API

После запуска приложения:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📈 Поддерживаемые форматы данных

### CSV/XLSX файлы
Проект поддерживает загрузку файлов с листами:
- `exchange` - данные о сделках
- `deposit` - данные о депозитах
- `withdraw` - данные о выводах
- `transfer` - данные о трансферах

### Пример файла
Смотрите `data/samples/969229.xlsx` для примера структуры данных.

## 🛠️ Разработка

### Установка зависимостей для разработки

```bash
pip install -r backend/requirements-dev.txt
```

### Запуск тестов

```bash
cd backend
pytest
```

### Линтинг и форматирование

```bash
cd backend
ruff check .
black .
isort .
```

## 🐳 Docker

### Сборка образа

```bash
docker build -t htx-project ./backend
```

### Запуск с Docker Compose

```bash
docker-compose up -d
```

## 📝 Лицензия

MIT License

## 🤝 Поддержка

Для вопросов и предложений создавайте issues в репозитории.

---

**Примечание**: Это проект в разработке. Некоторые функции могут быть не полностью реализованы.
