"""
Tests for MOVA Engine
Тести для MOVA Engine
"""

import pytest
from datetime import datetime
from src.mova.core.engine import MovaEngine
from src.mova.core.models import (
    Intent, Protocol, ToolAPI, ProtocolStep, Condition,
    IntentType, ActionType, ComparisonOperator
)


class TestMovaEngine:
    """Test MovaEngine functionality / Тест функціональності MovaEngine"""
    
    def setup_method(self):
        """Setup test environment / Налаштування тестового середовища"""
        self.engine = MovaEngine()
    
    def test_add_intent(self):
        """Test adding intent / Тест додавання наміру"""
        intent = Intent(
            name="test_intent",
            patterns=["test"],
            intent_type=IntentType.CUSTOM
        )
        
        result = self.engine.add_intent(intent)
        assert result is True
        assert "test_intent" in self.engine.intents
    
    def test_add_protocol(self):
        """Test adding protocol / Тест додавання протоколу"""
        step = ProtocolStep(
            id="test_step",
            action=ActionType.PROMPT,
            prompt="Test prompt"
        )
        
        protocol = Protocol(
            name="test_protocol",
            steps=[step]
        )
        
        result = self.engine.add_protocol(protocol)
        assert result is True
        assert "test_protocol" in self.engine.protocols
    
    def test_add_tool(self):
        """Test adding tool / Тест додавання інструменту"""
        tool = ToolAPI(
            id="test_tool",
            name="Test Tool",
            endpoint="https://api.test.com",
            method="GET"
        )
        
        result = self.engine.add_tool(tool)
        assert result is True
        assert "test_tool" in self.engine.tools
    
    def test_create_session(self):
        """Test session creation / Тест створення сесії"""
        session = self.engine.create_session("test_user")
        
        assert session.user_id == "test_user"
        assert session.active is True
        assert session.session_id in self.engine.sessions
    
    def test_recognize_intent(self):
        """Test intent recognition / Тест розпізнавання наміру"""
        # Add test intent
        intent = Intent(
            name="greeting",
            patterns=["hello", "hi"],
            intent_type=IntentType.GREETING
        )
        self.engine.add_intent(intent)
        
        # Create session
        session = self.engine.create_session("test_user")
        
        # Test recognition
        recognized = self.engine.recognize_intent("hello", session.session_id)
        assert recognized is not None
        assert recognized.name == "greeting"
    
    def test_execute_protocol(self):
        """Test protocol execution / Тест виконання протоколу"""
        # Create test protocol
        step = ProtocolStep(
            id="greet",
            action=ActionType.PROMPT,
            prompt="Hello!"
        )
        
        protocol = Protocol(
            name="greeting_protocol",
            steps=[step]
        )
        self.engine.add_protocol(protocol)
        
        # Create session
        session = self.engine.create_session("test_user")
        
        # Execute protocol
        result = self.engine.execute_protocol("greeting_protocol", session.session_id)
        assert result is not None
        assert "protocol" in result
        assert "steps_executed" in result
    
    def test_session_data_management(self):
        """Test session data management / Тест управління даними сесії"""
        session = self.engine.create_session("test_user")
        
        # Test getting session data
        data = self.engine.get_session_data(session.session_id)
        assert data is not None
        
        # Test updating session data
        test_data = {"key": "value"}
        result = self.engine.update_session_data(session.session_id, test_data)
        assert result is True
        
        # Verify data was updated
        updated_data = self.engine.get_session_data(session.session_id)
        assert updated_data["key"] == "value"
    
    def test_condition_evaluation(self):
        """Test condition evaluation / Тест оцінки умов"""
        condition = Condition(
            variable="test_var",
            operator=ComparisonOperator.EQUALS,
            value="test_value"
        )
        
        # Test equals condition
        result = self.engine._evaluate_condition(condition, "test_value")
        assert result is True
        
        # Test not equals condition
        condition.operator = ComparisonOperator.NOT_EQUALS
        result = self.engine._evaluate_condition(condition, "test_value")
        assert result is False
        
        # Test contains condition
        condition.operator = ComparisonOperator.CONTAINS
        result = self.engine._evaluate_condition(condition, "test_value_extra")
        assert result is True 