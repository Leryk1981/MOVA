from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class TaskDTO:
    task_id: str
    payload: Dict[str, Any]


@dataclass
class CacheItemDTO:
    key: str
    value: Any


__all__ = ["TaskDTO", "CacheItemDTO"]