#!/usr/bin/env python3
"""
Скрипт для шифрования HTX API ключей через Fernet
"""

from cryptography.fernet import Fernet
import os
import getpass


def generate_key():
    """Генерирует новый ключ шифрования Fernet"""
    return Fernet.generate_key()


def encrypt_value(value: str, key: bytes) -> str:
    """Шифрует значение с помощью Fernet"""
    f = Fernet(key)
    encrypted = f.encrypt(value.encode())
    return encrypted.decode()


def main():
    print("🔐 Генерация и шифрование HTX API ключей")
    print("=" * 50)
    
    # Генерируем новый ключ шифрования
    encryption_key = generate_key()
    print(f"Ключ шифрования: {encryption_key.decode()}")
    print()
    
    # Запрашиваем HTX API ключи
    print("Введите ваши HTX API ключи:")
    htx_api_key = getpass.getpass("HTX API Key: ")
    htx_api_secret = getpass.getpass("HTX API Secret: ")
    htx_subuid = input("HTX Sub UID (необязательно): ").strip()
    
    # Шифруем ключи
    encrypted_api_key = encrypt_value(htx_api_key, encryption_key)
    encrypted_api_secret = encrypt_value(htx_api_secret, encryption_key)
    encrypted_subuid = encrypt_value(htx_subuid, encryption_key) if htx_subuid else ""
    
    print("\n🔑 Зашифрованные ключи:")
    print("=" * 50)
    print(f"ENCRYPTION_KEY={encryption_key.decode()}")
    print(f"HTX_API_KEY={encrypted_api_key}")
    print(f"HTX_API_SECRET={encrypted_api_secret}")
    if encrypted_subuid:
        print(f"HTX_SUBUID={encrypted_subuid}")
    
    # Создаем .env файл
    env_content = f"""# HTX Project Environment Variables
# Generated on: {os.popen('date').read().strip()}

# Environment
ENV=dev
API_HOST=0.0.0.0
API_PORT=8004
DEBUG=true

# Database
DATABASE_URL=sqlite+aiosqlite:///./data/app.db
DATABASE_ECHO=false

# Encryption (ВАЖНО: НЕ коммитьте этот ключ в репозиторий!)
ENCRYPTION_KEY={encryption_key.decode()}

# HTX API (зашифрованные ключи)
HTX_API_KEY={encrypted_api_key}
HTX_API_SECRET={encrypted_api_secret}
HTX_BASE_URL=https://api.huobi.pro"""

    if encrypted_subuid:
        env_content += f"\nHTX_SUBUID={encrypted_subuid}"
    
    env_content += """

# 3Commas API (если нужно)
THREECOMMAS_API_KEY=
THREECOMMAS_API_SECRET=
THREECOMMAS_BASE_URL=https://api.3commas.io/public/api

# File processing
UPLOAD_DIR=./data/raw
PROCESSED_DIR=./data/processed
MAX_FILE_SIZE=52428800

# Security
JWT_SECRET=your-super-secret-jwt-key-change-this
JWT_EXPIRE_MINUTES=43200

# Background tasks
ENABLE_BACKGROUND_TASKS=false
"""
    
    # Сохраняем .env файл
    backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend")
    env_file = os.path.join(backend_dir, ".env")
    
    with open(env_file, "w", encoding="utf-8") as f:
        f.write(env_content)
    
    print(f"\n✅ .env файл создан: {env_file}")
    print("\n⚠️  ВАЖНО:")
    print("1. Не коммитьте .env файл в Git!")
    print("2. Сделайте резервную копию ключа шифрования")
    print("3. Проверьте что .env добавлен в .gitignore")


if __name__ == "__main__":
    main()
