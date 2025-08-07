"""
Data models for MOVA language
Моделі даних для мови MOVA
"""

from typing import Dict, List, Any, Optional, Union
from pydantic import BaseModel, Field
from enum import Enum


class IntentType(str, Enum):
    """Types of intents / Типи намірів"""
    GREETING = "greeting"
    QUESTION = "question" 
    COMMAND = "command"
    FEEDBACK = "feedback"
    CUSTOM = "custom"


class ActionType(str, Enum):
    """Types of actions / Типи дій"""
    PROMPT = "prompt"
    TOOL_API = "tool_api"
    CONDITION = "condition"
    END = "end"


class ComparisonOperator(str, Enum):
    """Comparison operators / Оператори порівняння"""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    CONTAINS = "contains"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"


class Intent(BaseModel):
    """Intent classification model / Модель класифікації наміру"""
    name: str = Field(..., description="Unique intent name / Унікальна назва наміру")
    patterns: List[str] = Field(..., description="Pattern phrases for recognition / Шаблонні фрази для розпізнавання")
    priority: int = Field(default=0, description="Intent priority / Пріоритет наміру")
    response_template: Optional[str] = Field(None, description="Response template / Шаблон відповіді")
    intent_type: IntentType = Field(default=IntentType.CUSTOM, description="Intent type / Тип наміру")


class Condition(BaseModel):
    """Condition model / Модель умови"""
    variable: str = Field(..., description="Variable to check / Змінна для перевірки")
    operator: ComparisonOperator = Field(..., description="Comparison operator / Оператор порівняння")
    value: Any = Field(..., description="Value to compare / Значення для порівняння")


class ProtocolStep(BaseModel):
    """Protocol step model / Модель кроку протоколу"""
    id: str = Field(..., description="Unique step identifier / Унікальний ідентифікатор кроку")
    action: ActionType = Field(..., description="Action type / Тип дії")
    prompt: Optional[str] = Field(None, description="Prompt text / Текст промпту")
    tool_api_id: Optional[str] = Field(None, description="API tool ID / ID API інструменту")
    conditions: Optional[List[Condition]] = Field(None, description="Conditions / Умови")
    next_step: Optional[str] = Field(None, description="Next step ID / ID наступного кроку")


class Protocol(BaseModel):
    """Protocol model / Модель протоколу"""
    name: str = Field(..., description="Protocol name / Назва протоколу")
    steps: List[ProtocolStep] = Field(..., description="Protocol steps / Кроки протоколу")
    description: Optional[str] = Field(None, description="Protocol description / Опис протоколу")


class ToolAPI(BaseModel):
    """API tool model / Модель API інструменту"""
    id: str = Field(..., description="Unique API ID / Унікальний ID API")
    name: str = Field(..., description="API name / Назва API")
    endpoint: str = Field(..., description="API endpoint / Кінцева точка API")
    method: str = Field(default="GET", description="HTTP method / HTTP метод")
    headers: Optional[Dict[str, str]] = Field(None, description="Request headers / Заголовки запиту")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Request parameters / Параметри запиту")
    authentication: Optional[Dict[str, str]] = Field(None, description="Authentication / Аутентифікація")


class Instruction(BaseModel):
    """Instruction model / Модель інструкції"""
    id: str = Field(..., description="Instruction ID / ID інструкції")
    title: str = Field(..., description="Instruction title / Заголовок інструкції")
    content: str = Field(..., description="Instruction content / Зміст інструкції")
    category: Optional[str] = Field(None, description="Instruction category / Категорія інструкції")
    tags: Optional[List[str]] = Field(None, description="Instruction tags / Теги інструкції")


class Profile(BaseModel):
    """User profile model / Модель профілю користувача"""
    user_id: str = Field(..., description="User ID / ID користувача")
    name: Optional[str] = Field(None, description="User name / Ім'я користувача")
    preferences: Dict[str, Any] = Field(default_factory=dict, description="User preferences / Налаштування користувача")
    language: str = Field(default="en", description="Preferred language / Бажана мова")
    timezone: Optional[str] = Field(None, description="User timezone / Часовий пояс користувача")


class Session(BaseModel):
    """Session model / Модель сесії"""
    session_id: str = Field(..., description="Session ID / ID сесії")
    user_id: str = Field(..., description="User ID / ID користувача")
    start_time: str = Field(..., description="Session start time / Час початку сесії")
    data: Dict[str, Any] = Field(default_factory=dict, description="Session data / Дані сесії")
    context: Dict[str, Any] = Field(default_factory=dict, description="Session context / Контекст сесії")
    active: bool = Field(default=True, description="Session active status / Статус активності сесії")


class Contract(BaseModel):
    """Contract model / Модель контракту"""
    contract_id: str = Field(..., description="Contract ID / ID контракту")
    parties: List[str] = Field(..., description="Contract parties / Сторони контракту")
    terms: Dict[str, Any] = Field(..., description="Contract terms / Умови контракту")
    conditions: List[Condition] = Field(default_factory=list, description="Contract conditions / Умови контракту")
    valid_from: str = Field(..., description="Contract validity start / Початок дії контракту")
    valid_until: Optional[str] = Field(None, description="Contract validity end / Кінець дії контракту") 