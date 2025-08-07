"""
Redis Manager for MOVA SDK
Менеджер Redis для MOVA SDK
"""

import json
import logging
from typing import Dict, Any, Optional, Union
from datetime import datetime, timedelta
import redis

logger = logging.getLogger(__name__)


class MovaRedisManager:
    """
    Redis manager for MOVA session data
    Менеджер Redis для даних сесій MOVA
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379", decode_responses: bool = True):
        """
        Initialize Redis manager
        Ініціалізація менеджера Redis
        
        Args:
            redis_url: Redis connection URL / URL підключення до Redis
            decode_responses: Decode responses as strings / Декодувати відповіді як рядки
        """
        self.redis_url = redis_url
        self.decode_responses = decode_responses
        self.client = None
        self._connect()
    
    def _connect(self) -> bool:
        """
        Connect to Redis server
        Підключення до Redis сервера
        
        Returns:
            bool: Connection success / Успішність підключення
        """
        try:
            self.client = redis.Redis.from_url(
                self.redis_url, 
                decode_responses=self.decode_responses
            )
            # Test connection
            self.client.ping()
            logger.info(f"Connected to Redis at {self.redis_url}")
            return True
        except redis.RedisError as e:
            logger.error(f"Failed to connect to Redis: {str(e)}")
            return False
    
    def is_connected(self) -> bool:
        """
        Check if connected to Redis
        Перевірити підключення до Redis
        
        Returns:
            bool: Connection status / Статус підключення
        """
        try:
            if self.client:
                self.client.ping()
                return True
        except redis.RedisError:
            pass
        return False
    
    def create_session(self, session_id: str, data: Dict[str, Any], ttl: int = 3600) -> bool:
        """
        Create new session in Redis
        Створити нову сесію в Redis
        
        Args:
            session_id: Session identifier / Ідентифікатор сесії
            data: Session data / Дані сесії
            ttl: Time to live in seconds / Час життя в секундах
            
        Returns:
            bool: Success status / Статус успіху
        """
        try:
            redis_key = f"mova:session:{session_id}"
            
            # Store session data as JSON
            for key, value in data.items():
                self.client.hset(redis_key, key, json.dumps(value))
            
            # Set TTL
            self.client.expire(redis_key, ttl)
            
            # Store session metadata
            metadata = {
                "created_at": datetime.now().isoformat(),
                "ttl": ttl,
                "data_keys": list(data.keys())
            }
            self.client.hset(redis_key, "_metadata", json.dumps(metadata))
            
            logger.info(f"Session {session_id} created in Redis with TTL {ttl}s")
            return True
            
        except redis.RedisError as e:
            logger.error(f"Failed to create session {session_id}: {str(e)}")
            return False
    
    def get_session_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session data from Redis
        Отримати дані сесії з Redis
        
        Args:
            session_id: Session identifier / Ідентифікатор сесії
            
        Returns:
            Optional[Dict[str, Any]]: Session data or None / Дані сесії або None
        """
        try:
            redis_key = f"mova:session:{session_id}"
            
            if not self.client.exists(redis_key):
                logger.warning(f"Session {session_id} not found in Redis")
                return None
            
            # Get all session data
            data = {}
            session_data = self.client.hgetall(redis_key)
            
            for key, value in session_data.items():
                if key != "_metadata":
                    try:
                        data[key] = json.loads(value)
                    except json.JSONDecodeError:
                        data[key] = value
            
            logger.info(f"Retrieved session {session_id} data from Redis")
            return data
            
        except redis.RedisError as e:
            logger.error(f"Failed to get session {session_id} data: {str(e)}")
            return None
    
    def update_session_data(self, session_id: str, key: str, value: Any) -> bool:
        """
        Update specific session data
        Оновити конкретні дані сесії
        
        Args:
            session_id: Session identifier / Ідентифікатор сесії
            key: Data key / Ключ даних
            value: Data value / Значення даних
            
        Returns:
            bool: Success status / Статус успіху
        """
        try:
            redis_key = f"mova:session:{session_id}"
            
            if not self.client.exists(redis_key):
                logger.warning(f"Session {session_id} not found in Redis")
                return False
            
            # Update data
            self.client.hset(redis_key, key, json.dumps(value))
            
            # Update metadata
            metadata = self.client.hget(redis_key, "_metadata")
            if metadata:
                try:
                    meta = json.loads(metadata)
                    if key not in meta.get("data_keys", []):
                        meta["data_keys"].append(key)
                        self.client.hset(redis_key, "_metadata", json.dumps(meta))
                except json.JSONDecodeError:
                    pass
            
            logger.info(f"Updated session {session_id} data: {key} = {value}")
            return True
            
        except redis.RedisError as e:
            logger.error(f"Failed to update session {session_id} data: {str(e)}")
            return False
    
    def update_session_data_batch(self, session_id: str, data: Dict[str, Any]) -> bool:
        """
        Update multiple session data items
        Оновити кілька елементів даних сесії
        
        Args:
            session_id: Session identifier / Ідентифікатор сесії
            data: Data to update / Дані для оновлення
            
        Returns:
            bool: Success status / Статус успіху
        """
        try:
            redis_key = f"mova:session:{session_id}"
            
            if not self.client.exists(redis_key):
                logger.warning(f"Session {session_id} not found in Redis")
                return False
            
            # Update multiple data items
            for key, value in data.items():
                self.client.hset(redis_key, key, json.dumps(value))
            
            # Update metadata
            metadata = self.client.hget(redis_key, "_metadata")
            if metadata:
                try:
                    meta = json.loads(metadata)
                    for key in data.keys():
                        if key not in meta.get("data_keys", []):
                            meta["data_keys"].append(key)
                    self.client.hset(redis_key, "_metadata", json.dumps(meta))
                except json.JSONDecodeError:
                    pass
            
            logger.info(f"Updated session {session_id} with {len(data)} data items")
            return True
            
        except redis.RedisError as e:
            logger.error(f"Failed to update session {session_id} data batch: {str(e)}")
            return False
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete session from Redis
        Видалити сесію з Redis
        
        Args:
            session_id: Session identifier / Ідентифікатор сесії
            
        Returns:
            bool: Success status / Статус успіху
        """
        try:
            redis_key = f"mova:session:{session_id}"
            result = self.client.delete(redis_key)
            
            if result > 0:
                logger.info(f"Session {session_id} deleted from Redis")
                return True
            else:
                logger.warning(f"Session {session_id} not found in Redis")
                return False
                
        except redis.RedisError as e:
            logger.error(f"Failed to delete session {session_id}: {str(e)}")
            return False
    
    def get_session_ttl(self, session_id: str) -> Optional[int]:
        """
        Get session TTL
        Отримати TTL сесії
        
        Args:
            session_id: Session identifier / Ідентифікатор сесії
            
        Returns:
            Optional[int]: TTL in seconds or None / TTL в секундах або None
        """
        try:
            redis_key = f"mova:session:{session_id}"
            ttl = self.client.ttl(redis_key)
            
            if ttl > 0:
                return ttl
            elif ttl == -1:
                logger.info(f"Session {session_id} has no TTL set")
                return None
            else:
                logger.warning(f"Session {session_id} has expired")
                return 0
                
        except redis.RedisError as e:
            logger.error(f"Failed to get TTL for session {session_id}: {str(e)}")
            return None
    
    def extend_session_ttl(self, session_id: str, ttl: int) -> bool:
        """
        Extend session TTL
        Продовжити TTL сесії
        
        Args:
            session_id: Session identifier / Ідентифікатор сесії
            ttl: New TTL in seconds / Новий TTL в секундах
            
        Returns:
            bool: Success status / Статус успіху
        """
        try:
            redis_key = f"mova:session:{session_id}"
            
            if not self.client.exists(redis_key):
                logger.warning(f"Session {session_id} not found in Redis")
                return False
            
            self.client.expire(redis_key, ttl)
            logger.info(f"Extended session {session_id} TTL to {ttl}s")
            return True
            
        except redis.RedisError as e:
            logger.error(f"Failed to extend TTL for session {session_id}: {str(e)}")
            return False
    
    def list_sessions(self, pattern: str = "mova:session:*") -> list:
        """
        List all sessions matching pattern
        Список всіх сесій, що відповідають шаблону
        
        Args:
            pattern: Redis key pattern / Шаблон ключа Redis
            
        Returns:
            list: List of session IDs / Список ID сесій
        """
        try:
            keys = self.client.keys(pattern)
            session_ids = [key.split(":")[-1] for key in keys]
            logger.info(f"Found {len(session_ids)} sessions matching pattern {pattern}")
            return session_ids
            
        except redis.RedisError as e:
            logger.error(f"Failed to list sessions: {str(e)}")
            return []
    
    def clear_all_sessions(self, pattern: str = "mova:session:*") -> bool:
        """
        Clear all sessions matching pattern
        Очистити всі сесії, що відповідають шаблону
        
        Args:
            pattern: Redis key pattern / Шаблон ключа Redis
            
        Returns:
            bool: Success status / Статус успіху
        """
        try:
            keys = self.client.keys(pattern)
            if keys:
                self.client.delete(*keys)
                logger.info(f"Cleared {len(keys)} sessions matching pattern {pattern}")
            return True
            
        except redis.RedisError as e:
            logger.error(f"Failed to clear sessions: {str(e)}")
            return False
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed session information
        Отримати детальну інформацію про сесію
        
        Args:
            session_id: Session identifier / Ідентифікатор сесії
            
        Returns:
            Optional[Dict[str, Any]]: Session info or None / Інформація про сесію або None
        """
        try:
            redis_key = f"mova:session:{session_id}"
            
            if not self.client.exists(redis_key):
                return None
            
            # Get metadata
            metadata = self.client.hget(redis_key, "_metadata")
            ttl = self.client.ttl(redis_key)
            
            info = {
                "session_id": session_id,
                "ttl": ttl if ttl > 0 else None,
                "exists": True
            }
            
            if metadata:
                try:
                    meta = json.loads(metadata)
                    info.update(meta)
                except json.JSONDecodeError:
                    pass
            
            return info
            
        except redis.RedisError as e:
            logger.error(f"Failed to get session info for {session_id}: {str(e)}")
            return None
    
    def close(self):
        """
        Close Redis connection
        Закрити з'єднання з Redis
        """
        if self.client:
            self.client.close()
            logger.info("Redis connection closed")


# Global Redis manager instance
_redis_manager = None


def get_redis_manager(redis_url: str = "redis://localhost:6379") -> MovaRedisManager:
    """
    Get global Redis manager instance
    Отримати глобальний екземпляр менеджера Redis
    
    Args:
        redis_url: Redis connection URL / URL підключення до Redis
        
    Returns:
        MovaRedisManager: Redis manager instance / Екземпляр менеджера Redis
    """
    global _redis_manager
    
    if _redis_manager is None or not _redis_manager.is_connected():
        _redis_manager = MovaRedisManager(redis_url)
    
    return _redis_manager


def close_redis_manager():
    """
    Close global Redis manager
    Закрити глобальний менеджер Redis
    """
    global _redis_manager
    
    if _redis_manager:
        _redis_manager.close()
        _redis_manager = None 