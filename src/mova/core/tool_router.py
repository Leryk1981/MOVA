"""
Tool Router for MOVA SDK
Диспетчеризація та виконання tool-calls
"""

import json
import logging
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class BaseTool(ABC):
    """Базовий клас для інструментів"""
    
    def __init__(self, name: str, description: str, schema: Dict[str, Any]):
        self.name = name
        self.description = description
        self.schema = schema
    
    @abstractmethod
    def run(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Виконати інструмент з заданими аргументами"""
        pass


class ToolRegistry:
    """Реєстр інструментів"""
    
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
    
    def register(self, tool: BaseTool):
        """Зареєструвати інструмент"""
        self._tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")
    
    def get(self, name: str) -> Optional[BaseTool]:
        """Отримати інструмент за назвою"""
        return self._tools.get(name)
    
    def list_tools(self) -> List[str]:
        """Отримати список назв усіх зареєстрованих інструментів"""
        return list(self._tools.keys())
    
    def to_llm_specs(self, allowed: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Конвертувати інструменти у формат LLM specs"""
        specs = []
        for tool in self._tools.values():
            if allowed and tool.name not in allowed:
                continue
            specs.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.schema
                }
            })
        return specs


class JSONSchemaValidator:
    """Валідатор JSON Schema"""
    
    @staticmethod
    def validate(schema: Dict[str, Any], data: Dict[str, Any]) -> bool:
        """Валідувати дані за схемою"""
        try:
            # Проста валідація для базових типів
            # В реальному проекті варто використовувати бібліотеку jsonschema
            properties = schema.get("properties", {})
            required = schema.get("required", [])
            
            # Перевірка обов'язкових полів
            for field in required:
                if field not in data:
                    logger.error(f"Missing required field: {field}")
                    return False
            
            # Перевірка типів
            for field, value in data.items():
                if field in properties:
                    field_schema = properties[field]
                    field_type = field_schema.get("type")
                    
                    if field_type == "string" and not isinstance(value, str):
                        logger.error(f"Field {field} must be string")
                        return False
                    elif field_type == "integer" and not isinstance(value, int):
                        logger.error(f"Field {field} must be integer")
                        return False
                    elif field_type == "number" and not isinstance(value, (int, float)):
                        logger.error(f"Field {field} must be number")
                        return False
                    elif field_type == "boolean" and not isinstance(value, bool):
                        logger.error(f"Field {field} must be boolean")
                        return False
                    elif field_type == "array" and not isinstance(value, list):
                        logger.error(f"Field {field} must be array")
                        return False
                    elif field_type == "object" and not isinstance(value, dict):
                        logger.error(f"Field {field} must be object")
                        return False
            
            return True
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return False


class ToolRouter:
    """Диспетчер для виконання tool-calls"""
    
    def __init__(self, registry: ToolRegistry):
        self.registry = registry
        self.validator = JSONSchemaValidator()
    
    def execute(self, call: Dict[str, Any]) -> Dict[str, Any]:
        """Виконати tool call"""
        try:
            tool_name = call.get("name")
            arguments = call.get("arguments", {})
            
            logger.info(f"Executing tool: {tool_name} with args: {arguments}")
            
            # Отримати інструмент
            tool = self.registry.get(tool_name)
            if not tool:
                error_msg = f"Tool not found: {tool_name}"
                logger.error(error_msg)
                return {"error": error_msg}
            
            # Валідувати аргументи
            if not self.validator.validate(tool.schema, arguments):
                error_msg = f"Invalid arguments for tool {tool_name}"
                logger.error(error_msg)
                return {"error": error_msg}
            
            # Виконати інструмент
            result = tool.run(arguments)
            logger.info(f"Tool {tool_name} executed successfully")
            
            return result
            
        except Exception as e:
            error_msg = f"Error executing tool call: {e}"
            logger.error(error_msg)
            return {"error": error_msg}
    
    def execute_batch(self, calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Виконати кілька tool calls"""
        results = []
        for call in calls:
            result = self.execute(call)
            results.append(result)
        return results