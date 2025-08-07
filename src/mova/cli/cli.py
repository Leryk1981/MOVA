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
from ..ml.integration import MLIntegration
from ..webhook_integration import get_webhook_integration
from ..redis_manager import get_redis_manager
from ..cache import get_cache
from ..config import get_config_value, set_config_value


console = Console()


@click.group()
@click.version_option(version="2.2.0", prog_name="MOVA")
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
def main(ctx, redis_url, llm_api_key, llm_model, llm_temperature, llm_max_tokens, llm_timeout, 
         webhook_enabled, cache_enabled, ml_enabled):
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
    llm_temperature = ctx.obj.get('llm_temperature')
    llm_max_tokens = ctx.obj.get('llm_max_tokens')
    llm_timeout = ctx.obj.get('llm_timeout')
    
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
        
        # Initialize integrations
        webhook_integration = get_webhook_integration()
        cache_manager = get_cache()
        ml_integration = MLIntegration() if ctx.obj.get('ml_enabled') else None
        
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
        
        if ctx.obj.get('webhook_enabled'):
            console.print("🔗 Webhook integration enabled")
        
        if ctx.obj.get('cache_enabled'):
            console.print("💾 Caching enabled")
        
        if ctx.obj.get('ml_enabled'):
            console.print("🤖 ML integration enabled")
        
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
                
                # Trigger webhook event
                webhook_integration.trigger_validation_event("started", {
                    "protocol": protocol['name'],
                    "session_id": session_id
                })
                
                if step_by_step:
                    # Execute step by step
                    result = execute_protocol_step_by_step(engine, protocol, session_id, verbose)
                else:
                    # Execute normally
                    try:
                        result = engine.execute_protocol(protocol['name'], session_id)
                        display_execution_result(result)
                        
                        # Trigger webhook event
                        webhook_integration.trigger_validation_event("completed", {
                            "protocol": protocol['name'],
                            "session_id": session_id,
                            "result": result
                        })
                        
                        # Generate ML recommendations if enabled
                        if ml_integration:
                            recommendations = ml_integration.generate_recommendations(
                                session_id=session_id,
                                protocol_name=protocol['name']
                            )
                            if recommendations:
                                display_recommendations(recommendations, verbose)
                                
                    except Exception as e:
                        console.print(f"❌ Error executing protocol {protocol['name']}: {e}", style="red")
                        
                        # Trigger webhook event
                        webhook_integration.trigger_validation_event("failed", {
                            "protocol": protocol['name'],
                            "session_id": session_id,
                            "error": str(e)
                        })
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


@main.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--session-id', default='cli_session', help='Session ID for analysis / ID сесії для аналізу')
@click.option('--output', '-o', type=click.Path(), help='Save recommendations to file / Зберегти рекомендації в файл')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output / Детальний вивід')
@click.pass_context
def analyze(ctx, file_path, session_id, output, verbose):
    """Analyze MOVA file and generate AI recommendations / Аналізувати MOVA файл та генерувати AI-рекомендації"""
    import asyncio
    asyncio.run(_analyze_async(ctx, file_path, session_id, output, verbose))


async def _analyze_async(ctx, file_path, session_id, output, verbose):
    """Analyze MOVA file and generate AI recommendations / Аналізувати MOVA файл та генерувати AI-рекомендації"""
    try:
        file_path = Path(file_path)
        
        # Choose parser based on file extension
        if file_path.suffix.lower() in ['.yaml', '.yml']:
            parser = MovaYamlParser()
        else:
            parser = MovaJsonParser()
        
        # Parse file
        data = parser.parse_file(str(file_path))
        
        # Initialize ML integration
        ml_integration = MLIntegration()
        
        console.print(Panel("🤖 AI-Powered Analysis", style="blue"))
        console.print(f"📄 Analyzing file: {file_path}")
        console.print(f"🆔 Session ID: {session_id}")
        
        # Generate recommendations
        recommendations = []
        
        # Configuration analysis
        if verbose:
            console.print("\n🔧 Analyzing configuration...")
        config_recs = await ml_integration.analyze_configuration_recommendations(data, session_id)
        recommendations.extend(config_recs)
        
        # Code quality analysis
        if verbose:
            console.print("📝 Analyzing code quality...")
        quality_recs = await ml_integration.analyze_code_quality_recommendations(data, session_id)
        recommendations.extend(quality_recs)
        
        # Performance analysis (mock metrics for CLI)
        if verbose:
            console.print("⚡ Analyzing performance patterns...")
        perf_metrics = {
            "avg_response_time": 1.5,
            "memory_usage": 0.6,
            "error_rate": 0.02
        }
        perf_recs = await ml_integration.analyze_performance_recommendations(perf_metrics, session_id)
        recommendations.extend(perf_recs)
        
        # Display recommendations
        display_recommendations(recommendations, verbose)
        
        # Export if specified
        if output:
            success = await ml_integration.export_recommendations(recommendations, output)
            if success:
                console.print(f"✅ Recommendations exported to: {output}", style="green")
            else:
                console.print(f"❌ Failed to export recommendations", style="red")
        
        # Summary
        console.print(f"\n📊 Analysis Summary:")
        console.print(f"  • Total recommendations: {len(recommendations)}")
        
        by_priority = {}
        by_type = {}
        for rec in recommendations:
            by_priority[rec.priority.value] = by_priority.get(rec.priority.value, 0) + 1
            by_type[rec.type.value] = by_type.get(rec.type.value, 0) + 1
        
        console.print(f"  • By priority: {by_priority}")
        console.print(f"  • By type: {by_type}")
        
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        logger.error(f"CLI analyze error: {e}")


@main.command()
@click.argument('error_message')
@click.option('--session-id', default='cli_session', help='Session ID for analysis / ID сесії для аналізу')
@click.option('--output', '-o', type=click.Path(), help='Save recommendations to file / Зберегти рекомендації в файл')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output / Детальний вивід')
@click.pass_context
def diagnose(ctx, error_message, session_id, output, verbose):
    """Diagnose error and generate AI recommendations / Діагностувати помилку та генерувати AI-рекомендації"""
    import asyncio
    asyncio.run(_diagnose_async(ctx, error_message, session_id, output, verbose))


async def _diagnose_async(ctx, error_message, session_id, output, verbose):
    """Diagnose error and generate AI recommendations / Діагностувати помилку та генерувати AI-рекомендації"""
    try:
        # Initialize ML integration
        ml_integration = MLIntegration()
        
        console.print(Panel("🔍 AI-Powered Error Diagnosis", style="yellow"))
        console.print(f"🚨 Error: {error_message}")
        console.print(f"🆔 Session ID: {session_id}")
        
        # Generate error recommendations
        recommendations = await ml_integration.analyze_error_recommendations(error_message, session_id)
        
        # Display recommendations
        display_recommendations(recommendations, verbose)
        
        # Export if specified
        if output:
            success = await ml_integration.export_recommendations(recommendations, output)
            if success:
                console.print(f"✅ Recommendations exported to: {output}", style="green")
            else:
                console.print(f"❌ Failed to export recommendations", style="red")
        
        # Summary
        console.print(f"\n📊 Diagnosis Summary:")
        console.print(f"  • Recommendations generated: {len(recommendations)}")
        
        if recommendations:
            critical_count = sum(1 for rec in recommendations if rec.priority.value == 'critical')
            if critical_count > 0:
                console.print(f"  ⚠️  Critical issues found: {critical_count}", style="red")
        
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        logger.error(f"CLI diagnose error: {e}")


@main.command()
@click.option('--session-id', default='cli_session', help='Session ID for analysis / ID сесії для аналізу')
@click.option('--output', '-o', type=click.Path(), help='Save recommendations to file / Зберегти рекомендації в файл')
@click.pass_context
def recommendations_summary(ctx, session_id, output):
    """Get AI recommendations summary / Отримати зведення AI-рекомендацій"""
    import asyncio
    asyncio.run(_recommendations_summary_async(ctx, session_id, output))


async def _recommendations_summary_async(ctx, session_id, output):
    """Get AI recommendations summary / Отримати зведення AI-рекомендацій"""
    try:
        # Initialize ML integration
        ml_integration = MLIntegration()
        
        console.print(Panel("📈 AI Recommendations Summary", style="cyan"))
        console.print(f"🆔 Session ID: {session_id}")
        
        # Get summary
        summary = await ml_integration.get_recommendation_summary()
        
        # Display summary
        display_recommendation_summary(summary)
        
        # Export if specified
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False, default=str)
            console.print(f"✅ Summary exported to: {output}", style="green")
        
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        logger.error(f"CLI recommendations_summary error: {e}")


# New commands for Redis management
@main.command()
@click.option('--redis-url', default='redis://localhost:6379', help='Redis connection URL / URL підключення до Redis')
@click.option('--session-id', help='Specific session ID to show / Конкретний ID сесії для показу')
@click.option('--pattern', default='mova:session:*', help='Session pattern to list / Патерн сесій для списку')
@click.pass_context
def redis_sessions(ctx, redis_url, session_id, pattern):
    """Manage Redis sessions / Керувати сесіями Redis"""
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
        logger.error(f"Redis sessions error: {e}")


@main.command()
@click.option('--redis-url', default='redis://localhost:6379', help='Redis connection URL / URL підключення до Redis')
@click.option('--session-id', help='Session ID to delete / ID сесії для видалення')
@click.option('--pattern', default='mova:session:*', help='Session pattern to clear / Патерн сесій для очищення')
@click.option('--confirm', is_flag=True, help='Confirm deletion / Підтвердити видалення')
@click.pass_context
def redis_clear(ctx, redis_url, session_id, pattern, confirm):
    """Clear Redis sessions / Очистити сесії Redis"""
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
        logger.error(f"Redis clear error: {e}")


# New commands for cache management
@main.command()
@click.option('--key', help='Specific cache key to show / Конкретний ключ кешу для показу')
@click.option('--stats', is_flag=True, help='Show cache statistics / Показати статистику кешу')
def cache_info(key, stats):
    """Show cache information / Показати інформацію про кеш"""
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
        logger.error(f"Cache info error: {e}")


@main.command()
@click.option('--key', help='Specific cache key to delete / Конкретний ключ кешу для видалення')
@click.option('--confirm', is_flag=True, help='Confirm deletion / Підтвердити видалення')
def cache_clear(key, confirm):
    """Clear cache / Очистити кеш"""
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
        logger.error(f"Cache clear error: {e}")


# New commands for webhook management
@main.command()
@click.option('--url', required=True, help='Webhook URL / URL webhook')
@click.option('--event-type', required=True, help='Event type / Тип події')
@click.option('--data', help='Event data (JSON) / Дані події (JSON)')
def webhook_test(url, event_type, data):
    """Test webhook endpoint / Тестувати webhook endpoint"""
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
        logger.error(f"Webhook test error: {e}")


@main.command()
def webhook_status():
    """Show webhook status / Показати статус webhook"""
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
        logger.error(f"Webhook status error: {e}")


# New commands for ML management
@main.command()
@click.option('--model-id', help='Specific model ID to show / Конкретний ID моделі для показу')
@click.option('--list-models', is_flag=True, help='List all available models / Показати всі доступні моделі')
def ml_models(model_id, list_models):
    """Show ML models information / Показати інформацію про ML моделі"""
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
        logger.error(f"ML models error: {e}")


@main.command()
@click.option('--model-id', required=True, help='Model ID to evaluate / ID моделі для оцінки')
@click.option('--test-data', required=True, type=click.Path(exists=True), help='Test data file / Файл тестових даних')
@click.option('--output', '-o', type=click.Path(), help='Save evaluation results to file / Зберегти результати оцінки в файл')
def ml_evaluate(model_id, test_data, output):
    """Evaluate ML model / Оцінити ML модель"""
    try:
        import asyncio
        
        # Load test data
        with open(test_data, 'r', encoding='utf-8') as f:
            test_data_list = json.load(f)
        
        ml_integration = MLIntegration()
        
        console.print(f"🔍 Evaluating model: {model_id}")
        console.print(f"📊 Test data: {len(test_data_list)} examples")
        
        # Run evaluation
        result = asyncio.run(ml_integration.evaluate_model(model_id, test_data_list))
        
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
        logger.error(f"ML evaluate error: {e}")


@main.command()
def ml_status():
    """Show ML system status / Показати статус ML системи"""
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
        logger.error(f"ML status error: {e}")


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
    main() 