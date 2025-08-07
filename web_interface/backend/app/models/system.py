"""
System models
Системні моделі
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from .common import StatusEnum


class ComponentStatus(BaseModel):
    """Статус компонента"""
    name: str
    status: StatusEnum
    version: Optional[str] = None
    uptime: Optional[float] = None
    details: Optional[Dict[str, Any]] = None


class SystemStatus(BaseModel):
    """Статус системи"""
    overall_status: StatusEnum
    version: str
    uptime: float
    components: List[ComponentStatus]
    timestamp: datetime = Field(default_factory=datetime.now)


class RedisStatus(BaseModel):
    """Статус Redis"""
    connected: bool
    url: str
    session_count: int
    memory_usage: Optional[float] = None
    error: Optional[str] = None


class CacheStatus(BaseModel):
    """Статус кешу"""
    enabled: bool
    cache_dir: str
    total_files: int
    total_size: int
    hit_rate: Optional[float] = None


class WebhookStatus(BaseModel):
    """Статус webhook"""
    enabled: bool
    endpoints_count: int
    last_event: Optional[datetime] = None
    error_rate: Optional[float] = None


class MLStatus(BaseModel):
    """Статус ML системи"""
    enabled: bool
    models_count: int
    active_models: List[str]
    last_training: Optional[datetime] = None
    accuracy: Optional[float] = None


class FileInfo(BaseModel):
    """Інформація про файл"""
    name: str
    size: int
    type: str
    modified: datetime
    path: str


class FileUploadResponse(BaseModel):
    """Відповідь на завантаження файлу"""
    filename: str
    size: int
    path: str
    uploaded_at: datetime = Field(default_factory=datetime.now)


class FileListResponse(BaseModel):
    """Відповідь зі списком файлів"""
    files: List[Dict[str, Any]]
    total: int
    directory: str


class LogEntry(BaseModel):
    """Запис логу"""
    timestamp: datetime
    level: str
    message: str
    module: Optional[str] = None
    function: Optional[str] = None


class LogResponse(BaseModel):
    """Відповідь з логами"""
    entries: List[LogEntry]
    total: int
    level_filter: Optional[str] = None


class MetricsData(BaseModel):
    """Дані метрик"""
    timestamp: datetime
    value: float
    label: str
    category: str


class MetricsResponse(BaseModel):
    """Відповідь з метриками"""
    metrics: List[MetricsData]
    time_range: str
    aggregation: str 