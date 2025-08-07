"""
Schema validator for MOVA language
Валідатор схем для мови MOVA
"""

import json
from typing import Dict, List, Any, Optional, Tuple
from jsonschema import validate, ValidationError
from loguru import logger


class MovaSchemaValidator:
    """
    Schema validator for MOVA language
    Валідатор схем для мови MOVA
    """
    
    def __init__(self):
        """Initialize schema validator / Ініціалізація валідатора схем"""
        self.schemas = self._load_schemas()
        logger.info("MOVA Schema Validator initialized / MOVA Schema Validator ініціалізовано")
    
    def _load_schemas(self) -> Dict[str, Any]:
        """Load validation schemas / Завантажити схеми валідації"""
        return {
            "mova": self._get_mova_schema(),
            "intent": self._get_intent_schema(),
            "protocol": self._get_protocol_schema(),
            "tool": self._get_tool_schema(),
            "instruction": self._get_instruction_schema(),
            "profile": self._get_profile_schema(),
            "session": self._get_session_schema(),
            "contract": self._get_contract_schema()
        }
    
    def validate_mova_file(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate complete MOVA file / Валідувати повний файл MOVA
        
        Args:
            data: MOVA data to validate / Дані MOVA для валідації
            
        Returns:
            Tuple[bool, List[str]]: Validation result and errors / Результат валідації та помилки
        """
        errors = []
        
        try:
            # Validate main structure
            validate(instance=data, schema=self.schemas["mova"])
            
            # Validate individual components
            if "intents" in data:
                for i, intent in enumerate(data["intents"]):
                    try:
                        validate(instance=intent, schema=self.schemas["intent"])
                    except ValidationError as e:
                        errors.append(f"Intent {i}: {e.message}")
            
            if "protocols" in data:
                for i, protocol in enumerate(data["protocols"]):
                    try:
                        validate(instance=protocol, schema=self.schemas["protocol"])
                    except ValidationError as e:
                        errors.append(f"Protocol {i}: {e.message}")
            
            if "tools" in data:
                for i, tool in enumerate(data["tools"]):
                    try:
                        validate(instance=tool, schema=self.schemas["tool"])
                    except ValidationError as e:
                        errors.append(f"Tool {i}: {e.message}")
            
            if "instructions" in data:
                for i, instruction in enumerate(data["instructions"]):
                    try:
                        validate(instance=instruction, schema=self.schemas["instruction"])
                    except ValidationError as e:
                        errors.append(f"Instruction {i}: {e.message}")
            
            if "profiles" in data:
                for i, profile in enumerate(data["profiles"]):
                    try:
                        validate(instance=profile, schema=self.schemas["profile"])
                    except ValidationError as e:
                        errors.append(f"Profile {i}: {e.message}")
            
            if "sessions" in data:
                for i, session in enumerate(data["sessions"]):
                    try:
                        validate(instance=session, schema=self.schemas["session"])
                    except ValidationError as e:
                        errors.append(f"Session {i}: {e.message}")
            
            if "contracts" in data:
                for i, contract in enumerate(data["contracts"]):
                    try:
                        validate(instance=contract, schema=self.schemas["contract"])
                    except ValidationError as e:
                        errors.append(f"Contract {i}: {e.message}")
            
        except ValidationError as e:
            errors.append(f"Main structure: {e.message}")
        
        is_valid = len(errors) == 0
        if is_valid:
            logger.info("MOVA file validation successful")
        else:
            logger.warning(f"MOVA file validation failed: {len(errors)} errors")
        
        return is_valid, errors
    
    def _get_mova_schema(self) -> Dict[str, Any]:
        """Get main MOVA schema / Отримати основну схему MOVA"""
        return {
            "type": "object",
            "properties": {
                "version": {"type": "string"},
                "intents": {"type": "array", "items": {"$ref": "#/definitions/intent"}},
                "protocols": {"type": "array", "items": {"$ref": "#/definitions/protocol"}},
                "tools": {"type": "array", "items": {"$ref": "#/definitions/tool"}},
                "instructions": {"type": "array", "items": {"$ref": "#/definitions/instruction"}},
                "profiles": {"type": "array", "items": {"$ref": "#/definitions/profile"}},
                "sessions": {"type": "array", "items": {"$ref": "#/definitions/session"}},
                "contracts": {"type": "array", "items": {"$ref": "#/definitions/contract"}}
            },
            "required": ["version"],
            "definitions": {
                "intent": self._get_intent_schema(),
                "protocol": self._get_protocol_schema(),
                "tool": self._get_tool_schema(),
                "instruction": self._get_instruction_schema(),
                "profile": self._get_profile_schema(),
                "session": self._get_session_schema(),
                "contract": self._get_contract_schema()
            }
        }
    
    def _get_intent_schema(self) -> Dict[str, Any]:
        """Get intent schema / Отримати схему наміру"""
        return {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "patterns": {"type": "array", "items": {"type": "string"}},
                "priority": {"type": "integer", "default": 0},
                "response_template": {"type": "string"},
                "intent_type": {
                    "type": "string",
                    "enum": ["greeting", "question", "command", "feedback", "custom"]
                }
            },
            "required": ["name", "patterns"]
        }
    
    def _get_protocol_schema(self) -> Dict[str, Any]:
        """Get protocol schema / Отримати схему протоколу"""
        return {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "steps": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "action": {
                                "type": "string",
                                "enum": ["prompt", "tool_api", "condition", "end"]
                            },
                            "prompt": {"type": "string"},
                            "tool_api_id": {"type": "string"},
                            "conditions": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "variable": {"type": "string"},
                                        "operator": {
                                            "type": "string",
                                            "enum": ["equals", "not_equals", "contains", "greater_than", "less_than"]
                                        },
                                        "value": {}
                                    },
                                    "required": ["variable", "operator", "value"]
                                }
                            },
                            "next_step": {"type": "string"}
                        },
                        "required": ["id", "action"]
                    }
                },
                "description": {"type": "string"}
            },
            "required": ["name", "steps"]
        }
    
    def _get_tool_schema(self) -> Dict[str, Any]:
        """Get tool schema / Отримати схему інструменту"""
        return {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "name": {"type": "string"},
                "endpoint": {"type": "string"},
                "method": {"type": "string", "default": "GET"},
                "headers": {"type": "object"},
                "parameters": {"type": "object"},
                "authentication": {"type": "object"}
            },
            "required": ["id", "name", "endpoint"]
        }
    
    def _get_instruction_schema(self) -> Dict[str, Any]:
        """Get instruction schema / Отримати схему інструкції"""
        return {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "title": {"type": "string"},
                "content": {"type": "string"},
                "category": {"type": "string"},
                "tags": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["id", "title", "content"]
        }
    
    def _get_profile_schema(self) -> Dict[str, Any]:
        """Get profile schema / Отримати схему профілю"""
        return {
            "type": "object",
            "properties": {
                "user_id": {"type": "string"},
                "name": {"type": "string"},
                "preferences": {"type": "object"},
                "language": {"type": "string", "default": "en"},
                "timezone": {"type": "string"}
            },
            "required": ["user_id"]
        }
    
    def _get_session_schema(self) -> Dict[str, Any]:
        """Get session schema / Отримати схему сесії"""
        return {
            "type": "object",
            "properties": {
                "session_id": {"type": "string"},
                "user_id": {"type": "string"},
                "start_time": {"type": "string"},
                "data": {"type": "object"},
                "context": {"type": "object"},
                "active": {"type": "boolean", "default": True}
            },
            "required": ["session_id", "user_id", "start_time"]
        }
    
    def _get_contract_schema(self) -> Dict[str, Any]:
        """Get contract schema / Отримати схему контракту"""
        return {
            "type": "object",
            "properties": {
                "contract_id": {"type": "string"},
                "parties": {"type": "array", "items": {"type": "string"}},
                "terms": {"type": "object"},
                "conditions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "variable": {"type": "string"},
                            "operator": {
                                "type": "string",
                                "enum": ["equals", "not_equals", "contains", "greater_than", "less_than"]
                            },
                            "value": {}
                        },
                        "required": ["variable", "operator", "value"]
                    }
                },
                "valid_from": {"type": "string"},
                "valid_until": {"type": "string"}
            },
            "required": ["contract_id", "parties", "terms", "valid_from"]
        }
    
    def validate_intent(self, intent_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate intent data / Валідувати дані наміру"""
        return self._validate_component(intent_data, "intent")
    
    def validate_protocol(self, protocol_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate protocol data / Валідувати дані протоколу"""
        return self._validate_component(protocol_data, "protocol")
    
    def validate_tool(self, tool_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate tool data / Валідувати дані інструменту"""
        return self._validate_component(tool_data, "tool")
    
    def _validate_component(self, data: Dict[str, Any], component_type: str) -> Tuple[bool, List[str]]:
        """Validate component data / Валідувати дані компонента"""
        errors = []
        try:
            validate(instance=data, schema=self.schemas[component_type])
        except ValidationError as e:
            errors.append(e.message)
        
        is_valid = len(errors) == 0
        if is_valid:
            logger.info(f"{component_type.capitalize()} validation successful")
        else:
            logger.warning(f"{component_type.capitalize()} validation failed: {errors}")
        
        return is_valid, errors 