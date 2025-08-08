from dataclasses import dataclass
from typing import Any, Dict

@dataclass
class TaskDTO:
    task_id: str
    payload: Dict[str, Any]

__all__ = ["TaskDTO"]