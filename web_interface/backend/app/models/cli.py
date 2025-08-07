"""
CLI command models
Моделі для CLI команд
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from .common import StatusEnum, PriorityEnum


class CLIRunRequest(BaseModel):
    """Запит на виконання CLI команди"""
    command: str
    file_path: Optional[str] = None
    options: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None


class CLIRunResponse(BaseModel):
    """Відповідь на виконання CLI команди"""
    command: str
    status: StatusEnum
    output: Optional[str] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None
    session_id: Optional[str] = None


class ParseRequest(BaseModel):
    """Запит на парсинг файлу"""
    file_path: str
    validate: bool = False
    output: Optional[str] = None


class ValidateRequest(BaseModel):
    """Запит на валідацію файлу"""
    file_path: str
    advanced: bool = False
    detailed: bool = False
    output: Optional[str] = None


class RunRequest(BaseModel):
    """Запит на запуск протоколу"""
    file_path: str
    session_id: Optional[str] = None
    verbose: bool = False
    step_by_step: bool = False
    redis_url: Optional[str] = None
    llm_api_key: Optional[str] = None
    llm_model: Optional[str] = None
    webhook_enabled: bool = False
    cache_enabled: bool = False
    ml_enabled: bool = False


class TestRequest(BaseModel):
    """Запит на тестування"""
    file_path: str
    step_id: Optional[str] = None
    api_id: Optional[str] = None
    verbose: bool = False
    dry_run: bool = False


class AnalyzeRequest(BaseModel):
    """Запит на аналіз"""
    file_path: str
    session_id: str = "web_session"
    output: Optional[str] = None
    verbose: bool = False


class DiagnoseRequest(BaseModel):
    """Запит на діагностику"""
    error_message: str
    session_id: str = "web_session"
    output: Optional[str] = None
    verbose: bool = False


class RedisSessionsRequest(BaseModel):
    """Запит на отримання сесій Redis"""
    redis_url: str = "redis://localhost:6379"
    session_id: Optional[str] = None
    pattern: str = "mova:session:*"


class RedisClearRequest(BaseModel):
    """Запит на очищення Redis"""
    redis_url: str = "redis://localhost:6379"
    session_id: Optional[str] = None
    pattern: str = "mova:session:*"
    confirm: bool = False


class CacheInfoRequest(BaseModel):
    """Запит на інформацію про кеш"""
    key: Optional[str] = None
    stats: bool = False


class CacheClearRequest(BaseModel):
    """Запит на очищення кешу"""
    key: Optional[str] = None
    confirm: bool = False


class WebhookTestRequest(BaseModel):
    """Запит на тестування webhook"""
    url: str
    event_type: str
    data: Optional[Dict[str, Any]] = None


class MLModelsRequest(BaseModel):
    """Запит на отримання ML моделей"""
    model_id: Optional[str] = None
    list_models: bool = False


class MLEvaluateRequest(BaseModel):
    """Запит на оцінку ML моделі"""
    model_id: str
    test_data: str  # JSON string
    output: Optional[str] = None


class RecommendationSummaryRequest(BaseModel):
    """Запит на зведення рекомендацій"""
    session_id: str = "web_session"
    output: Optional[str] = None 