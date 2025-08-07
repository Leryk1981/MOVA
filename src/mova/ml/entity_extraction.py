"""
Система извлечения сущностей для MOVA SDK

Предоставляет функциональность для извлечения именованных сущностей:
- EntityExtractor: Извлекатель сущностей
- EntityExtractionSystem: Система извлечения сущностей
"""

import asyncio
import logging
import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from .models import Entity, EntityResult, EntityType, MLModelConfig, MLModelType
from .foundation import ModelRegistry, FeatureExtractor


logger = logging.getLogger(__name__)


class EntityExtractor:
    """Извлекатель сущностей"""
    
    def __init__(self, model_config: MLModelConfig):
        self.config = model_config
        self.model = None
        self._load_model()
        self._setup_patterns()
    
    def _load_model(self) -> None:
        """Загрузка модели извлекателя"""
        try:
            if self.config.model_type == MLModelType.SPACY:
                self.model = self._load_spacy_model()
            elif self.config.model_type == MLModelType.BERT:
                self.model = self._load_bert_model()
            else:
                logger.warning(f"Неподдерживаемый тип модели: {self.config.model_type}")
                self.model = self._load_fallback_model()
        except Exception as e:
            logger.error(f"Ошибка загрузки модели: {e}")
            self.model = self._load_fallback_model()
    
    def _load_spacy_model(self) -> Dict[str, Any]:
        """Загрузка spaCy модели (заглушка)"""
        # TODO: Реализовать загрузку реальной spaCy модели
        logger.info(f"Загрузка spaCy модели: {self.config.model_name}")
        return {
            "type": "spacy",
            "name": self.config.model_name,
            "config": self.config.model_dump(),
            "loaded": True
        }
    
    def _load_bert_model(self) -> Dict[str, Any]:
        """Загрузка BERT модели для NER (заглушка)"""
        # TODO: Реализовать загрузку реальной BERT NER модели
        logger.info(f"Загрузка BERT NER модели: {self.config.model_name}")
        return {
            "type": "bert",
            "name": self.config.model_name,
            "config": self.config.model_dump(),
            "loaded": True
        }
    
    def _load_fallback_model(self) -> Dict[str, Any]:
        """Загрузка fallback модели (регулярные выражения)"""
        logger.info("Загрузка fallback модели (регулярные выражения)")
        return {
            "type": "regex",
            "name": "fallback_regex",
            "config": self.config.model_dump(),
            "loaded": True
        }
    
    def _setup_patterns(self) -> None:
        """Настройка паттернов для извлечения сущностей"""
        self.patterns = {
            EntityType.EMAIL: [
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                r'\b[а-яА-Я0-9._%+-]+@[а-яА-Я0-9.-]+\.[A-Z|a-z]{2,}\b'
            ],
            EntityType.PHONE: [
                r'\b\+?[1-9]\d{1,14}\b',
                r'\b\+?[1-9]\d{3}\d{3}\d{2}\d{2}\b',  # +7 999 123 45 67
                r'\b8\d{10}\b',  # 8 999 123 45 67
                r'\b\+7\d{10}\b'  # +7 999 123 45 67
            ],
            EntityType.PERSON: [
                r'\b[A-ZА-Я][a-zа-я]+\s+[A-ZА-Я][a-zа-я]+\b',
                r'\b[A-ZА-Я][a-zа-я]+\s+[A-ZА-Я]\.\s*[A-ZА-Я]\.\b'
            ],
            EntityType.ORGANIZATION: [
                r'\b[A-ZА-Я][A-ZА-Яa-zа-я\s&]+(?:ООО|ИП|АО|ЗАО|ОАО)\b',
                r'\b(?:ООО|ИП|АО|ЗАО|ОАО)\s+["""][^"""]+["""]\b'
            ],
            EntityType.LOCATION: [
                r'\b(?:г\.|город|село|деревня|поселок)\s+[А-Яа-я]+\b',
                r'\b(?:ул\.|улица|проспект|переулок)\s+[А-Яа-я]+\b'
            ],
            EntityType.DATE: [
                r'\b\d{1,2}\.\d{1,2}\.\d{4}\b',
                r'\b\d{4}-\d{2}-\d{2}\b',
                r'\b(?:сегодня|вчера|завтра|позавчера|послезавтра)\b'
            ],
            EntityType.TIME: [
                r'\b\d{1,2}:\d{2}(?::\d{2})?\b',
                r'\b(?:утро|день|вечер|ночь)\b'
            ],
            EntityType.MONEY: [
                r'\b\d+(?:,\d{3})*(?:\.\d{2})?\s*(?:руб|рублей|рубля|₽|доллар|долларов|€|евро)\b',
                r'\b(?:руб|рублей|рубля|₽|доллар|долларов|€|евро)\s*\d+(?:,\d{3})*(?:\.\d{2})?\b'
            ],
            EntityType.PERCENT: [
                r'\b\d+(?:\.\d+)?%\b',
                r'\b(?:процент|процентов)\s*\d+(?:\.\d+)?\b'
            ]
        }
    
    async def extract_entities(self, text: str) -> EntityResult:
        """Extract entities from text / Витяг сутностей з тексту"""
        try:
            if self.model["type"] == "spacy":
                return await self._extract_with_spacy(text)
            elif self.model["type"] == "bert":
                return await self._extract_with_bert(text)
            else:
                return await self._extract_with_regex(text)
        except Exception as e:
            logger.error(f"Ошибка извлечения сущностей: {e}")
            return await self._extract_with_regex(text)
    
    async def _extract_with_spacy(self, text: str) -> EntityResult:
        """Извлечение с использованием spaCy (заглушка)"""
        # TODO: Implement real extraction with spaCy / Реалізувати реальний витяг з spaCy
        loop = asyncio.get_event_loop()
        entities = await loop.run_in_executor(None, self._extract_sync, text)
        return EntityResult(
            entities=entities,
            text=text,
            metadata={
                "model": "spacy",
                "model_name": self.model["name"],
                "extraction_method": "spacy_ner"
            }
        )
    
    async def _extract_with_bert(self, text: str) -> EntityResult:
        """Извлечение с использованием BERT (заглушка)"""
        # TODO: Реализовать реальное извлечение с BERT
        loop = asyncio.get_event_loop()
        entities = await loop.run_in_executor(None, self._extract_sync, text)
        return EntityResult(
            entities=entities,
            text=text,
            metadata={
                "model": "bert",
                "model_name": self.model["name"],
                "extraction_method": "bert_ner"
            }
        )
    
    async def _extract_with_regex(self, text: str) -> EntityResult:
        """Извлечение с использованием регулярных выражений"""
        loop = asyncio.get_event_loop()
        entities = await loop.run_in_executor(None, self._extract_sync, text)
        return EntityResult(
            entities=entities,
            text=text,
            metadata={
                "model": "regex",
                "model_name": "fallback_regex",
                "extraction_method": "regex_patterns"
            }
        )
    
    def _extract_sync(self, text: str) -> List[Entity]:
        """Синхронное извлечение сущностей"""
        entities = []
        
        # Извлечение с использованием паттернов
        for entity_type, patterns in self.patterns.items():
            for pattern in patterns:
                for match in re.finditer(pattern, text, re.IGNORECASE):
                    # Проверка на перекрытие с уже найденными сущностями
                    if not self._is_overlapping(match, entities):
                        confidence = self._calculate_confidence(match.group(), entity_type)
                        entities.append(Entity(
                            text=match.group(),
                            entity_type=entity_type,
                            start=match.start(),
                            end=match.end(),
                            confidence=confidence
                        ))
        
        # Сортировка по позиции в тексте
        entities.sort(key=lambda x: x.start)
        
        return entities
    
    def _is_overlapping(self, match: re.Match, entities: List[Entity]) -> bool:
        """Проверка на перекрытие с существующими сущностями"""
        match_start, match_end = match.start(), match.end()
        for entity in entities:
            if (match_start < entity.end and match_end > entity.start):
                return True
        return False
    
    def _calculate_confidence(self, text: str, entity_type: EntityType) -> float:
        """Расчет уверенности в извлечении сущности"""
        base_confidence = 0.8
        
        # Дополнительные проверки для повышения уверенности
        if entity_type == EntityType.EMAIL:
            if '@' in text and '.' in text.split('@')[1]:
                base_confidence = 0.98
        elif entity_type == EntityType.PHONE:
            if len(text.replace('+', '').replace(' ', '')) >= 10:
                base_confidence = 0.95
        elif entity_type == EntityType.PERSON:
            if len(text.split()) >= 2:
                base_confidence = 0.90
        
        return min(base_confidence, 0.99)
    
    def get_supported_entities(self) -> List[EntityType]:
        """Получение списка поддерживаемых типов сущностей"""
        return list(EntityType)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Получение информации о модели"""
        return {
            "model_type": self.model["type"],
            "model_name": self.model["name"],
            "config": self.config.model_dump(),
            "loaded": self.model["loaded"],
            "supported_entities": [entity.value for entity in self.get_supported_entities()],
            "patterns_count": len(self.patterns)
        }


class EntityExtractionSystem:
    """Система извлечения сущностей"""
    
    def __init__(self, model_registry: ModelRegistry, feature_extractor: FeatureExtractor):
        self.model_registry = model_registry
        self.feature_extractor = feature_extractor
        self.extractors: Dict[str, EntityExtractor] = {}
        self._setup_extractors()
    
    def _setup_extractors(self) -> None:
        """Настройка извлекателей"""
        # Создание извлекателей для каждого типа модели
        for model_id in self.model_registry.list_models():
            if "entity" in model_id.lower():
                config = self.model_registry.get_model_config(model_id)
                if config:
                    self.extractors[model_id] = EntityExtractor(config)
    
    async def extract_entities(self, text: str, model_id: str = "entity_extractor") -> Optional[EntityResult]:
        """Извлечение сущностей"""
        try:
            # Получение или создание извлекателя
            extractor = self.extractors.get(model_id)
            if not extractor:
                config = self.model_registry.get_model_config(model_id)
                if config:
                    extractor = EntityExtractor(config)
                    self.extractors[model_id] = extractor
                else:
                    logger.error(f"Модель {model_id} не найдена")
                    return None
            
            # Извлечение сущностей
            result = await extractor.extract_entities(text)
            
            # Фильтрация по порогу уверенности
            filtered_entities = [
                entity for entity in result.entities 
                if entity.confidence >= extractor.config.confidence_threshold
            ]
            
            result.entities = filtered_entities
            return result
        except Exception as e:
            logger.error(f"Ошибка извлечения сущностей: {e}")
            return None
    
    async def extract_entities_batch(self, texts: List[str], model_id: str = "entity_extractor") -> List[Optional[EntityResult]]:
        """Пакетное извлечение сущностей"""
        tasks = [self.extract_entities(text, model_id) for text in texts]
        return await asyncio.gather(*tasks)
    
    def get_extractor_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Получение информации об извлекателе"""
        extractor = self.extractors.get(model_id)
        if extractor:
            return extractor.get_model_info()
        return None
    
    def list_available_extractors(self) -> List[str]:
        """Список доступных извлекателей"""
        return list(self.extractors.keys())
    
    async def add_custom_entity_pattern(self, entity_type: EntityType, pattern: str, model_id: str = "entity_extractor") -> bool:
        """Добавление пользовательского паттерна для извлечения сущностей"""
        try:
            extractor = self.extractors.get(model_id)
            if extractor and extractor.model["type"] == "regex":
                if entity_type not in extractor.patterns:
                    extractor.patterns[entity_type] = []
                extractor.patterns[entity_type].append(pattern)
                logger.info(f"Добавлен пользовательский паттерн для {entity_type}: {pattern}")
                return True
            else:
                logger.warning("Пользовательские паттерны поддерживаются только для regex моделей")
                return False
        except Exception as e:
            logger.error(f"Ошибка добавления пользовательского паттерна: {e}")
            return False
    
    async def train_extractor(self, model_id: str, training_data: List[Tuple[str, List[Entity]]]) -> bool:
        """Обучение извлекателя (заглушка)"""
        # TODO: Реализовать обучение извлекателя
        logger.info(f"Обучение извлекателя {model_id} с {len(training_data)} примерами")
        return True
    
    async def evaluate_extractor(self, model_id: str, test_data: List[Tuple[str, List[Entity]]]) -> Dict[str, float]:
        """Оценка извлекателя (заглушка)"""
        # TODO: Реализовать оценку извлекателя
        logger.info(f"Оценка извлекателя {model_id} с {len(test_data)} примерами")
        return {
            "precision": 0.85,
            "recall": 0.82,
            "f1_score": 0.83,
            "accuracy": 0.80
        } 