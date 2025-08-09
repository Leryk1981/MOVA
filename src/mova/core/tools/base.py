"""
Base tool classes for MOVA SDK
Базові класи інструментів для MOVA SDK
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


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