"""
Базовая ML инфраструктура для MOVA SDK

Предоставляет основные компоненты для работы с ML моделями:
- ModelRegistry: Реестр моделей
- FeatureExtractor: Извлечение признаков
- PredictionService: Сервис предсказаний
- MLFoundation: Основной класс ML системы
"""

import asyncio
import json
import logging
import os
import pickle
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from concurrent.futures import ThreadPoolExecutor

from .models import (
    MLModelConfig, 
    MLModelType, 
    MLPrediction, 
    IntentResult,
    EntityResult,
    ContextResult,
    SentimentResult
)


logger = logging.getLogger(__name__)


class ModelRegistry:
    """Реестр ML моделей"""
    
    def __init__(self, models_dir: str = "models"):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)
        self._models: Dict[str, MLModelConfig] = {}
        self._loaded_models: Dict[str, Any] = {}
        self._load_registry()
    
    def _load_registry(self) -> None:
        """Загрузка реестра моделей из файла"""
        registry_file = self.models_dir / "registry.json"
        if registry_file.exists():
            try:
                with open(registry_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for model_id, config_data in data.items():
                        self._models[model_id] = MLModelConfig(**config_data)
                logger.info(f"Загружен реестр с {len(self._models)} моделями")
            except Exception as e:
                logger.error(f"Ошибка загрузки реестра: {e}")
    
    def _save_registry(self) -> None:
        """Сохранение реестра моделей в файл"""
        registry_file = self.models_dir / "registry.json"
        try:
            data = {
                model_id: config.model_dump() 
                for model_id, config in self._models.items()
            }
            with open(registry_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info("Реестр моделей сохранен")
        except Exception as e:
            logger.error(f"Ошибка сохранения реестра: {e}")
    
    def register_model(self, model_id: str, config: MLModelConfig) -> None:
        """Регистрация новой модели"""
        self._models[model_id] = config
        self._save_registry()
        logger.info(f"Модель {model_id} зарегистрирована")
    
    def unregister_model(self, model_id: str) -> None:
        """Удаление модели из реестра"""
        if model_id in self._models:
            del self._models[model_id]
            if model_id in self._loaded_models:
                del self._loaded_models[model_id]
            self._save_registry()
            logger.info(f"Модель {model_id} удалена из реестра")
    
    def get_model_config(self, model_id: str) -> Optional[MLModelConfig]:
        """Получение конфигурации модели"""
        return self._models.get(model_id)
    
    def list_models(self) -> List[str]:
        """Список всех зарегистрированных моделей"""
        return list(self._models.keys())
    
    def is_model_loaded(self, model_id: str) -> bool:
        """Проверка загружена ли модель"""
        return model_id in self._loaded_models
    
    def load_model(self, model_id: str) -> Optional[Any]:
        """Загрузка модели в память"""
        if model_id in self._loaded_models:
            return self._loaded_models[model_id]
        
        config = self.get_model_config(model_id)
        if not config:
            logger.error(f"Модель {model_id} не найдена в реестре")
            return None
        
        try:
            # Здесь будет логика загрузки различных типов моделей
            model = self._load_model_by_type(config)
            self._loaded_models[model_id] = model
            logger.info(f"Модель {model_id} загружена")
            return model
        except Exception as e:
            logger.error(f"Ошибка загрузки модели {model_id}: {e}")
            return None
    
    def _load_model_by_type(self, config: MLModelConfig) -> Any:
        """Загрузка модели по типу"""
        model_path = Path(config.model_path)
        
        if config.model_type == MLModelType.BERT:
            return self._load_bert_model(config)
        elif config.model_type == MLModelType.ROBERTA:
            return self._load_roberta_model(config)
        elif config.model_type == MLModelType.SPACY:
            return self._load_spacy_model(config)
        elif config.model_type == MLModelType.TRANSFORMER:
            return self._load_transformer_model(config)
        else:
            raise ValueError(f"Неподдерживаемый тип модели: {config.model_type}")
    
    def _load_bert_model(self, config: MLModelConfig) -> Any:
        """Загрузка BERT модели (заглушка)"""
        # TODO: Реализовать загрузку BERT модели
        logger.info(f"Загрузка BERT модели: {config.model_name}")
        return {"type": "bert", "config": config.model_dump()}
    
    def _load_roberta_model(self, config: MLModelConfig) -> Any:
        """Загрузка RoBERTa модели (заглушка)"""
        # TODO: Реализовать загрузку RoBERTa модели
        logger.info(f"Загрузка RoBERTa модели: {config.model_name}")
        return {"type": "roberta", "config": config.model_dump()}
    
    def _load_spacy_model(self, config: MLModelConfig) -> Any:
        """Загрузка spaCy модели (заглушка)"""
        # TODO: Реализовать загрузку spaCy модели
        logger.info(f"Загрузка spaCy модели: {config.model_name}")
        return {"type": "spacy", "config": config.model_dump()}
    
    def _load_transformer_model(self, config: MLModelConfig) -> Any:
        """Загрузка Transformer модели (заглушка)"""
        # TODO: Реализовать загрузку Transformer модели
        logger.info(f"Загрузка Transformer модели: {config.model_name}")
        return {"type": "transformer", "config": config.model_dump()}


class FeatureExtractor:
    """Извлечение признаков из текста"""
    
    def __init__(self):
        self._extractors: Dict[str, Any] = {}
        self._setup_extractors()
    
    def _setup_extractors(self) -> None:
        """Настройка экстракторов признаков"""
        # TODO: Реализовать различные экстракторы
        self._extractors = {
            "basic": self._extract_basic_features,
            "bert": self._extract_bert_features,
            "spacy": self._extract_spacy_features
        }
    
    def extract_features(self, text: str, extractor_type: str = "basic") -> Dict[str, Any]:
        """Извлечение признаков из текста"""
        extractor = self._extractors.get(extractor_type)
        if not extractor:
            raise ValueError(f"Неизвестный тип экстрактора: {extractor_type}")
        
        return extractor(text)
    
    def _extract_basic_features(self, text: str) -> Dict[str, Any]:
        """Базовое извлечение признаков"""
        return {
            "length": len(text),
            "word_count": len(text.split()),
            "char_count": len(text.replace(" ", "")),
            "has_numbers": any(c.isdigit() for c in text),
            "has_uppercase": any(c.isupper() for c in text),
            "has_special_chars": any(not c.isalnum() and not c.isspace() for c in text)
        }
    
    def _extract_bert_features(self, text: str) -> Dict[str, Any]:
        """Извлечение BERT признаков (заглушка)"""
        # TODO: Реализовать BERT токенизацию и эмбеддинги
        return {
            "bert_embeddings": [0.0] * 768,  # Заглушка
            "bert_tokens": text.split()[:512]  # Заглушка
        }
    
    def _extract_spacy_features(self, text: str) -> Dict[str, Any]:
        """Извлечение spaCy признаков (заглушка)"""
        # TODO: Реализовать spaCy обработку
        return {
            "spacy_tokens": text.split(),
            "spacy_pos": ["NOUN"] * len(text.split()),  # Заглушка
            "spacy_entities": []  # Заглушка
        }


class PredictionService:
    """Сервис для выполнения предсказаний"""
    
    def __init__(self, model_registry: ModelRegistry, feature_extractor: FeatureExtractor):
        self.model_registry = model_registry
        self.feature_extractor = feature_extractor
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    async def predict_intent(self, text: str, model_id: str = "intent_classifier") -> Optional[IntentResult]:
        """Предсказание намерения"""
        try:
            model = self.model_registry.load_model(model_id)
            if not model:
                return None
            
            # Feature extraction / Витяг ознак
            features = self.feature_extractor.extract_features(text, "bert")
            
            # Выполнение предсказания в отдельном потоке
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.executor, 
                self._predict_intent_sync, 
                model, 
                text, 
                features
            )
            
            return result
        except Exception as e:
            logger.error(f"Ошибка предсказания намерения: {e}")
            return None
    
    def _predict_intent_sync(self, model: Any, text: str, features: Dict[str, Any]) -> IntentResult:
        """Синхронное предсказание намерения (заглушка)"""
        # TODO: Реализовать реальное предсказание
        from .models import IntentType
        
        # Простая логика на основе ключевых слов
        text_lower = text.lower()
        if "регистрация" in text_lower or "зарегистрировать" in text_lower:
            intent = IntentType.USER_REGISTRATION
            confidence = 0.95
        elif "войти" in text_lower or "логин" in text_lower:
            intent = IntentType.USER_LOGIN
            confidence = 0.90
        elif "валидация" in text_lower or "проверить" in text_lower:
            intent = IntentType.DATA_VALIDATION
            confidence = 0.85
        else:
            intent = IntentType.HELP_REQUEST
            confidence = 0.70
        
        return IntentResult(
            intent=intent,
            confidence=confidence,
            text=text,
            metadata={"model": model.get("type", "unknown")}
        )
    
    async def predict_entities(self, text: str, model_id: str = "entity_extractor") -> Optional[EntityResult]:
        """Предсказание сущностей"""
        try:
            model = self.model_registry.load_model(model_id)
            if not model:
                return None
            
            features = self.feature_extractor.extract_features(text, "spacy")
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.executor,
                self._predict_entities_sync,
                model,
                text,
                features
            )
            
            return result
        except Exception as e:
            logger.error(f"Ошибка предсказания сущностей: {e}")
            return None
    
    def _predict_entities_sync(self, model: Any, text: str, features: Dict[str, Any]) -> EntityResult:
        """Синхронное предсказание сущностей (заглушка)"""
        # TODO: Реализовать реальное извлечение сущностей
        from .models import Entity, EntityType
        
        entities = []
        
        # Простое извлечение email
        import re
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        for match in re.finditer(email_pattern, text):
            entities.append(Entity(
                text=match.group(),
                entity_type=EntityType.EMAIL,
                start=match.start(),
                end=match.end(),
                confidence=0.98
            ))
        
        return EntityResult(
            entities=entities,
            text=text,
            metadata={"model": model.get("type", "unknown")}
        )
    
    async def predict_sentiment(self, text: str, model_id: str = "sentiment_analyzer") -> Optional[SentimentResult]:
        """Predict sentiment / Передбачення настроєнь"""
        try:
            model = self.model_registry.load_model(model_id)
            if not model:
                return None
            
            features = self.feature_extractor.extract_features(text, "bert")
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.executor,
                self._predict_sentiment_sync,
                model,
                text,
                features
            )
            
            return result
        except Exception as e:
            logger.error(f"Ошибка предсказания настроения: {e}")
            return None
    
    def _predict_sentiment_sync(self, model: Any, text: str, features: Dict[str, Any]) -> SentimentResult:
        """Синхронное предсказание настроения (заглушка)"""
        # TODO: Реализовать реальный анализ настроений
        from .models import SentimentType
        
        text_lower = text.lower()
        positive_words = ["хорошо", "отлично", "супер", "класс", "нравится"]
        negative_words = ["плохо", "ужасно", "не нравится", "проблема", "ошибка"]
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            sentiment = SentimentType.POSITIVE
            confidence = 0.85
            positive_score = 0.85
            negative_score = 0.10
            neutral_score = 0.05
        elif negative_count > positive_count:
            sentiment = SentimentType.NEGATIVE
            confidence = 0.80
            positive_score = 0.10
            negative_score = 0.80
            neutral_score = 0.10
        else:
            sentiment = SentimentType.NEUTRAL
            confidence = 0.70
            positive_score = 0.30
            negative_score = 0.30
            neutral_score = 0.40
        
        return SentimentResult(
            sentiment=sentiment,
            confidence=confidence,
            text=text,
            positive_score=positive_score,
            negative_score=negative_score,
            neutral_score=neutral_score,
            metadata={"model": model.get("type", "unknown")}
        )


class MLFoundation:
    """Основной класс ML системы"""
    
    def __init__(self, models_dir: str = "models"):
        self.model_registry = ModelRegistry(models_dir)
        self.feature_extractor = FeatureExtractor()
        self.prediction_service = PredictionService(self.model_registry, self.feature_extractor)
        self._setup_default_models()
    
    def _setup_default_models(self) -> None:
        """Настройка моделей по умолчанию"""
        from .models import MLModelConfig, MLModelType
        
        # Регистрация моделей по умолчанию
        default_models = {
            "intent_classifier": MLModelConfig(
                model_type=MLModelType.BERT,
                model_path="models/intent_classifier/",
                model_name="bert-base-multilingual-cased",
                confidence_threshold=0.8
            ),
            "entity_extractor": MLModelConfig(
                model_type=MLModelType.SPACY,
                model_path="models/entity_extractor/",
                model_name="ru_core_news_sm",
                confidence_threshold=0.7
            ),
            "sentiment_analyzer": MLModelConfig(
                model_type=MLModelType.BERT,
                model_path="models/sentiment_analyzer/",
                model_name="bert-base-multilingual-cased",
                confidence_threshold=0.75
            )
        }
        
        for model_id, config in default_models.items():
            if model_id not in self.model_registry.list_models():
                self.model_registry.register_model(model_id, config)
    
    async def analyze_text(self, text: str, session_id: Optional[str] = None) -> MLPrediction:
        """Комплексный анализ текста"""
        start_time = datetime.utcnow()
        
        # Параллельное выполнение всех предсказаний
        intent_task = self.prediction_service.predict_intent(text)
        entities_task = self.prediction_service.predict_entities(text)
        sentiment_task = self.prediction_service.predict_sentiment(text)
        
        intent_result, entities_result, sentiment_result = await asyncio.gather(
            intent_task, entities_task, sentiment_task
        )
        
        end_time = datetime.utcnow()
        processing_time = (end_time - start_time).total_seconds()
        
        return MLPrediction(
            intent=intent_result,
            entities=entities_result,
            sentiment=sentiment_result,
            text=text,
            session_id=session_id,
            processing_time=processing_time,
            metadata={
                "models_used": ["intent_classifier", "entity_extractor", "sentiment_analyzer"],
                "timestamp": start_time.isoformat()
            }
        )
    
    def get_model_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Получение информации о модели"""
        config = self.model_registry.get_model_config(model_id)
        if not config:
            return None
        
        return {
            "model_id": model_id,
            "config": config.model_dump(),
            "loaded": self.model_registry.is_model_loaded(model_id),
            "path": config.model_path
        }
    
    def list_available_models(self) -> List[Dict[str, Any]]:
        """Список всех доступных моделей"""
        models = []
        for model_id in self.model_registry.list_models():
            model_info = self.get_model_info(model_id)
            if model_info:
                models.append(model_info)
        return models 