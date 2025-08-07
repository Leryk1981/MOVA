"""
Async Command Line Interface for MOVA language
Асинхронний інтерфейс командного рядка для мови MOVA
"""

import asyncio
import click
import json
import os
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from loguru import logger

from ..core.async_engine import create_async_mova_engine, AsyncMovaEngine
from ..core.models import ProtocolStep
from ..parser.json_parser import MovaJsonParser
from ..parser.yaml_parser import MovaYamlParser
from ..validator.schema_validator import MovaSchemaValidator
from ..validator.advanced_validator import MovaAdvancedValidator
from ..ml.integration import MLIntegration
from ..webhook_integration import get_webhook_integration
from ..redis_manager import get_redis_manager
from ..cache import get_cache
from ..config import get_config_value, set_config_value


console = Console()


@click.group()
@click.version_option(version="2.2.0", prog_name="Async MOVA")
@click.option('--redis-url', default=None, help='Redis connection URL / URL підключення до Redis')
@click.option('--llm-api-key', default=None, help='OpenRouter API key / OpenRouter API ключ')
@click.option('--llm-model', default='openai/gpt-3.5-turbo', help='LLM model to use / Модель LLM для використання')
@click.option('--llm-temperature', default=0.7, type=float, help='LLM temperature (0.0-2.0) / Температура LLM')
@click.option('--llm-max-tokens', default=1000, type=int, help='LLM max tokens / Максимальна кількість токенів')
@click.option('--llm-timeout', default=30, type=int, help='LLM timeout in seconds / Таймаут LLM в секундах')
@click.option('--webhook-enabled', is_flag=True, help='Enable webhook integration / Увімкнути інтеграцію webhook')
@click.option('--cache-enabled', is_flag=True, help='Enable caching / Увімкнути кешування')
@click.option('--ml-enabled', is_flag=True, help='Enable ML integration / Увімкнути ML інтеграцію')
@click.pass_context
def async_main(ctx, redis_url, llm_api_key, llm_model, llm_temperature, llm_max_tokens, llm_timeout,
               webhook_enabled, cache_enabled, ml_enabled):
    """
    Async MOVA - Machine-Operable Verbal Actions
    
    A declarative language for LLM interactions with async support
    Декларативна мова для взаємодії з LLM з асинхронною підтримкою
    """
    # Store global options in context
    ctx.ensure_object(dict)
    ctx.obj['redis_url'] = redis_url
    ctx.obj['llm_api_key'] = llm_api_key
    ctx.obj['llm_model'] = llm_model
    ctx.obj['llm_temperature'] = llm_temperature
    ctx.obj['llm_max_tokens'] = llm_max_tokens
    ctx.obj['llm_timeout'] = llm_timeout
    ctx.obj['webhook_enabled'] = webhook_enabled
    ctx.obj['cache_enabled'] = cache_enabled
    ctx.obj['ml_enabled'] = ml_enabled
    
    # Initialize integrations based on flags
    if webhook_enabled:
        set_config_value("webhook_enabled", True)
    if cache_enabled:
        set_config_value("cache_enabled", True)
    if ml_enabled:
        set_config_value("ml_enabled", True)


@async_main.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--validate', is_flag=True, help='Validate file schema / Валідувати схему файлу')
@click.option('--output', '-o', type=click.Path(), help='Output file path / Шлях до вихідного файлу')
def parse(file_path, validate, output):
    """Parse MOVA file asynchronously / Парсити MOVA файл асинхронно"""
    asyncio.run(_async_parse(file_path, validate, output))


async def _async_parse(file_path, validate, output):
    """Async parse implementation / Асинхронна реалізація парсингу"""
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
        await display_parsed_data_async(data)
        
        # Export if output specified
        if output:
            export_data(data, output, parser)
            
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        logger.error(f"Async CLI parse error: {e}")


@async_main.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--advanced', '-a', is_flag=True, help='Use advanced validation / Використовувати розширену валідацію')
@click.option('--detailed', '-d', is_flag=True, help='Show detailed validation report / Показати детальний звіт валідації')
@click.option('--output', '-o', type=click.Path(), help='Save validation report to file / Зберегти звіт валідації в файл')
def validate(file_path, advanced, detailed, output):
    """Validate MOVA file schema asynchronously / Валідувати схему MOVA файлу асинхронно"""
    asyncio.run(_async_validate(file_path, advanced, detailed, output))


async def _async_validate(file_path, advanced, detailed, output):
    """Async validate implementation / Асинхронна реалізація валідації"""
    try:
        file_path = Path(file_path)
        
        # Choose parser based on file extension
        if file_path.suffix.lower() in ['.yaml', '.yml']:
            parser = MovaYamlParser()
        else:
            parser = MovaJsonParser()
        
        # Parse file
        data = parser.parse_file(str(file_path))
        
        if advanced:
            # Use advanced validator
            validator = MovaAdvancedValidator()
            validator.validate_mova_structure(data)
            validator.validate_unique_ids(data)
            validator.validate_references(data)
            validator.validate_step_consistency(data)
            validator.validate_api_endpoints(data)
            
            report = validator.generate_validation_report()
            
            if detailed:
                display_advanced_validation_report(report)
            else:
                display_validation_summary(report)
            
            if output:
                save_validation_report(report, output)
            
            if validator.is_valid:
                console.print(Panel("✅ Advanced validation passed", style="green"))
            else:
                console.print(Panel("❌ Advanced validation failed", style="red"))
                return 1
        else:
            # Use basic validator
            validator = MovaSchemaValidator()
            is_valid, errors = validator.validate_mova_file(data)
            
            if is_valid:
                console.print(Panel("✅ Basic validation passed", style="green"))
            else:
                console.print(Panel("❌ Basic validation failed", style="red"))
                if errors:
                    for error in errors:
                        console.print(f"  • {error}", style="red")
                return 1
        
        return 0
        
    except Exception as e:
        console.print(f"❌ Validation error: {e}", style="red")
        logger.error(f"Async CLI validation error: {e}")
        return 1


@async_main.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--session-id', help='Session ID / ID сесії')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output / Детальний вивід')
@click.option('--step-by-step', is_flag=True, help='Execute step by step with confirmation / Виконувати покроково з підтвердженням')
@click.pass_context
def run(ctx, file_path, session_id, verbose, step_by_step):
    """Run MOVA file asynchronously / Запустити MOVA файл асинхронно"""
    asyncio.run(_async_run(ctx, file_path, session_id, verbose, step_by_step))


async def _async_run(ctx, file_path, session_id, verbose, step_by_step):
    """Async run implementation / Асинхронна реалізація запуску"""
    try:
        file_path = Path(file_path)
        
        # Choose parser based on file extension
        if file_path.suffix.lower() in ['.yaml', '.yml']:
            parser = MovaYamlParser()
        else:
            parser = MovaJsonParser()
        
        # Parse file
        data = parser.parse_file(str(file_path))
        
        # Create async engine
        engine = await create_async_mova_engine(
            redis_url=ctx.obj.get('redis_url'),
            llm_api_key=ctx.obj.get('llm_api_key'),
            llm_model=ctx.obj.get('llm_model')
        )
        
        try:
            # Initialize integrations
            webhook_integration = get_webhook_integration()
            cache_manager = get_cache()
            ml_integration = MLIntegration() if ctx.obj.get('ml_enabled') else None
            
            # Load data to engine
            load_data_to_engine(engine, data)
            
            # Create or use existing session
            if not session_id:
                session = engine.create_session("async_user")
                session_id = session.session_id
            else:
                session_data = engine.get_session_data(session_id)
                if not session_data:
                    session = engine.create_session("async_user")
                    session_id = session.session_id
            
            if verbose:
                console.print(f"Using session: {session_id}")
                console.print(f"Redis URL: {ctx.obj.get('redis_url') or 'In-memory'}")
                console.print(f"LLM Model: {ctx.obj.get('llm_model') or 'Mock'}")
                console.print(f"Webhook enabled: {ctx.obj.get('webhook_enabled')}")
                console.print(f"Cache enabled: {ctx.obj.get('cache_enabled')}")
                console.print(f"ML enabled: {ctx.obj.get('ml_enabled')}")
            
            # Execute protocols
            results = []
            for protocol in data.get("protocols", []):
                if verbose:
                    console.print(f"Executing protocol: {protocol['name']}")
                
                # Trigger webhook event
                webhook_integration.trigger_validation_event("started", {
                    "protocol": protocol['name'],
                    "session_id": session_id
                })
                
                if step_by_step:
                    result = await execute_protocol_step_by_step_async(engine, protocol, session_id, verbose)
                else:
                    result = await engine.execute_protocol(protocol['name'], session_id)
                
                results.append(result)
                
                # Trigger webhook event
                if "error" in result:
                    webhook_integration.trigger_validation_event("failed", {
                        "protocol": protocol['name'],
                        "session_id": session_id,
                        "error": result.get("error")
                    })
                else:
                    webhook_integration.trigger_validation_event("completed", {
                        "protocol": protocol['name'],
                        "session_id": session_id,
                        "result": result
                    })
                
                # Generate ML recommendations if enabled
                if ml_integration and "error" not in result:
                    recommendations = await ml_integration.generate_recommendations(
                        session_id=session_id,
                        protocol_name=protocol['name']
                    )
                    if recommendations:
                        display_recommendations(recommendations, verbose)
                
                if verbose:
                    display_execution_result(result)
            
            # Display final results
            if len(results) == 1:
                display_execution_result(results[0])
            else:
                console.print(f"Executed {len(results)} protocols")
            
        finally:
            # Cleanup
            await engine.cleanup()
            
    except Exception as e:
        console.print(f"❌ Execution error: {e}", style="red")
        logger.error(f"Async CLI execution error: {e}")


@async_main.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--step-id', help='Test specific step by ID / Тестувати конкретний крок за ID')
@click.option('--api-id', help='Test specific API by ID / Тестувати конкретний API за ID')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output / Детальний вивід')
@click.option('--dry-run', is_flag=True, help='Show what would be executed without running / Показати що буде виконано без запуску')
@click.pass_context
def test(ctx, file_path, step_id, api_id, verbose, dry_run):
    """Test MOVA components asynchronously / Тестувати компоненти MOVA асинхронно"""
    asyncio.run(_async_test(ctx, file_path, step_id, api_id, verbose, dry_run))


async def _async_test(ctx, file_path, step_id, api_id, verbose, dry_run):
    """Async test implementation / Асинхронна реалізація тестування"""
    try:
        file_path = Path(file_path)
        
        # Choose parser based on file extension
        if file_path.suffix.lower() in ['.yaml', '.yml']:
            parser = MovaYamlParser()
        else:
            parser = MovaJsonParser()
        
        # Parse file
        data = parser.parse_file(str(file_path))
        
        # Create async engine
        engine = await create_async_mova_engine(
            redis_url=ctx.obj.get('redis_url'),
            llm_api_key=ctx.obj.get('llm_api_key'),
            llm_model=ctx.obj.get('llm_model')
        )
        
        try:
            # Load data to engine
            load_data_to_engine(engine, data)
            
            if step_id:
                await test_specific_step_async(engine, data, step_id, verbose, dry_run)
            elif api_id:
                await test_specific_api_async(engine, data, api_id, verbose, dry_run)
            else:
                await test_all_components_async(engine, data, verbose, dry_run)
                
        finally:
            # Cleanup
            await engine.cleanup()
            
    except Exception as e:
        console.print(f"❌ Test error: {e}", style="red")
        logger.error(f"Async CLI test error: {e}")


async def test_specific_step_async(engine: AsyncMovaEngine, data: dict, step_id: str, verbose: bool, dry_run: bool):
    """Test specific step asynchronously / Тестувати конкретний крок асинхронно"""
    console.print(f"Testing step: {step_id}")
    
    for protocol in data.get("protocols", []):
        for step in protocol.get("steps", []):
            if step.get("id") == step_id:
                if dry_run:
                    console.print(f"Would test step: {step}")
                else:
                    session = engine.create_session("test_user")
                    try:
                        result = await engine._execute_step(step, session)
                        if verbose:
                            console.print(f"Step result: {result}")
                        else:
                            console.print(f"✅ Step {step_id} executed successfully")
                    except Exception as e:
                        console.print(f"❌ Step {step_id} failed: {e}", style="red")
                return
    
    console.print(f"❌ Step {step_id} not found", style="red")


async def test_specific_api_async(engine: AsyncMovaEngine, data: dict, api_id: str, verbose: bool, dry_run: bool):
    """Test specific API asynchronously / Тестувати конкретний API асинхронно"""
    console.print(f"Testing API: {api_id}")
    
    for tool in data.get("tools", []):
        if tool.get("id") == api_id:
            if dry_run:
                console.print(f"Would test API: {tool}")
            else:
                session = engine.create_session("test_user")
                try:
                    result = await engine._execute_async_api_call(tool, {})
                    if verbose:
                        console.print(f"API result: {result}")
                    else:
                        console.print(f"✅ API {api_id} executed successfully")
                except Exception as e:
                    console.print(f"❌ API {api_id} failed: {e}", style="red")
            return
    
    console.print(f"❌ API {api_id} not found", style="red")


async def test_all_components_async(engine: AsyncMovaEngine, data: dict, verbose: bool, dry_run: bool):
    """Test all components asynchronously / Тестувати всі компоненти асинхронно"""
    console.print("Testing all components...")
    
    # Test intents
    for intent in data.get("intents", []):
        if dry_run:
            console.print(f"Would test intent: {intent['name']}")
        else:
            try:
                engine.add_intent(intent)
                console.print(f"✅ Intent {intent['name']} added successfully")
            except Exception as e:
                console.print(f"❌ Intent {intent['name']} failed: {e}", style="red")
    
    # Test protocols
    for protocol in data.get("protocols", []):
        if dry_run:
            console.print(f"Would test protocol: {protocol['name']}")
        else:
            try:
                engine.add_protocol(protocol)
                console.print(f"✅ Protocol {protocol['name']} added successfully")
            except Exception as e:
                console.print(f"❌ Protocol {protocol['name']} failed: {e}", style="red")
    
    # Test tools
    for tool in data.get("tools", []):
        if dry_run:
            console.print(f"Would test tool: {tool['id']}")
        else:
            try:
                engine.add_tool(tool)
                console.print(f"✅ Tool {tool['id']} added successfully")
            except Exception as e:
                console.print(f"❌ Tool {tool['id']} failed: {e}", style="red")
    
    console.print("Component testing completed")


async def execute_protocol_step_by_step_async(engine: AsyncMovaEngine, protocol: dict, session_id: str, verbose: bool):
    """Execute protocol step by step asynchronously / Виконати протокол покроково асинхронно"""
    console.print(f"Executing protocol '{protocol['name']}' step by step...")
    
    result = {
        "protocol_name": protocol['name'],
        "session_id": session_id,
        "steps_executed": [],
        "success": True
    }
    
    for i, step in enumerate(protocol.get("steps", []), 1):
        console.print(f"\nStep {i}/{len(protocol['steps'])}: {step.get('id', 'unknown')}")
        console.print(f"Action: {step.get('action', 'unknown')}")
        
        if verbose:
            console.print(f"Step details: {step}")
        
        # Ask for confirmation
        if not click.confirm("Continue to next step?"):
            console.print("Execution cancelled by user")
            break
        
        try:
            step_result = await engine._execute_step(step, engine.sessions[session_id])
            result["steps_executed"].append({
                "step_id": step.get("id"),
                "action": step.get("action"),
                "result": step_result
            })
            
            if verbose:
                console.print(f"Step result: {step_result}")
            else:
                console.print(f"✅ Step completed")
            
            if step.get("action") == "end":
                console.print("Protocol completed")
                break
                
        except Exception as e:
            console.print(f"❌ Step failed: {e}", style="red")
            result["success"] = False
            result["error"] = str(e)
            break
    
    return result


async def display_parsed_data_async(data: dict):
    """Display parsed data asynchronously / Відобразити парсені дані асинхронно"""
    console.print("\n📄 Parsed MOVA Data:")
    
    # Display intents
    if data.get("intents"):
        table = Table(title="Intents")
        table.add_column("Name", style="cyan")
        table.add_column("Patterns", style="green")
        table.add_column("Priority", style="yellow")
        
        for intent in data["intents"]:
            table.add_row(
                intent.get("name", ""),
                ", ".join(intent.get("patterns", [])),
                str(intent.get("priority", ""))
            )
        console.print(table)
    
    # Display protocols
    if data.get("protocols"):
        table = Table(title="Protocols")
        table.add_column("Name", style="cyan")
        table.add_column("Description", style="green")
        table.add_column("Steps", style="yellow")
        
        for protocol in data["protocols"]:
            table.add_row(
                protocol.get("name", ""),
                protocol.get("description", ""),
                str(len(protocol.get("steps", [])))
            )
        console.print(table)
    
    # Display tools
    if data.get("tools"):
        table = Table(title="Tools")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Method", style="yellow")
        table.add_column("Endpoint", style="blue")
        
        for tool in data["tools"]:
            table.add_row(
                tool.get("id", ""),
                tool.get("name", ""),
                tool.get("method", ""),
                tool.get("endpoint", "")
            )
        console.print(table)


def display_validation_summary(report: dict):
    """Display validation summary / Відобразити підсумок валідації"""
    console.print(f"\n📊 Validation Summary:")
    console.print(f"✅ Valid: {report['is_valid']}")
    console.print(f"❌ Errors: {len(report['errors'])}")
    console.print(f"⚠️  Warnings: {len(report['warnings'])}")
    
    if report['stats']:
        console.print(f"\n📈 Statistics:")
        for key, value in report['stats'].items():
            console.print(f"  {key}: {value}")


def display_advanced_validation_report(report: dict):
    """Display advanced validation report / Відобразити розширений звіт валідації"""
    console.print(f"\n🔍 Advanced Validation Report:")
    console.print(f"✅ Valid: {report['is_valid']}")
    console.print(f"❌ Errors: {len(report['errors'])}")
    console.print(f"⚠️  Warnings: {len(report['warnings'])}")
    
    if report['errors']:
        console.print(f"\n❌ Errors:")
        for error in report['errors']:
            console.print(f"  • {error['field']}: {error['message']}")
    
    if report['warnings']:
        console.print(f"\n⚠️  Warnings:")
        for warning in report['warnings']:
            console.print(f"  • {warning['field']}: {warning['message']}")
    
    if report['stats']:
        console.print(f"\n📈 Statistics:")
        for key, value in report['stats'].items():
            console.print(f"  {key}: {value}")
    
    if report['recommendations']:
        console.print(f"\n💡 Recommendations:")
        for recommendation in report['recommendations']:
            console.print(f"  • {recommendation}")


def save_validation_report(report: dict, output_path: str):
    """Save validation report to file / Зберегти звіт валідації у файл"""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        console.print(f"✅ Validation report saved to {output_path}")
    except Exception as e:
        console.print(f"❌ Failed to save validation report: {e}", style="red")


def display_execution_result(result: dict):
    """Display execution result / Відобразити результат виконання"""
    console.print(f"\n🎯 Execution Result:")
    console.print(f"Protocol: {result.get('protocol_name', 'Unknown')}")
    console.print(f"Session: {result.get('session_id', 'Unknown')}")
    console.print(f"Success: {result.get('success', False)}")
    
    if result.get('error'):
        console.print(f"Error: {result['error']}", style="red")
    
    if result.get('steps_executed'):
        console.print(f"Steps executed: {len(result['steps_executed'])}")
    
    if result.get('final_result'):
        console.print(f"Final result: {result['final_result']}")


def export_data(data: dict, output_path: str, parser):
    """Export data to file / Експортувати дані у файл"""
    try:
        if output_path.endswith('.json'):
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        elif output_path.endswith(('.yaml', '.yml')):
            import yaml
            with open(output_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
        
        console.print(f"✅ Data exported to {output_path}")
    except Exception as e:
        console.print(f"❌ Failed to export data: {e}", style="red")


def load_data_to_engine(engine: AsyncMovaEngine, data: dict):
    """Load data to engine / Завантажити дані до движка"""
    # Load intents
    for intent_data in data.get("intents", []):
        try:
            from ..core.models import Intent
            intent = Intent(**intent_data)
            engine.add_intent(intent)
        except Exception as e:
            logger.warning(f"Failed to load intent {intent_data.get('name', 'unknown')}: {e}")
    
    # Load protocols
    for protocol_data in data.get("protocols", []):
        try:
            from ..core.models import Protocol
            protocol = Protocol(**protocol_data)
            engine.add_protocol(protocol)
        except Exception as e:
            logger.warning(f"Failed to load protocol {protocol_data.get('name', 'unknown')}: {e}")
    
    # Load tools
    for tool_data in data.get("tools", []):
        try:
            from ..core.models import ToolAPI
            tool = ToolAPI(**tool_data)
            engine.add_tool(tool)
        except Exception as e:
            logger.warning(f"Failed to load tool {tool_data.get('id', 'unknown')}: {e}")


# New async commands for Redis management
@async_main.command()
@click.option('--redis-url', default='redis://localhost:6379', help='Redis connection URL / URL підключення до Redis')
@click.option('--session-id', help='Specific session ID to show / Конкретний ID сесії для показу')
@click.option('--pattern', default='mova:session:*', help='Session pattern to list / Патерн сесій для списку')
@click.pass_context
def redis_sessions(ctx, redis_url, session_id, pattern):
    """Manage Redis sessions asynchronously / Керувати сесіями Redis асинхронно"""
    asyncio.run(_async_redis_sessions(ctx, redis_url, session_id, pattern))


async def _async_redis_sessions(ctx, redis_url, session_id, pattern):
    """Async Redis sessions management / Асинхронне керування сесіями Redis"""
    try:
        redis_manager = get_redis_manager(redis_url)
        
        if not redis_manager.is_connected():
            console.print("❌ Failed to connect to Redis", style="red")
            return
        
        if session_id:
            # Show specific session
            session_data = redis_manager.get_session_data(session_id)
            if session_data:
                console.print(Panel(f"Session: {session_id}", style="blue"))
                console.print(json.dumps(session_data, indent=2, ensure_ascii=False))
            else:
                console.print(f"❌ Session {session_id} not found", style="red")
        else:
            # List all sessions
            sessions = redis_manager.list_sessions(pattern)
            if sessions:
                table = Table(title="Redis Sessions")
                table.add_column("Session ID", style="cyan")
                table.add_column("TTL", style="yellow")
                table.add_column("Created", style="green")
                
                for session in sessions:
                    session_info = redis_manager.get_session_info(session)
                    if session_info:
                        table.add_row(
                            session_info.get('session_id', 'Unknown'),
                            str(session_info.get('ttl', 'Unknown')),
                            session_info.get('created_at', 'Unknown')
                        )
                
                console.print(table)
            else:
                console.print("ℹ️  No sessions found")
                
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        logger.error(f"Async Redis sessions error: {e}")


@async_main.command()
@click.option('--redis-url', default='redis://localhost:6379', help='Redis connection URL / URL підключення до Redis')
@click.option('--session-id', help='Session ID to delete / ID сесії для видалення')
@click.option('--pattern', default='mova:session:*', help='Session pattern to clear / Патерн сесій для очищення')
@click.option('--confirm', is_flag=True, help='Confirm deletion / Підтвердити видалення')
@click.pass_context
def redis_clear(ctx, redis_url, session_id, pattern, confirm):
    """Clear Redis sessions asynchronously / Очистити сесії Redis асинхронно"""
    asyncio.run(_async_redis_clear(ctx, redis_url, session_id, pattern, confirm))


async def _async_redis_clear(ctx, redis_url, session_id, pattern, confirm):
    """Async Redis clear implementation / Асинхронна реалізація очищення Redis"""
    try:
        redis_manager = get_redis_manager(redis_url)
        
        if not redis_manager.is_connected():
            console.print("❌ Failed to connect to Redis", style="red")
            return
        
        if session_id:
            # Delete specific session
            if not confirm and not click.confirm(f"Delete session {session_id}?"):
                return
            
            if redis_manager.delete_session(session_id):
                console.print(f"✅ Session {session_id} deleted", style="green")
            else:
                console.print(f"❌ Failed to delete session {session_id}", style="red")
        else:
            # Clear all sessions
            if not confirm and not click.confirm(f"Clear all sessions matching pattern '{pattern}'?"):
                return
            
            if redis_manager.clear_all_sessions(pattern):
                console.print(f"✅ All sessions cleared", style="green")
            else:
                console.print("❌ Failed to clear sessions", style="red")
                
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        logger.error(f"Async Redis clear error: {e}")


# New async commands for cache management
@async_main.command()
@click.option('--key', help='Specific cache key to show / Конкретний ключ кешу для показу')
@click.option('--stats', is_flag=True, help='Show cache statistics / Показати статистику кешу')
def cache_info(key, stats):
    """Show cache information asynchronously / Показати інформацію про кеш асинхронно"""
    asyncio.run(_async_cache_info(key, stats))


async def _async_cache_info(key, stats):
    """Async cache info implementation / Асинхронна реалізація інформації про кеш"""
    try:
        cache_manager = get_cache()
        
        if key:
            # Show specific cache entry
            value = cache_manager.get(key)
            if value is not None:
                console.print(Panel(f"Cache Key: {key}", style="blue"))
                console.print(json.dumps(value, indent=2, ensure_ascii=False))
            else:
                console.print(f"❌ Cache key '{key}' not found", style="red")
        elif stats:
            # Show cache statistics
            stats_data = cache_manager.get_stats()
            console.print(Panel("Cache Statistics", style="blue"))
            
            table = Table()
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="yellow")
            
            for metric, value in stats_data.items():
                table.add_row(metric, str(value))
            
            console.print(table)
        else:
            console.print("ℹ️  Use --key to show specific cache entry or --stats for statistics")
            
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        logger.error(f"Async cache info error: {e}")


@async_main.command()
@click.option('--key', help='Specific cache key to delete / Конкретний ключ кешу для видалення')
@click.option('--confirm', is_flag=True, help='Confirm deletion / Підтвердити видалення')
def cache_clear(key, confirm):
    """Clear cache asynchronously / Очистити кеш асинхронно"""
    asyncio.run(_async_cache_clear(key, confirm))


async def _async_cache_clear(key, confirm):
    """Async cache clear implementation / Асинхронна реалізація очищення кешу"""
    try:
        cache_manager = get_cache()
        
        if key:
            # Delete specific cache entry
            if not confirm and not click.confirm(f"Delete cache key '{key}'?"):
                return
            
            if cache_manager.delete(key):
                console.print(f"✅ Cache key '{key}' deleted", style="green")
            else:
                console.print(f"❌ Failed to delete cache key '{key}'", style="red")
        else:
            # Clear all cache
            if not confirm and not click.confirm("Clear all cache?"):
                return
            
            if cache_manager.clear():
                console.print("✅ All cache cleared", style="green")
            else:
                console.print("❌ Failed to clear cache", style="red")
                
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        logger.error(f"Async cache clear error: {e}")


# New async commands for webhook management
@async_main.command()
@click.option('--url', required=True, help='Webhook URL / URL webhook')
@click.option('--event-type', required=True, help='Event type / Тип події')
@click.option('--data', help='Event data (JSON) / Дані події (JSON)')
def webhook_test(url, event_type, data):
    """Test webhook endpoint asynchronously / Тестувати webhook endpoint асинхронно"""
    asyncio.run(_async_webhook_test(url, event_type, data))


async def _async_webhook_test(url, event_type, data):
    """Async webhook test implementation / Асинхронна реалізація тестування webhook"""
    try:
        from ..webhook import trigger_webhook_event, WebhookEventType
        
        # Parse event data if provided
        event_data = None
        if data:
            try:
                event_data = json.loads(data)
            except json.JSONDecodeError:
                console.print("❌ Invalid JSON data", style="red")
                return
        
        # Map event type to enum
        event_map = {
            "validation_started": WebhookEventType.VALIDATION_STARTED,
            "validation_completed": WebhookEventType.VALIDATION_COMPLETED,
            "validation_failed": WebhookEventType.VALIDATION_FAILED,
            "cache_updated": WebhookEventType.CACHE_UPDATED,
            "cache_cleared": WebhookEventType.CACHE_CLEARED,
            "redis_connected": WebhookEventType.REDIS_CONNECTED,
            "redis_disconnected": WebhookEventType.REDIS_DISCONNECTED,
            "llm_request_started": WebhookEventType.LLM_REQUEST_STARTED,
            "llm_request_completed": WebhookEventType.LLM_REQUEST_COMPLETED,
            "llm_request_failed": WebhookEventType.LLM_REQUEST_FAILED,
            "ml_intent_recognized": WebhookEventType.ML_INTENT_RECOGNIZED,
            "ml_entity_extracted": WebhookEventType.ML_ENTITY_EXTRACTED,
            "ml_prediction_made": WebhookEventType.ML_PREDICTION_MADE
        }
        
        webhook_event = event_map.get(event_type)
        if not webhook_event:
            console.print(f"❌ Unknown event type: {event_type}", style="red")
            console.print(f"Available types: {list(event_map.keys())}")
            return
        
        # Trigger webhook
        trigger_webhook_event(webhook_event, event_data)
        console.print(f"✅ Webhook event '{event_type}' triggered", style="green")
        
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        logger.error(f"Async webhook test error: {e}")


@async_main.command()
def webhook_status():
    """Show webhook status asynchronously / Показати статус webhook асинхронно"""
    asyncio.run(_async_webhook_status())


async def _async_webhook_status():
    """Async webhook status implementation / Асинхронна реалізація статусу webhook"""
    try:
        webhook_integration = get_webhook_integration()
        
        console.print(Panel("Webhook Status", style="blue"))
        console.print(f"Enabled: {webhook_integration._enabled}")
        
        if webhook_integration._enabled:
            webhook_manager = webhook_integration.webhook_manager
            if webhook_manager:
                console.print(f"Manager initialized: {webhook_manager is not None}")
                # Add more status information as needed
            else:
                console.print("Manager not initialized")
        else:
            console.print("Webhook integration is disabled")
            
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        logger.error(f"Async webhook status error: {e}")


# New async commands for ML management
@async_main.command()
@click.option('--model-id', help='Specific model ID to show / Конкретний ID моделі для показу')
@click.option('--list-models', is_flag=True, help='List all available models / Показати всі доступні моделі')
def ml_models(model_id, list_models):
    """Show ML models information asynchronously / Показати інформацію про ML моделі асинхронно"""
    asyncio.run(_async_ml_models(model_id, list_models))


async def _async_ml_models(model_id, list_models):
    """Async ML models implementation / Асинхронна реалізація ML моделей"""
    try:
        ml_integration = MLIntegration()
        
        if model_id:
            # Show specific model info
            model_info = ml_integration.get_model_info(model_id)
            if model_info:
                console.print(Panel(f"Model: {model_id}", style="blue"))
                console.print(json.dumps(model_info, indent=2, ensure_ascii=False))
            else:
                console.print(f"❌ Model '{model_id}' not found", style="red")
        elif list_models:
            # List all models
            models = ml_integration.list_available_models()
            if models:
                table = Table(title="Available ML Models")
                table.add_column("Model ID", style="cyan")
                table.add_column("Type", style="yellow")
                table.add_column("Status", style="green")
                
                for model in models:
                    table.add_row(
                        model.get('id', 'Unknown'),
                        model.get('type', 'Unknown'),
                        model.get('status', 'Unknown')
                    )
                
                console.print(table)
            else:
                console.print("ℹ️  No models found")
        else:
            console.print("ℹ️  Use --model-id to show specific model or --list-models for all models")
            
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        logger.error(f"Async ML models error: {e}")


@async_main.command()
@click.option('--model-id', required=True, help='Model ID to evaluate / ID моделі для оцінки')
@click.option('--test-data', required=True, type=click.Path(exists=True), help='Test data file / Файл тестових даних')
@click.option('--output', '-o', type=click.Path(), help='Save evaluation results to file / Зберегти результати оцінки в файл')
def ml_evaluate(model_id, test_data, output):
    """Evaluate ML model asynchronously / Оцінити ML модель асинхронно"""
    asyncio.run(_async_ml_evaluate(model_id, test_data, output))


async def _async_ml_evaluate(model_id, test_data, output):
    """Async ML evaluate implementation / Асинхронна реалізація оцінки ML"""
    try:
        # Load test data
        with open(test_data, 'r', encoding='utf-8') as f:
            test_data_list = json.load(f)
        
        ml_integration = MLIntegration()
        
        console.print(f"🔍 Evaluating model: {model_id}")
        console.print(f"📊 Test data: {len(test_data_list)} examples")
        
        # Run evaluation
        result = await ml_integration.evaluate_model(model_id, test_data_list)
        
        # Display results
        console.print(Panel("Model Evaluation Results", style="blue"))
        console.print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # Export if specified
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            console.print(f"✅ Results exported to: {output}", style="green")
            
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        logger.error(f"Async ML evaluate error: {e}")


@async_main.command()
def ml_status():
    """Show ML system status asynchronously / Показати статус ML системи асинхронно"""
    asyncio.run(_async_ml_status())


async def _async_ml_status():
    """Async ML status implementation / Асинхронна реалізація статусу ML"""
    try:
        ml_integration = MLIntegration()
        
        status = ml_integration.get_system_status()
        
        console.print(Panel("ML System Status", style="blue"))
        
        table = Table()
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="yellow")
        table.add_column("Details", style="green")
        
        for component, info in status.items():
            table.add_row(
                component,
                info.get('status', 'Unknown'),
                str(info.get('details', ''))
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        logger.error(f"Async ML status error: {e}")


def display_recommendations(recommendations, verbose=False):
    """Display ML recommendations / Відобразити ML рекомендації"""
    if not recommendations:
        console.print("ℹ️  No recommendations available")
        return
    
    console.print(Panel("🤖 AI Recommendations", style="cyan"))
    
    for i, rec in enumerate(recommendations, 1):
        # Color based on priority
        priority_colors = {
            "critical": "red",
            "high": "yellow", 
            "medium": "blue",
            "low": "green"
        }
        color = priority_colors.get(rec.priority.value, "white")
        
        console.print(f"{i}. [{rec.priority.value.upper()}] {rec.title}", style=color)
        console.print(f"   Type: {rec.type.value}")
        console.print(f"   Description: {rec.description}")
        
        if verbose and rec.details:
            console.print(f"   Details: {rec.details}")
        
        if rec.suggestions:
            console.print("   Suggestions:")
            for suggestion in rec.suggestions:
                console.print(f"     • {suggestion}")
        
        console.print()  # Empty line for readability


def display_recommendation_summary(summary):
    """Display recommendation summary / Відобразити підсумок рекомендацій"""
    console.print(Panel("📊 Recommendation Summary", style="cyan"))
    
    # Overall statistics
    if "total_recommendations" in summary:
        console.print(f"Total recommendations: {summary['total_recommendations']}")
    
    # By priority
    if "by_priority" in summary:
        console.print("\nBy Priority:")
        for priority, count in summary["by_priority"].items():
            console.print(f"  {priority}: {count}")
    
    # By type
    if "by_type" in summary:
        console.print("\nBy Type:")
        for rec_type, count in summary["by_type"].items():
            console.print(f"  {rec_type}: {count}")
    
    # Recent recommendations
    if "recent_recommendations" in summary:
        console.print(f"\nRecent recommendations: {len(summary['recent_recommendations'])}")
        for rec in summary["recent_recommendations"][:5]:  # Show last 5
            console.print(f"  • {rec['title']} ({rec['priority']})")


if __name__ == "__main__":
    async_main() 