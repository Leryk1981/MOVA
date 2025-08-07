"""
Example usage of MOVA SDK
Приклад використання MOVA SDK
"""

import asyncio
from mova import (
    MovaEngine, Intent, Protocol, ToolAPI,
    MovaConfig, ConfigManager, get_config,
    create_http_client, create_async_http_client,
    generate_id, format_timestamp, cached,
    validate_email, validate_url
)


def basic_usage_example():
    """Basic SDK usage example / Базовий приклад використання SDK"""
    print("=== Basic MOVA SDK Usage ===")
    
    # Initialize engine
    engine = MovaEngine()
    
    # Create intent
    intent = Intent(
        name="greeting",
        patterns=["hello", "hi", "привіт"],
        priority=1,
        intent_type="greeting",
        response_template="Hello! How can I help you?"
    )
    
    # Add intent to engine
    engine.add_intent(intent)
    
    # Create session
    session = engine.create_session("user123")
    print(f"Created session: {session.session_id}")
    
    # Recognize intent
    recognized_intent = engine.recognize_intent("hello", session.session_id)
    if recognized_intent:
        print(f"Recognized intent: {recognized_intent.name}")
    
    print()


def configuration_example():
    """Configuration management example / Приклад управління конфігурацією"""
    print("=== Configuration Management ===")
    
    # Get global config
    config = get_config()
    print(f"Default language: {config.default_language}")
    print(f"API timeout: {config.api_timeout}")
    
    # Create custom config manager
    config_manager = ConfigManager()
    config_manager.update(
        debug_mode=True,
        verbose_output=True,
        api_timeout=60
    )
    
    print(f"Debug mode: {config_manager.get('debug_mode')}")
    print(f"API timeout: {config_manager.get('api_timeout')}")
    
    print()


def http_client_example():
    """HTTP client usage example / Приклад використання HTTP клієнта"""
    print("=== HTTP Client Usage ===")
    
    # Create HTTP client
    client = create_http_client(
        base_url="https://api.example.com",
        headers={"Authorization": "Bearer token123"}
    )
    
    # Make request (this would fail in example, but shows usage)
    try:
        # response = client.get("/users", params={"limit": 10})
        # print(f"Response: {response}")
        print("HTTP client configured successfully")
    except Exception as e:
        print(f"HTTP request failed (expected): {e}")
    
    print()


async def async_http_client_example():
    """Async HTTP client usage example / Приклад використання асинхронного HTTP клієнта"""
    print("=== Async HTTP Client Usage ===")
    
    async with create_async_http_client(
        base_url="https://api.example.com",
        headers={"Authorization": "Bearer token123"}
    ) as client:
        try:
            # response = await client.get("/users", params={"limit": 10})
            # print(f"Async response: {response}")
            print("Async HTTP client configured successfully")
        except Exception as e:
            print(f"Async HTTP request failed (expected): {e}")
    
    print()


def utility_functions_example():
    """Utility functions usage example / Приклад використання утилітарних функцій"""
    print("=== Utility Functions ===")
    
    # Generate ID
    session_id = generate_id("session")
    print(f"Generated session ID: {session_id}")
    
    # Format timestamp
    timestamp = format_timestamp()
    print(f"Current timestamp: {timestamp}")
    
    # Validate email
    email = "user@example.com"
    is_valid = validate_email(email)
    print(f"Email {email} is valid: {is_valid}")
    
    # Validate URL
    url = "https://api.example.com/v1/users"
    is_valid = validate_url(url)
    print(f"URL {url} is valid: {is_valid}")
    
    print()


@cached(ttl=300)  # Cache for 5 minutes
def expensive_operation(data: str) -> str:
    """Example of cached function / Приклад кешованої функції"""
    print(f"Performing expensive operation with: {data}")
    return f"Processed: {data}"


def caching_example():
    """Caching usage example / Приклад використання кешування"""
    print("=== Caching Example ===")
    
    # First call - will execute
    result1 = expensive_operation("test_data")
    print(f"First result: {result1}")
    
    # Second call - will use cache
    result2 = expensive_operation("test_data")
    print(f"Second result: {result2}")
    
    print()


def protocol_example():
    """Protocol creation example / Приклад створення протоколу"""
    print("=== Protocol Creation ===")
    
    from mova import Protocol, ProtocolStep, ActionType, Condition, ComparisonOperator
    
    # Create protocol steps
    step1 = ProtocolStep(
        id="greet",
        action=ActionType.PROMPT,
        prompt="Hello! Welcome to our service."
    )
    
    step2 = ProtocolStep(
        id="check_user",
        action=ActionType.CONDITION,
        conditions=[
            Condition(
                variable="user_type",
                operator=ComparisonOperator.EQUALS,
                value="premium"
            )
        ]
    )
    
    step3 = ProtocolStep(
        id="end",
        action=ActionType.END
    )
    
    # Create protocol
    protocol = Protocol(
        name="welcome_protocol",
        steps=[step1, step2, step3],
        description="Welcome protocol for new users"
    )
    
    print(f"Created protocol: {protocol.name}")
    print(f"Number of steps: {len(protocol.steps)}")
    
    print()


def main():
    """Main example function / Основна функція прикладу"""
    print("MOVA SDK Usage Examples")
    print("=" * 50)
    
    # Run examples
    basic_usage_example()
    configuration_example()
    http_client_example()
    utility_functions_example()
    caching_example()
    protocol_example()
    
    # Run async example
    asyncio.run(async_http_client_example())
    
    print("All examples completed!")


if __name__ == "__main__":
    main() 