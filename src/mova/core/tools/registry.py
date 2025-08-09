"""
Tool registry for MOVA SDK
Реєстр інструментів для MOVA SDK
"""

from typing import Dict, List, Optional, Any
from .base import BaseTool


class ToolRegistry:
    """Реєстр інструментів"""
    
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
    
    def register(self, tool: BaseTool):
        """Зареєструвати інструмент"""
        self._tools[tool.name] = tool
    
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
    
    def unregister(self, name: str) -> bool:
        """Видалити інструмент з реєстру"""
        if name in self._tools:
            del self._tools[name]
            return True
        return False
    
    def clear(self):
        """Очистити реєстр"""
        self._tools.clear()
    
    def size(self) -> int:
        """Отримати кількість інструментів у реєстрі"""
        return len(self._tools)