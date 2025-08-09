"""
Enhanced Validator for MOVA SDK
Покращений валідатор для MOVA SDK
"""

import json
import logging
import re
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from datetime import datetime

from pydantic import BaseModel, Field

from .config import get_config_value
from .webhook_integration import (
    trigger_validation_started, 
    trigger_validation_completed, 
    trigger_validation_failed
)


class ValidationLevel(str, Enum):
    """Validation levels / Рівні валідації"""
    BASIC = "basic"      # Basic syntax and structure validation
    STRICT = "strict"    # Strict validation with business rules
    FULL = "full"        # Full validation with external dependencies


class ValidationStatus(str, Enum):
    """Validation status codes / Коди статусу валідації"""
    PASSED = "passed"
    WARNING = "warning"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class ValidationResult:
    """Validation result data structure 
    Структура даних результату валідації"""
    status: ValidationStatus
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    execution_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


class ValidationReport(BaseModel):
    """Comprehensive validation report / Комплексний звіт валідації"""
    file_path: str
    validation_level: ValidationLevel
    overall_status: ValidationStatus
    results: List[ValidationResult] = Field(default_factory=list)
    summary: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            ValidationStatus: lambda v: v.value,
            ValidationLevel: lambda v: v.value
        }


class MovaValidator:
    """
    Enhanced MOVA validator with detailed reporting
    Покращений валідатор MOVA з детальними звітами
    """
    
    def __init__(
        self, 
        validation_level: ValidationLevel = ValidationLevel.STRICT
    ):
        """
        Initialize validator
        Ініціалізувати валідатор
        
        Args:
            validation_level: Validation level / Рівень валідації
        """
        self.validation_level = validation_level
        self.logger = logging.getLogger(__name__)
        self.cache_enabled = get_config_value("cache_enabled", True)
        self.cache_ttl = get_config_value("cache_ttl", 3600)
        
        # Validation rules configuration
        self.rules = {
            "max_file_size": get_config_value(
                "validation_max_file_size", 1024 * 1024),  # 1MB
            "max_depth": get_config_value("validation_max_depth", 10),
            "require_description": get_config_value(
                "validation_require_description", True),
            "strict_naming": get_config_value(
                "validation_strict_naming", True),
            "allowed_extensions": get_config_value(
                "validation_allowed_extensions", [".json", ".mova"])
        }
        
        # Performance tracking
        self.stats = {
            "files_validated": 0,
            "total_errors": 0,
            "total_warnings": 0,
            "avg_execution_time": 0.0
        }
    
    def validate_file(self, file_path: Union[str, Path]) -> ValidationReport:
        """
        Validate MOVA file
        Валідувати MOVA файл
        
        Args:
            file_path: Path to MOVA file / Шлях до MOVA файлу
            
        Returns:
            Validation report / Звіт валідації
        """
        file_path = Path(file_path)
        start_time = datetime.now()
        
        # Trigger validation started webhook
        trigger_validation_started({
            "file_path": str(file_path),
            "validation_level": self.validation_level.value
        })
        
        try:
            # Check cache if enabled
            cache_key = f"validation_{file_path}_{self.validation_level.value}"
            if self.cache_enabled:
                cached_result = self._get_cached_validation(cache_key)
                if cached_result:
                    return cached_result
            
            # Perform validation
            results = []
            
            # Basic file checks
            results.append(self._validate_file_exists(file_path))
            if results[-1].status == ValidationStatus.FAILED:
                return self._create_report(file_path, results, start_time)
            
            results.append(self._validate_file_size(file_path))
            results.append(self._validate_file_extension(file_path))
            
            # Parse and validate content
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = json.load(f)
                
                results.append(self._validate_json_structure(content))
                results.append(self._validate_mova_schema(content))
                
                if self.validation_level in [
                    ValidationLevel.STRICT, ValidationLevel.FULL
                ]:
                    results.append(self._validate_business_rules(content))
                
                if self.validation_level == ValidationLevel.FULL:
                    results.append(
                        self._validate_external_dependencies(content)
                    )
                    
            except json.JSONDecodeError as e:
                results.append(ValidationResult(
                    status=ValidationStatus.FAILED,
                    message=f"Invalid JSON: {str(e)}",
                    errors=["File contains invalid JSON syntax"]
                ))
            except Exception as e:
                results.append(ValidationResult(
                    status=ValidationStatus.FAILED,
                    message=f"Validation error: {str(e)}",
                    errors=[f"Unexpected error during validation: {str(e)}"]
                ))
            
            # Create report
            report = self._create_report(file_path, results, start_time)
            
            # Cache result if enabled
            if (self.cache_enabled and 
                    report.overall_status != ValidationStatus.FAILED):
                self._cache_validation_result(cache_key, report)
            
            # Trigger validation completed webhook
            trigger_validation_completed({
                "file_path": str(file_path),
                "validation_level": self.validation_level.value,
                "status": report.overall_status.value,
                "execution_time": report.metadata.get("execution_time", 0)
            })
            
            return report
            
        except Exception as e:
            # Trigger validation failed webhook
            trigger_validation_failed({
                "file_path": str(file_path),
                "validation_level": self.validation_level.value,
                "error": str(e)
            })
            
            self.logger.error(f"Validation failed for {file_path}: {e}")
            return ValidationReport(
                file_path=str(file_path),
                validation_level=self.validation_level,
                overall_status=ValidationStatus.FAILED,
                results=[ValidationResult(
                    status=ValidationStatus.FAILED,
                    message=f"Validation failed: {str(e)}",
                    errors=[str(e)]
                )]
            )
    
    def _validate_file_exists(self, file_path: Path) -> ValidationResult:
        """Validate file exists / Валідувати існування файлу"""
        if not file_path.exists():
            return ValidationResult(
                status=ValidationStatus.FAILED,
                message="File does not exist",
                errors=[f"File not found: {file_path}"]
            )
        return ValidationResult(
            status=ValidationStatus.PASSED,
            message="File exists"
        )
    
    def _validate_file_size(self, file_path: Path) -> ValidationResult:
        """Validate file size / Валідувати розмір файлу"""
        size = file_path.stat().st_size
        max_size = self.rules["max_file_size"]
        
        if size > max_size:
            return ValidationResult(
                status=ValidationStatus.FAILED,
                message="File size exceeds limit",
                errors=[
                    f"File size ({size} bytes) exceeds maximum "
                    f"allowed size ({max_size} bytes)"
                ],
                suggestions=["Consider splitting the file into smaller parts"]
            )
        
        return ValidationResult(
            status=ValidationStatus.PASSED,
            message=f"File size is acceptable ({size} bytes)"
        )
    
    def _validate_file_extension(self, file_path: Path) -> ValidationResult:
        """Validate file extension / Валідувати розширення файлу"""
        extension = file_path.suffix.lower()
        allowed_extensions = self.rules["allowed_extensions"]
        
        if extension not in allowed_extensions:
            return ValidationResult(
                status=ValidationStatus.FAILED,
                message="Invalid file extension",
                errors=[f"Extension '{extension}' is not allowed"],
                suggestions=[
                    f"Use one of the allowed extensions: "
                    f"{', '.join(allowed_extensions)}"
                ]
            )
        
        return ValidationResult(
            status=ValidationStatus.PASSED,
            message=f"File extension is valid ({extension})"
        )
    
    def _validate_json_structure(
        self, 
        content: Dict[str, Any]
    ) -> ValidationResult:
        """Validate basic JSON structure / Валідувати базову структуру JSON"""
        errors = []
        warnings = []
        
        # Check for required fields
        required_fields = ["version", "name", "description"]
        for req_field in required_fields:
            if req_field not in content:
                errors.append(f"Missing required field: {req_field}")
        
        # Check version format
        if "version" in content:
            version = content["version"]
            if (not isinstance(version, str) or 
                    not re.match(r'^\d+\.\d+\.\d+$', version)):
                errors.append("Version must be in format X.Y.Z")
        
        # Check name format
        if "name" in content and self.rules["strict_naming"]:
            name = content["name"]
            if not re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', name):
                warnings.append(
                    "Name should start with a letter and contain only "
                    "alphanumeric characters, hyphens, and underscores"
                )
        
        # Check description length
        if "description" in content and self.rules["require_description"]:
            description = content["description"]
            if len(description) < 10:
                warnings.append(
                    "Description should be at least 10 characters long"
                )
        
        status = (
            ValidationStatus.FAILED if errors 
            else (ValidationStatus.WARNING if warnings 
                  else ValidationStatus.PASSED)
        )
        
        return ValidationResult(
            status=status,
            message="JSON structure validation completed",
            errors=errors,
            warnings=warnings
        )
    
    def _validate_mova_schema(
        self, 
        content: Dict[str, Any]
    ) -> ValidationResult:
        """Validate MOVA-specific schema / Валідувати MOVA-специфічну схему"""
        errors = []
        warnings = []
        
        # Check for MOVA-specific structure
        if "steps" not in content:
            errors.append("Missing 'steps' field required for MOVA files")
        else:
            steps = content["steps"]
            if not isinstance(steps, list) or len(steps) == 0:
                errors.append("'steps' must be a non-empty list")
            else:
                for i, step in enumerate(steps):
                    step_errors = self._validate_step(step, i)
                    errors.extend(step_errors)
        
        # Check for optional but recommended fields
        recommended_fields = ["author", "tags", "category"]
        for rec_field in recommended_fields:
            if rec_field not in content:
                warnings.append(f"Recommended field missing: {rec_field}")
        
        status = (
            ValidationStatus.FAILED if errors 
            else (ValidationStatus.WARNING if warnings 
                  else ValidationStatus.PASSED)
        )
        
        return ValidationResult(
            status=status,
            message="MOVA schema validation completed",
            errors=errors,
            warnings=warnings
        )
    
    def _validate_step(self, step: Dict[str, Any], index: int) -> List[str]:
        """Validate individual step / Валідувати окремий крок"""
        errors = []
        
        # Check required step fields
        if "type" not in step:
            errors.append(f"Step {index}: Missing 'type' field")
        elif step["type"] not in ["prompt", "condition", "action", "loop"]:
            errors.append(f"Step {index}: Invalid step type '{step['type']}'")
        
        if "name" not in step:
            errors.append(f"Step {index}: Missing 'name' field")
        
        # Validate step-specific fields
        if step.get("type") == "prompt":
            if "prompt" not in step:
                errors.append(
                    f"Step {index}: Prompt step missing 'prompt' field"
                )
            elif (not isinstance(step["prompt"], str) or 
                  len(step["prompt"].strip()) == 0):
                errors.append(
                    f"Step {index}: Prompt must be a non-empty string"
                )
        
        elif step.get("type") == "condition":
            if "condition" not in step:
                errors.append(
                    f"Step {index}: Condition step missing 'condition' field"
                )
            if "true_path" not in step or "false_path" not in step:
                errors.append(
                    f"Step {index}: Condition step missing "
                    f"'true_path' or 'false_path'"
                )
        
        return errors
    
    def _validate_business_rules(
        self, 
        content: Dict[str, Any]
    ) -> ValidationResult:
        """Validate business rules / Валідувати бізнес-правила"""
        errors = []
        warnings = []
        
        # Check for circular references in steps
        if "steps" in content:
            circular_refs = self._check_circular_references(content["steps"])
            if circular_refs:
                errors.extend([
                    f"Circular reference detected: {ref}" 
                    for ref in circular_refs
                ])
        
        # Check for unreachable steps
        if "steps" in content:
            unreachable = self._check_unreachable_steps(content["steps"])
            if unreachable:
                warnings.extend([
                    f"Unreachable step detected: {step}" 
                    for step in unreachable
                ])
        
        # Validate step depth
        if "steps" in content:
            max_depth = self._calculate_max_depth(content["steps"])
            if max_depth > self.rules["max_depth"]:
                errors.append(
                    f"Step depth ({max_depth}) exceeds maximum "
                    f"allowed depth ({self.rules['max_depth']})"
                )
        
        status = (
            ValidationStatus.FAILED if errors 
            else (ValidationStatus.WARNING if warnings 
                  else ValidationStatus.PASSED)
        )
        
        return ValidationResult(
            status=status,
            message="Business rules validation completed",
            errors=errors,
            warnings=warnings
        )
    
    def _validate_external_dependencies(
        self, 
        content: Dict[str, Any]
    ) -> ValidationResult:
        """Validate external dependencies / Валідувати зовнішні залежності"""
        errors = []
        warnings = []
        
        # Check for external tool references
        if "tools" in content:
            tools = content["tools"]
            for tool in tools:
                if not self._validate_tool_reference(tool):
                    warnings.append(
                        f"External tool reference may not be valid: {tool}"
                    )
        
        # Check for external API references
        api_refs = self._extract_api_references(content)
        for ref in api_refs:
            if not self._validate_api_reference(ref):
                warnings.append(
                    f"External API reference may not be valid: {ref}"
                )
        
        status = (
            ValidationStatus.FAILED if errors 
            else (ValidationStatus.WARNING if warnings 
                  else ValidationStatus.PASSED)
        )
        
        return ValidationResult(
            status=status,
            message="External dependencies validation completed",
            errors=errors,
            warnings=warnings
        )
    
    def _check_circular_references(
        self, 
        steps: List[Dict[str, Any]]
    ) -> List[str]:
        """Check for circular references in steps 
        Перевірити циклічні посилання в кроках"""
        # Simplified circular reference detection
        # In a real implementation, this would be more sophisticated
        return []
    
    def _check_unreachable_steps(
        self, 
        steps: List[Dict[str, Any]]
    ) -> List[str]:
        """Check for unreachable steps / Перевірити недосяжні кроки"""
        # Simplified unreachable step detection
        # In a real implementation, this would analyze the flow graph
        return []
    
    def _calculate_max_depth(self, steps: List[Dict[str, Any]]) -> int:
        """Calculate maximum step depth 
        Розрахувати максимальну глибину кроків"""
        # Simplified depth calculation
        # In a real implementation, this would traverse the step tree
        return 1
    
    def _validate_tool_reference(self, tool: str) -> bool:
        """Validate tool reference / Валідувати посилання на інструмент"""
        # Simplified tool validation
        # In a real implementation, this would check against a tool registry
        return True
    
    def _extract_api_references(self, content: Dict[str, Any]) -> List[str]:
        """Extract API references from content 
        Витягти посилання на API з контенту"""
        # Simplified API reference extraction
        # In a real implementation, this would parse the content 
        # more thoroughly
        return []
    
    def _validate_api_reference(self, ref: str) -> bool:
        """Validate API reference / Валідувати посилання на API"""
        # Simplified API validation
        # In a real implementation, this might make HTTP requests 
        # to validate endpoints
        return True
    
    def _create_report(
        self, 
        file_path: Path, 
        results: List[ValidationResult], 
        start_time: datetime
    ) -> ValidationReport:
        """Create validation report / Створити звіт валідації"""
        execution_time = (datetime.now() - start_time).total_seconds()
        
        # Determine overall status
        has_failed = any(r.status == ValidationStatus.FAILED for r in results)
        has_warnings = any(
            r.status == ValidationStatus.WARNING for r in results
        )
        
        overall_status = (
            ValidationStatus.FAILED if has_failed 
            else (ValidationStatus.WARNING if has_warnings 
                  else ValidationStatus.PASSED)
        )
        
        # Calculate summary statistics
        total_errors = sum(len(r.errors) for r in results)
        total_warnings = sum(len(r.warnings) for r in results)
        total_suggestions = sum(len(r.suggestions) for r in results)
        
        # Update stats
        self.stats["files_validated"] += 1
        self.stats["total_errors"] += total_errors
        self.stats["total_warnings"] += total_warnings
        self.stats["avg_execution_time"] = (
            (self.stats["avg_execution_time"] * 
             (self.stats["files_validated"] - 1) + execution_time) 
            / self.stats["files_validated"]
        )
        
        return ValidationReport(
            file_path=str(file_path),
            validation_level=self.validation_level,
            overall_status=overall_status,
            results=results,
            summary={
                "total_errors": total_errors,
                "total_warnings": total_warnings,
                "total_suggestions": total_suggestions,
                "checks_performed": len(results)
            },
            metadata={
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat(),
                "validator_version": "2.2"
            }
        )
    
    def _get_cached_validation(
        self, 
        cache_key: str
    ) -> Optional[ValidationReport]:
        """Get cached validation result 
        Отримати кешований результат валідації"""
        try:
            from .cache import get_cache
            cache = get_cache()
            cached_data = cache.get(cache_key)
            if cached_data:
                return ValidationReport.parse_raw(cached_data)
        except Exception as e:
            self.logger.warning(f"Failed to get cached validation: {e}")
        return None
    
    def _cache_validation_result(
        self, 
        cache_key: str, 
        report: ValidationReport
    ) -> None:
        """Cache validation result / Кешувати результат валідації"""
        try:
            from .cache import get_cache
            cache = get_cache()
            cache.set(cache_key, report.json(), self.cache_ttl)
        except Exception as e:
            self.logger.warning(f"Failed to cache validation result: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get validation statistics / Отримати статистику валідації"""
        return self.stats.copy()
    
    def reset_stats(self) -> None:
        """Reset validation statistics / Скинути статистику валідації"""
        self.stats = {
            "files_validated": 0,
            "total_errors": 0,
            "total_warnings": 0,
            "avg_execution_time": 0.0
        }


# Factory function
def create_validator(
    validation_level: ValidationLevel = ValidationLevel.STRICT
) -> MovaValidator:
    """Create validator instance / Створити екземпляр валідатора"""
    return MovaValidator(validation_level)


# Convenience functions
def validate_file(
    file_path: Union[str, Path], 
    level: ValidationLevel = ValidationLevel.STRICT
) -> ValidationReport:
    """Validate MOVA file with default settings 
    Валідувати MOVA файл з налаштуваннями за замовчуванням"""
    validator = create_validator(level)
    return validator.validate_file(file_path)


def validate_files(
    file_paths: List[Union[str, Path]], 
    level: ValidationLevel = ValidationLevel.STRICT
) -> List[ValidationReport]:
    """Validate multiple MOVA files / Валідувати кілька MOVA файлів"""
    validator = create_validator(level)
    return [validator.validate_file(path) for path in file_paths]