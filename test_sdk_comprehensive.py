#!/usr/bin/env python3
"""
Comprehensive test script for MOVA SDK
Комплексний тестовий скрипт для MOVA SDK
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mova.core.models import (
    Intent, Protocol, ToolAPI, Instruction, Profile, 
    Session, Contract, ProtocolStep, Condition,
    IntentType, ActionType, ComparisonOperator
)
from mova.core.engine import MovaEngine
from mova.parser.json_parser import MovaJsonParser
from mova.config import get_config, set_config_value
from mova.utils import generate_id, format_timestamp


def test_basic_models():
    """Test basic model creation / Тест базового створення моделей"""
    print("🔧 Testing basic models...")
    
    # Test Intent
    intent = Intent(
        name="test_greeting",
        patterns=["hello", "hi", "привіт"],
        priority=1,
        intent_type=IntentType.GREETING,
        response_template="Привіт! Як справи?"
    )
    assert intent.name == "test_greeting"
    assert len(intent.patterns) == 3
    print("✅ Intent model works correctly")
    
    # Test Protocol
    step = ProtocolStep(
        id="greet",
        action=ActionType.PROMPT,
        prompt="Привіт! Радий вас бачити!"
    )
    
    protocol = Protocol(
        name="greeting_protocol",
        steps=[step],
        description="Simple greeting protocol"
    )
    assert protocol.name == "greeting_protocol"
    assert len(protocol.steps) == 1
    print("✅ Protocol model works correctly")
    
    # Test ToolAPI
    tool = ToolAPI(
        id="weather_api",
        name="Weather Service",
        endpoint="https://api.weather.com/v1/current",
        method="GET",
        parameters={"key": "{API_KEY}", "q": "{city}"}
    )
    assert tool.id == "weather_api"
    assert tool.method == "GET"
    print("✅ ToolAPI model works correctly")


def test_engine_functionality():
    """Test MovaEngine functionality / Тест функціональності MovaEngine"""
    print("\n🚀 Testing MovaEngine...")
    
    engine = MovaEngine()
    
    # Create test data
    intent = Intent(
        name="greeting",
        patterns=["hello", "hi"],
        intent_type=IntentType.GREETING
    )
    
    step = ProtocolStep(
        id="greet",
        action=ActionType.PROMPT,
        prompt="Hello!"
    )
    
    protocol = Protocol(
        name="greeting_protocol",
        steps=[step]
    )
    
    tool = ToolAPI(
        id="test_api",
        name="Test API",
        endpoint="https://api.test.com",
        method="GET"
    )
    
    # Add components to engine
    assert engine.add_intent(intent)
    assert engine.add_protocol(protocol)
    assert engine.add_tool(tool)
    print("✅ Engine components added successfully")
    
    # Test session creation
    session = engine.create_session("test_user")
    assert session.user_id == "test_user"
    assert session.active is True
    print("✅ Session creation works correctly")
    
    # Test intent recognition
    recognized_intent = engine.recognize_intent("hello", session.session_id)
    assert recognized_intent is not None
    assert recognized_intent.name == "greeting"
    print("✅ Intent recognition works correctly")


def test_json_parser():
    """Test JSON parser functionality / Тест функціональності JSON парсера"""
    print("\n📄 Testing JSON parser...")
    
    parser = MovaJsonParser()
    
    # Test data
    test_data = {
        "version": "2.0",
        "intents": [
            {
                "name": "test_intent",
                "patterns": ["test"],
                "intent_type": "custom"
            }
        ],
        "protocols": [
            {
                "name": "test_protocol",
                "steps": [
                    {
                        "id": "test_step",
                        "action": "prompt",
                        "prompt": "Test prompt"
                    }
                ]
            }
        ]
    }
    
    # Parse JSON string
    result = parser.parse_string(json.dumps(test_data))
    assert "intents" in result
    assert "protocols" in result
    assert len(result["intents"]) == 1
    assert len(result["protocols"]) == 1
    print("✅ JSON parser works correctly")


def test_configuration():
    """Test configuration management / Тест управління конфігурацією"""
    print("\n⚙️ Testing configuration...")
    
    # Get default config
    config = get_config()
    assert config.log_level == "INFO"
    assert config.cache_enabled is True
    print("✅ Default configuration loaded")
    
    # Test config modification
    set_config_value("log_level", "DEBUG")
    set_config_value("debug_mode", True)
    
    updated_config = get_config()
    assert updated_config.log_level == "DEBUG"
    assert updated_config.debug_mode is True
    print("✅ Configuration modification works correctly")


def test_utilities():
    """Test utility functions / Тест утилітних функцій"""
    print("\n🔧 Testing utilities...")
    
    # Test ID generation
    id1 = generate_id()
    id2 = generate_id()
    assert id1 != id2
    assert len(id1) > 0
    print("✅ ID generation works correctly")
    
    # Test timestamp formatting
    timestamp = format_timestamp()
    assert isinstance(timestamp, str)
    assert len(timestamp) > 0
    print("✅ Timestamp formatting works correctly")


def test_example_file():
    """Test parsing example file / Тест парсингу прикладу файлу"""
    print("\n📁 Testing example file parsing...")
    
    example_file = Path("examples/basic_example.json")
    if example_file.exists():
        parser = MovaJsonParser()
        result = parser.parse_file(str(example_file))
        
        assert "intents" in result
        assert "protocols" in result
        assert "tools" in result
        assert "profiles" in result
        
        print(f"✅ Example file parsed successfully:")
        print(f"   - Intents: {len(result['intents'])}")
        print(f"   - Protocols: {len(result['protocols'])}")
        print(f"   - Tools: {len(result['tools'])}")
        print(f"   - Profiles: {len(result['profiles'])}")
    else:
        print("⚠️ Example file not found")


def main():
    """Main test function / Основна тестова функція"""
    print("🧪 Starting comprehensive MOVA SDK tests...")
    print("=" * 50)
    
    try:
        test_basic_models()
        test_engine_functionality()
        test_json_parser()
        test_configuration()
        test_utilities()
        test_example_file()
        
        print("\n" + "=" * 50)
        print("🎉 All tests passed successfully!")
        print("✅ MOVA SDK is working correctly")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main()) 