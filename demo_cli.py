#!/usr/bin/env python3
"""
Demo script for MOVA CLI integration
Демонстраційний скрипт для показу інтеграції MOVA CLI
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def demo_cli_commands():
    """Demonstrate CLI commands"""
    print("🚀 MOVA CLI Integration Demo")
    print("=" * 50)
    
    try:
        # Import CLI modules
        from mova.cli.cli import main
        from mova.cli.async_cli import async_main
        
        print("✅ CLI modules imported successfully")
        
        # Show available commands
        print("\n📋 Available CLI Commands:")
        print("-" * 30)
        
        # Main CLI commands
        main_commands = [cmd.name for cmd in main.commands.values()]
        print("Main CLI Commands:")
        for cmd in sorted(main_commands):
            print(f"  • mova {cmd}")
        
        # Async CLI commands
        async_commands = [cmd.name for cmd in async_main.commands.values()]
        print("\nAsync CLI Commands:")
        for cmd in sorted(async_commands):
            print(f"  • async-mova {cmd}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import CLI modules: {e}")
        return False

def demo_integrations():
    """Demonstrate integrations"""
    print("\n🔧 Integration Demo:")
    print("-" * 30)
    
    try:
        # ML Integration
        from mova.ml.integration import MLIntegration
        ml = MLIntegration()
        models = ml.list_available_models()
        print(f"✅ ML Integration: {len(models)} models available")
        
        # Webhook Integration
        from mova.webhook_integration import get_webhook_integration
        webhook = get_webhook_integration()
        print(f"✅ Webhook Integration: {'Enabled' if webhook._enabled else 'Disabled'}")
        
        # Cache Integration
        from mova.cache import get_cache
        cache = get_cache()
        stats = cache.get_stats()
        print(f"✅ Cache Integration: {len(stats)} metrics available")
        
        # Redis Integration
        from mova.redis_manager import get_redis_manager
        redis_manager = get_redis_manager("redis://localhost:6379")
        connected = redis_manager.is_connected()
        print(f"✅ Redis Integration: {'Connected' if connected else 'Not connected (expected)'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration demo failed: {e}")
        return False

def demo_usage_examples():
    """Show usage examples"""
    print("\n📖 Usage Examples:")
    print("-" * 30)
    
    examples = [
        "Basic usage:",
        "  mova parse examples/basic_example.json",
        "  mova validate examples/basic_example.json --advanced",
        "  mova run examples/basic_example.json",
        "",
        "With integrations:",
        "  mova run protocol.json --redis-url redis://localhost:6379 --llm-api-key your-key --webhook-enabled --cache-enabled --ml-enabled",
        "",
        "Redis management:",
        "  mova redis-sessions --redis-url redis://localhost:6379",
        "  mova redis-clear --redis-url redis://localhost:6379 --confirm",
        "",
        "Cache management:",
        "  mova cache-info --stats",
        "  mova cache-clear --confirm",
        "",
        "Webhook testing:",
        "  mova webhook-test --url https://your-webhook.com --event-type validation_started",
        "  mova webhook-status",
        "",
        "ML operations:",
        "  mova ml-models --list-models",
        "  mova ml-evaluate --model-id intent_classifier --test-data test_data.json",
        "  mova ml-status",
        "",
        "AI analysis:",
        "  mova analyze protocol.json --verbose",
        "  mova diagnose 'Connection timeout' --output diagnosis.json",
        "  mova recommendations-summary --output summary.json",
        "",
        "Async CLI:",
        "  async-mova run protocol.json --redis-url redis://localhost:6379 --llm-api-key your-key --webhook-enabled --cache-enabled --ml-enabled"
    ]
    
    for example in examples:
        print(example)

def main():
    """Main demo function"""
    print("🎯 MOVA CLI Integration Completion Demo")
    print("=" * 60)
    
    # Test CLI commands
    if not demo_cli_commands():
        return 1
    
    # Test integrations
    if not demo_integrations():
        return 1
    
    # Show usage examples
    demo_usage_examples()
    
    print("\n" + "=" * 60)
    print("✅ CLI Integration Demo Completed Successfully!")
    print("\n📚 For detailed usage examples, see: examples/cli_usage_examples.md")
    print("📋 For integration report, see: CLI_INTEGRATION_COMPLETION_REPORT.md")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 