"""
Configuration module tests
Тести для модуля конфігурації
"""

# Import config test modules
from .test_schema import TestConfigSchema
from .test_loader import TestConfigLoader

__all__ = [
    "TestConfigSchema",
    "TestConfigLoader"
]