"""
Intent Recognition Module for MOVA SDK
Модуль розпізнавання намірів для MOVA SDK

This module provides functionality to recognize user intents from text input.
Цей модуль надає функціональність для розпізнавання намірів
користувача з текстового вводу.
"""

import re
import json
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from dataclasses import dataclass
from pathlib import Path
try:
    from loguru import logger
except ImportError:
    import logging as logger
    logger.basicConfig(level=logger.INFO)


class IntentType(Enum):
    """Types of intents / Типи намірів"""
    GREETING = "greeting"
    FAREWELL = "farewell"
    QUESTION = "question"
    REQUEST = "request"
    COMMAND = "command"
    CONFIRMATION = "confirmation"
    NEGATION = "negation"
    UNKNOWN = "unknown"


@dataclass
class Intent:
    """Intent data class / Клас даних наміру"""
    name: str
    type: IntentType
    confidence: float
    patterns: List[str]
    response_template: Optional[str] = None
    entities: Optional[Dict[str, Any]] = None
    priority: int = 0


class IntentRecognizer:
    """Intent recognition class / Клас розпізнавання намірів"""
    
    def __init__(self, language: str = "uk"):
        """
        Initialize intent recognizer / Ініціалізація розпізнавача намірів
        
        Args:
            language: Language code (default: "uk") /
            Код мови (за замовчуванням: "uk")
        """
        self.language = language
        self.intents: Dict[str, Intent] = {}
        self.entity_patterns: Dict[str, re.Pattern] = {}
        self._load_default_intents()
        self._load_entity_patterns()
        
    def _load_default_intents(self):
        """Load default intents / Завантаження типових намірів"""
        default_intents = {
            "greeting": Intent(
                name="greeting",
                type=IntentType.GREETING,
                confidence=0.0,
                patterns=[
                    r"(?i)\b(привіт|вітаю|добрий\s+(день|ранок|вечір)|"
                    r"здоров|хай\s+буде|hello|hi|hey)\b",
                    r"(?i)\b(доброго\s+(дня|ранку|вечора))\b"
                ],
                response_template="Привіт! Чим я можу допомогти?",
                priority=1
            ),
            "farewell": Intent(
                name="farewell",
                type=IntentType.FAREWELL,
                confidence=0.0,
                patterns=[
                    r"(?i)\b(до\s+побачення|бувай|гарного\s+дня|"
                    r"побачення|bye|goodbye|see\s+you)\b",
                    r"(?i)\b(до\s+зустрічі|прощавайте)\b"
                ],
                response_template="До побачення! Гарного дня!",
                priority=1
            ),
            "confirmation": Intent(
                name="confirmation",
                type=IntentType.CONFIRMATION,
                confidence=0.0,
                patterns=[
                    r"(?i)\b(так|звичайно|звісно|погоджуюсь|"
                    r"yes|yeah|yep|ok|okay)\b",
                    r"(?i)\b(звісно\s+що|безумовно)\b"
                ],
                response_template="Добре, продовжуємо.",
                priority=2
            ),
            "negation": Intent(
                name="negation",
                type=IntentType.NEGATION,
                confidence=0.0,
                patterns=[
                    r"(?i)\b(ні|ніколи|не\s+погоджуюсь|no|nope|not)\b",
                    r"(?i)\b(не\s+хочу|відмовляюсь)\b"
                ],
                response_template="Зрозуміло, скасовуємо.",
                priority=2
            ),
            "question": Intent(
                name="question",
                type=IntentType.QUESTION,
                confidence=0.0,
                patterns=[
                    r"(?i)\b(що|де|коли|чому|як|скільки|хто|чий|який|"
                    r"which|where|when|why|how|many|who|whose)\b",
                    r"(?i)\b(чи\s+можна|чи\s+є|чи\s+можеш|"
                    r"can|could|would|should)\b"
                ],
                priority=1
            ),
            "request": Intent(
                name="request",
                type=IntentType.REQUEST,
                confidence=0.0,
                patterns=[
                    r"(?i)\b(допоможи|потрібно|хочу|бажаю|молю|"
                    r"help|need|want|would\s+like|please)\b",
                    r"(?i)\b(зроби|створи|знайди|покажи|do|create|find|show)\b"
                ],
                priority=1
            ),
            "command": Intent(
                name="command",
                type=IntentType.COMMAND,
                confidence=0.0,
                patterns=[
                    r"(?i)\b(запусти|зупини|перезавантаж|виключи|увімкни|"
                    r"start|stop|restart|turn\s+off|turn\s+on)\b",
                    r"(?i)\b(виконай|зроби|зміни|execute|do|change)\b"
                ],
                priority=1
            )
        }
        
        for name, intent in default_intents.items():
            self.intents[name] = intent
    
    def _load_entity_patterns(self):
        """Load entity patterns / Завантаження шаблонів сутностей"""
        entity_patterns = {
            "time": r"(?i)\b(\d{1,2}:\d{2}|\d{1,2}\s+(годин|хвилин)|"
            r"завтра|сьогодні|ввечері|вранці|вдень)\b",
            "date": r"(?i)\b(\d{1,2}\.\d{1,2}\.\d{4}|\d{4}-\d{2}-\d{2}|"
            r"завтра|сьогодні|післязавтра)\b",
            "phone": r"(?i)\b(\+?\d{12}|\d{10}|\d{3}\s\d{3}\s\d{2}\s\d{2})\b",
            "email": r"(?i)\b([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+"
            r"\.[a-zA-Z]{2,})\b",
            "number": r"(?i)\b(\d+|\d+\.\d+)\b"
        }
        
        for name, pattern in entity_patterns.items():
            self.entity_patterns[name] = re.compile(pattern)
    
    def add_intent(self, intent: Intent):
        """
        Add custom intent / Додати власний намір
        
        Args:
            intent: Intent object / Об'єкт наміру
        """
        self.intents[intent.name] = intent
        logger.info(f"Added custom intent: {intent.name}")
    
    def remove_intent(self, name: str):
        """
        Remove intent / Видалити намір
        
        Args:
            name: Intent name / Назва наміру
        """
        if name in self.intents:
            del self.intents[name]
            logger.info(f"Removed intent: {name}")
    
    def recognize(self, text: str) -> Tuple[Intent, Dict[str, Any]]:
        """
        Recognize intent from text / Розпізнати намір з тексту
        
        Args:
            text: Input text / Вхідний текст
            
        Returns:
            Tuple of (intent, entities) / Кортеж (намір, сутності)
        """
        text = text.strip().lower()
        
        # Extract entities
        entities = self._extract_entities(text)
        
        # Calculate confidence for each intent
        best_intent = None
        best_confidence = 0.0
        
        for intent in self.intents.values():
            confidence = self._calculate_confidence(text, intent)
            
            # Adjust confidence based on priority
            confidence += intent.priority * 0.05
            
            if confidence > best_confidence:
                best_confidence = confidence
                best_intent = intent
        
        # Create result intent with confidence
        if best_intent:
            result_intent = Intent(
                name=best_intent.name,
                type=best_intent.type,
                confidence=min(best_confidence, 1.0),
                patterns=best_intent.patterns,
                response_template=best_intent.response_template,
                entities=entities,
                priority=best_intent.priority
            )
        else:
            result_intent = Intent(
                name="unknown",
                type=IntentType.UNKNOWN,
                confidence=0.0,
                patterns=[],
                entities=entities
            )
        
        return result_intent, entities
    
    def _calculate_confidence(self, text: str, intent: Intent) -> float:
        """
        Calculate confidence score for intent /
        Розрахувати оцінку впевненості для наміру
        
        Args:
            text: Input text / Вхідний текст
            intent: Intent object / Об'єкт наміру
            
        Returns:
            Confidence score (0.0-1.0) / Оцінка впевненості (0.0-1.0)
        """
        max_confidence = 0.0
        
        for pattern in intent.patterns:
            matches = re.findall(pattern, text)
            if matches:
                # Calculate confidence based on number of matches
                confidence = min(len(matches) * 0.3, 0.9)
                
                # Boost confidence for full word matches
                full_match = re.search(pattern, text)
                if full_match and full_match.group(0) == text:
                    confidence += 0.1
                
                max_confidence = max(max_confidence, confidence)
        
        return max_confidence
    
    def _extract_entities(self, text: str) -> Dict[str, Any]:
        """
        Extract entities from text / Витягти сутності з тексту
        
        Args:
            text: Input text / Вхідний текст
            
        Returns:
            Dictionary of entities / Словник сутностей
        """
        entities = {}
        
        for entity_name, pattern in self.entity_patterns.items():
            matches = pattern.findall(text)
            if matches:
                entities[entity_name] = matches
        
        return entities
    
    def get_intent_by_name(self, name: str) -> Optional[Intent]:
        """
        Get intent by name / Отримати намір за назвою
        
        Args:
            name: Intent name / Назва наміру
            
        Returns:
            Intent object or None / Об'єкт наміру або None
        """
        return self.intents.get(name)
    
    def get_all_intents(self) -> List[Intent]:
        """
        Get all intents / Отримати всі наміри
        
        Returns:
            List of all intents / Список всіх намірів
        """
        return list(self.intents.values())
    
    def save_intents(self, file_path: str):
        """
        Save intents to file / Зберегти наміри у файл
        
        Args:
            file_path: Path to save file / Шлях до файлу для збереження
        """
        intents_data = {}
        
        for name, intent in self.intents.items():
            intents_data[name] = {
                "name": intent.name,
                "type": intent.type.value,
                "patterns": intent.patterns,
                "response_template": intent.response_template,
                "priority": intent.priority
            }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(intents_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved intents to: {file_path}")
    
    def load_intents(self, file_path: str):
        """
        Load intents from file / Завантажити наміри з файлу
        
        Args:
            file_path: Path to load file / Шлях до файлу для завантаження
        """
        if not Path(file_path).exists():
            logger.warning(f"Intents file not found: {file_path}")
            return
        
        with open(file_path, 'r', encoding='utf-8') as f:
            intents_data = json.load(f)
        
        for name, data in intents_data.items():
            intent = Intent(
                name=data["name"],
                type=IntentType(data["type"]),
                confidence=0.0,
                patterns=data["patterns"],
                response_template=data.get("response_template"),
                priority=data.get("priority", 0)
            )
            self.intents[name] = intent
        
        logger.info(f"Loaded intents from: {file_path}")
    
    def train(self, training_data: List[Dict[str, Any]]):
        """
        Train intent recognizer with custom data /
        Навчання розпізнавача намірів з власними даними
        
        Args:
            training_data: List of training examples /
            Список навчальних прикладів
        """
        for example in training_data:
            text = example.get("text", "")
            intent_name = example.get("intent", "")
            
            if text and intent_name:
                # Extract entities if provided
                # entities = example.get("entities", {})
                
                # Create or update intent
                if intent_name not in self.intents:
                    self.intents[intent_name] = Intent(
                        name=intent_name,
                        type=IntentType.REQUEST,
                        confidence=0.0,
                        patterns=[],
                        priority=1
                    )
                
                # Add text as pattern if not already present
                intent = self.intents[intent_name]
                pattern_text = re.escape(text.lower())
                
                # Create a simple pattern that matches the text
                pattern = rf"(?i)\b{pattern_text}\b"
                if pattern not in intent.patterns:
                    intent.patterns.append(pattern)
        
        logger.info(f"Trained with {len(training_data)} examples")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get recognizer statistics / Отримати статистику розпізнавача
        
        Returns:
            Dictionary with statistics / Словник зі статистикою
        """
        return {
            "total_intents": len(self.intents),
            "intent_types": {
                intent_type.value: sum(
                    1 for i in self.intents.values()
                    if i.type == intent_type
                )
                for intent_type in IntentType
            },
            "entity_types": list(self.entity_patterns.keys()),
            "language": self.language
        }


# Example usage / Приклад використання
if __name__ == "__main__":
    # Initialize recognizer / Ініціалізація розпізнавача
    recognizer = IntentRecognizer(language="uk")
    
    # Recognize intent / Розпізнати намір
    text = "Привіт! Як справи?"
    intent, entities = recognizer.recognize(text)
    
    print(f"Text: {text}")
    print(f"Intent: {intent.name} (confidence: {intent.confidence:.2f})")
    print(f"Entities: {entities}")
    
    # Add custom intent / Додати власний намір
    custom_intent = Intent(
        name="schedule_appointment",
        type=IntentType.REQUEST,
        confidence=0.0,
        patterns=[
            r"(?i)\b(записатись|запис|запланувати|призначити)\b",
            r"(?i)\b(на\s+(завтра|сьогодні|післязавтра))\b"
        ],
        response_template="Я можу допомогти вам записатися. На який час?",
        priority=3
    )
    recognizer.add_intent(custom_intent)
    
    # Test custom intent / Тестування власного наміру
    text = "Хочу записатися на завтра"
    intent, entities = recognizer.recognize(text)
    
    print(f"\nText: {text}")
    print(f"Intent: {intent.name} (confidence: {intent.confidence:.2f})")
    print(f"Entities: {entities}")
    
    # Get statistics / Отримати статистику
    stats = recognizer.get_statistics()
    print(f"\nStatistics: {stats}")