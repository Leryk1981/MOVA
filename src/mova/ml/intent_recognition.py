"""
Система распознавания намерений для MOVA SDK

Предоставляет функциональность для классификации намерений пользователя:
- IntentClassifier: Классификатор намерений
- IntentRecognitionSystem: Система распознавания намерений
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from .models import IntentResult, IntentType, MLModelConfig, MLModelType
from .foundation import ModelRegistry, FeatureExtractor


logger = logging.getLogger(__name__)


class IntentClassifier:
    """Классификатор намерений"""
    
    def __init__(self, model_config: MLModelConfig):
        self.config = model_config
        self.model = None
        self._load_model()
    
    def _load_model(self) -> None:
        """Load classifier model / Завантаження моделі класифікатора"""
        try:
            if self.config.model_type == MLModelType.BERT:
                self.model = self._load_bert_model()
            elif self.config.model_type == MLModelType.ROBERTA:
                self.model = self._load_roberta_model()
            else:
                logger.warning(f"Неподдерживаемый тип модели: {self.config.model_type}")
                self.model = self._load_fallback_model()
        except Exception as e:
            logger.error(f"Ошибка загрузки модели: {e}")
            self.model = self._load_fallback_model()
    
    def _load_bert_model(self) -> Dict[str, Any]:
        """Загрузка BERT модели (заглушка)"""
        # TODO: Implement real BERT model loading / Реалізувати завантаження реальної BERT моделі
        logger.info(f"Загрузка BERT модели: {self.config.model_name}")
        return {
            "type": "bert",
            "name": self.config.model_name,
            "config": self.config.model_dump(),
            "loaded": True
        }
    
    def _load_roberta_model(self) -> Dict[str, Any]:
        """Загрузка RoBERTa модели (заглушка)"""
        # TODO: Реализовать загрузку реальной RoBERTa модели
        logger.info(f"Загрузка RoBERTa модели: {self.config.model_name}")
        return {
            "type": "roberta",
            "name": self.config.model_name,
            "config": self.config.model_dump(),
            "loaded": True
        }
    
    def _load_fallback_model(self) -> Dict[str, Any]:
        """Загрузка fallback модели (правила)"""
        logger.info("Загрузка fallback модели (правила)")
        return {
            "type": "rules",
            "name": "fallback_rules",
            "config": self.config.model_dump(),
            "loaded": True
        }
    
    async def classify(self, text: str) -> IntentResult:
        """Classify intent / Класифікація наміру"""
        try:
            if self.model["type"] in ["bert", "roberta"]:
                return await self._classify_with_ml_model(text)
            else:
                return await self._classify_with_rules(text)
        except Exception as e:
            logger.error(f"Ошибка классификации: {e}")
            return await self._classify_with_rules(text)
    
    async def _classify_with_ml_model(self, text: str) -> IntentResult:
        """Классификация с использованием ML модели (заглушка)"""
        # TODO: Реализовать реальную классификацию с ML моделью
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, self._classify_sync, text)
        return result
    
    def _classify_sync(self, text: str) -> IntentResult:
        """Синхронная классификация (заглушка)"""
        # Простая логика на основе ключевых слов
        text_lower = text.lower()
        
        # Определение намерения по ключевым словам
        intent_keywords = {
            IntentType.USER_REGISTRATION: [
                "регистрация", "зарегистрировать", "регистрировать", "создать аккаунт",
                "новый пользователь", "записаться", "подписаться"
            ],
            IntentType.USER_LOGIN: [
                "войти", "логин", "авторизация", "авторизоваться", "вход",
                "войти в систему", "подключиться"
            ],
            IntentType.DATA_VALIDATION: [
                "валидация", "проверить", "проверка", "валидировать",
                "корректность", "правильность", "валидность"
            ],
            IntentType.CONFIG_UPDATE: [
                "настройки", "конфигурация", "изменить", "обновить",
                "настроить", "параметры", "конфиг"
            ],
            IntentType.CACHE_OPERATION: [
                "кэш", "кеш", "кэширование", "очистить кэш",
                "сбросить кэш", "кэш операции"
            ],
            IntentType.REDIS_OPERATION: [
                "redis", "редис", "база данных", "хранилище",
                "операции redis", "redis операции"
            ],
            IntentType.LLM_REQUEST: [
                "искусственный интеллект", "ai", "модель", "генерация",
                "ответ", "анализ", "обработка текста"
            ],
            IntentType.ERROR_REPORT: [
                "ошибка", "проблема", "не работает", "сломалось",
                "баг", "отчет об ошибке", "сообщить об ошибке"
            ]
        }
        
        # Поиск наиболее подходящего намерения
        best_intent = IntentType.HELP_REQUEST
        best_confidence = 0.3
        best_match_count = 0
        
        for intent, keywords in intent_keywords.items():
            match_count = sum(1 for keyword in keywords if keyword in text_lower)
            if match_count > best_match_count:
                best_match_count = match_count
                best_intent = intent
                best_confidence = min(0.3 + (match_count * 0.2), 0.95)
        
        # Дополнительная логика для повышения точности
        if "помощь" in text_lower or "help" in text_lower:
            best_intent = IntentType.HELP_REQUEST
            best_confidence = 0.9
        
        return IntentResult(
            intent=best_intent,
            confidence=best_confidence,
            text=text,
            metadata={
                "model": self.model["type"],
                "model_name": self.model["name"],
                "keywords_matched": best_match_count,
                "classification_method": "keyword_based"
            }
        )
    
    async def _classify_with_rules(self, text: str) -> IntentResult:
        """Классификация с использованием правил"""
        return await self._classify_with_ml_model(text)  # Используем ту же логику
    
    def get_supported_intents(self) -> List[IntentType]:
        """Получение списка поддерживаемых намерений"""
        return list(IntentType)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Получение информации о модели"""
        return {
            "model_type": self.model["type"],
            "model_name": self.model["name"],
            "config": self.config.model_dump(),
            "loaded": self.model["loaded"],
            "supported_intents": [intent.value for intent in self.get_supported_intents()]
        }


class IntentRecognitionSystem:
    """Система распознавания намерений"""
    
    def __init__(self, model_registry: ModelRegistry, feature_extractor: FeatureExtractor):
        self.model_registry = model_registry
        self.feature_extractor = feature_extractor
        self.classifiers: Dict[str, IntentClassifier] = {}
        self._setup_classifiers()
    
    def _setup_classifiers(self) -> None:
        """Настройка классификаторов"""
        # Создание классификаторов для каждого типа модели
        for model_id in self.model_registry.list_models():
            if "intent" in model_id.lower():
                config = self.model_registry.get_model_config(model_id)
                if config:
                    self.classifiers[model_id] = IntentClassifier(config)
    
    async def recognize_intent(self, text: str, model_id: str = "intent_classifier") -> Optional[IntentResult]:
        """Распознавание намерения"""
        try:
            # Получение или создание классификатора
            classifier = self.classifiers.get(model_id)
            if not classifier:
                config = self.model_registry.get_model_config(model_id)
                if config:
                    classifier = IntentClassifier(config)
                    self.classifiers[model_id] = classifier
                else:
                    logger.error(f"Модель {model_id} не найдена")
                    return None
            
            # Классификация
            result = await classifier.classify(text)
            
            # Проверка порога уверенности
            if result.confidence < classifier.config.confidence_threshold:
                logger.warning(f"Низкая уверенность в классификации: {result.confidence}")
                if classifier.config.fallback_to_rules:
                    # Fallback к правилам
                    fallback_result = await self._fallback_to_rules(text)
                    if fallback_result:
                        return fallback_result
            
            return result
        except Exception as e:
            logger.error(f"Ошибка распознавания намерения: {e}")
            return None
    
    async def _fallback_to_rules(self, text: str) -> Optional[IntentResult]:
        """Fallback к правилам"""
        try:
            # Создание fallback классификатора
            fallback_config = MLModelConfig(
                model_type=MLModelType.CUSTOM,
                model_path="",
                model_name="fallback_rules",
                confidence_threshold=0.5,
                fallback_to_rules=False
            )
            
            fallback_classifier = IntentClassifier(fallback_config)
            return await fallback_classifier.classify(text)
        except Exception as e:
            logger.error(f"Ошибка fallback к правилам: {e}")
            return None
    
    async def recognize_intent_batch(self, texts: List[str], model_id: str = "intent_classifier") -> List[Optional[IntentResult]]:
        """Пакетное распознавание намерений"""
        tasks = [self.recognize_intent(text, model_id) for text in texts]
        return await asyncio.gather(*tasks)
    
    def get_classifier_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Получение информации о классификаторе"""
        classifier = self.classifiers.get(model_id)
        if classifier:
            return classifier.get_model_info()
        return None
    
    def list_available_classifiers(self) -> List[str]:
        """Список доступных классификаторов"""
        return list(self.classifiers.keys())
    
    async def train_classifier(self, model_id: str, training_data: List[Tuple[str, IntentType]]) -> bool:
        """Обучение классификатора (заглушка)"""
        # TODO: Реализовать обучение классификатора
        logger.info(f"Обучение классификатора {model_id} с {len(training_data)} примерами")
        return True
    
    async def evaluate_classifier(self, model_id: str, test_data: List[Tuple[str, IntentType]]) -> Dict[str, float]:
        """Оценка классификатора (заглушка)"""
        # TODO: Реализовать оценку классификатора
        logger.info(f"Оценка классификатора {model_id} с {len(test_data)} примерами")
        return {
            "accuracy": 0.85,
            "precision": 0.82,
            "recall": 0.88,
            "f1_score": 0.85
        } 