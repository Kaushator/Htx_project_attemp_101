# Перенос и запуск проекта в WSL (Ubuntu)

Этот гайд помогает перенести локальную разработку проекта в окружение WSL2 (рекомендуется дистрибутив Ubuntu).

## Почему это полезно
- Быстрее работа с файлами и зависимостями в Linux FS (`/home/...`).
- Совместимость с Linux-инструментами, Docker и CI.
- Избегаем нестабильного Alpine-дистрибутива `docker-desktop` для разработки кода.

## 1) Установка и подготовка WSL
1. Установите WSL и дистрибутив Ubuntu (Microsoft Store).
2. Запустите Ubuntu, создайте пользователя.
3. Обновите пакеты и установите системные зависимости Python/сборки:

```bash
sudo apt update
sudo apt install -y python3-venv python3-pip build-essential python3-dev libssl-dev libffi-dev make git curl
```

Опционально: если нужен другой Python (3.11+), установите через `pyenv` или `deadsnakes`.

## 2) Размещение проекта в Linux ФС
Рекомендуется хранить код внутри Linux ФС, а не на смонтированном диске Windows.

```bash
mkdir -p ~/projects
cd ~/projects
git clone <URL_ВАШЕГО_РЕПО> Htx_project_attemp_101
cd Htx_project_attemp_101
```

Открывайте этот путь через VS Code: команда «WSL: Open Folder in WSL…».

Если репозиторий уже находится на диске Windows (например, `E:\Htx_project_attemp_101`), можно просто пере-клонировать его в `~/projects` или скопировать:

```bash
# из PowerShell на Windows
wsl -- bash -lc "mkdir -p ~/projects && cp -r /mnt/e/Htx_project_attemp_101 ~/projects/"
```

## 3) Быстрый старт
Есть два варианта — скрипт или Makefile.

Вариант A: скрипты
```bash
./scripts/wsl_setup.sh
./scripts/run_dev.sh
```

Вариант B: Makefile (выполняйте из корня)
```bash
make install
make dev
```

Что делает настройка:
- Создаёт виртуальное окружение `.venv/` и активирует его.
- Устанавливает зависимости из `backend/requirements.txt` (и dev — через `make install`).
- Копирует `backend/env.example` в `backend/.env` (если отсутствует).
- Создаёт каталоги `backend/data/raw`, `backend/data/processed`, `backend/data/samples` и `backend/logs` (Linux ФС).
- Запускает API на http://localhost:8000/docs с ускорителями `uvloop`/`httptools`.

## 4) Запуск в Docker (опционально)
- В Docker Desktop включите интеграцию с вашим Ubuntu.
- Запуск из корня проекта:

```bash
docker compose up --build
```

## 5) Типичные проблемы
- VS Code подключается к `docker-desktop` (Alpine) и ругается на `libstdc++`.
  - Для разработки кода используйте ваш дистрибутив Ubuntu (через «WSL: Connect to WSL»), а не `docker-desktop`.
  - Если нужно именно Alpine, установите пакет (на свой страх и риск):
    ```bash
    wsl -d docker-desktop -e sh -c "apk update && apk add libstdc++"
    ```
- Медленная файловая система и непредсказуемые ошибки путей — переместите проект в `/home/<user>/...`.
  - В проекте по умолчанию данные и логи теперь лежат в `backend/data` и `backend/logs`.
  - Перенесите старые `data/` и `logs/` из Windows-копии в эти каталоги внутри WSL, если нужно сохранить историю.

## 6) Тесты и качество
```bash
make test
make lint
make format
```

## 7) Полезно знать
- Перезапуск сервера: Ctrl+C и снова `make dev` или `./scripts/run_dev.sh`.
- Проверка venv: `which python` → должен указывать на `./.venv/bin/python`.
- SQLite БД в `./data/app.db` создаётся автоматически (через `sqlite+aiosqlite`).
