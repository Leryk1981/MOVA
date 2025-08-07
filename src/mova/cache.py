"""
Caching system for MOVA SDK
Система кешування для MOVA SDK
"""

import json
import hashlib
import time
from typing import Any, Optional, Dict
from pathlib import Path
from functools import wraps
from loguru import logger

from .config import get_config_value


class CacheManager:
    """
    Cache manager for MOVA SDK
    Менеджер кешу для MOVA SDK
    """
    
    def __init__(self):
        """Initialize cache manager / Ініціалізація менеджера кешу"""
        self.cache_enabled = get_config_value("cache_enabled", True)
        self.cache_ttl = get_config_value("cache_ttl", 3600)
        self.cache_dir = Path(get_config_value("cache_dir", ".mova_cache"))
        
        if self.cache_enabled:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Cache initialized at: {self.cache_dir}")
    
    def _generate_key(self, data: Any) -> str:
        """Generate cache key from data / Згенерувати ключ кешу з даних"""
        if isinstance(data, str):
            key_data = data
        else:
            key_data = json.dumps(data, sort_keys=True)
        
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _get_cache_path(self, key: str) -> Path:
        """Get cache file path / Отримати шлях до файлу кешу"""
        return self.cache_dir / f"{key}.json"
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache / Отримати значення з кешу
        
        Args:
            key: Cache key / Ключ кешу
            
        Returns:
            Cached value or None / Кешоване значення або None
        """
        if not self.cache_enabled:
            return None
        
        try:
            cache_path = self._get_cache_path(key)
            if not cache_path.exists():
                return None
            
            # Check if cache is expired
            if time.time() - cache_path.stat().st_mtime > self.cache_ttl:
                cache_path.unlink()
                return None
            
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.debug(f"Cache hit for key: {key}")
                return data['value']
                
        except Exception as e:
            logger.warning(f"Cache read error for key {key}: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set value in cache / Встановити значення в кеш
        
        Args:
            key: Cache key / Ключ кешу
            value: Value to cache / Значення для кешування
            ttl: Time to live in seconds / Час життя в секундах
            
        Returns:
            Success status / Статус успіху
        """
        if not self.cache_enabled:
            return False
        
        try:
            cache_path = self._get_cache_path(key)
            cache_data = {
                'value': value,
                'timestamp': time.time(),
                'ttl': ttl or self.cache_ttl
            }
            
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            
            logger.debug(f"Cache set for key: {key}")
            return True
            
        except Exception as e:
            logger.warning(f"Cache write error for key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        Delete value from cache / Видалити значення з кешу
        
        Args:
            key: Cache key / Ключ кешу
            
        Returns:
            Success status / Статус успіху
        """
        try:
            cache_path = self._get_cache_path(key)
            if cache_path.exists():
                cache_path.unlink()
                logger.debug(f"Cache deleted for key: {key}")
                return True
            return False
        except Exception as e:
            logger.warning(f"Cache delete error for key {key}: {e}")
            return False
    
    def clear(self) -> bool:
        """
        Clear all cache / Очистити весь кеш
        
        Returns:
            Success status / Статус успіху
        """
        try:
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
            logger.info("Cache cleared")
            return True
        except Exception as e:
            logger.warning(f"Cache clear error: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics / Отримати статистику кешу
        
        Returns:
            Cache statistics / Статистика кешу
        """
        if not self.cache_enabled:
            return {"enabled": False}
        
        try:
            cache_files = list(self.cache_dir.glob("*.json"))
            total_size = sum(f.stat().st_size for f in cache_files)
            
            return {
                "enabled": True,
                "cache_dir": str(self.cache_dir),
                "file_count": len(cache_files),
                "total_size": total_size,
                "ttl": self.cache_ttl
            }
        except Exception as e:
            logger.warning(f"Cache stats error: {e}")
            return {"enabled": False, "error": str(e)}


# Global cache instance
cache_manager = CacheManager()


def cached(ttl: Optional[int] = None, key_func=None):
    """
    Decorator for caching function results
    Декоратор для кешування результатів функцій
    
    Args:
        ttl: Time to live in seconds / Час життя в секундах
        key_func: Custom key generation function / Функція генерації ключа
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = cache_manager._generate_key({
                    'func': func.__name__,
                    'args': args,
                    'kwargs': kwargs
                })
            
            # Try to get from cache
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator


def get_cache() -> CacheManager:
    """Get global cache manager / Отримати глобальний менеджер кешу"""
    return cache_manager 