"""
ML Models and data types for MOVA SDK
ML моделі та типи даних для MOVA SDK

Defines data structures for ML predictions, results and configuration.
Визначає структури даних для ML передбачень, результатів та конфігурації.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field


class MLModelType(str, Enum):
    """ML model types / Типи ML моделей"""
    BERT = "bert"
    ROBERTA = "roberta"
    SPACY = "spacy"
    TRANSFORMER = "transformer"
    CUSTOM = "custom"


class IntentType(str, Enum):
    """Intent types / Типи намірів"""
    USER_REGISTRATION = "user_registration"
    USER_LOGIN = "user_login"
    DATA_VALIDATION = "data_validation"
    CONFIG_UPDATE = "config_update"
    CACHE_OPERATION = "cache_operation"
    REDIS_OPERATION = "redis_operation"
    LLM_REQUEST = "llm_request"
    ERROR_REPORT = "error_report"
    HELP_REQUEST = "help_request"
    CUSTOM = "custom"


class EntityType(str, Enum):
    """Entity types / Типи сутностей"""
    PERSON = "PERSON"
    EMAIL = "EMAIL"
    PHONE = "PHONE"
    ORGANIZATION = "ORGANIZATION"
    LOCATION = "LOCATION"
    DATE = "DATE"
    TIME = "TIME"
    MONEY = "MONEY"
    PERCENT = "PERCENT"
    CUSTOM = "CUSTOM"


class SentimentType(str, Enum):
    """Sentiment types / Типи настроєнь"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"


class MLModelConfig(BaseModel):
    """ML model configuration / Конфігурація ML моделі"""
    model_type: MLModelType = Field(..., description="Model type / Тип моделі")
    model_path: str = Field(..., description="Model path / Шлях до моделі")
    model_name: str = Field(..., description="Model name / Назва моделі")
    version: str = Field(default="1.0.0", description="Model version / Версія моделі")
    confidence_threshold: float = Field(default=0.8, description="Confidence threshold / Поріг впевненості")
    fallback_to_rules: bool = Field(default=True, description="Fallback to rules / Fallback до правил")
    max_length: int = Field(default=512, description="Maximum input length / Максимальна довжина входу")
    batch_size: int = Field(default=32, description="Batch size / Розмір батчу")
    device: str = Field(default="cpu", description="Device for computation / Пристрій для обчислень")
    
    class Config:
        json_schema_extra = {
            "example": {
                "model_type": "bert",
                "model_path": "models/intent_classifier/",
                "model_name": "bert-base-multilingual-cased",
                "version": "1.0.0",
                "confidence_threshold": 0.8,
                "max_length": 512,
                "batch_size": 32,
                "device": "cpu"
            }
        }


class IntentResult(BaseModel):
    """Intent recognition result / Результат розпізнавання наміру"""
    intent: IntentType = Field(..., description="Recognized intent / Розпізнаний намір")
    confidence: float = Field(..., description="Prediction confidence / Впевненість у передбаченні")
    text: str = Field(..., description="Source text / Вихідний текст")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp / Часова мітка")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata / Додаткові метадані")
    
    class Config:
        json_schema_extra = {
            "example": {
                "intent": "user_registration",
                "confidence": 0.95,
                "text": "Зарегистрируй меня как пользователя",
                "timestamp": "2024-01-01T12:00:00Z",
                "metadata": {"model": "bert-base-multilingual-cased"}
            }
        }


class Entity(BaseModel):
    """Extracted entity / Витягнута сутність"""
    text: str = Field(..., description="Entity text / Текст сутності")
    entity_type: EntityType = Field(..., description="Entity type / Тип сутності")
    start: int = Field(..., description="Start position / Початкова позиція")
    end: int = Field(..., description="End position / Кінцева позиція")
    confidence: float = Field(..., description="Extraction confidence / Впевненість у витягу")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "john@example.com",
                "entity_type": "EMAIL",
                "start": 15,
                "end": 30,
                "confidence": 0.98
            }
        }


class EntityResult(BaseModel):
    """Entity extraction result / Результат витягу сутностей"""
    entities: List[Entity] = Field(default_factory=list, description="List of extracted entities / Список витягнутих сутностей")
    text: str = Field(..., description="Source text / Вихідний текст")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp / Часова мітка")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata / Додаткові метадані")
    
    class Config:
        json_schema_extra = {
            "example": {
                "entities": [
                    {
                        "text": "john@example.com",
                        "entity_type": "EMAIL",
                        "start": 15,
                        "end": 30,
                        "confidence": 0.98
                    }
                ],
                "text": "Мой email john@example.com",
                "timestamp": "2024-01-01T12:00:00Z",
                "metadata": {"model": "spacy"}
            }
        }


class ContextResult(BaseModel):
    """Context analysis result / Результат аналізу контексту"""
    session_id: str = Field(..., description="Session ID / ID сесії")
    user_id: Optional[str] = Field(default=None, description="User ID / ID користувача")
    conversation_history: List[str] = Field(default_factory=list, description="Conversation history / Історія розмови")
    user_preferences: Dict[str, Any] = Field(default_factory=dict, description="User preferences / Переваги користувача")
    context_score: float = Field(..., description="Context score / Оцінка контексту")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp / Часова мітка")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata / Додаткові метадані")
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "session_123",
                "user_id": "user_456",
                "conversation_history": ["Привет", "Как дела?"],
                "user_preferences": {"language": "ru"},
                "context_score": 0.85,
                "timestamp": "2024-01-01T12:00:00Z",
                "metadata": {"model": "transformer"}
            }
        }


class SentimentResult(BaseModel):
    """Sentiment analysis result / Результат аналізу настроєнь"""
    sentiment: SentimentType = Field(..., description="Sentiment type / Тип настроєнь")
    confidence: float = Field(..., description="Prediction confidence / Впевненість у передбаченні")
    text: str = Field(..., description="Source text / Вихідний текст")
    positive_score: float = Field(..., description="Positive score / Оцінка позитивності")
    negative_score: float = Field(..., description="Negative score / Оцінка негативності")
    neutral_score: float = Field(..., description="Neutral score / Оцінка нейтральності")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp / Часова мітка")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata / Додаткові метадані")
    
    class Config:
        json_schema_extra = {
            "example": {
                "sentiment": "positive",
                "confidence": 0.92,
                "text": "Отличная работа!",
                "positive_score": 0.92,
                "negative_score": 0.05,
                "neutral_score": 0.03,
                "timestamp": "2024-01-01T12:00:00Z",
                "metadata": {"model": "bert"}
            }
        }


class MLPrediction(BaseModel):
    """Comprehensive ML prediction result / Комплексний результат ML передбачення"""
    intent: Optional[IntentResult] = Field(default=None, description="Intent recognition result / Результат розпізнавання наміру")
    entities: Optional[EntityResult] = Field(default=None, description="Entity extraction result / Результат витягу сутностей")
    context: Optional[ContextResult] = Field(default=None, description="Context analysis result / Результат аналізу контексту")
    sentiment: Optional[SentimentResult] = Field(default=None, description="Sentiment analysis result / Результат аналізу настроєнь")
    text: str = Field(..., description="Source text / Вихідний текст")
    session_id: Optional[str] = Field(default=None, description="Session ID / ID сесії")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp / Часова мітка")
    processing_time: float = Field(..., description="Processing time in seconds / Час обробки в секундах")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata / Додаткові метадані")
    
    class Config:
        json_schema_extra = {
            "example": {
                "intent": {
                    "intent": "user_registration",
                    "confidence": 0.95,
                    "text": "Зарегистрируй меня как пользователя",
                    "timestamp": "2024-01-01T12:00:00Z"
                },
                "entities": {
                    "entities": [
                        {
                            "text": "john@example.com",
                            "entity_type": "EMAIL",
                            "start": 15,
                            "end": 30,
                            "confidence": 0.98
                        }
                    ],
                    "text": "Зарегистрируй меня как пользователя john@example.com",
                    "timestamp": "2024-01-01T12:00:00Z"
                },
                "sentiment": {
                    "sentiment": "positive",
                    "confidence": 0.85,
                    "text": "Зарегистрируй меня как пользователя",
                    "positive_score": 0.85,
                    "negative_score": 0.10,
                    "neutral_score": 0.05,
                    "timestamp": "2024-01-01T12:00:00Z"
                },
                "text": "Зарегистрируй меня как пользователя john@example.com",
                "session_id": "session_123",
                "timestamp": "2024-01-01T12:00:00Z",
                "processing_time": 0.15,
                "metadata": {"models_used": ["bert", "spacy"]}
            }
        }


class TrainingExample(BaseModel):
    """Training example / Приклад для навчання моделі"""
    text: str = Field(..., description="Example text / Текст прикладу")
    intent: Optional[IntentType] = Field(default=None, description="Expected intent / Очікуваний намір")
    entities: Optional[List[Entity]] = Field(default=None, description="Expected entities / Очікувані сутності")
    sentiment: Optional[SentimentType] = Field(default=None, description="Expected sentiment / Очікувані настрої")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Example context / Контекст прикладу")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "Зарегистрируй меня как пользователя john@example.com",
                "intent": "user_registration",
                "entities": [
                    {
                        "text": "john@example.com",
                        "entity_type": "EMAIL",
                        "start": 15,
                        "end": 30,
                        "confidence": 1.0
                    }
                ],
                "sentiment": "positive",
                "context": {"session_id": "session_123"}
            }
        }


class TrainingConfig(BaseModel):
    """Training configuration / Конфігурація навчання"""
    model_type: MLModelType = Field(..., description="Model type for training / Тип моделі для навчання")
    training_data: List[TrainingExample] = Field(..., description="Training data / Дані для навчання")
    validation_data: Optional[List[TrainingExample]] = Field(default=None, description="Validation data / Дані для валідації")
    epochs: int = Field(default=10, description="Number of epochs / Кількість епох")
    learning_rate: float = Field(default=2e-5, description="Learning rate / Швидкість навчання")
    batch_size: int = Field(default=16, description="Batch size / Розмір батчу")
    max_length: int = Field(default=512, description="Maximum length / Максимальна довжина")
    save_path: str = Field(..., description="Path for saving model / Шлях для збереження моделі")
    
    class Config:
        json_schema_extra = {
            "example": {
                "model_type": "bert",
                "training_data": [
                    {
                        "text": "Зарегистрируй меня",
                        "intent": "user_registration"
                    }
                ],
                "epochs": 10,
                "learning_rate": 2e-5,
                "batch_size": 16,
                "max_length": 512,
                "save_path": "models/intent_classifier/"
            }
        } 