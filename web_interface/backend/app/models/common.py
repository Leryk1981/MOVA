"""
Common data models
Спільні моделі даних
"""

from typing import Optional, Any, Dict, List
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class StatusEnum(str, Enum):
    """Статус операції"""
    SUCCESS = "success"
    ERROR = "error"
    PENDING = "pending"
    RUNNING = "running"


class PriorityEnum(str, Enum):
    """Пріоритет"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ResponseModel(BaseModel):
    """Базова модель відповіді"""
    status: StatusEnum
    message: str
    data: Optional[Any] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class ErrorModel(BaseModel):
    """Модель помилки"""
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None


class PaginationModel(BaseModel):
    """Модель пагінації"""
    page: int = Field(default=1, ge=1)
    size: int = Field(default=10, ge=1, le=100)
    total: int = Field(default=0, ge=0)
    pages: int = Field(default=0, ge=0)


class PaginatedResponse(BaseModel):
    """Пагінована відповідь"""
    items: List[Any]
    pagination: PaginationModel





class SystemInfo(BaseModel):
    """Інформація про систему"""
    version: str
    uptime: float
    memory_usage: float
    cpu_usage: float
    disk_usage: float
    active_connections: int 