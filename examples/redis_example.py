#!/usr/bin/env python3
"""
Redis Integration Example for MOVA SDK
Приклад інтеграції Redis з MOVA SDK
"""

import json
from pathlib import Path
from src.mova.core.engine import MovaEngine
from src.mova.core.models import (
    Intent, Protocol, ToolAPI, ProtocolStep, Condition,
    IntentType, ActionType, ComparisonOperator
)
from src.mova.redis_manager import MovaRedisManager


def create_redis_example():
    """Create example with Redis integration / Створити приклад з Redis інтеграцією"""
    
    # Example data
    example_data = {
        "version": "2.2",
        "intents": [
            {
                "name": "order_pizza",
                "patterns": ["order pizza", "buy pizza", "want pizza"],
                "priority": 5,
                "intent_type": "command",
                "response_template": "Great! What kind of pizza would you like, {session.data.user_name}?"
            }
        ],
        "protocols": [
            {
                "name": "pizza_order",
                "description": "Pizza ordering protocol with Redis session storage",
                "steps": [
                    {
                        "id": "greet",
                        "action": "prompt",
                        "prompt": "Welcome to PizzaBot! What's your name?"
                    },
                    {
                        "id": "ask_pizza_type",
                        "action": "prompt",
                        "prompt": "Hello {session.data.user_name}! What type of pizza would you like?"
                    },
                    {
                        "id": "check_availability",
                        "action": "tool_api",
                        "tool_api_id": "pizza_api"
                    },
                    {
                        "id": "confirm_order",
                        "action": "prompt",
                        "prompt": "Perfect! Your {session.data.pizza_type} pizza is available. Confirm order?"
                    },
                    {
                        "id": "end",
                        "action": "end"
                    }
                ]
            }
        ],
        "tools": [
            {
                "id": "pizza_api",
                "name": "Pizza Availability API",
                "endpoint": "https://api.pizzashop.com/check",
                "method": "POST",
                "parameters": {
                    "pizza_type": "{session.data.pizza_type}"
                }
            }
        ]
    }
    
    return example_data


def run_redis_example():
    """Run Redis integration example / Запустити приклад Redis інтеграції"""
    
    print("🍕 MOVA SDK Redis Integration Example")
    print("=" * 50)
    
    # Create example data
    example_data = create_redis_example()
    
    # Initialize engine with Redis
    redis_url = "redis://localhost:6379"
    engine = MovaEngine(redis_url=redis_url)
    
    print(f"🔗 Connected to Redis: {redis_url}")
    
    # Load data into engine
    load_data_to_engine(engine, example_data)
    
    # Create session
    session = engine.create_session("test_user", ttl=1800)
    print(f"📝 Created session: {session.session_id}")
    
    # Simulate user interaction
    print("\n👤 Simulating user interaction...")
    
    # Step 1: User provides name
    user_name = "John"
    engine.update_session_data(session.session_id, {"user_name": user_name})
    print(f"✅ User name set: {user_name}")
    
    # Step 2: User chooses pizza type
    pizza_type = "Margherita"
    engine.update_session_data(session.session_id, {"pizza_type": pizza_type})
    print(f"✅ Pizza type set: {pizza_type}")
    
    # Step 3: Execute protocol
    print(f"\n🚀 Executing pizza order protocol...")
    result = engine.execute_protocol("pizza_order", session.session_id)
    
    # Display results
    print(f"\n📊 Execution Results:")
    print(f"  • Protocol: {result['protocol']}")
    print(f"  • Steps executed: {len(result['steps_executed'])}")
    
    for step_result in result['steps_executed']:
        print(f"  • Step {step_result['step_id']}: {step_result['action']}")
    
    # Show session data from Redis
    print(f"\n💾 Session data from Redis:")
    session_data = engine.get_session_data(session.session_id)
    for key, value in session_data.items():
        print(f"  • {key}: {value}")
    
    # Test Redis manager directly
    print(f"\n🔧 Testing Redis manager directly...")
    redis_manager = engine.redis_manager
    
    if redis_manager:
        # Get session info
        session_info = redis_manager.get_session_info(session.session_id)
        if session_info:
            print(f"  • Session TTL: {session_info.get('ttl')} seconds")
            print(f"  • Created at: {session_info.get('created_at')}")
        
        # List all sessions
        sessions = redis_manager.list_sessions()
        print(f"  • Total sessions in Redis: {len(sessions)}")
    
    print(f"\n✅ Redis integration example completed!")


def load_data_to_engine(engine: MovaEngine, data: dict):
    """Load data into engine / Завантажити дані в движок"""
    
    # Load intents
    if "intents" in data:
        for intent_data in data["intents"]:
            intent = Intent(
                name=intent_data["name"],
                patterns=intent_data["patterns"],
                priority=intent_data.get("priority", 0),
                intent_type=IntentType(intent_data.get("intent_type", "custom")),
                response_template=intent_data.get("response_template")
            )
            engine.add_intent(intent)
    
    # Load protocols
    if "protocols" in data:
        for protocol_data in data["protocols"]:
            steps = []
            for step_data in protocol_data.get("steps", []):
                step = ProtocolStep(
                    id=step_data["id"],
                    action=ActionType(step_data["action"]),
                    prompt=step_data.get("prompt"),
                    tool_api_id=step_data.get("tool_api_id")
                )
                steps.append(step)
            
            protocol = Protocol(
                name=protocol_data["name"],
                steps=steps,
                description=protocol_data.get("description")
            )
            engine.add_protocol(protocol)
    
    # Load tools
    if "tools" in data:
        for tool_data in data["tools"]:
            tool = ToolAPI(
                id=tool_data["id"],
                name=tool_data["name"],
                endpoint=tool_data["endpoint"],
                method=tool_data.get("method", "GET"),
                parameters=tool_data.get("parameters", {})
            )
            engine.add_tool(tool)


def test_redis_operations():
    """Test Redis operations / Тест операцій Redis"""
    
    print("\n🧪 Testing Redis Operations")
    print("-" * 30)
    
    try:
        # Initialize Redis manager
        redis_manager = MovaRedisManager("redis://localhost:6379")
        
        if not redis_manager.is_connected():
            print("❌ Failed to connect to Redis")
            return
        
        print("✅ Connected to Redis")
        
        # Test session operations
        session_id = "test_session_123"
        test_data = {
            "user_id": "test_user",
            "pizza_type": "Pepperoni",
            "order_count": 1
        }
        
        # Create session
        success = redis_manager.create_session(session_id, test_data, 3600)
        print(f"📝 Create session: {'✅' if success else '❌'}")
        
        # Get session data
        data = redis_manager.get_session_data(session_id)
        print(f"📖 Get session data: {'✅' if data else '❌'}")
        if data:
            print(f"   Data: {data}")
        
        # Update session data
        update_data = {"order_count": 2, "status": "confirmed"}
        success = redis_manager.update_session_data_batch(session_id, update_data)
        print(f"✏️ Update session data: {'✅' if success else '❌'}")
        
        # Get updated data
        updated_data = redis_manager.get_session_data(session_id)
        print(f"📖 Updated data: {updated_data}")
        
        # Get session info
        info = redis_manager.get_session_info(session_id)
        print(f"ℹ️ Session info: {info}")
        
        # List sessions
        sessions = redis_manager.list_sessions()
        print(f"📋 Total sessions: {len(sessions)}")
        
        # Clean up
        redis_manager.delete_session(session_id)
        print(f"🗑️ Cleanup: Session deleted")
        
    except Exception as e:
        print(f"❌ Redis test failed: {e}")


if __name__ == "__main__":
    # Test Redis operations first
    test_redis_operations()
    
    # Run main example
    run_redis_example() 