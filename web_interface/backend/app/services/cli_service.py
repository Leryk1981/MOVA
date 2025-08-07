"""
CLI service for executing MOVA commands
Сервіс для виконання CLI команд MOVA
"""

import asyncio
import subprocess
import tempfile
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from loguru import logger

from ..models.cli import CLIRunRequest, CLIRunResponse
from ..models.common import StatusEnum
from .mova_service import mova_service


class CLIService:
    """Сервіс для виконання CLI команд"""
    
    def __init__(self):
        """Ініціалізація сервісу"""
        self.mova_sdk_path = Path(__file__).parent.parent.parent.parent.parent / "src"
    
    async def execute_cli_command(self, request: CLIRunRequest) -> CLIRunResponse:
        """Виконання CLI команди"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Формуємо команду
            command_parts = ["python", "-m", "mova.cli.cli"]
            
            if request.command == "run":
                command_parts.extend(["run", request.file_path])
                if request.options:
                    for key, value in request.options.items():
                        if isinstance(value, bool) and value:
                            command_parts.append(f"--{key}")
                        elif not isinstance(value, bool):
                            command_parts.extend([f"--{key}", str(value)])
            
            elif request.command == "parse":
                command_parts.extend(["parse", request.file_path])
                if request.options and request.options.get("validate"):
                    command_parts.append("--validate")
            
            elif request.command == "validate":
                command_parts.extend(["validate", request.file_path])
                if request.options:
                    if request.options.get("advanced"):
                        command_parts.append("--advanced")
                    if request.options.get("detailed"):
                        command_parts.append("--detailed")
            
            elif request.command == "test":
                command_parts.extend(["test", request.file_path])
                if request.options:
                    if request.options.get("verbose"):
                        command_parts.append("--verbose")
                    if request.options.get("dry_run"):
                        command_parts.append("--dry-run")
            
            else:
                # Інші команди
                command_parts.append(request.command)
                if request.file_path:
                    command_parts.append(request.file_path)
                if request.options:
                    for key, value in request.options.items():
                        if isinstance(value, bool) and value:
                            command_parts.append(f"--{key}")
                        elif not isinstance(value, bool):
                            command_parts.extend([f"--{key}", str(value)])
            
            # Виконуємо команду
            logger.info(f"Executing CLI command: {' '.join(command_parts)}")
            
            # Змінюємо робочу директорію на SDK
            original_cwd = os.getcwd()
            os.chdir(self.mova_sdk_path)
            
            try:
                # Виконуємо команду
                process = await asyncio.create_subprocess_exec(
                    *command_parts,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=str(self.mova_sdk_path)
                )
                
                stdout, stderr = await process.communicate()
                
                execution_time = asyncio.get_event_loop().time() - start_time
                
                if process.returncode == 0:
                    return CLIRunResponse(
                        command=request.command,
                        status=StatusEnum.SUCCESS,
                        output=stdout.decode('utf-8'),
                        execution_time=execution_time,
                        session_id=request.session_id
                    )
                else:
                    return CLIRunResponse(
                        command=request.command,
                        status=StatusEnum.ERROR,
                        error=stderr.decode('utf-8'),
                        execution_time=execution_time,
                        session_id=request.session_id
                    )
            
            finally:
                # Повертаємо оригінальну робочу директорію
                os.chdir(original_cwd)
        
        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            logger.error(f"CLI command execution failed: {e}")
            
            return CLIRunResponse(
                command=request.command,
                status=StatusEnum.ERROR,
                error=str(e),
                execution_time=execution_time,
                session_id=request.session_id
            )
    
    async def execute_mova_parse(self, file_path: str, validate: bool = False) -> Dict[str, Any]:
        """Виконання команди parse через MOVA SDK"""
        try:
            from mova.parser.json_parser import MovaJsonParser
            from mova.parser.yaml_parser import MovaYamlParser
            from mova.validator.schema_validator import MovaSchemaValidator
            
            # Визначаємо парсер
            path = Path(file_path)
            if path.suffix.lower() in ['.yaml', '.yml']:
                parser = MovaYamlParser()
            else:
                parser = MovaJsonParser()
            
            # Парсимо файл
            data = parser.parse_file(str(path))
            
            result = {
                "success": True,
                "data": data,
                "file_path": file_path,
                "parser_type": type(parser).__name__
            }
            
            # Валідуємо якщо потрібно
            if validate:
                validator = MovaSchemaValidator()
                is_valid, errors = validator.validate_mova_file(data)
                result["validation"] = {
                    "is_valid": is_valid,
                    "errors": errors
                }
            
            return result
        
        except Exception as e:
            logger.error(f"Parse failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "file_path": file_path
            }
    
    async def execute_mova_validate(self, file_path: str, advanced: bool = False) -> Dict[str, Any]:
        """Виконання команди validate через MOVA SDK"""
        try:
            from mova.parser.json_parser import MovaJsonParser
            from mova.parser.yaml_parser import MovaYamlParser
            from mova.validator.schema_validator import MovaSchemaValidator
            from mova.validator.advanced_validator import MovaAdvancedValidator
            
            # Парсимо файл
            path = Path(file_path)
            if path.suffix.lower() in ['.yaml', '.yml']:
                parser = MovaYamlParser()
            else:
                parser = MovaJsonParser()
            
            data = parser.parse_file(str(path))
            
            if advanced:
                # Розширена валідація
                validator = MovaAdvancedValidator()
                validator.validate_mova_structure(data)
                validator.validate_unique_ids(data)
                validator.validate_references(data)
                validator.validate_step_consistency(data)
                validator.validate_api_endpoints(data)
                
                report = validator.generate_validation_report()
                
                return {
                    "success": True,
                    "advanced": True,
                    "report": report,
                    "is_valid": validator.is_valid
                }
            else:
                # Базова валідація
                validator = MovaSchemaValidator()
                is_valid, errors = validator.validate_mova_file(data)
                
                return {
                    "success": True,
                    "advanced": False,
                    "is_valid": is_valid,
                    "errors": errors
                }
        
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "file_path": file_path
            }
    
    async def execute_mova_run(self, file_path: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Виконання команди run через MOVA SDK"""
        try:
            # Створюємо движок
            engine = mova_service.create_sync_engine(
                redis_url=options.get("redis_url"),
                llm_api_key=options.get("llm_api_key"),
                llm_model=options.get("llm_model")
            )
            
            # Парсимо файл
            from mova.parser.json_parser import MovaJsonParser
            from mova.parser.yaml_parser import MovaYamlParser
            
            path = Path(file_path)
            if path.suffix.lower() in ['.yaml', '.yml']:
                parser = MovaYamlParser()
            else:
                parser = MovaJsonParser()
            
            data = parser.parse_file(str(file_path))
            
            # Завантажуємо дані в движок
            # Тут потрібно реалізувати завантаження даних
            
            # Виконуємо протоколи
            results = []
            for protocol in data.get("protocols", []):
                try:
                    result = engine.execute_protocol(protocol['name'], options.get("session_id", "web_session"))
                    results.append({
                        "protocol": protocol['name'],
                        "success": True,
                        "result": result
                    })
                except Exception as e:
                    results.append({
                        "protocol": protocol['name'],
                        "success": False,
                        "error": str(e)
                    })
            
            return {
                "success": True,
                "results": results,
                "protocols_count": len(data.get("protocols", []))
            }
        
        except Exception as e:
            logger.error(f"Run failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "file_path": file_path
            }


# Глобальний екземпляр сервісу
cli_service = CLIService() 