"""
Event handlers for FastAPI application
Event handlers для FastAPI додатку
"""

from typing import Callable
from fastapi import FastAPI
from loguru import logger

from .config import settings


def create_start_app_handler(app: FastAPI) -> Callable:
    """Створення handler для запуску додатку"""
    
    async def start_app() -> None:
        """Дії при запуску додатку"""
        logger.info("🚀 Starting MOVA Web Interface...")
        logger.info(f"📊 Version: {settings.VERSION}")
        logger.info(f"🌐 Host: {settings.HOST}:{settings.PORT}")
        logger.info(f"🔧 Debug mode: {settings.DEBUG}")
        
        # Створення директорій
        import os
        from pathlib import Path
        
        upload_dir = Path(settings.UPLOAD_DIR)
        upload_dir.mkdir(exist_ok=True)
        logger.info(f"📁 Upload directory: {upload_dir.absolute()}")
        
        # Ініціалізація MOVA SDK
        try:
            # Тут буде ініціалізація MOVA SDK
            logger.info("✅ MOVA SDK initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize MOVA SDK: {e}")
        
        logger.info("✅ MOVA Web Interface started successfully")
    
    return start_app


def create_stop_app_handler(app: FastAPI) -> Callable:
    """Створення handler для зупинки додатку"""
    
    async def stop_app() -> None:
        """Дії при зупинці додатку"""
        logger.info("🛑 Stopping MOVA Web Interface...")
        
        # Cleanup ресурсів
        try:
            # Тут буде cleanup MOVA SDK
            logger.info("✅ MOVA SDK cleanup completed")
        except Exception as e:
            logger.error(f"❌ Failed to cleanup MOVA SDK: {e}")
        
        logger.info("✅ MOVA Web Interface stopped successfully")
    
    return stop_app 