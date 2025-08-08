"""
Main API routes
Основні API роути
"""

from fastapi import APIRouter

from .cli import router as cli_router
from .system import router as system_router
from .files import router as files_router
from .ml import router as ml_router

# Створюємо головний роутер
api_router = APIRouter()

# Підключаємо підроутери
api_router.include_router(cli_router, prefix="/cli", tags=["CLI"])
api_router.include_router(system_router, prefix="/system", tags=["System"])
api_router.include_router(files_router, prefix="/files", tags=["Files"])
api_router.include_router(ml_router, prefix="/ml", tags=["ML"]) 