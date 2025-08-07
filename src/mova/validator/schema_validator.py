"""
Schema validator for MOVA language
Валідатор схем для мови MOVA
"""

import json
from typing import Dict, List, Any, Optional, Tuple
from jsonschema import validate, ValidationError
from loguru import logger

from .advanced_validator import MovaAdvancedValidator


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
            
        except ValidationError as e:
            errors.append(f"Main structure: {e.message}")
        
        # Run advanced validation
        advanced_validator = MovaAdvancedValidator()
        
        # Run all validation checks manually
        advanced_validator.validate_mova_structure(data)
        advanced_validator.validate_unique_ids(data)
        advanced_validator.validate_references(data)
        advanced_validator.validate_step_consistency(data)
        advanced_validator.validate_api_endpoints(data)
        advanced_validator.validate_condition_syntax(data)
        advanced_validator.validate_placeholder_syntax(data)
        
        # Get advanced validation report
        advanced_report = advanced_validator.generate_validation_report()
        
        # Add advanced validation errors
        for error in advanced_report.get("errors", []):
            errors.append(f"{error['field']}: {error['message']}")
        
        is_valid = len(errors) == 0
        if is_valid:
            logger.info("MOVA file validation successful")
        else:
            logger.warning(f"MOVA file validation failed: {len(errors)} errors")
        
        return is_valid, errors
    
    def validate_mova_file_advanced(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate MOVA file with advanced validation features
        Валідувати MOVA файл з розширеними можливостями валідації
        
        Args:
            data: MOVA data to validate / Дані MOVA для валідації
            
        Returns:
            Dict[str, Any]: Comprehensive validation report / Комплексний звіт валідації
        """
        # Basic schema validation only (without advanced validation)
        errors = []
        try:
            validate(instance=data, schema=self.schemas["mova"])
            basic_valid = True
        except ValidationError as e:
            errors.append(f"Main structure: {e.message}")
            basic_valid = False
        
        # Advanced validation
        advanced_validator = MovaAdvancedValidator()
        
        # Run all validation checks manually
        advanced_validator.validate_mova_structure(data)
        advanced_validator.validate_unique_ids(data)
        advanced_validator.validate_references(data)
        advanced_validator.validate_step_consistency(data)
        advanced_validator.validate_api_endpoints(data)
        advanced_validator.validate_condition_syntax(data)
        advanced_validator.validate_placeholder_syntax(data)
        
        # Get advanced validation report
        advanced_report = advanced_validator.generate_validation_report()
        
        # Combine results
        combined_report = {
            "basic_validation": {
                "is_valid": basic_valid,
                "errors": errors
            },
            "advanced_validation": advanced_report,
            "overall_valid": basic_valid and advanced_report["is_valid"],
            "total_errors": len(errors) + len(advanced_report.get("errors", [])),
            "total_warnings": len(advanced_report.get("warnings", []))
        }
        
        return combined_report
    
    def validate_schema_compatibility(self, data: Dict[str, Any], target_version: str = "2.2") -> Dict[str, Any]:
        """
        Validate schema compatibility with target version
        Валідувати сумісність схеми з цільовою версією
        """
        version = data.get("version", "unknown")
        
        compatibility_report = {
            "current_version": version,
            "target_version": target_version,
            "is_compatible": True,
            "migration_notes": []
        }
        
        # Version compatibility checks
        if version != target_version:
            compatibility_report["is_compatible"] = False
            compatibility_report["migration_notes"].append(
                f"Schema version {version} differs from target {target_version}"
            )
        
        # Check for deprecated fields
        deprecated_fields = self._check_deprecated_fields(data, version)
        if deprecated_fields:
            compatibility_report["migration_notes"].extend(deprecated_fields)
        
        return compatibility_report
    
    def _check_deprecated_fields(self, data: Dict[str, Any], version: str) -> List[str]:
        """Check for deprecated fields based on version / Перевірити застарілі поля на основі версії"""
        deprecated_notes = []
        
        # Version-specific deprecation checks
        if version < "2.2":
            # Check for old field names
            for protocol in data.get("protocols", []):
                if "protocol_id" in protocol:
                    deprecated_notes.append("'protocol_id' is deprecated, use 'name' instead")
                if "step_id" in protocol:
                    deprecated_notes.append("'step_id' is deprecated, use 'id' instead")
        
        return deprecated_notes
    
    def generate_schema_documentation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate documentation from schema
        Згенерувати документацію зі схеми
        """
        doc = {
            "version": data.get("version", "unknown"),
            "components": {
                "intents": [],
                "protocols": [],
                "tools": [],
                "profiles": [],
                "contracts": []
            },
            "statistics": {
                "total_intents": len(data.get("intents", [])),
                "total_protocols": len(data.get("protocols", [])),
                "total_tools": len(data.get("tools", [])),
                "total_steps": sum(len(p.get("steps", [])) for p in data.get("protocols", [])),
                "total_profiles": len(data.get("profiles", [])),
                "total_contracts": len(data.get("contracts", []))
            }
        }
        
        # Document intents
        for intent in data.get("intents", []):
            doc["components"]["intents"].append({
                "name": intent.get("name"),
                "patterns": len(intent.get("patterns", [])),
                "has_template": bool(intent.get("response_template"))
            })
        
        # Document protocols
        for protocol in data.get("protocols", []):
            steps = protocol.get("steps", [])
            doc["components"]["protocols"].append({
                "name": protocol.get("name"),
                "steps_count": len(steps),
                "has_conditions": any(step.get("conditions") for step in steps),
                "has_api_calls": any(step.get("tool_api_id") for step in steps)
            })
        
        # Document tools
        for tool in data.get("tools", []):
            doc["components"]["tools"].append({
                "id": tool.get("id"),
                "name": tool.get("name"),
                "method": tool.get("method", "GET"),
                "has_auth": bool(tool.get("authentication"))
            })
        
        return doc
    
    def _get_mova_schema(self) -> Dict[str, Any]:
        """Get main MOVA schema / Отримати основну схему MOVA"""
        return {
            "type": "object",
            "properties": {
                "version": {"type": "string"},
                "intents": {"type": "array", "items": {"type": "object"}},
                "protocols": {"type": "array", "items": {"type": "object"}},
                "tools": {"type": "array", "items": {"type": "object"}},
                "instructions": {"type": "array", "items": {"type": "object"}},
                "profiles": {"type": "array", "items": {"type": "object"}},
                "sessions": {"type": "array", "items": {"type": "object"}},
                "contracts": {"type": "array", "items": {"type": "object"}}
            },
            "required": ["version"]
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