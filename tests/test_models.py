"""
Tests for MOVA data models
Тести для моделей даних MOVA
"""

import pytest
from datetime import datetime
from src.mova.core.models import (
    Intent, Protocol, ToolAPI, Instruction, Profile, 
    Session, Contract, ProtocolStep, Condition,
    IntentType, ActionType, ComparisonOperator
)


class TestIntent:
    """Test Intent model / Тест моделі Intent"""
    
    def test_intent_creation(self):
        """Test basic intent creation / Тест базового створення наміру"""
        intent = Intent(
            name="greeting",
            patterns=["hello", "hi"],
            priority=1,
            intent_type=IntentType.GREETING
        )
        
        assert intent.name == "greeting"
        assert intent.patterns == ["hello", "hi"]
        assert intent.priority == 1
        assert intent.intent_type == IntentType.GREETING
    
    def test_intent_with_template(self):
        """Test intent with response template / Тест наміру з шаблоном відповіді"""
        intent = Intent(
            name="weather",
            patterns=["weather", "погода"],
            response_template="The weather is {condition}"
        )
        
        assert intent.response_template == "The weather is {condition}"


class TestProtocol:
    """Test Protocol model / Тест моделі Protocol"""
    
    def test_protocol_creation(self):
        """Test basic protocol creation / Тест базового створення протоколу"""
        step = ProtocolStep(
            id="start",
            action=ActionType.PROMPT,
            prompt="Hello!"
        )
        
        protocol = Protocol(
            name="greeting_protocol",
            steps=[step],
            description="Simple greeting"
        )
        
        assert protocol.name == "greeting_protocol"
        assert len(protocol.steps) == 1
        assert protocol.steps[0].id == "start"
    
    def test_protocol_with_conditions(self):
        """Test protocol with conditions / Тест протоколу з умовами"""
        condition = Condition(
            variable="user_input",
            operator=ComparisonOperator.CONTAINS,
            value="hello"
        )
        
        step = ProtocolStep(
            id="check_input",
            action=ActionType.CONDITION,
            conditions=[condition]
        )
        
        protocol = Protocol(
            name="conditional_protocol",
            steps=[step]
        )
        
        assert len(protocol.steps[0].conditions) == 1
        assert protocol.steps[0].conditions[0].variable == "user_input"


class TestToolAPI:
    """Test ToolAPI model / Тест моделі ToolAPI"""
    
    def test_tool_creation(self):
        """Test basic tool creation / Тест базового створення інструменту"""
        tool = ToolAPI(
            id="weather_api",
            name="Weather Service",
            endpoint="https://api.weather.com/v1/current",
            method="GET",
            parameters={"key": "{API_KEY}", "q": "{city}"}
        )
        
        assert tool.id == "weather_api"
        assert tool.name == "Weather Service"
        assert tool.method == "GET"
        assert "key" in tool.parameters


class TestSession:
    """Test Session model / Тест моделі Session"""
    
    def test_session_creation(self):
        """Test session creation / Тест створення сесії"""
        session = Session(
            session_id="test_session",
            user_id="user123",
            start_time=datetime.now().isoformat(),
            data={"key": "value"},
            context={"language": "en"}
        )
        
        assert session.session_id == "test_session"
        assert session.user_id == "user123"
        assert session.data["key"] == "value"
        assert session.active is True


class TestProfile:
    """Test Profile model / Тест моделі Profile"""
    
    def test_profile_creation(self):
        """Test profile creation / Тест створення профілю"""
        profile = Profile(
            user_id="user123",
            name="John Doe",
            preferences={"theme": "dark"},
            language="en",
            timezone="UTC"
        )
        
        assert profile.user_id == "user123"
        assert profile.name == "John Doe"
        assert profile.language == "en"
        assert profile.preferences["theme"] == "dark"


class TestContract:
    """Test Contract model / Тест моделі Contract"""
    
    def test_contract_creation(self):
        """Test contract creation / Тест створення контракту"""
        contract = Contract(
            contract_id="contract_001",
            parties=["user1", "user2"],
            terms={"service": "weather_api"},
            valid_from=datetime.now().isoformat()
        )
        
        assert contract.contract_id == "contract_001"
        assert len(contract.parties) == 2
        assert contract.terms["service"] == "weather_api" 