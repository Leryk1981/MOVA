"""
Command Line Interface for MOVA language
Інтерфейс командного рядка для мови MOVA
"""

import click
import json
import os
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from loguru import logger

from ..core.engine import MovaEngine
from ..core.models import ProtocolStep
from ..parser.json_parser import MovaJsonParser
from ..parser.yaml_parser import MovaYamlParser
from ..validator.schema_validator import MovaSchemaValidator


console = Console()


@click.group()
@click.version_option(version="2.2.0", prog_name="MOVA")
@click.option('--redis-url', default=None, help='Redis connection URL / URL підключення до Redis')
@click.option('--llm-api-key', default=None, help='OpenRouter API key / OpenRouter API ключ')
@click.option('--llm-model', default='openai/gpt-3.5-turbo', help='LLM model to use / Модель LLM для використання')
@click.option('--llm-temperature', default=0.7, type=float, help='LLM temperature (0.0-2.0) / Температура LLM')
@click.option('--llm-max-tokens', default=1000, type=int, help='LLM max tokens / Максимальна кількість токенів')
@click.option('--llm-timeout', default=30, type=int, help='LLM timeout in seconds / Таймаут LLM в секундах')
@click.pass_context
def main(ctx, redis_url, llm_api_key, llm_model, llm_temperature, llm_max_tokens, llm_timeout):
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
    ctx.obj['llm_temperature'] = llm_temperature
    ctx.obj['llm_max_tokens'] = llm_max_tokens
    ctx.obj['llm_timeout'] = llm_timeout


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
                if errors:
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
@click.option('--advanced', '-a', is_flag=True, help='Use advanced validation / Використовувати розширену валідацію')
@click.option('--detailed', '-d', is_flag=True, help='Show detailed validation report / Показати детальний звіт валідації')
@click.option('--output', '-o', type=click.Path(), help='Save validation report to file / Зберегти звіт валідації в файл')
def validate(file_path, advanced, detailed, output):
    """Validate MOVA file schema / Валідувати схему MOVA файлу"""
    try:
        file_path = Path(file_path)
        
        # Choose parser based on file extension
        if file_path.suffix.lower() in ['.yaml', '.yml']:
            parser = MovaYamlParser()
        else:
            parser = MovaJsonParser()
        
        # Parse file
        data = parser.parse_file(str(file_path))
        
        # Validate schema
        validator = MovaSchemaValidator()
        
        if advanced:
            # Advanced validation
            try:
                report = validator.validate_mova_file_advanced(data)
                
                if detailed:
                    display_advanced_validation_report(report)
                else:
                    display_validation_summary(report)
                
                # Save report if requested
                if output:
                    save_validation_report(report, output)
            except Exception as e:
                console.print(f"❌ Advanced validation error: {e}", style="red")
                logger.error(f"Advanced validation error: {e}")
                
        else:
            # Basic validation
            is_valid, errors = validator.validate_mova_file(data)
            
            if is_valid:
                console.print(Panel("✅ File validation successful", style="green"))
            else:
                console.print(Panel("❌ File validation failed", style="red"))
                if errors:
                    for error in errors:
                        console.print(f"  • {error}", style="red")
        
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        logger.error(f"CLI validate error: {e}")


@main.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--session-id', help='Session ID / ID сесії')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output / Детальний вивід')
@click.option('--step-by-step', is_flag=True, help='Execute step by step with confirmation / Виконувати покроково з підтвердженням')
@click.pass_context
def run(ctx, file_path, session_id, verbose, step_by_step):
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
        
        # Update LLM configuration if provided
        if engine.llm_client:
            engine.llm_client.config.temperature = llm_temperature
            engine.llm_client.config.max_tokens = llm_max_tokens
            engine.llm_client.config.timeout = llm_timeout
        
        if redis_url:
            console.print(f"🔗 Using Redis: {redis_url}")
        else:
            console.print("💾 Using in-memory storage")
            
        if llm_api_key:
            console.print(f"🤖 Using LLM model: {llm_model}")
            console.print(f"🌡️  Temperature: {llm_temperature}")
            console.print(f"📝 Max tokens: {llm_max_tokens}")
            console.print(f"⏱️  Timeout: {llm_timeout}s")
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
                
                if step_by_step:
                    # Execute step by step
                    result = execute_protocol_step_by_step(engine, protocol, session_id, verbose)
                else:
                    # Execute normally
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


@main.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--step-id', help='Test specific step by ID / Тестувати конкретний крок за ID')
@click.option('--api-id', help='Test specific API by ID / Тестувати конкретний API за ID')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output / Детальний вивід')
@click.option('--dry-run', is_flag=True, help='Show what would be executed without running / Показати що буде виконано без запуску')
@click.pass_context
def test(ctx, file_path, step_id, api_id, verbose, dry_run):
    """Test MOVA file components / Тестувати компоненти MOVA файлу"""
    try:
        # Get global options from context
        redis_url = ctx.obj.get('redis_url')
        llm_api_key = ctx.obj.get('llm_api_key')
        llm_model = ctx.obj.get('llm_model')
        llm_temperature = ctx.obj.get('llm_temperature')
        llm_max_tokens = ctx.obj.get('llm_max_tokens')
        llm_timeout = ctx.obj.get('llm_timeout')
        
        file_path = Path(file_path)
        
        # Choose parser based on file extension
        if file_path.suffix.lower() in ['.yaml', '.yml']:
            parser = MovaYamlParser()
        else:
            parser = MovaJsonParser()
        
        # Parse file
        data = parser.parse_file(str(file_path))
        
        # Initialize engine
        engine = MovaEngine(
            redis_url=redis_url,
            llm_api_key=llm_api_key,
            llm_model=llm_model
        )
        
        console.print(Panel("🧪 MOVA Component Testing", style="blue"))
        
        if verbose:
            console.print(f"📁 File: {file_path}")
            console.print(f"🔗 Redis: {redis_url or 'In-memory'}")
            console.print(f"🤖 LLM: {llm_model or 'Mock'}")
        
        # Load data into engine
        load_data_to_engine(engine, data)
        
        # Test specific components
        if step_id:
            test_specific_step(engine, data, step_id, verbose, dry_run)
        elif api_id:
            test_specific_api(engine, data, api_id, verbose, dry_run)
        else:
            # Test all components
            test_all_components(engine, data, verbose, dry_run)
        
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        logger.error(f"CLI test error: {e}")


def test_specific_step(engine, data, step_id, verbose, dry_run):
    """Test a specific step / Тестувати конкретний крок"""
    console.print(f"\n🎯 Testing step: {step_id}")
    
    # Find step in protocols
    step_found = False
    for protocol in data.get("protocols", []):
        for step in protocol.get("steps", []):
            if step.get("id") == step_id:
                step_found = True
                console.print(f"📋 Found in protocol: {protocol.get('name')}")
                
                if dry_run:
                    console.print(f"🔍 Would test step: {step}")
                else:
                    # Create test session
                    session = engine.create_session("test_user")
                    
                    # Execute step
                    if step.get("action") == "prompt":
                        result = engine._execute_prompt_step(
                            ProtocolStep(**step), session
                        )
                        console.print(f"✅ Step result: {result}")
                    elif step.get("action") == "tool_api":
                        result = engine._execute_api_step(
                            ProtocolStep(**step), session
                        )
                        console.print(f"✅ API result: {result}")
                    else:
                        console.print(f"⚠️  Action type not supported for testing: {step.get('action')}")
                
                break
        if step_found:
            break
    
    if not step_found:
        console.print(f"❌ Step '{step_id}' not found in any protocol")


def test_specific_api(engine, data, api_id, verbose, dry_run):
    """Test a specific API / Тестувати конкретний API"""
    console.print(f"\n🔌 Testing API: {api_id}")
    
    # Find API in tools
    api_found = False
    for tool in data.get("tools", []):
        if tool.get("id") == api_id:
            api_found = True
            console.print(f"📋 Found API: {tool.get('name')}")
            console.print(f"🌐 Endpoint: {tool.get('endpoint')}")
            
            if dry_run:
                console.print(f"🔍 Would test API: {tool}")
            else:
                # Test API call
                try:
                    # Convert tool dict to ToolAPI object
                    from src.mova.core.models import ToolAPI
                    tool_obj = ToolAPI(**tool)
                    result = engine._execute_api_call(tool_obj, {})
                    console.print(f"✅ API test result: {result}")
                except Exception as e:
                    console.print(f"❌ API test failed: {e}")
            
            break
    
    if not api_found:
        console.print(f"❌ API '{api_id}' not found in tools")


def test_all_components(engine, data, verbose, dry_run):
    """Test all components / Тестувати всі компоненти"""
    console.print("\n🔍 Testing all components...")
    
    # Test intents
    intents = data.get("intents", [])
    console.print(f"📋 Intents: {len(intents)} found")
    for intent in intents:
        console.print(f"  • {intent.get('name')} ({len(intent.get('patterns', []))} patterns)")
    
    # Test protocols
    protocols = data.get("protocols", [])
    console.print(f"📋 Protocols: {len(protocols)} found")
    for protocol in protocols:
        steps = protocol.get("steps", [])
        console.print(f"  • {protocol.get('name')} ({len(steps)} steps)")
        if verbose:
            for step in steps:
                console.print(f"    - {step.get('id')}: {step.get('action')}")
    
    # Test tools
    tools = data.get("tools", [])
    console.print(f"🔌 Tools: {len(tools)} found")
    for tool in tools:
        console.print(f"  • {tool.get('name')} ({tool.get('method', 'GET')} {tool.get('endpoint')})")
    
    # Test LLM connection if available
    if engine.llm_client:
        console.print("\n🤖 Testing LLM connection...")
        try:
            if engine.llm_client.test_connection():
                console.print("✅ LLM connection successful")
            else:
                console.print("❌ LLM connection failed")
        except Exception as e:
            console.print(f"❌ LLM test error: {e}")
    
    # Test Redis connection if available
    if engine.redis_manager:
        console.print("\n🔗 Testing Redis connection...")
        try:
            if engine.redis_manager.is_connected():
                console.print("✅ Redis connection successful")
            else:
                console.print("❌ Redis connection failed")
        except Exception as e:
            console.print(f"❌ Redis test error: {e}")
    
    console.print("\n✅ Component testing completed")


def display_validation_summary(report: dict):
    """Display validation summary / Показати підсумок валідації"""
    console.print(Panel("🔍 MOVA Validation Summary", style="blue"))
    
    # Overall status
    if report["overall_valid"]:
        console.print("✅ Overall validation: PASSED", style="green")
    else:
        console.print("❌ Overall validation: FAILED", style="red")
    
    # Statistics
    stats = report["advanced_validation"]["summary"]["statistics"]
    console.print(f"📊 Components: {stats['intents']} intents, {stats['protocols']} protocols, {stats['tools']} tools")
    console.print(f"📋 Steps: {stats['steps']} total")
    
    # Issues
    total_errors = report["total_errors"]
    total_warnings = report["total_warnings"]
    
    if total_errors > 0:
        console.print(f"❌ Errors: {total_errors}", style="red")
    if total_warnings > 0:
        console.print(f"⚠️  Warnings: {total_warnings}", style="yellow")
    
    if total_errors == 0 and total_warnings == 0:
        console.print("🎉 No issues found!", style="green")


def display_advanced_validation_report(report: dict):
    """Display detailed validation report / Показати детальний звіт валідації"""
    console.print(Panel("🔍 MOVA Advanced Validation Report", style="blue"))
    
    # Basic validation
    basic = report["basic_validation"]
    if basic["is_valid"]:
        console.print("✅ Basic schema validation: PASSED", style="green")
    else:
        console.print("❌ Basic schema validation: FAILED", style="red")
        for error in basic["errors"]:
            console.print(f"  • {error}", style="red")
    
    # Advanced validation
    advanced = report["advanced_validation"]
    console.print(f"\n📊 Advanced Validation Statistics:")
    stats = advanced["summary"]["statistics"]
    console.print(f"  • Intents: {stats['intents']}")
    console.print(f"  • Protocols: {stats['protocols']}")
    console.print(f"  • Tools: {stats['tools']}")
    console.print(f"  • Steps: {stats['steps']}")
    console.print(f"  • Duplicates: {stats['duplicates']}")
    console.print(f"  • Invalid references: {stats['references']}")
    
    # Errors
    if advanced["errors"]:
        console.print(f"\n❌ Errors ({len(advanced['errors'])}):", style="red")
        for error in advanced["errors"]:
            console.print(f"  • {error['field']}: {error['message']}", style="red")
    
    # Warnings
    if advanced["warnings"]:
        console.print(f"\n⚠️  Warnings ({len(advanced['warnings'])}):", style="yellow")
        for warning in advanced["warnings"]:
            console.print(f"  • {warning['field']}: {warning['message']}", style="yellow")
    
    # Recommendations
    if advanced["recommendations"]:
        console.print(f"\n💡 Recommendations:", style="cyan")
        for rec in advanced["recommendations"]:
            console.print(f"  • {rec}", style="cyan")


def save_validation_report(report: dict, output_path: str):
    """Save validation report to file / Зберегти звіт валідації в файл"""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        console.print(f"📄 Validation report saved to: {output_path}", style="green")
    except Exception as e:
        console.print(f"❌ Failed to save report: {e}", style="red")


def execute_protocol_step_by_step(engine, protocol, session_id, verbose):
    """Execute protocol step by step with user confirmation / Виконати протокол покроково з підтвердженням користувача"""
    from rich.prompt import Confirm
    
    console.print(f"\n🎯 Step-by-step execution of protocol: {protocol['name']}")
    
    steps = protocol.get("steps", [])
    results = []
    
    for i, step in enumerate(steps, 1):
        console.print(f"\n📋 Step {i}/{len(steps)}: {step.get('id')} ({step.get('action')})")
        
        if verbose:
            console.print(f"   Details: {step}")
        
        # Ask for confirmation
        if not Confirm.ask(f"Execute step {i}?"):
            console.print("⏸️  Step skipped")
            continue
        
        try:
            # Execute step
            session = engine.sessions.get(session_id)
            if not session:
                console.print("❌ Session not found")
                break
            
            # Convert step dict to ProtocolStep object
            from src.mova.core.models import ProtocolStep
            step_obj = ProtocolStep(**step)
            
            # Execute step
            result = engine._execute_step(step_obj, session)
            results.append(result)
            
            console.print(f"✅ Step {i} completed: {result}")
            
            # Show session data if verbose
            if verbose:
                console.print(f"   Session data: {session.data}")
            
        except Exception as e:
            console.print(f"❌ Step {i} failed: {e}")
            results.append({"error": str(e)})
            
            if not Confirm.ask("Continue with next step?"):
                break
    
    return {
        "protocol": protocol['name'],
        "steps_executed": len(results),
        "results": results
    }


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