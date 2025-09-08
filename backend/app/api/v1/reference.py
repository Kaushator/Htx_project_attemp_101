"""
Интеграция маршрутов нового модуля htx_reference в FastAPI приложение
"""

from fastapi import APIRouter
from app.api.v1.endpoints import htx_reference

router = APIRouter()

# Добавляем маршруты из модуля htx_reference
router.include_router(htx_reference.router)
