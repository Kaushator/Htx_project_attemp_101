#!/usr/bin/env python3
"""
Отладка подписи HTX API
"""

import hmac
import hashlib
from datetime import datetime
from urllib.parse import quote
from app.core.config import settings

def debug_signature():
    """Отладка генерации подписи"""
    
    # Получаем расшифрованные ключи
    api_key = settings.htx_api_key
    api_secret = settings.htx_api_secret
    subuid = settings.htx_subuid
    
    print(f"API Key: {api_key[:8]}...")
    print(f"API Secret: {api_secret[:8]}...")
    print(f"SubUID: {subuid}")
    
    # Тестируем подпись для запроса баланса
    method = "GET"
    path = "/v1/account/accounts/balance"
    timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
    
    params = {
        'AccessKeyId': api_key,
        'SignatureMethod': 'HmacSHA256',
        'SignatureVersion': '2',
        'Timestamp': timestamp
    }
    
    if subuid:
        params['SubUid'] = subuid
    
    # Создаем строку для подписи - попробуем разные варианты
    param_str = '&'.join([f"{k}={quote(str(v), safe='')}" for k, v in sorted(params.items())])
    
    # Варианты payload
    payload1 = f"{method}\napi.huobi.pro\n{path}\n{param_str}"
    payload2 = f"{method}\napi.htx.com\n{path}\n{param_str}"
    
    print(f"\nTimestamp: {timestamp}")
    print(f"Param string: {param_str}")
    print(f"\nPayload variant 1 (huobi.pro):\n{payload1}")
    print(f"\nPayload variant 2 (htx.com):\n{payload2}")
    
    # Генерируем подписи
    sig1 = hmac.new(api_secret.encode('utf-8'), payload1.encode('utf-8'), hashlib.sha256).hexdigest()
    sig2 = hmac.new(api_secret.encode('utf-8'), payload2.encode('utf-8'), hashlib.sha256).hexdigest()
    
    print(f"\nSignature 1: {sig1}")
    print(f"Signature 2: {sig2}")

if __name__ == "__main__":
    debug_signature()
