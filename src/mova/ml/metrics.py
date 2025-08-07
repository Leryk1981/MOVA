"""
Система метрик для ML в MOVA SDK

Предоставляет функциональность для отслеживания и анализа метрик:
- MLMetrics: Основной класс метрик
- AccuracyMetric: Метрика точности
- F1ScoreMetric: F1-мера
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from collections import defaultdict, deque
from dataclasses import dataclass, field

from .models import IntentResult, EntityResult, SentimentResult, MLPrediction


logger = logging.getLogger(__name__)


@dataclass
class MetricPoint:
    """Точка метрики"""
    timestamp: datetime
    value: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MetricSummary:
    """Сводка метрики"""
    name: str
    current_value: float
    average_value: float
    min_value: float
    max_value: float
    total_points: int
    last_updated: datetime


class BaseMetric:
    """Базовая метрика"""
    
    def __init__(self, name: str, window_size: int = 1000):
        self.name = name
        self.window_size = window_size
        self.data_points: deque = deque(maxlen=window_size)
        self._lock = asyncio.Lock()
    
    async def add_point(self, value: float, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Добавление точки метрики"""
        async with self._lock:
            point = MetricPoint(
                timestamp=datetime.utcnow(),
                value=value,
                metadata=metadata or {}
            )
            self.data_points.append(point)
    
    async def get_summary(self) -> MetricSummary:
        """Получение сводки метрики"""
        async with self._lock:
            if not self.data_points:
                return MetricSummary(
                    name=self.name,
                    current_value=0.0,
                    average_value=0.0,
                    min_value=0.0,
                    max_value=0.0,
                    total_points=0,
                    last_updated=datetime.utcnow()
                )
            
            values = [point.value for point in self.data_points]
            current_value = values[-1] if values else 0.0
            average_value = sum(values) / len(values) if values else 0.0
            min_value = min(values) if values else 0.0
            max_value = max(values) if values else 0.0
            
            return MetricSummary(
                name=self.name,
                current_value=current_value,
                average_value=average_value,
                min_value=min_value,
                max_value=max_value,
                total_points=len(self.data_points),
                last_updated=self.data_points[-1].timestamp if self.data_points else datetime.utcnow()
            )
    
    async def get_data_points(self, limit: Optional[int] = None) -> List[MetricPoint]:
        """Получение точек данных"""
        async with self._lock:
            points = list(self.data_points)
            if limit:
                points = points[-limit:]
            return points
    
    async def clear(self) -> None:
        """Очистка метрики"""
        async with self._lock:
            self.data_points.clear()


class AccuracyMetric(BaseMetric):
    """Метрика точности"""
    
    def __init__(self, name: str = "accuracy", window_size: int = 1000):
        super().__init__(name, window_size)
        self.correct_predictions = 0
        self.total_predictions = 0
    
    async def update(self, predicted: Any, actual: Any, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Обновление метрики точности"""
        is_correct = predicted == actual
        self.correct_predictions += int(is_correct)
        self.total_predictions += 1
        
        accuracy = self.correct_predictions / self.total_predictions if self.total_predictions > 0 else 0.0
        
        await self.add_point(accuracy, {
            "correct_predictions": self.correct_predictions,
            "total_predictions": self.total_predictions,
            "is_correct": is_correct,
            **(metadata or {})
        })
    
    async def reset(self) -> None:
        """Сброс метрики"""
        async with self._lock:
            self.correct_predictions = 0
            self.total_predictions = 0
            await self.clear()


class F1ScoreMetric(BaseMetric):
    """F1-мера"""
    
    def __init__(self, name: str = "f1_score", window_size: int = 1000):
        super().__init__(name, window_size)
        self.true_positives = 0
        self.false_positives = 0
        self.false_negatives = 0
    
    async def update(self, predicted: bool, actual: bool, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Обновление F1-меры"""
        if predicted and actual:
            self.true_positives += 1
        elif predicted and not actual:
            self.false_positives += 1
        elif not predicted and actual:
            self.false_negatives += 1
        
        precision = self.true_positives / (self.true_positives + self.false_positives) if (self.true_positives + self.false_positives) > 0 else 0.0
        recall = self.true_positives / (self.true_positives + self.false_negatives) if (self.true_positives + self.false_negatives) > 0 else 0.0
        
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        
        await self.add_point(f1_score, {
            "precision": precision,
            "recall": recall,
            "true_positives": self.true_positives,
            "false_positives": self.false_positives,
            "false_negatives": self.false_negatives,
            **(metadata or {})
        })
    
    async def reset(self) -> None:
        """Сброс метрики"""
        async with self._lock:
            self.true_positives = 0
            self.false_positives = 0
            self.false_negatives = 0
            await self.clear()


class ResponseTimeMetric(BaseMetric):
    """Метрика времени отклика"""
    
    def __init__(self, name: str = "response_time", window_size: int = 1000):
        super().__init__(name, window_size)
    
    async def measure(self, func, *args, **kwargs) -> Any:
        """Измерение времени выполнения функции"""
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            end_time = time.time()
            response_time = end_time - start_time
            await self.add_point(response_time, {
                "function": func.__name__,
                "args": str(args),
                "kwargs": str(kwargs)
            })


class ConfidenceMetric(BaseMetric):
    """Метрика уверенности"""
    
    def __init__(self, name: str = "confidence", window_size: int = 1000):
        super().__init__(name, window_size)
    
    async def update(self, confidence: float, prediction_type: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Обновление метрики уверенности"""
        await self.add_point(confidence, {
            "prediction_type": prediction_type,
            **(metadata or {})
        })


class MLMetrics:
    """Основной класс для управления метриками ML"""
    
    def __init__(self):
        self.metrics: Dict[str, BaseMetric] = {}
        self._setup_default_metrics()
    
    def _setup_default_metrics(self) -> None:
        """Настройка метрик по умолчанию"""
        self.metrics.update({
            "intent_accuracy": AccuracyMetric("intent_accuracy"),
            "entity_f1": F1ScoreMetric("entity_f1"),
            "sentiment_accuracy": AccuracyMetric("sentiment_accuracy"),
            "response_time": ResponseTimeMetric("response_time"),
            "confidence": ConfidenceMetric("confidence"),
            "overall_accuracy": AccuracyMetric("overall_accuracy"),
            # Recommendation metrics
            "recommendations_generated": BaseMetric("recommendations_generated"),
            "config_recommendations": BaseMetric("config_recommendations"),
            "perf_recommendations": BaseMetric("perf_recommendations"),
            "error_recommendations": BaseMetric("error_recommendations"),
            "quality_recommendations": BaseMetric("quality_recommendations"),
            "critical_recommendations": BaseMetric("critical_recommendations"),
            "high_recommendations": BaseMetric("high_recommendations"),
            "medium_recommendations": BaseMetric("medium_recommendations"),
            "low_recommendations": BaseMetric("low_recommendations"),
            "avg_impact_score": BaseMetric("avg_impact_score"),
            "avg_confidence": BaseMetric("avg_confidence")
        })
    
    async def log_prediction(self, prediction: MLPrediction) -> None:
        """Логирование предсказания"""
        try:
            # Логирование времени отклика
            await self.metrics["response_time"].add_point(
                prediction.processing_time,
                {"prediction_type": "full_analysis"}
            )
            
            # Логирование уверенности
            if prediction.intent:
                await self.metrics["confidence"].update(
                    prediction.intent.confidence,
                    "intent",
                    {"intent": prediction.intent.intent.value}
                )
            
            if prediction.sentiment:
                await self.metrics["confidence"].update(
                    prediction.sentiment.confidence,
                    "sentiment",
                    {"sentiment": prediction.sentiment.sentiment.value}
                )
            
            # Логирование количества сущностей
            if prediction.entities:
                entity_count = len(prediction.entities.entities)
                await self.metrics["confidence"].add_point(
                    entity_count,
                    {"prediction_type": "entity_count", "count": entity_count}
                )
            
            logger.info(f"Предсказание залогировано: {prediction.processing_time:.3f}s")
            
        except Exception as e:
            logger.error(f"Ошибка логирования предсказания: {e}")
    
    async def log_intent_prediction(self, predicted: IntentResult, actual: Optional[IntentResult] = None) -> None:
        """Логирование предсказания намерения"""
        try:
            if actual:
                await self.metrics["intent_accuracy"].update(
                    predicted.intent,
                    actual.intent,
                    {
                        "predicted_confidence": predicted.confidence,
                        "actual_confidence": actual.confidence
                    }
                )
            
            await self.metrics["confidence"].update(
                predicted.confidence,
                "intent",
                {"intent": predicted.intent.value}
            )
            
        except Exception as e:
            logger.error(f"Ошибка логирования предсказания намерения: {e}")
    
    async def log_entity_prediction(self, predicted: EntityResult, actual: Optional[EntityResult] = None) -> None:
        """Логирование предсказания сущностей"""
        try:
            if actual:
                # Простое сравнение количества сущностей
                predicted_count = len(predicted.entities)
                actual_count = len(actual.entities)
                
                await self.metrics["entity_f1"].update(
                    predicted_count > 0,
                    actual_count > 0,
                    {
                        "predicted_count": predicted_count,
                        "actual_count": actual_count
                    }
                )
            
            # Логирование уверенности для каждой сущности
            for entity in predicted.entities:
                await self.metrics["confidence"].update(
                    entity.confidence,
                    "entity",
                    {"entity_type": entity.entity_type.value}
                )
            
        except Exception as e:
            logger.error(f"Ошибка логирования предсказания сущностей: {e}")
    
    async def log_sentiment_prediction(self, predicted: SentimentResult, actual: Optional[SentimentResult] = None) -> None:
        """Логирование предсказания настроения"""
        try:
            if actual:
                await self.metrics["sentiment_accuracy"].update(
                    predicted.sentiment,
                    actual.sentiment,
                    {
                        "predicted_confidence": predicted.confidence,
                        "actual_confidence": actual.confidence
                    }
                )
            
            await self.metrics["confidence"].update(
                predicted.confidence,
                "sentiment",
                {"sentiment": predicted.sentiment.value}
            )
            
        except Exception as e:
            logger.error(f"Ошибка логирования предсказания настроения: {e}")

    async def update_recommendation_metrics(self, recommendations_count: int) -> None:
        """Обновление метрик рекомендаций"""
        try:
            await self.metrics["recommendations_generated"].add_point(
                recommendations_count,
                {"timestamp": datetime.utcnow().isoformat()}
            )
            
        except Exception as e:
            logger.error(f"Ошибка обновления метрик рекомендаций: {e}")

    async def log_recommendation_metrics(self, recommendations: List[Any]) -> None:
        """Логирование метрик рекомендаций"""
        try:
            # Подсчет по типам
            config_count = sum(1 for r in recommendations if hasattr(r, 'type') and r.type == 'configuration')
            perf_count = sum(1 for r in recommendations if hasattr(r, 'type') and r.type == 'performance')
            error_count = sum(1 for r in recommendations if hasattr(r, 'type') and r.type == 'error_resolution')
            quality_count = sum(1 for r in recommendations if hasattr(r, 'type') and r.type == 'code_quality')
            
            # Подсчет по приоритетам
            critical_count = sum(1 for r in recommendations if hasattr(r, 'priority') and r.priority == 'critical')
            high_count = sum(1 for r in recommendations if hasattr(r, 'priority') and r.priority == 'high')
            medium_count = sum(1 for r in recommendations if hasattr(r, 'priority') and r.priority == 'medium')
            low_count = sum(1 for r in recommendations if hasattr(r, 'priority') and r.priority == 'low')
            
            # Средние значения
            impact_scores = [r.impact_score for r in recommendations if hasattr(r, 'impact_score')]
            confidence_scores = [r.confidence for r in recommendations if hasattr(r, 'confidence')]
            
            avg_impact = sum(impact_scores) / len(impact_scores) if impact_scores else 0.0
            avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
            
            # Обновление метрик
            await self.metrics["config_recommendations"].add_point(config_count)
            await self.metrics["perf_recommendations"].add_point(perf_count)
            await self.metrics["error_recommendations"].add_point(error_count)
            await self.metrics["quality_recommendations"].add_point(quality_count)
            
            await self.metrics["critical_recommendations"].add_point(critical_count)
            await self.metrics["high_recommendations"].add_point(high_count)
            await self.metrics["medium_recommendations"].add_point(medium_count)
            await self.metrics["low_recommendations"].add_point(low_count)
            
            await self.metrics["avg_impact_score"].add_point(avg_impact)
            await self.metrics["avg_confidence"].add_point(avg_confidence)
            
        except Exception as e:
            logger.error(f"Ошибка логирования метрик рекомендаций: {e}")
    
    async def get_metrics_summary(self) -> Dict[str, MetricSummary]:
        """Получение сводки всех метрик"""
        summary = {}
        for name, metric in self.metrics.items():
            summary[name] = await metric.get_summary()
        return summary
    
    async def get_metric_data(self, metric_name: str, limit: Optional[int] = None) -> List[MetricPoint]:
        """Получение данных метрики"""
        metric = self.metrics.get(metric_name)
        if metric:
            return await metric.get_data_points(limit)
        return []
    
    async def reset_metric(self, metric_name: str) -> bool:
        """Сброс метрики"""
        metric = self.metrics.get(metric_name)
        if metric:
            if hasattr(metric, 'reset'):
                await metric.reset()
            else:
                await metric.clear()
            return True
        return False
    
    async def reset_all_metrics(self) -> None:
        """Сброс всех метрик"""
        for metric in self.metrics.values():
            if hasattr(metric, 'reset'):
                await metric.reset()
            else:
                await metric.clear()
        logger.info("Все метрики сброшены")
    
    async def export_metrics(self, file_path: str) -> bool:
        """Экспорт метрик в файл"""
        try:
            export_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "metrics": {}
            }
            
            for name, metric in self.metrics.items():
                summary = await metric.get_summary()
                data_points = await metric.get_data_points()
                
                export_data["metrics"][name] = {
                    "summary": {
                        "current_value": summary.current_value,
                        "average_value": summary.average_value,
                        "min_value": summary.min_value,
                        "max_value": summary.max_value,
                        "total_points": summary.total_points,
                        "last_updated": summary.last_updated.isoformat()
                    },
                    "data_points": [
                        {
                            "timestamp": point.timestamp.isoformat(),
                            "value": point.value,
                            "metadata": point.metadata
                        }
                        for point in data_points
                    ]
                }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Метрики экспортированы в {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка экспорта метрик: {e}")
            return False
    
    async def import_metrics(self, file_path: str) -> bool:
        """Импорт метрик из файла"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            for name, metric_data in import_data.get("metrics", {}).items():
                metric = self.metrics.get(name)
                if metric:
                    # Очистка текущих данных
                    await metric.clear()
                    
                    # Импорт точек данных
                    for point_data in metric_data.get("data_points", []):
                        point = MetricPoint(
                            timestamp=datetime.fromisoformat(point_data["timestamp"]),
                            value=point_data["value"],
                            metadata=point_data.get("metadata", {})
                        )
                        metric.data_points.append(point)
            
            logger.info(f"Метрики импортированы из {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка импорта метрик: {e}")
            return False
    
    def add_custom_metric(self, name: str, metric: BaseMetric) -> None:
        """Добавление пользовательской метрики"""
        self.metrics[name] = metric
        logger.info(f"Добавлена пользовательская метрика: {name}")
    
    def remove_metric(self, name: str) -> bool:
        """Удаление метрики"""
        if name in self.metrics:
            del self.metrics[name]
            logger.info(f"Метрика удалена: {name}")
            return True
        return False 