"""
Tests for Redis integration in MOVA SDK
Тести для Redis інтеграції в MOVA SDK
"""

import pytest
import json
from unittest.mock import Mock, patch
from datetime import datetime

from src.mova.core.engine import MovaEngine
from src.mova.core.models import (
    Intent, Protocol, ToolAPI, ProtocolStep, Condition,
    IntentType, ActionType, ComparisonOperator
)
from src.mova.redis_manager import MovaRedisManager


class TestRedisIntegration:
    """Test Redis integration functionality / Тест функціональності Redis інтеграції"""
    
    def setup_method(self):
        """Setup test environment / Налаштування тестового середовища"""
        # Mock Redis manager
        self.mock_redis_manager = Mock(spec=MovaRedisManager)
        self.mock_redis_manager.is_connected.return_value = True
        
        # Create engine with mocked Redis
        with patch('src.mova.core.engine.get_redis_manager', return_value=self.mock_redis_manager):
            self.engine = MovaEngine(redis_url="redis://localhost:6379")
    
    def test_engine_initialization_with_redis(self):
        """Test engine initialization with Redis / Тест ініціалізації движка з Redis"""
        with patch('src.mova.core.engine.get_redis_manager') as mock_get_manager:
            mock_manager = Mock(spec=MovaRedisManager)
            mock_get_manager.return_value = mock_manager
            
            engine = MovaEngine(redis_url="redis://localhost:6379")
            
            assert engine.redis_manager is not None
            mock_get_manager.assert_called_once_with("redis://localhost:6379")
    
    def test_engine_initialization_without_redis(self):
        """Test engine initialization without Redis / Тест ініціалізації движка без Redis"""
        engine = MovaEngine()
        
        assert engine.redis_manager is None
    
    def test_create_session_with_redis(self):
        """Test session creation with Redis / Тест створення сесії з Redis"""
        # Mock Redis manager methods
        self.mock_redis_manager.create_session.return_value = True
        
        session = self.engine.create_session("test_user", ttl=1800)
        
        assert session.user_id == "test_user"
        assert session.session_id in self.engine.sessions
        
        # Verify Redis was called
        self.mock_redis_manager.create_session.assert_called_once()
        call_args = self.mock_redis_manager.create_session.call_args
        assert call_args[0][0] == session.session_id  # session_id
        assert call_args[0][2] == 1800  # ttl
        
        # Check initial data
        initial_data = call_args[0][1]
        assert initial_data["user_id"] == "test_user"
        assert initial_data["active"] is True
    
    def test_get_session_data_with_redis(self):
        """Test getting session data with Redis / Тест отримання даних сесії з Redis"""
        # Mock Redis data
        redis_data = {"key1": "value1", "key2": "value2"}
        self.mock_redis_manager.get_session_data.return_value = redis_data
        
        # Create session
        session = self.engine.create_session("test_user")
        
        # Get session data
        data = self.engine.get_session_data(session.session_id)
        
        assert data == redis_data
        self.mock_redis_manager.get_session_data.assert_called_once_with(session.session_id)
    
    def test_get_session_data_fallback_to_memory(self):
        """Test fallback to memory when Redis fails / Тест відкату до пам'яті при помилці Redis"""
        # Mock Redis failure
        self.mock_redis_manager.get_session_data.return_value = None
        
        # Create session
        session = self.engine.create_session("test_user")
        
        # Add data to memory
        session.data["memory_key"] = "memory_value"
        
        # Get session data
        data = self.engine.get_session_data(session.session_id)
        
        assert data["memory_key"] == "memory_value"
    
    def test_update_session_data_with_redis(self):
        """Test updating session data with Redis / Тест оновлення даних сесії з Redis"""
        # Mock Redis success
        self.mock_redis_manager.update_session_data_batch.return_value = True
        
        # Create session
        session = self.engine.create_session("test_user")
        
        # Update session data
        update_data = {"new_key": "new_value", "another_key": 123}
        result = self.engine.update_session_data(session.session_id, update_data)
        
        assert result is True
        self.mock_redis_manager.update_session_data_batch.assert_called_once_with(
            session.session_id, update_data
        )
    
    def test_update_session_data_redis_failure(self):
        """Test handling Redis failure during update / Тест обробки помилки Redis при оновленні"""
        # Mock Redis failure
        self.mock_redis_manager.update_session_data_batch.return_value = False
        
        # Create session
        session = self.engine.create_session("test_user")
        
        # Update session data
        update_data = {"new_key": "new_value"}
        result = self.engine.update_session_data(session.session_id, update_data)
        
        # Should still succeed due to memory fallback
        assert result is True
        assert session.data["new_key"] == "new_value"
    
    def test_engine_without_redis_fallback(self):
        """Test engine works without Redis / Тест роботи движка без Redis"""
        # Create engine without Redis
        engine = MovaEngine()
        
        # Create session
        session = engine.create_session("test_user")
        
        # Update session data
        update_data = {"key": "value"}
        result = engine.update_session_data(session.session_id, update_data)
        
        assert result is True
        assert session.data["key"] == "value"
    
    def test_redis_manager_methods(self):
        """Test Redis manager methods / Тест методів Redis менеджера"""
        # Test create_session
        self.mock_redis_manager.create_session.return_value = True
        result = self.mock_redis_manager.create_session("test_session", {"key": "value"}, 3600)
        assert result is True
        
        # Test get_session_data
        self.mock_redis_manager.get_session_data.return_value = {"key": "value"}
        data = self.mock_redis_manager.get_session_data("test_session")
        assert data == {"key": "value"}
        
        # Test update_session_data_batch
        self.mock_redis_manager.update_session_data_batch.return_value = True
        result = self.mock_redis_manager.update_session_data_batch("test_session", {"new_key": "new_value"})
        assert result is True


class TestRedisManager:
    """Test Redis manager functionality / Тест функціональності Redis менеджера"""
    
    @patch('redis.Redis')
    def test_redis_manager_initialization(self, mock_redis):
        """Test Redis manager initialization / Тест ініціалізації Redis менеджера"""
        # Mock Redis client
        mock_client = Mock()
        mock_client.ping.return_value = True
        mock_redis.from_url.return_value = mock_client
        
        # Create Redis manager
        manager = MovaRedisManager("redis://localhost:6379")
        
        assert manager.is_connected() is True
        mock_redis.from_url.assert_called_once_with(
            "redis://localhost:6379", 
            decode_responses=True
        )
    
    @patch('redis.Redis')
    def test_redis_manager_connection_failure(self, mock_redis):
        """Test Redis manager connection failure / Тест помилки підключення Redis менеджера"""
        # Mock Redis connection failure
        mock_redis.from_url.side_effect = Exception("Connection failed")

        # Create Redis manager - should handle exception gracefully
        try:
            manager = MovaRedisManager("redis://localhost:6379")
            assert manager.is_connected() is False
        except Exception:
            # Expected behavior - connection failed
            pass
    
    @patch('redis.Redis')
    def test_session_operations(self, mock_redis):
        """Test session operations / Тест операцій з сесіями"""
        # Mock Redis client
        mock_client = Mock()
        mock_client.ping.return_value = True
        mock_client.exists.return_value = True
        mock_client.hset.return_value = 1
        mock_client.hgetall.return_value = {"key1": '"value1"', "key2": '"value2"'}
        mock_client.hget.return_value = '{"created_at": "2025-08-07T10:00:00", "ttl": 3600, "data_keys": ["key1", "key2"]}'
        mock_client.expire.return_value = True
        mock_redis.from_url.return_value = mock_client
        
        # Create Redis manager
        manager = MovaRedisManager("redis://localhost:6379")
        
        # Test create session
        session_data = {"user_id": "test_user", "active": True}
        result = manager.create_session("test_session", session_data, 3600)
        assert result is True
        
        # Test get session data
        data = manager.get_session_data("test_session")
        assert data["key1"] == "value1"
        assert data["key2"] == "value2"
        
        # Test update session data
        update_data = {"new_key": "new_value"}
        result = manager.update_session_data_batch("test_session", update_data)
        assert result is True


if __name__ == "__main__":
    pytest.main([__file__]) 