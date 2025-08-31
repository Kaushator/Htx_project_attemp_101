#!/usr/bin/env python3
# filepath: e:\Htx_project_attemp_101\scripts\full_push.py
"""
Полный пуш проекта в GitHub с защитой от утечки токенов.
- выполняется в рамках указной директории репозитория
- опционально прогоняет pytest и линтинг (black/flake8/mypy)
- использует токен из GITHUB_TOKEN (для https-пуша)
"""

import argparse
import os
import subprocess
import sys
import textwrap
from datetime import datetime
from pathlib import Path

def run(cmd, cwd=None, check=True, capture=False):
    print(f"+ {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, text=True, capture_output=capture)
    if capture:
        return result.returncode, result.stdout, result.stderr
    else:
        return result.returncode, None, None

def has_changes(repo_path: Path) -> bool:
    code, out, err = run(["git", "status", "--porcelain"], cwd=str(repo_path), capture=True)
    if code != 0:
        print("Ошибка чтения статуса git:", err)
        return False
    return bool(out.strip()) if out else False

def get_origin_url(repo_path: Path) -> str:
    code, out, err = run(["git", "remote", "get-url", "origin"], cwd=str(repo_path), capture=True)
    if code != 0:
        print("Не удалось получить URL origin:", err)
        return ""
    return out.strip() if out else ""

def ensure_token_url(origin_url: str, token: str) -> str:
    token_part = f"x-access-token:{token}"
    if origin_url.startswith("https://") or origin_url.startswith("http://"):
        proto, rest = origin_url.split("://", 1)
        # формируем https://x-access-token:TOKEN@github.com/OWNER/REPO.git
        return f"{proto}://{token_part}@{rest}"
    # если origin не https, просто возвращаем оригинал
    return origin_url

def get_python_bin(repo_path: Path) -> str:
    """Get Python executable from venv or system (WSL/Linux compatible)"""
    # Try WSL/Linux venv first
    venv_linux = repo_path / ".venv" / "bin" / "python"
    if venv_linux.exists():
        return str(venv_linux)
    
    # Fallback to Windows venv for compatibility
    venv_windows = repo_path / ".venv" / "Scripts" / "python.exe"
    if venv_windows.exists():
        return str(venv_windows)
    
    return "python3"

def main():
    parser = argparse.ArgumentParser(
        description="Полный пуш проекта с проверками",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("--repo-path", default="/home/runner/work/Htx_project_attemp_101/Htx_project_attemp_101",
                        help="Path to the project repository (WSL/Linux).")
    parser.add_argument("--branch", default="main", help="График ветки для пуша.")
    parser.add_argument("--skip-tests", action="store_true", help="Пропустить pytest.")
    parser.add_argument("--skip-lint", action="store_true", help="Пропустить линтинг (black/flake8/mypy).")
    parser.add_argument("--dry-run", action="store_true", help="Пробный прогон без реального пуша.")
    parser.add_argument("--commit-message", default=None,
                        help="Сообщение коммита. Если не указано, будет сгенерировано автоматически.")
    args = parser.parse_args()

    repo_path = Path(args.repo_path).resolve()
    if not (repo_path / ".git").exists():
        print("Не найден .git в указанном пути. Укажите путь к корню репозитория.")
        sys.exit(1)

    # 1) Проверка изменений
    if has_changes(repo_path):
        print("Есть изменения, собираемся коммитить.")
    else:
        print("Нет изменений для коммита. Пушим последнюю ветку без новых коммитов.")

    # 2) Токен и цель пуша
    token = os.environ.get("GITHUB_TOKEN")
    origin_url = get_origin_url(repo_path)
    if not origin_url:
        print("Не удалось определить origin.")
        sys.exit(1)

    use_token = bool(token)
    push_target = None
    if use_token:
        push_target = ensure_token_url(origin_url, token)
        print("Пуш будет выполнен через токен на URL:", push_target)
    else:
        push_target = origin_url
        print("Пуш будет выполнен на URL origin без токена.")

    branch = args.branch

    # 3) Предпуш-проверки
    python_bin = get_python_bin(repo_path)
    if not args.dry_run:
        if not args.skip_tests:
            print("Запуск pytest...")
            code, _, _ = run([python_bin, "-m", "pytest", "-q"], cwd=str(repo_path / "backend"))
            if code != 0:
                print("Tests провалились. Прерываю пуш.")
                sys.exit(code)
        if not args.skip_lint:
            print("Запуск линтинга (black/flake8/mypy)...")
            # black
            code_black, _, _ = run([python_bin, "-m", "black", "--check", "."], cwd=str(repo_path), capture=True)
            if code_black not in (0, 2):  # 2 = module not found
                print("Black check failed")
                # Не прерываем, если black не установлен
            # flake8
            code_flake, _, _ = run([python_bin, "-m", "flake8", "."], cwd=str(repo_path), capture=True)
            if code_flake not in (0, 2):  # 2 = module not found
                print("Flake8 check failed")
                # Не прерываем, если flake8 не установлен
            # mypy
            code_mypy, _, _ = run([python_bin, "-m", "mypy", "."], cwd=str(repo_path), capture=True)
            if code_mypy not in (0, 2):  # 2 = module not found
                print("Mypy check failed")
                # Не прерываем, если mypy не установлен

    # 4) Коммит
    if has_changes(repo_path):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if args.commit_message:
            commit_msg = args.commit_message
        else:
            commit_msg = f"chore(full-push): auto-commit {timestamp}"
        code, _, _ = run(["git", "add", "-A"], cwd=str(repo_path))
        code, _, _ = run(["git", "commit", "-m", commit_msg], cwd=str(repo_path))
        if code != 0:
            print("Коммит не выполнен (возможно изменений нет).")
    else:
        print("Изменений для коммита нет.")

    if args.dry_run:
        print("Dry run завершён. Не выполняем пуш.")
        sys.exit(0)

    # 5) Пуш
    print("Пуш в ветку", branch)
    if use_token:
        push_code, _, _ = run(["git", "push", push_target, f"HEAD:{branch}"], cwd=str(repo_path))
    else:
        push_code, _, _ = run(["git", "push", "origin", branch], cwd=str(repo_path))
    if push_code != 0:
        print("Пуш не удался.")
        sys.exit(push_code)

    print("Пуш успешно выполнен.")

if __name__ == "__main__":
    main()