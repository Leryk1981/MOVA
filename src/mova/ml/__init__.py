"""
ML Integration Module for MOVA SDK
Модуль інтеграції ML для MOVA SDK

This module provides machine learning capabilities for:
Цей модуль надає можливості машинного навчання для:
- Intent Recognition / Распізнавання намірів
- Entity Extraction / Витяг сутностей
- Context Analysis / Аналіз контексту
- Sentiment Analysis / Аналіз настроєнь
"""

from .foundation import MLFoundation, ModelRegistry, FeatureExtractor, PredictionService
from .models import (
    MLPrediction, 
    IntentResult, 
    EntityResult, 
    ContextResult,
    SentimentResult,
    MLModelType,
    MLModelConfig
)
from .intent_recognition import IntentClassifier, IntentRecognitionSystem
from .entity_extraction import EntityExtractor, EntityExtractionSystem
from .context_analysis import ContextAnalyzer, ContextAnalysisSystem
from .training import ModelTrainer, TrainingConfig
from .metrics import MLMetrics, AccuracyMetric, F1ScoreMetric
from .integration import MLIntegration

__version__ = "1.0.0"
__all__ = [
    # Foundation
    "MLFoundation",
    "ModelRegistry", 
    "FeatureExtractor",
    "PredictionService",
    
    # Models
    "MLPrediction",
    "IntentResult",
    "EntityResult", 
    "ContextResult",
    "SentimentResult",
    "MLModelType",
    "MLModelConfig",
    
    # Systems
    "IntentClassifier",
    "IntentRecognitionSystem",
    "EntityExtractor",
    "EntityExtractionSystem", 
    "ContextAnalyzer",
    "ContextAnalysisSystem",
    
    # Training & Metrics
    "ModelTrainer",
    "TrainingConfig",
    "MLMetrics",
    "AccuracyMetric",
    "F1ScoreMetric",
    
    # Integration
    "MLIntegration"
] 