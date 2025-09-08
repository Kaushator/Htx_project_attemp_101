# WSL2 RECOMMENDED PROJECT

⚠️ **ВАЖНО: Рекомендуется использовать WSL2 (Windows Subsystem for Linux версии 2)**

## Системные требования:
- WSL 2 с Ubuntu (рекомендуется)
- Python 3.12+ в WSL
- Node.js в WSL
- Docker в WSL (опционально, для контейнеризации)

## Виртуальное окружение:
- `.venv_wsl2/` - оптимизированное WSL2 окружение
- `.venv_wsl/` - устаревшее WSL окружение
- ~~`.venv/`~~ - удалено (было Windows-окружение)

## Запуск проекта:

### Быстрый запуск на WSL2 (рекомендуется):
```bash
# Из Windows PowerShell/CMD:
launch_wsl2.bat

# Из WSL2 напрямую:
./start_wsl2.sh
```

### Устаревший метод:
```bash
# Из Windows PowerShell/CMD:
quick_start.bat
```

### Ручной запуск в WSL:
```bash
# Подготовка окружения:
wsl -d Ubuntu -- bash -c "cd /mnt/e/Htx_project_attemp_101 && ./scripts/wsl_setup.sh"

# Запуск backend:
wsl -d Ubuntu -- bash -c "cd /mnt/e/Htx_project_attemp_101/backend && source ../.venv_wsl/bin/activate && python -m uvicorn app.main:app --host 0.0.0.0 --port 8004 --reload"

# Запуск frontend:
wsl -d Ubuntu -- bash -c "cd /mnt/e/Htx_project_attemp_101/frontend && npm run dev -- --host 0.0.0.0 --port 3000"
```

## Порты:
- Backend: http://localhost:8004
- Frontend: http://localhost:3000
- API Docs: http://localhost:8004/docs

## Что было очищено:
- ✅ Windows .bat файлы (кроме quick_start.bat)
- ✅ PowerShell .ps1 файлы
- ✅ Windows виртуальное окружение (.venv/)
- ✅ Python кеши (__pycache__)
- ✅ Временные файлы
- ✅ Дублирующиеся папки
- ✅ Тестовые файлы из корня

## GitHub совместимость:
- Все GitHub файлы (.github/, githooks/) сохранены
- Git история не затронута
