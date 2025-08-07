"""
Command Line Interface for MOVA language
Інтерфейс командного рядка для мови MOVA
"""

import click
import os
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from loguru import logger

from ..core.engine import MovaEngine
from ..parser.json_parser import MovaJsonParser
from ..parser.yaml_parser import MovaYamlParser
from ..validator.schema_validator import MovaSchemaValidator


console = Console()


@click.group()
@click.version_option(version="2.2.0", prog_name="MOVA")
@click.option('--redis-url', default=None, help='Redis connection URL / URL підключення до Redis')
@click.option('--llm-api-key', default=None, help='OpenRouter API key / OpenRouter API ключ')
@click.option('--llm-model', default='openai/gpt-3.5-turbo', help='LLM model to use / Модель LLM для використання')
@click.pass_context
def main(ctx, redis_url, llm_api_key, llm_model):
    """
    MOVA - Machine-Operable Verbal Actions
    
    A declarative language for LLM interactions
    Декларативна мова для взаємодії з LLM
    """
    # Store global options in context
    ctx.ensure_object(dict)
    ctx.obj['redis_url'] = redis_url
    ctx.obj['llm_api_key'] = llm_api_key
    ctx.obj['llm_model'] = llm_model


@main.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--validate', is_flag=True, help='Validate file schema / Валідувати схему файлу')
@click.option('--output', '-o', type=click.Path(), help='Output file path / Шлях до вихідного файлу')
def parse(file_path, validate, output):
    """Parse MOVA file / Парсити MOVA файл"""
    try:
        file_path = Path(file_path)
        
        # Choose parser based on file extension
        if file_path.suffix.lower() in ['.yaml', '.yml']:
            parser = MovaYamlParser()
        else:
            parser = MovaJsonParser()
        
        # Parse file
        data = parser.parse_file(str(file_path))
        
        # Validate if requested
        if validate:
            validator = MovaSchemaValidator()
            is_valid, errors = validator.validate_mova_file(data)
            
            if is_valid:
                console.print(Panel("✅ File validation successful", style="green"))
            else:
                console.print(Panel("❌ File validation failed", style="red"))
                for error in errors:
                    console.print(f"  • {error}", style="red")
        
        # Display parsed data
        display_parsed_data(data)
        
        # Export if output specified
        if output:
            export_data(data, output, parser)
            
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        logger.error(f"CLI parse error: {e}")


@main.command()
@click.argument('file_path', type=click.Path(exists=True))
def validate(file_path):
    """Validate MOVA file schema / Валідувати схему MOVA файлу"""
    try:
        file_path = Path(file_path)
        
        # Choose parser based on file extension
        if file_path.suffix.lower() in ['.yaml', '.yml']:
            parser = MovaYamlParser()
        else:
            parser = MovaJsonParser()
        
        # Parse and validate
        data = parser.parse_file(str(file_path))
        validator = MovaSchemaValidator()
        is_valid, errors = validator.validate_mova_file(data)
        
        if is_valid:
            console.print(Panel("✅ File is valid", style="green"))
        else:
            console.print(Panel("❌ File is invalid", style="red"))
            for error in errors:
                console.print(f"  • {error}", style="red")
                
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        logger.error(f"CLI validate error: {e}")


@main.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--session-id', help='Session ID / ID сесії')
@click.pass_context
def run(ctx, file_path, session_id):
    """Run MOVA file / Запустити MOVA файл"""
    # Get global options from context
    redis_url = ctx.obj.get('redis_url')
    llm_api_key = ctx.obj.get('llm_api_key')
    llm_model = ctx.obj.get('llm_model')
    
    try:
        file_path = Path(file_path)
        
        # Choose parser based on file extension
        if file_path.suffix.lower() in ['.yaml', '.yml']:
            parser = MovaYamlParser()
        else:
            parser = MovaJsonParser()
        
        # Parse file
        data = parser.parse_file(str(file_path))
        
        # Initialize engine with Redis and LLM if provided
        engine = MovaEngine(
            redis_url=redis_url,
            llm_api_key=llm_api_key,
            llm_model=llm_model
        )
        
        if redis_url:
            console.print(f"🔗 Using Redis: {redis_url}")
        else:
            console.print("💾 Using in-memory storage")
            
        if llm_api_key:
            console.print(f"🤖 Using LLM model: {llm_model}")
        else:
            console.print("🤖 Using mock LLM responses")
        
        # Load data into engine
        load_data_to_engine(engine, data)
        
        # Create session if not provided
        if not session_id:
            session_id = engine.create_session("default_user").session_id
        
        console.print(f"🚀 Running MOVA file with session: {session_id}")
        
        # Run protocols if available
        if data.get("protocols"):
            for protocol in data["protocols"]:
                console.print(f"📋 Executing protocol: {protocol['name']}")
                try:
                    result = engine.execute_protocol(protocol['name'], session_id)
                    display_execution_result(result)
                except Exception as e:
                    console.print(f"❌ Error executing protocol {protocol['name']}: {e}", style="red")
        else:
            console.print("ℹ️  No protocols found in file")
        
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        logger.error(f"CLI run error: {e}")


@main.command()
def init():
    """Initialize new MOVA project / Ініціалізувати новий проект MOVA"""
    try:
        # Create project structure
        create_project_structure()
        
        # Create example files
        create_example_files()
        
        console.print(Panel("✅ MOVA project initialized successfully", style="green"))
        console.print("📁 Project structure created:")
        console.print("  • src/mova/ - Source code")
        console.print("  • examples/ - Example files")
        console.print("  • schemas/ - JSON schemas")
        console.print("  • tests/ - Test files")
        
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        logger.error(f"CLI init error: {e}")


def display_parsed_data(data: dict):
    """Display parsed data in a nice format / Відобразити розпарсені дані в гарному форматі"""
    console.print(Panel("📊 Parsed MOVA Data", style="blue"))
    
    # Create summary table
    table = Table(title="File Summary")
    table.add_column("Component", style="cyan")
    table.add_column("Count", style="magenta")
    
    components = [
        ("Intents", "intents"),
        ("Protocols", "protocols"),
        ("Tools", "tools"),
        ("Instructions", "instructions"),
        ("Profiles", "profiles"),
        ("Sessions", "sessions"),
        ("Contracts", "contracts")
    ]
    
    for name, key in components:
        count = len(data.get(key, []))
        table.add_row(name, str(count))
    
    console.print(table)


def display_execution_result(result: dict):
    """Display execution result / Відобразити результат виконання"""
    if "error" in result:
        console.print(f"❌ Execution failed: {result['error']}", style="red")
    else:
        console.print(f"✅ Protocol '{result['protocol']}' executed successfully", style="green")
        console.print(f"📝 Steps executed: {len(result['steps_executed'])}")


def export_data(data: dict, output_path: str, parser):
    """Export data to file / Експортувати дані до файлу"""
    try:
        output_path = Path(output_path)
        
        if output_path.suffix.lower() in ['.yaml', '.yml']:
            success = parser.export_to_yaml(data, str(output_path))
        else:
            success = parser.export_to_json(data, str(output_path))
        
        if success:
            console.print(f"💾 Data exported to: {output_path}", style="green")
        else:
            console.print(f"❌ Failed to export data", style="red")
            
    except Exception as e:
        console.print(f"❌ Export error: {e}", style="red")


def load_data_to_engine(engine: MovaEngine, data: dict):
    """Load parsed data into engine / Завантажити розпарсені дані до движка"""
    console.print(f"📊 Loading data: {list(data.keys())}")
    
    # Load intents
    intents = data.get("intents") or []
    console.print(f"📋 Loading {len(intents)} intents")
    for intent_data in intents:
        from ..core.models import Intent, IntentType
        intent = Intent(
            name=intent_data["name"],
            patterns=intent_data["patterns"],
            priority=intent_data.get("priority", 0),
            response_template=intent_data.get("response_template"),
            intent_type=IntentType(intent_data.get("intent_type", "custom"))
        )
        engine.add_intent(intent)
    
    # Load protocols
    protocols = data.get("protocols") or []
    console.print(f"📋 Loading {len(protocols)} protocols")
    for protocol_data in protocols:
        from ..core.models import Protocol, ProtocolStep, ActionType, Condition, ComparisonOperator
        
        console.print(f"  📋 Loading protocol: {protocol_data.get('name', 'Unknown')}")
        steps = []
        steps_data = protocol_data.get("steps") or []
        console.print(f"    📋 Loading {len(steps_data)} steps")
        for step_data in steps_data:
            conditions = []
            conditions_data = step_data.get("conditions") or []
            for condition_data in conditions_data:
                condition = Condition(
                    variable=condition_data["variable"],
                    operator=ComparisonOperator(condition_data["operator"]),
                    value=condition_data["value"]
                )
                conditions.append(condition)
            
            step = ProtocolStep(
                id=step_data["id"],
                action=ActionType(step_data["action"]),
                prompt=step_data.get("prompt"),
                tool_api_id=step_data.get("tool_api_id"),
                conditions=conditions if conditions else None,
                next_step=step_data.get("next_step")
            )
            steps.append(step)
        
        protocol = Protocol(
            name=protocol_data["name"],
            steps=steps,
            description=protocol_data.get("description")
        )
        engine.add_protocol(protocol)
    
    # Load tools
    tools = data.get("tools") or []
    console.print(f"📋 Loading {len(tools)} tools")
    for tool_data in tools:
        from ..core.models import ToolAPI
        tool = ToolAPI(
            id=tool_data["id"],
            name=tool_data["name"],
            endpoint=tool_data["endpoint"],
            method=tool_data.get("method", "GET"),
            headers=tool_data.get("headers"),
            parameters=tool_data.get("parameters"),
            authentication=tool_data.get("authentication")
        )
        engine.add_tool(tool)


def create_project_structure():
    """Create project directory structure / Створити структуру директорій проекту"""
    directories = [
        "src/mova/core",
        "src/mova/parser", 
        "src/mova/validator",
        "src/mova/cli",
        "examples",
        "schemas",
        "tests",
        "docs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)


def create_example_files():
    """Create example MOVA files / Створити приклади MOVA файлів"""
    # Create example JSON file
    example_json = {
        "version": "2.0",
        "intents": [
            {
                "name": "greeting",
                "patterns": ["hello", "hi", "привіт"],
                "priority": 1,
                "intent_type": "greeting",
                "response_template": "Hello! How can I help you?"
            }
        ],
        "protocols": [
            {
                "name": "simple_conversation",
                "description": "Simple conversation protocol",
                "steps": [
                    {
                        "id": "start",
                        "action": "prompt",
                        "prompt": "Welcome to the conversation!"
                    },
                    {
                        "id": "end",
                        "action": "end"
                    }
                ]
            }
        ]
    }
    
    with open("examples/example.json", "w", encoding="utf-8") as f:
        import json
        json.dump(example_json, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main() 