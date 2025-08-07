"""
Система анализа контекста для MOVA SDK

Предоставляет функциональность для анализа контекста разговора:
- ContextAnalyzer: Анализатор контекста
- ContextAnalysisSystem: Система анализа контекста
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, deque

from .models import ContextResult, MLModelConfig, MLModelType
from .foundation import ModelRegistry, FeatureExtractor


logger = logging.getLogger(__name__)


class ContextAnalyzer:
    """Анализатор контекста"""
    
    def __init__(self, model_config: MLModelConfig):
        self.config = model_config
        self.model = None
        self._load_model()
        self._setup_context_storage()
    
    def _load_model(self) -> None:
        """Загрузка модели анализатора"""
        try:
            if self.config.model_type == MLModelType.TRANSFORMER:
                self.model = self._load_transformer_model()
            elif self.config.model_type == MLModelType.BERT:
                self.model = self._load_bert_model()
            else:
                logger.warning(f"Неподдерживаемый тип модели: {self.config.model_type}")
                self.model = self._load_fallback_model()
        except Exception as e:
            logger.error(f"Ошибка загрузки модели: {e}")
            self.model = self._load_fallback_model()
    
    def _load_transformer_model(self) -> Dict[str, Any]:
        """Загрузка Transformer модели (заглушка)"""
        # TODO: Реализовать загрузку реальной Transformer модели
        logger.info(f"Загрузка Transformer модели: {self.config.model_name}")
        return {
            "type": "transformer",
            "name": self.config.model_name,
            "config": self.config.model_dump(),
            "loaded": True
        }
    
    def _load_bert_model(self) -> Dict[str, Any]:
        """Загрузка BERT модели для анализа контекста (заглушка)"""
        # TODO: Implement real BERT model loading / Реалізувати завантаження реальної BERT моделі
        logger.info(f"Загрузка BERT модели: {self.config.model_name}")
        return {
            "type": "bert",
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
    
    def _setup_context_storage(self) -> None:
        """Настройка хранилища контекста"""
        self.context_storage = defaultdict(lambda: {
            "conversation_history": deque(maxlen=100),
            "user_preferences": {},
            "session_data": {},
            "last_activity": None,
            "context_score": 0.0
        })
    
    async def analyze_context(self, session_id: str, current_text: str, user_id: Optional[str] = None) -> ContextResult:
        """Analyze context for session / Аналіз контексту для сесії"""
        try:
            # Получение или создание контекста сессии
            context_data = self.context_storage[session_id]
            
            # Обновление истории разговора
            context_data["conversation_history"].append({
                "text": current_text,
                "timestamp": datetime.utcnow(),
                "user_id": user_id
            })
            
            # Обновление времени последней активности
            context_data["last_activity"] = datetime.utcnow()
            
            # Context analysis / Аналіз контексту
            if self.model["type"] in ["transformer", "bert"]:
                context_score = await self._analyze_with_ml_model(session_id, current_text)
            else:
                context_score = await self._analyze_with_rules(session_id, current_text)
            
            # Обновление оценки контекста
            context_data["context_score"] = context_score
            
            # Обновление предпочтений пользователя
            if user_id:
                await self._update_user_preferences(session_id, user_id, current_text)
            
            return ContextResult(
                session_id=session_id,
                user_id=user_id,
                conversation_history=[msg["text"] for msg in context_data["conversation_history"]],
                user_preferences=context_data["user_preferences"],
                context_score=context_score,
                metadata={
                    "model": self.model["type"],
                    "model_name": self.model["name"],
                    "analysis_method": "ml_based" if self.model["type"] in ["transformer", "bert"] else "rule_based"
                }
            )
        except Exception as e:
            logger.error(f"Ошибка анализа контекста: {e}")
            return await self._create_fallback_context(session_id, user_id, current_text)
    
    async def _analyze_with_ml_model(self, session_id: str, current_text: str) -> float:
        """Анализ с использованием ML модели (заглушка)"""
        # TODO: Implement real analysis with ML model / Реалізувати реальний аналіз з ML моделлю
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._analyze_sync, session_id, current_text)
    
    async def _analyze_with_rules(self, session_id: str, current_text: str) -> float:
        """Анализ с использованием правил"""
        return await self._analyze_with_ml_model(session_id, current_text)
    
    def _analyze_sync(self, session_id: str, current_text: str) -> float:
        """Синхронный анализ контекста"""
        context_data = self.context_storage[session_id]
        history = context_data["conversation_history"]
        
        # Базовая оценка контекста
        base_score = 0.5
        
        # Факторы, влияющие на оценку контекста
        factors = {
            "history_length": min(len(history) / 10.0, 1.0),  # Длина истории
            "recent_activity": 1.0,  # Недавняя активность
            "text_complexity": min(len(current_text.split()) / 20.0, 1.0),  # Сложность текста
            "user_preferences": len(context_data["user_preferences"]) / 5.0,  # Предпочтения пользователя
            "session_duration": self._calculate_session_duration(session_id)  # Длительность сессии
        }
        
        # Взвешенная оценка
        weights = {
            "history_length": 0.2,
            "recent_activity": 0.3,
            "text_complexity": 0.2,
            "user_preferences": 0.2,
            "session_duration": 0.1
        }
        
        context_score = sum(factors[key] * weights[key] for key in factors)
        return min(context_score, 1.0)
    
    def _calculate_session_duration(self, session_id: str) -> float:
        """Расчет длительности сессии"""
        context_data = self.context_storage[session_id]
        if not context_data["last_activity"]:
            return 0.0
        
        duration = datetime.utcnow() - context_data["last_activity"]
        return min(duration.total_seconds() / 3600.0, 1.0)  # Нормализация до 1 часа
    
    async def _update_user_preferences(self, session_id: str, user_id: str, text: str) -> None:
        """Обновление предпочтений пользователя"""
        context_data = self.context_storage[session_id]
        preferences = context_data["user_preferences"]
        
        # Анализ предпочтений на основе текста
        text_lower = text.lower()
        
        # Определение языка
        if any(char in text for char in "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"):
            preferences["language"] = "ru"
        elif any(char in text for char in "abcdefghijklmnopqrstuvwxyz"):
            preferences["language"] = "en"
        
        # Определение темы разговора
        topics = {
            "technical": ["технический", "техника", "программирование", "код", "алгоритм"],
            "business": ["бизнес", "компания", "проект", "клиент", "продажи"],
            "personal": ["личный", "семья", "друзья", "хобби", "интересы"]
        }
        
        for topic, keywords in topics.items():
            if any(keyword in text_lower for keyword in keywords):
                preferences["topic"] = topic
                break
        
        # Определение стиля общения
        if any(word in text_lower for word in ["пожалуйста", "спасибо", "благодарю"]):
            preferences["communication_style"] = "formal"
        elif any(word in text_lower for word in ["привет", "пока", "увидимся"]):
            preferences["communication_style"] = "casual"
    
    async def _create_fallback_context(self, session_id: str, user_id: Optional[str], current_text: str) -> ContextResult:
        """Создание fallback контекста"""
        return ContextResult(
            session_id=session_id,
            user_id=user_id,
            conversation_history=[current_text],
            user_preferences={},
            context_score=0.5,
            metadata={
                "model": "fallback",
                "model_name": "fallback_rules",
                "analysis_method": "fallback"
            }
        )
    
    def get_session_context(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Получение контекста сессии"""
        if session_id in self.context_storage:
            context_data = self.context_storage[session_id]
            return {
                "session_id": session_id,
                "conversation_history": list(context_data["conversation_history"]),
                "user_preferences": context_data["user_preferences"],
                "last_activity": context_data["last_activity"],
                "context_score": context_data["context_score"]
            }
        return None
    
    def clear_session_context(self, session_id: str) -> bool:
        """Очистка контекста сессии"""
        if session_id in self.context_storage:
            del self.context_storage[session_id]
            logger.info(f"Контекст сессии {session_id} очищен")
            return True
        return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Получение информации о модели"""
        return {
            "model_type": self.model["type"],
            "model_name": self.model["name"],
            "config": self.config.model_dump(),
            "loaded": self.model["loaded"],
            "active_sessions": len(self.context_storage)
        }


class ContextAnalysisSystem:
    """Система анализа контекста"""
    
    def __init__(self, model_registry: ModelRegistry, feature_extractor: FeatureExtractor):
        self.model_registry = model_registry
        self.feature_extractor = feature_extractor
        self.analyzers: Dict[str, ContextAnalyzer] = {}
        self._setup_analyzers()
    
    def _setup_analyzers(self) -> None:
        """Настройка анализаторов"""
        # Создание анализаторов для каждого типа модели
        for model_id in self.model_registry.list_models():
            if "context" in model_id.lower():
                config = self.model_registry.get_model_config(model_id)
                if config:
                    self.analyzers[model_id] = ContextAnalyzer(config)
    
    async def analyze_context(self, session_id: str, current_text: str, user_id: Optional[str] = None, model_id: str = "context_analyzer") -> Optional[ContextResult]:
        """Анализ контекста"""
        try:
            # Получение или создание анализатора
            analyzer = self.analyzers.get(model_id)
            if not analyzer:
                config = self.model_registry.get_model_config(model_id)
                if config:
                    analyzer = ContextAnalyzer(config)
                    self.analyzers[model_id] = analyzer
                else:
                    logger.error(f"Модель {model_id} не найдена")
                    return None
            
            # Context analysis / Аналіз контексту
            result = await analyzer.analyze_context(session_id, current_text, user_id)
            
            # Проверка порога уверенности
            if result.context_score < analyzer.config.confidence_threshold:
                logger.warning(f"Низкая оценка контекста: {result.context_score}")
            
            return result
        except Exception as e:
            logger.error(f"Ошибка анализа контекста: {e}")
            return None
    
    async def analyze_context_batch(self, sessions: List[Tuple[str, str, Optional[str]]], model_id: str = "context_analyzer") -> List[Optional[ContextResult]]:
        """Пакетный анализ контекста"""
        tasks = [
            self.analyze_context(session_id, text, user_id, model_id) 
            for session_id, text, user_id in sessions
        ]
        return await asyncio.gather(*tasks)
    
    def get_analyzer_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Получение информации об анализаторе"""
        analyzer = self.analyzers.get(model_id)
        if analyzer:
            return analyzer.get_model_info()
        return None
    
    def list_available_analyzers(self) -> List[str]:
        """Список доступных анализаторов"""
        return list(self.analyzers.keys())
    
    def get_session_context(self, session_id: str, model_id: str = "context_analyzer") -> Optional[Dict[str, Any]]:
        """Получение контекста сессии"""
        analyzer = self.analyzers.get(model_id)
        if analyzer:
            return analyzer.get_session_context(session_id)
        return None
    
    def clear_session_context(self, session_id: str, model_id: str = "context_analyzer") -> bool:
        """Очистка контекста сессии"""
        analyzer = self.analyzers.get(model_id)
        if analyzer:
            return analyzer.clear_session_context(session_id)
        return False
    
    async def train_analyzer(self, model_id: str, training_data: List[Tuple[str, str, Dict[str, Any]]]) -> bool:
        """Обучение анализатора (заглушка)"""
        # TODO: Реализовать обучение анализатора
        logger.info(f"Обучение анализатора {model_id} с {len(training_data)} примерами")
        return True
    
    async def evaluate_analyzer(self, model_id: str, test_data: List[Tuple[str, str, Dict[str, Any]]]) -> Dict[str, float]:
        """Оценка анализатора (заглушка)"""
        # TODO: Реализовать оценку анализатора
        logger.info(f"Оценка анализатора {model_id} с {len(test_data)} примерами")
        return {
            "context_accuracy": 0.85,
            "preference_accuracy": 0.80,
            "session_continuity": 0.90
        } 