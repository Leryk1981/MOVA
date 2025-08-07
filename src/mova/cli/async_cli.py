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


console = Console()


@click.group()
@click.version_option(version="2.2.0", prog_name="Async MOVA")
@click.option('--redis-url', default=None, help='Redis connection URL / URL підключення до Redis')
@click.option('--llm-api-key', default=None, help='OpenRouter API key / OpenRouter API ключ')
@click.option('--llm-model', default='openai/gpt-3.5-turbo', help='LLM model to use / Модель LLM для використання')
@click.option('--llm-temperature', default=0.7, type=float, help='LLM temperature (0.0-2.0) / Температура LLM')
@click.option('--llm-max-tokens', default=1000, type=int, help='LLM max tokens / Максимальна кількість токенів')
@click.option('--llm-timeout', default=30, type=int, help='LLM timeout in seconds / Таймаут LLM в секундах')
@click.pass_context
def async_main(ctx, redis_url, llm_api_key, llm_model, llm_temperature, llm_max_tokens, llm_timeout):
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
            
            # Execute protocols
            results = []
            for protocol in data.get("protocols", []):
                if verbose:
                    console.print(f"Executing protocol: {protocol['name']}")
                
                if step_by_step:
                    result = await execute_protocol_step_by_step_async(engine, protocol, session_id, verbose)
                else:
                    result = await engine.execute_protocol(protocol['name'], session_id)
                
                results.append(result)
                
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


if __name__ == "__main__":
    async_main() 