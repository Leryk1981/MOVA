"""
Система обучения моделей для MOVA SDK

Предоставляет функциональность для обучения ML моделей:
- ModelTrainer: Тренер моделей
- TrainingConfig: Конфигурация обучения
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union
from concurrent.futures import ThreadPoolExecutor

from .models import (
    TrainingConfig, 
    TrainingExample, 
    MLModelConfig, 
    MLModelType,
    IntentType,
    EntityType,
    SentimentType
)
from .foundation import ModelRegistry


logger = logging.getLogger(__name__)


class ModelTrainer:
    """Тренер ML моделей"""
    
    def __init__(self, model_registry: ModelRegistry):
        self.model_registry = model_registry
        self.executor = ThreadPoolExecutor(max_workers=2)
        self._training_history: List[Dict[str, Any]] = []
    
    async def train_intent_classifier(
        self, 
        training_data: List[TrainingExample], 
        config: TrainingConfig
    ) -> Dict[str, Any]:
        """Обучение классификатора намерений"""
        try:
            logger.info(f"Начало обучения классификатора намерений с {len(training_data)} примерами")
            
            # Валидация данных
            validated_data = self._validate_intent_training_data(training_data)
            if not validated_data:
                raise ValueError("Некорректные данные для обучения")
            
            # Подготовка данных
            prepared_data = await self._prepare_intent_data(validated_data)
            
            # Model training / Навчання моделі
            loop = asyncio.get_event_loop()
            training_result = await loop.run_in_executor(
                self.executor,
                self._train_intent_model_sync,
                prepared_data,
                config
            )
            
            # Сохранение модели
            model_path = await self._save_trained_model(training_result, config)
            
            # Обновление реестра моделей
            await self._update_model_registry(training_result, config, model_path)
            
            # Логирование результатов
            self._log_training_result("intent_classifier", training_result, config)
            
            return {
                "success": True,
                "model_path": str(model_path),
                "training_metrics": training_result.get("metrics", {}),
                "training_time": training_result.get("training_time", 0),
                "model_config": training_result.get("config", {})
            }
            
        except Exception as e:
            logger.error(f"Ошибка обучения классификатора намерений: {e}")
            return {
                "success": False,
                "error": str(e),
                "training_time": 0
            }
    
    async def train_entity_extractor(
        self, 
        training_data: List[TrainingExample], 
        config: TrainingConfig
    ) -> Dict[str, Any]:
        """Обучение извлекателя сущностей"""
        try:
            logger.info(f"Начало обучения извлекателя сущностей с {len(training_data)} примерами")
            
            # Валидация данных
            validated_data = self._validate_entity_training_data(training_data)
            if not validated_data:
                raise ValueError("Некорректные данные для обучения")
            
            # Подготовка данных
            prepared_data = await self._prepare_entity_data(validated_data)
            
            # Model training / Навчання моделі
            loop = asyncio.get_event_loop()
            training_result = await loop.run_in_executor(
                self.executor,
                self._train_entity_model_sync,
                prepared_data,
                config
            )
            
            # Сохранение модели
            model_path = await self._save_trained_model(training_result, config)
            
            # Обновление реестра моделей
            await self._update_model_registry(training_result, config, model_path)
            
            # Логирование результатов
            self._log_training_result("entity_extractor", training_result, config)
            
            return {
                "success": True,
                "model_path": str(model_path),
                "training_metrics": training_result.get("metrics", {}),
                "training_time": training_result.get("training_time", 0),
                "model_config": training_result.get("config", {})
            }
            
        except Exception as e:
            logger.error(f"Ошибка обучения извлекателя сущностей: {e}")
            return {
                "success": False,
                "error": str(e),
                "training_time": 0
            }
    
    async def train_sentiment_analyzer(
        self, 
        training_data: List[TrainingExample], 
        config: TrainingConfig
    ) -> Dict[str, Any]:
        """Обучение анализатора настроений"""
        try:
            logger.info(f"Начало обучения анализатора настроений с {len(training_data)} примерами")
            
            # Валидация данных
            validated_data = self._validate_sentiment_training_data(training_data)
            if not validated_data:
                raise ValueError("Некорректные данные для обучения")
            
            # Подготовка данных
            prepared_data = await self._prepare_sentiment_data(validated_data)
            
            # Model training / Навчання моделі
            loop = asyncio.get_event_loop()
            training_result = await loop.run_in_executor(
                self.executor,
                self._train_sentiment_model_sync,
                prepared_data,
                config
            )
            
            # Сохранение модели
            model_path = await self._save_trained_model(training_result, config)
            
            # Обновление реестра моделей
            await self._update_model_registry(training_result, config, model_path)
            
            # Логирование результатов
            self._log_training_result("sentiment_analyzer", training_result, config)
            
            return {
                "success": True,
                "model_path": str(model_path),
                "training_metrics": training_result.get("metrics", {}),
                "training_time": training_result.get("training_time", 0),
                "model_config": training_result.get("config", {})
            }
            
        except Exception as e:
            logger.error(f"Ошибка обучения анализатора настроений: {e}")
            return {
                "success": False,
                "error": str(e),
                "training_time": 0
            }
    
    def _validate_intent_training_data(self, data: List[TrainingExample]) -> List[TrainingExample]:
        """Валидация данных для обучения классификатора намерений"""
        validated = []
        for example in data:
            if example.text and example.intent:
                validated.append(example)
            else:
                logger.warning(f"Пропущен некорректный пример: {example}")
        return validated
    
    def _validate_entity_training_data(self, data: List[TrainingExample]) -> List[TrainingExample]:
        """Валидация данных для обучения извлекателя сущностей"""
        validated = []
        for example in data:
            if example.text and example.entities:
                validated.append(example)
            else:
                logger.warning(f"Пропущен некорректный пример: {example}")
        return validated
    
    def _validate_sentiment_training_data(self, data: List[TrainingExample]) -> List[TrainingExample]:
        """Валидация данных для обучения анализатора настроений"""
        validated = []
        for example in data:
            if example.text and example.sentiment:
                validated.append(example)
            else:
                logger.warning(f"Пропущен некорректный пример: {example}")
        return validated
    
    async def _prepare_intent_data(self, data: List[TrainingExample]) -> Dict[str, Any]:
        """Подготовка данных для обучения классификатора намерений"""
        texts = [example.text for example in data]
        intents = [example.intent.value for example in data if example.intent]
        
        return {
            "texts": texts,
            "intents": intents,
            "intent_mapping": {intent.value: i for i, intent in enumerate(IntentType)},
            "num_classes": len(IntentType)
        }
    
    async def _prepare_entity_data(self, data: List[TrainingExample]) -> Dict[str, Any]:
        """Подготовка данных для обучения извлекателя сущностей"""
        texts = [example.text for example in data]
        entities_list = [example.entities for example in data if example.entities]
        
        return {
            "texts": texts,
            "entities": entities_list,
            "entity_types": list(EntityType)
        }
    
    async def _prepare_sentiment_data(self, data: List[TrainingExample]) -> Dict[str, Any]:
        """Подготовка данных для обучения анализатора настроений"""
        texts = [example.text for example in data]
        sentiments = [example.sentiment.value for example in data if example.sentiment]
        
        return {
            "texts": texts,
            "sentiments": sentiments,
            "sentiment_mapping": {sentiment.value: i for i, sentiment in enumerate(SentimentType)},
            "num_classes": len(SentimentType)
        }
    
    def _train_intent_model_sync(self, data: Dict[str, Any], config: TrainingConfig) -> Dict[str, Any]:
        """Синхронное обучение модели классификации намерений (заглушка)"""
        # TODO: Реализовать реальное обучение модели
        import time
        start_time = time.time()
        
        # Имитация обучения
        time.sleep(2)  # Имитация времени обучения
        
        training_time = time.time() - start_time
        
        return {
            "model": {"type": "intent_classifier", "trained": True},
            "metrics": {
                "accuracy": 0.92,
                "precision": 0.89,
                "recall": 0.91,
                "f1_score": 0.90
            },
            "training_time": training_time,
            "config": config.model_dump(),
            "data_stats": {
                "total_examples": len(data["texts"]),
                "num_classes": data["num_classes"]
            }
        }
    
    def _train_entity_model_sync(self, data: Dict[str, Any], config: TrainingConfig) -> Dict[str, Any]:
        """Синхронное обучение модели извлечения сущностей (заглушка)"""
        # TODO: Реализовать реальное обучение модели
        import time
        start_time = time.time()
        
        # Имитация обучения
        time.sleep(3)  # Имитация времени обучения
        
        training_time = time.time() - start_time
        
        return {
            "model": {"type": "entity_extractor", "trained": True},
            "metrics": {
                "precision": 0.87,
                "recall": 0.85,
                "f1_score": 0.86
            },
            "training_time": training_time,
            "config": config.model_dump(),
            "data_stats": {
                "total_examples": len(data["texts"]),
                "entity_types": len(data["entity_types"])
            }
        }
    
    def _train_sentiment_model_sync(self, data: Dict[str, Any], config: TrainingConfig) -> Dict[str, Any]:
        """Синхронное обучение модели анализа настроений (заглушка)"""
        # TODO: Реализовать реальное обучение модели
        import time
        start_time = time.time()
        
        # Имитация обучения
        time.sleep(2.5)  # Имитация времени обучения
        
        training_time = time.time() - start_time
        
        return {
            "model": {"type": "sentiment_analyzer", "trained": True},
            "metrics": {
                "accuracy": 0.88,
                "precision": 0.86,
                "recall": 0.87,
                "f1_score": 0.86
            },
            "training_time": training_time,
            "config": config.model_dump(),
            "data_stats": {
                "total_examples": len(data["texts"]),
                "num_classes": data["num_classes"]
            }
        }
    
    async def _save_trained_model(self, training_result: Dict[str, Any], config: TrainingConfig) -> Path:
        """Сохранение обученной модели"""
        model_path = Path(config.save_path)
        model_path.mkdir(parents=True, exist_ok=True)
        
        # Сохранение модели (заглушка)
        model_file = model_path / "model.pkl"
        with open(model_file, 'wb') as f:
            # TODO: Реализовать реальное сохранение модели
            import pickle
            pickle.dump(training_result["model"], f)
        
        # Сохранение конфигурации
        config_file = model_path / "config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(training_result["config"], f, indent=2, ensure_ascii=False)
        
        # Сохранение метрик
        metrics_file = model_path / "metrics.json"
        with open(metrics_file, 'w', encoding='utf-8') as f:
            json.dump(training_result["metrics"], f, indent=2, ensure_ascii=False)
        
        logger.info(f"Модель сохранена в {model_path}")
        return model_path
    
    async def _update_model_registry(self, training_result: Dict[str, Any], config: TrainingConfig, model_path: Path) -> None:
        """Обновление реестра моделей"""
        model_config = MLModelConfig(
            model_type=config.model_type,
            model_path=str(model_path),
            model_name=f"trained_{config.model_type.value}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            version="1.0.0",
            confidence_threshold=0.8
        )
        
        model_id = f"{config.model_type.value}_trained"
        self.model_registry.register_model(model_id, model_config)
        logger.info(f"Модель {model_id} зарегистрирована в реестре")
    
    def _log_training_result(self, model_type: str, training_result: Dict[str, Any], config: TrainingConfig) -> None:
        """Логирование результатов обучения"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "model_type": model_type,
            "training_time": training_result.get("training_time", 0),
            "metrics": training_result.get("metrics", {}),
            "config": config.model_dump(),
            "data_stats": training_result.get("data_stats", {})
        }
        
        self._training_history.append(log_entry)
        
        # Сохранение истории обучения
        history_file = Path("training_history.json")
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(self._training_history, f, indent=2, ensure_ascii=False)
    
    def get_training_history(self) -> List[Dict[str, Any]]:
        """Получение истории обучения"""
        return self._training_history.copy()
    
    async def evaluate_model(self, model_id: str, test_data: List[TrainingExample]) -> Dict[str, Any]:
        """Оценка модели"""
        try:
            logger.info(f"Оценка модели {model_id} с {len(test_data)} тестовыми примерами")
            
            # TODO: Реализовать реальную оценку модели
            loop = asyncio.get_event_loop()
            evaluation_result = await loop.run_in_executor(
                self.executor,
                self._evaluate_model_sync,
                model_id,
                test_data
            )
            
            return {
                "success": True,
                "model_id": model_id,
                "evaluation_metrics": evaluation_result,
                "test_data_size": len(test_data)
            }
            
        except Exception as e:
            logger.error(f"Ошибка оценки модели: {e}")
            return {
                "success": False,
                "error": str(e),
                "model_id": model_id
            }
    
    def _evaluate_model_sync(self, model_id: str, test_data: List[TrainingExample]) -> Dict[str, float]:
        """Синхронная оценка модели (заглушка)"""
        # TODO: Реализовать реальную оценку модели
        import time
        time.sleep(1)  # Имитация времени оценки
        
        return {
            "accuracy": 0.89,
            "precision": 0.87,
            "recall": 0.88,
            "f1_score": 0.87
        } 