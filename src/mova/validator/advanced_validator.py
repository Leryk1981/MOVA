"""
Advanced validation for MOVA SDK
Розширена валідація для MOVA SDK
"""

from typing import Dict, Any, List, Optional, Set
from pathlib import Path
import json
from loguru import logger

from pydantic import BaseModel, ValidationError, field_validator, model_validator
from pydantic.json_schema import GenerateJsonSchema

from ..core.models import Intent, Protocol, ProtocolStep, ToolAPI, Session, Profile, Contract, Instruction


class MovaAdvancedValidator(BaseModel):
    """
    Advanced validator for MOVA files with comprehensive validation
    Розширений валідатор для MOVA файлів з комплексною валідацією
    """
    
    # Validation results
    is_valid: bool = True
    errors: List[Dict[str, Any]] = []
    warnings: List[Dict[str, Any]] = []
    
    # Validation statistics
    stats: Dict[str, int] = {
        "intents": 0,
        "protocols": 0,
        "tools": 0,
        "steps": 0,
        "references": 0,
        "duplicates": 0
    }
    
    def __init__(self, **data):
        super().__init__(**data)
        self._validated_ids: Set[str] = set()
        self._referenced_ids: Set[str] = set()
    
    def validate_mova_structure(self, data: Dict[str, Any]) -> None:
        """Validate overall MOVA structure / Валідувати загальну структуру MOVA"""
        try:
            # Validate version
            if not data.get("version"):
                self._add_error("version", "Missing required 'version' field")
            
            # Validate required sections
            required_sections = ['intents', 'protocols', 'tools']
            for section in required_sections:
                if not data.get(section):
                    self._add_warning(section, f"Section '{section}' is empty or missing")
            
        except Exception as e:
            self._add_error("structure", f"Structure validation failed: {str(e)}")
    
    def validate_unique_ids(self, data: Dict[str, Any]) -> None:
        """Validate uniqueness of all IDs / Валідувати унікальність всіх ID"""
        all_ids: Set[str] = set()
        
        # Check intents
        for intent in data.get("intents", []):
            intent_id = intent.get("name")
            if intent_id in all_ids:
                self._add_error("intents", f"Duplicate intent ID: {intent_id}")
                self.stats["duplicates"] += 1
            all_ids.add(intent_id)
            self.stats["intents"] += 1
        
        # Check protocols
        for protocol in data.get("protocols", []):
            protocol_id = protocol.get("name")
            if protocol_id in all_ids:
                self._add_error("protocols", f"Duplicate protocol ID: {protocol_id}")
                self.stats["duplicates"] += 1
            all_ids.add(protocol_id)
            self.stats["protocols"] += 1
            
            # Check steps within protocol
            for step in protocol.get("steps", []):
                step_id = step.get("id")
                if step_id in all_ids:
                    self._add_error("steps", f"Duplicate step ID: {step_id}")
                    self.stats["duplicates"] += 1
                all_ids.add(step_id)
                self.stats["steps"] += 1
        
        # Check tools
        for tool in data.get("tools", []):
            tool_id = tool.get("id")
            if tool_id in all_ids:
                self._add_error("tools", f"Duplicate tool ID: {tool_id}")
                self.stats["duplicates"] += 1
            all_ids.add(tool_id)
            self.stats["tools"] += 1
    
    def validate_references(self, data: Dict[str, Any]) -> None:
        """Validate all references between components / Валідувати всі посилання між компонентами"""
        # Collect all valid IDs
        valid_ids = set()
        
        # Add intent names
        for intent in data.get("intents", []):
            valid_ids.add(intent.get("name"))
        
        # Add protocol names
        for protocol in data.get("protocols", []):
            valid_ids.add(protocol.get("name"))
            
            # Add step IDs
            for step in protocol.get("steps", []):
                valid_ids.add(step.get("id"))
        
        # Add tool IDs
        for tool in data.get("tools", []):
            valid_ids.add(tool.get("id"))
        
        # Validate step references
        for protocol in data.get("protocols", []):
            for step in protocol.get("steps", []):
                # Check next_step_id references
                next_step_id = step.get("next_step_id")
                if next_step_id and next_step_id not in valid_ids:
                    self._add_error("references", f"Invalid next_step_id reference: {next_step_id}")
                    self.stats["references"] += 1
                
                # Check tool_api_id references
                tool_api_id = step.get("tool_api_id")
                if tool_api_id and tool_api_id not in valid_ids:
                    self._add_error("references", f"Invalid tool_api_id reference: {tool_api_id}")
                    self.stats["references"] += 1
    
    def validate_step_consistency(self, data: Dict[str, Any]) -> None:
        """Validate step consistency within protocols / Валідувати консистентність кроків в протоколах"""
        for protocol in data.get("protocols", []):
            steps = protocol.get("steps", [])
            
            if not steps:
                self._add_warning("protocols", f"Protocol '{protocol.get('name')}' has no steps")
                continue
            
            # Check for orphaned steps (no incoming references)
            step_ids = {step.get("id") for step in steps}
            referenced_ids = set()
            
            for step in steps:
                next_step_id = step.get("next_step_id")
                if next_step_id:
                    referenced_ids.add(next_step_id)
            
            # Find orphaned steps (except the first one)
            orphaned = step_ids - referenced_ids
            if len(orphaned) > 1:  # More than just the first step
                self._add_warning("steps", f"Protocol '{protocol.get('name')}' has orphaned steps: {orphaned}")
            
            # Check for cycles
            if self._has_cycle(steps):
                self._add_error("steps", f"Protocol '{protocol.get('name')}' has circular references")
    
    def _has_cycle(self, steps: List[Dict[str, Any]]) -> bool:
        """Check for cycles in step references / Перевірити циклічні посилання в кроках"""
        visited = set()
        rec_stack = set()
        
        def dfs(step_id: str) -> bool:
            if step_id in rec_stack:
                return True
            if step_id in visited:
                return False
            
            visited.add(step_id)
            rec_stack.add(step_id)
            
            # Find step by ID
            step = next((s for s in steps if s.get("id") == step_id), None)
            if step and step.get("next_step_id"):
                if dfs(step.get("next_step_id")):
                    return True
            
            rec_stack.remove(step_id)
            return False
        
        # Check each step
        for step in steps:
            step_id = step.get("id")
            if step_id not in visited:
                if dfs(step_id):
                    return True
        
        return False
    
    def validate_api_endpoints(self, data: Dict[str, Any]) -> None:
        """Validate API endpoint configurations / Валідувати конфігурації API ендпоінтів"""
        for tool in data.get("tools", []):
            endpoint = tool.get("endpoint")
            method = tool.get("method", "GET")
            
            # Validate endpoint format
            if not endpoint:
                self._add_error("tools", f"Tool '{tool.get('id')}' has no endpoint")
                continue
            
            # Basic URL validation
            if not (endpoint.startswith("http://") or endpoint.startswith("https://")):
                self._add_warning("tools", f"Tool '{tool.get('id')}' endpoint may not be a valid URL: {endpoint}")
            
            # Validate method
            valid_methods = ["GET", "POST", "PUT", "DELETE", "PATCH"]
            if method.upper() not in valid_methods:
                self._add_error("tools", f"Tool '{tool.get('id')}' has invalid method: {method}")
            
            # Validate authentication if present
            auth = tool.get("authentication")
            if auth:
                auth_type = auth.get("type")
                if auth_type not in ["api_key", "basic", "bearer"]:
                    self._add_error("tools", f"Tool '{tool.get('id')}' has invalid auth type: {auth_type}")
    
    def validate_condition_syntax(self, data: Dict[str, Any]) -> None:
        """Validate condition syntax in steps / Валідувати синтаксис умов в кроках"""
        for protocol in data.get("protocols", []):
            for step in protocol.get("steps", []):
                conditions = step.get("conditions")
                
                if conditions is not None:  # Check if conditions exist
                    for condition in conditions:
                        # Validate operator
                        operator = condition.get("operator")
                        valid_operators = ["equals", "not_equals", "contains", "greater_than", "less_than", "exists", "not_exists"]
                        if operator not in valid_operators:
                            self._add_error("conditions", f"Invalid condition operator: {operator}")
                        
                        # Validate variable syntax
                        variable = condition.get("variable")
                        if variable and not self._is_valid_variable_syntax(variable):
                            self._add_error("conditions", f"Invalid variable syntax: {variable}")
    
    def _is_valid_variable_syntax(self, variable: str) -> bool:
        """Check if variable syntax is valid / Перевірити чи синтаксис змінної валідний"""
        # Basic validation for session.data.key format
        if variable.startswith("session.data."):
            key_part = variable[12:]  # Remove "session.data."
            return bool(key_part and key_part.replace("_", "").replace(".", "").isalnum())
        return True
    
    def validate_placeholder_syntax(self, data: Dict[str, Any]) -> None:
        """Validate placeholder syntax in prompts and parameters / Валідувати синтаксис плейсхолдерів"""
        for protocol in data.get("protocols", []):
            for step in protocol.get("steps", []):
                prompt = step.get("prompt", "")
                if prompt:
                    self._validate_placeholders_in_text(prompt, "prompt")
        
        for tool in data.get("tools", []):
            parameters = tool.get("parameters", {})
            for key, value in parameters.items():
                if isinstance(value, str):
                    self._validate_placeholders_in_text(value, f"tool.{tool.get('id')}.parameters.{key}")
    
    def _validate_placeholders_in_text(self, text: str, context: str) -> None:
        """Validate placeholders in text / Валідувати плейсхолдери в тексті"""
        import re
        
        # Find all placeholders
        placeholders = re.findall(r'\{([^}]+)\}', text)
        
        for placeholder in placeholders:
            if not self._is_valid_placeholder_syntax(placeholder):
                self._add_error("placeholders", f"Invalid placeholder syntax in {context}: {{{placeholder}}}")
    
    def _is_valid_placeholder_syntax(self, placeholder: str) -> bool:
        """Check if placeholder syntax is valid / Перевірити чи синтаксис плейсхолдера валідний"""
        # Allow session.data.key format
        if placeholder.startswith("session.data."):
            key_part = placeholder[12:]
            return bool(key_part and key_part.replace("_", "").replace(".", "").isalnum())
        
        # Allow simple variable names
        if placeholder.replace("_", "").isalnum():
            return True
        
        return False
    
    def generate_validation_report(self) -> Dict[str, Any]:
        """Generate comprehensive validation report / Згенерувати комплексний звіт валідації"""
        return {
            "is_valid": self.is_valid,
            "summary": {
                "total_errors": len(self.errors),
                "total_warnings": len(self.warnings),
                "statistics": self.stats
            },
            "errors": self.errors,
            "warnings": self.warnings,
            "recommendations": self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on validation results / Згенерувати рекомендації на основі результатів валідації"""
        recommendations = []
        
        if self.stats["duplicates"] > 0:
            recommendations.append("Remove duplicate IDs to ensure unique component identification")
        
        if self.stats["references"] > 0:
            recommendations.append("Fix invalid references to ensure proper component linking")
        
        if len(self.warnings) > len(self.errors):
            recommendations.append("Address warnings to improve data quality and consistency")
        
        if self.stats["protocols"] == 0:
            recommendations.append("Add at least one protocol to make the configuration functional")
        
        if self.stats["tools"] == 0:
            recommendations.append("Consider adding API tools for external integrations")
        
        return recommendations
    
    def _add_error(self, field: str, message: str) -> None:
        """Add validation error / Додати помилку валідації"""
        self.is_valid = False
        self.errors.append({
            "field": field,
            "message": message,
            "type": "error"
        })
        logger.error(f"Validation error in {field}: {message}")
    
    def _add_warning(self, field: str, message: str) -> None:
        """Add validation warning / Додати попередження валідації"""
        self.warnings.append({
            "field": field,
            "message": message,
            "type": "warning"
        })
        logger.warning(f"Validation warning in {field}: {message}")


class MovaSchemaValidator:
    """
    Schema validator with advanced features
    Валідатор схем з розширеними можливостями
    """
    
    def __init__(self):
        self.advanced_validator = MovaAdvancedValidator()
    
    def validate_mova_file(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate MOVA file with comprehensive checks
        Валідувати MOVA файл з комплексними перевірками
        """
        logger.info("Starting comprehensive MOVA validation")
        
        # Reset validator state
        self.advanced_validator = MovaAdvancedValidator()
        
        try:
            # Run all validation checks
            self.advanced_validator.validate_mova_structure(data)
            self.advanced_validator.validate_unique_ids(data)
            self.advanced_validator.validate_references(data)
            self.advanced_validator.validate_step_consistency(data)
            self.advanced_validator.validate_api_endpoints(data)
            self.advanced_validator.validate_condition_syntax(data)
            self.advanced_validator.validate_placeholder_syntax(data)
            
            # Generate report
            report = self.advanced_validator.generate_validation_report()
            
            logger.info(f"Validation completed: {len(report['errors'])} errors, {len(report['warnings'])} warnings")
            
            return report
            
        except Exception as e:
            logger.error(f"Validation failed with exception: {str(e)}")
            return {
                "is_valid": False,
                "summary": {"total_errors": 1, "total_warnings": 0},
                "errors": [{"field": "validation", "message": f"Validation exception: {str(e)}", "type": "error"}],
                "warnings": [],
                "recommendations": ["Check file format and structure"]
            }
    
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