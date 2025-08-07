"""
Интеграция ML с MOVA SDK

Предоставляет интеграцию ML функциональности с основной системой MOVA:
- MLIntegration: Основной класс интеграции
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from .foundation import MLFoundation
from .intent_recognition import IntentRecognitionSystem
from .entity_extraction import EntityExtractionSystem
from .context_analysis import ContextAnalysisSystem
from .training import ModelTrainer
from .metrics import MLMetrics
from .models import (
    MLPrediction, 
    IntentResult, 
    EntityResult, 
    ContextResult,
    SentimentResult,
    TrainingExample,
    TrainingConfig
)
from ..webhook_integration import trigger_ml_intent_recognized, trigger_ml_entity_extracted, trigger_ml_prediction_made


logger = logging.getLogger(__name__)


class MLIntegration:
    """Интеграция ML с MOVA SDK"""
    
    def __init__(self, models_dir: str = "models"):
        self.foundation = MLFoundation(models_dir)
        self.intent_system = IntentRecognitionSystem(
            self.foundation.model_registry,
            self.foundation.feature_extractor
        )
        self.entity_system = EntityExtractionSystem(
            self.foundation.model_registry,
            self.foundation.feature_extractor
        )
        self.context_system = ContextAnalysisSystem(
            self.foundation.model_registry,
            self.foundation.feature_extractor
        )
        self.trainer = ModelTrainer(self.foundation.model_registry)
        self.metrics = MLMetrics()
        self._enabled = True
    
    @property
    def enabled(self) -> bool:
        """Проверка включена ли ML интеграция"""
        return self._enabled
    
    @enabled.setter
    def enabled(self, value: bool) -> None:
        """Установка статуса ML интеграции"""
        self._enabled = value
        logger.info(f"ML интеграция {'включена' if value else 'отключена'}")
    
    async def analyze_text(self, text: str, session_id: Optional[str] = None, user_id: Optional[str] = None) -> Optional[MLPrediction]:
        """Комплексный анализ текста"""
        if not self.enabled:
            logger.warning("ML интеграция отключена")
            return None
        
        try:
            start_time = datetime.utcnow()
            
            # Параллельное выполнение всех анализов
            intent_task = self.intent_system.recognize_intent(text)
            entities_task = self.entity_system.extract_entities(text)
            context_task = self.context_system.analyze_context(session_id, text, user_id)
            sentiment_task = self.foundation.prediction_service.predict_sentiment(text)
            
            intent_result, entities_result, context_result, sentiment_result = await asyncio.gather(
                intent_task, entities_task, context_task, sentiment_task
            )
            
            end_time = datetime.utcnow()
            processing_time = (end_time - start_time).total_seconds()
            
            # Создание комплексного результата
            prediction = MLPrediction(
                intent=intent_result,
                entities=entities_result,
                context=context_result,
                sentiment=sentiment_result,
                text=text,
                session_id=session_id,
                processing_time=processing_time,
                metadata={
                    "models_used": ["intent_classifier", "entity_extractor", "context_analyzer", "sentiment_analyzer"],
                    "timestamp": start_time.isoformat(),
                    "ml_integration_version": "1.0.0"
                }
            )
            
            # Логирование метрик
            await self.metrics.log_prediction(prediction)
            
            # Отправка webhook событий
            await self._trigger_webhook_events(prediction)
            
            logger.info(f"ML анализ завершен за {processing_time:.3f}s")
            return prediction
            
        except Exception as e:
            logger.error(f"Ошибка ML анализа: {e}")
            return None
    
    async def _trigger_webhook_events(self, prediction: MLPrediction) -> None:
        """Отправка webhook событий"""
        try:
            # Событие распознавания намерения
            if prediction.intent:
                trigger_ml_intent_recognized({
                    "intent": prediction.intent.intent.value,
                    "confidence": prediction.intent.confidence,
                    "text": prediction.text,
                    "session_id": prediction.session_id,
                    "processing_time": prediction.processing_time
                })
            
            # Событие извлечения сущностей
            if prediction.entities and prediction.entities.entities:
                trigger_ml_entity_extracted({
                    "entities_count": len(prediction.entities.entities),
                    "entity_types": [entity.entity_type.value for entity in prediction.entities.entities],
                    "text": prediction.text,
                    "session_id": prediction.session_id,
                    "processing_time": prediction.processing_time
                })
            
            # Событие предсказания
            trigger_ml_prediction_made({
                "prediction_type": "full_analysis",
                "text": prediction.text,
                "session_id": prediction.session_id,
                "processing_time": prediction.processing_time,
                "has_intent": prediction.intent is not None,
                "has_entities": prediction.entities is not None and len(prediction.entities.entities) > 0,
                "has_sentiment": prediction.sentiment is not None
            })
            
        except Exception as e:
            logger.error(f"Ошибка отправки webhook событий: {e}")
    
    async def recognize_intent(self, text: str, model_id: str = "intent_classifier") -> Optional[IntentResult]:
        """Распознавание намерения"""
        if not self.enabled:
            return None
        
        try:
            result = await self.intent_system.recognize_intent(text, model_id)
            if result:
                await self.metrics.log_intent_prediction(result)
            return result
        except Exception as e:
            logger.error(f"Ошибка распознавания намерения: {e}")
            return None
    
    async def extract_entities(self, text: str, model_id: str = "entity_extractor") -> Optional[EntityResult]:
        """Извлечение сущностей"""
        if not self.enabled:
            return None
        
        try:
            result = await self.entity_system.extract_entities(text, model_id)
            if result:
                await self.metrics.log_entity_prediction(result)
            return result
        except Exception as e:
            logger.error(f"Ошибка извлечения сущностей: {e}")
            return None
    
    async def analyze_context(self, session_id: str, text: str, user_id: Optional[str] = None, model_id: str = "context_analyzer") -> Optional[ContextResult]:
        """Анализ контекста"""
        if not self.enabled:
            return None
        
        try:
            result = await self.context_system.analyze_context(session_id, text, user_id, model_id)
            return result
        except Exception as e:
            logger.error(f"Ошибка анализа контекста: {e}")
            return None
    
    async def predict_sentiment(self, text: str, model_id: str = "sentiment_analyzer") -> Optional[SentimentResult]:
        """Predict sentiment / Передбачення настроєнь"""
        if not self.enabled:
            return None
        
        try:
            result = await self.foundation.prediction_service.predict_sentiment(text, model_id)
            if result:
                await self.metrics.log_sentiment_prediction(result)
            return result
        except Exception as e:
            logger.error(f"Ошибка предсказания настроения: {e}")
            return None
    
    async def train_model(self, model_type: str, training_data: List[TrainingExample], config: TrainingConfig) -> Dict[str, Any]:
        """Обучение модели"""
        if not self.enabled:
            return {"success": False, "error": "ML интеграция отключена"}
        
        try:
            if model_type == "intent_classifier":
                return await self.trainer.train_intent_classifier(training_data, config)
            elif model_type == "entity_extractor":
                return await self.trainer.train_entity_extractor(training_data, config)
            elif model_type == "sentiment_analyzer":
                return await self.trainer.train_sentiment_analyzer(training_data, config)
            else:
                return {"success": False, "error": f"Неизвестный тип модели: {model_type}"}
        except Exception as e:
            logger.error(f"Ошибка обучения модели: {e}")
            return {"success": False, "error": str(e)}
    
    async def evaluate_model(self, model_id: str, test_data: List[TrainingExample]) -> Dict[str, Any]:
        """Оценка модели"""
        if not self.enabled:
            return {"success": False, "error": "ML интеграция отключена"}
        
        try:
            return await self.trainer.evaluate_model(model_id, test_data)
        except Exception as e:
            logger.error(f"Ошибка оценки модели: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_metrics_summary(self) -> Dict[str, Any]:
        """Получение сводки метрик"""
        try:
            summary = await self.metrics.get_metrics_summary()
            return {
                "success": True,
                "metrics": {
                    name: {
                        "current_value": metric.current_value,
                        "average_value": metric.average_value,
                        "min_value": metric.min_value,
                        "max_value": metric.max_value,
                        "total_points": metric.total_points,
                        "last_updated": metric.last_updated.isoformat()
                    }
                    for name, metric in summary.items()
                }
            }
        except Exception as e:
            logger.error(f"Ошибка получения сводки метрик: {e}")
            return {"success": False, "error": str(e)}
    
    async def export_metrics(self, file_path: str) -> bool:
        """Экспорт метрик"""
        return await self.metrics.export_metrics(file_path)
    
    async def import_metrics(self, file_path: str) -> bool:
        """Импорт метрик"""
        return await self.metrics.import_metrics(file_path)
    
    def get_model_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Получение информации о модели"""
        return self.foundation.get_model_info(model_id)
    
    def list_available_models(self) -> List[Dict[str, Any]]:
        """Список доступных моделей"""
        return self.foundation.list_available_models()
    
    def get_classifier_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Получение информации о классификаторе"""
        return self.intent_system.get_classifier_info(model_id)
    
    def get_extractor_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Получение информации об извлекателе"""
        return self.entity_system.get_extractor_info(model_id)
    
    def get_analyzer_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Получение информации об анализаторе"""
        return self.context_system.get_analyzer_info(model_id)
    
    def list_available_classifiers(self) -> List[str]:
        """Список доступных классификаторов"""
        return self.intent_system.list_available_classifiers()
    
    def list_available_extractors(self) -> List[str]:
        """Список доступных извлекателей"""
        return self.entity_system.list_available_extractors()
    
    def list_available_analyzers(self) -> List[str]:
        """Список доступных анализаторов"""
        return self.context_system.list_available_analyzers()
    
    async def add_custom_entity_pattern(self, entity_type: str, pattern: str, model_id: str = "entity_extractor") -> bool:
        """Добавление пользовательского паттерна для извлечения сущностей"""
        from .models import EntityType
        try:
            entity_enum = EntityType(entity_type)
            return await self.entity_system.add_custom_entity_pattern(entity_enum, pattern, model_id)
        except ValueError:
            logger.error(f"Неизвестный тип сущности: {entity_type}")
            return False
    
    def get_session_context(self, session_id: str, model_id: str = "context_analyzer") -> Optional[Dict[str, Any]]:
        """Получение контекста сессии"""
        return self.context_system.get_session_context(session_id, model_id)
    
    def clear_session_context(self, session_id: str, model_id: str = "context_analyzer") -> bool:
        """Очистка контекста сессии"""
        return self.context_system.clear_session_context(session_id, model_id)
    
    async def reset_metrics(self, metric_name: Optional[str] = None) -> bool:
        """Сброс метрик"""
        if metric_name:
            return await self.metrics.reset_metric(metric_name)
        else:
            await self.metrics.reset_all_metrics()
            return True
    
    def get_training_history(self) -> List[Dict[str, Any]]:
        """Получение истории обучения"""
        return self.trainer.get_training_history()
    
    async def batch_analyze(self, texts: List[str], session_ids: Optional[List[str]] = None, user_ids: Optional[List[str]] = None) -> List[Optional[MLPrediction]]:
        """Пакетный анализ текстов"""
        if not self.enabled:
            return [None] * len(texts)
        
        try:
            tasks = []
            for i, text in enumerate(texts):
                session_id = session_ids[i] if session_ids and i < len(session_ids) else None
                user_id = user_ids[i] if user_ids and i < len(user_ids) else None
                tasks.append(self.analyze_text(text, session_id, user_id))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Обработка исключений
            processed_results = []
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Ошибка в пакетном анализе: {result}")
                    processed_results.append(None)
                else:
                    processed_results.append(result)
            
            return processed_results
            
        except Exception as e:
            logger.error(f"Ошибка пакетного анализа: {e}")
            return [None] * len(texts)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Получение статуса системы"""
        return {
            "enabled": self.enabled,
            "models_loaded": len(self.foundation.model_registry._loaded_models),
            "total_models": len(self.foundation.model_registry.list_models()),
            "active_sessions": len(self.context_system.analyzers.get("context_analyzer", {}).context_storage if self.context_system.analyzers else {}),
            "metrics_count": len(self.metrics.metrics),
            "available_classifiers": len(self.list_available_classifiers()),
            "available_extractors": len(self.list_available_extractors()),
            "available_analyzers": len(self.list_available_analyzers())
        } 