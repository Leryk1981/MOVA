"""
MOVA SDK service
Сервіс для роботи з MOVA SDK
"""

import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any, List
from loguru import logger

# Додаємо шлях до MOVA SDK
sdk_path = Path(__file__).parent.parent.parent.parent.parent / "src"
sys.path.insert(0, str(sdk_path))

try:
    from mova.core.engine import MovaEngine
    from mova.core.async_engine import create_async_mova_engine, AsyncMovaEngine
    from mova.ml.integration import MLIntegration
    from mova.webhook_integration import get_webhook_integration
    from mova.redis_manager import get_redis_manager
    from mova.cache import get_cache
    from mova.config import get_config_value, set_config_value
    MOVA_AVAILABLE = True
except ImportError as e:
    logger.warning(f"MOVA SDK not available: {e}")
    MOVA_AVAILABLE = False


class MovaService:
    """Сервіс для роботи з MOVA SDK"""
    
    def __init__(self):
        """Ініціалізація сервісу"""
        self.engine: Optional[MovaEngine] = None
        self.async_engine: Optional[AsyncMovaEngine] = None
        self.ml_integration: Optional[MLIntegration] = None
        self.webhook_integration = None
        self.redis_manager = None
        self.cache_manager = None
        
        if MOVA_AVAILABLE:
            self._initialize_components()
    
    def _initialize_components(self):
        """Ініціалізація компонентів MOVA"""
        try:
            # Ініціалізація webhook інтеграції
            self.webhook_integration = get_webhook_integration()
            logger.info("✅ Webhook integration initialized")
            
            # Ініціалізація кешу
            self.cache_manager = get_cache()
            logger.info("✅ Cache manager initialized")
            
            # ML інтеграція буде ініціалізована при потребі
            logger.info("✅ MOVA SDK components initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize MOVA components: {e}")
    
    async def create_async_engine(self, redis_url: Optional[str] = None, 
                                llm_api_key: Optional[str] = None,
                                llm_model: Optional[str] = None) -> AsyncMovaEngine:
        """Створення асинхронного движка"""
        if not MOVA_AVAILABLE:
            raise RuntimeError("MOVA SDK not available")
        
        try:
            self.async_engine = await create_async_mova_engine(
                redis_url=redis_url,
                llm_api_key=llm_api_key,
                llm_model=llm_model
            )
            logger.info("✅ Async MOVA engine created")
            return self.async_engine
        except Exception as e:
            logger.error(f"❌ Failed to create async engine: {e}")
            raise
    
    def create_sync_engine(self, redis_url: Optional[str] = None,
                          llm_api_key: Optional[str] = None,
                          llm_model: Optional[str] = None) -> MovaEngine:
        """Створення синхронного движка"""
        if not MOVA_AVAILABLE:
            raise RuntimeError("MOVA SDK not available")
        
        try:
            self.engine = MovaEngine(
                redis_url=redis_url,
                llm_api_key=llm_api_key,
                llm_model=llm_model
            )
            logger.info("✅ Sync MOVA engine created")
            return self.engine
        except Exception as e:
            logger.error(f"❌ Failed to create sync engine: {e}")
            raise
    
    def get_ml_integration(self) -> MLIntegration:
        """Отримання ML інтеграції"""
        if not MOVA_AVAILABLE:
            raise RuntimeError("MOVA SDK not available")
        
        if self.ml_integration is None:
            self.ml_integration = MLIntegration()
            logger.info("✅ ML integration initialized")
        
        return self.ml_integration
    
    def get_redis_manager(self, redis_url: str = "redis://localhost:6379"):
        """Отримання Redis менеджера"""
        if not MOVA_AVAILABLE:
            raise RuntimeError("MOVA SDK not available")
        
        return get_redis_manager(redis_url)
    
    def get_cache_manager(self):
        """Отримання кеш менеджера"""
        if not MOVA_AVAILABLE:
            raise RuntimeError("MOVA SDK not available")
        
        return self.cache_manager
    
    def get_webhook_integration(self):
        """Отримання webhook інтеграції"""
        if not MOVA_AVAILABLE:
            raise RuntimeError("MOVA SDK not available")
        
        return self.webhook_integration
    
    async def cleanup(self):
        """Очищення ресурсів"""
        try:
            if self.async_engine:
                await self.async_engine.cleanup()
                logger.info("✅ Async engine cleaned up")
        except Exception as e:
            logger.error(f"❌ Failed to cleanup async engine: {e}")
        
        try:
            if self.engine:
                # Синхронний движок не потребує cleanup
                pass
        except Exception as e:
            logger.error(f"❌ Failed to cleanup sync engine: {e}")
    
    def is_available(self) -> bool:
        """Перевірка доступності MOVA SDK"""
        return MOVA_AVAILABLE
    
    def get_sdk_info(self) -> Dict[str, Any]:
        """Отримання інформації про SDK"""
        return {
            "available": MOVA_AVAILABLE,
            "version": "2.2.0",
            "components": {
                "engine": self.engine is not None,
                "async_engine": self.async_engine is not None,
                "ml_integration": self.ml_integration is not None,
                "webhook_integration": self.webhook_integration is not None,
                "cache_manager": self.cache_manager is not None
            }
        }


# Глобальний екземпляр сервісу
mova_service = MovaService() 