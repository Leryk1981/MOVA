"""
Memory System for MOVA SDK
Система пам'яті для MOVA SDK

This module provides functionality to store, retrieve, and manage
conversation memory.
Цей модуль надає функціональність для зберігання, отримання та
управління пам'яттю розмови.
"""

import json
import time
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass, asdict
from pathlib import Path
from uuid import uuid4
try:
    from loguru import logger
except ImportError:
    import logging as logger
    logger.basicConfig(level=logger.INFO)


class MemoryType(Enum):
    """Types of memory entries / Типи записів пам'яті"""
    CONVERSATION = "conversation"
    CONTEXT = "context"
    KNOWLEDGE = "knowledge"
    ENTITY = "entity"
    RELATIONSHIP = "relationship"
    PREFERENCE = "preference"
    SYSTEM = "system"


class MemoryPriority(Enum):
    """Priority levels for memory entries /
    Рівні пріоритету для записів пам'яті"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class MemoryEntry:
    """Memory entry data class / Клас даних запису пам'яті"""
    id: str
    type: MemoryType
    content: Any
    timestamp: float
    session_id: str
    user_id: str
    priority: MemoryPriority = MemoryPriority.NORMAL
    ttl: Optional[float] = None  # Time to live in seconds
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Post-initialization processing / Післяініціалізаційна обробка"""
        if self.tags is None:
            self.tags = []
        if self.metadata is None:
            self.metadata = {}
    
    def is_expired(self) -> bool:
        """Check if memory entry is expired /
        Перевірити, чи закінчився термін дії запису пам'яті"""
        if self.ttl is None:
            return False
        return time.time() > self.timestamp + self.ttl
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary / Конвертувати у словник"""
        data = asdict(self)
        data['type'] = self.type.value
        data['priority'] = self.priority.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryEntry':
        """Create from dictionary / Створити зі словника"""
        data['type'] = MemoryType(data['type'])
        data['priority'] = MemoryPriority(data['priority'])
        return cls(**data)


class MemorySystem:
    """Memory system class / Клас системи пам'яті"""
    
    def __init__(self, storage_path: Optional[str] = None,
                 max_memory_size: int = 10000):
        """
        Initialize memory system / Ініціалізація системи пам'яті
        
        Args:
            storage_path: Path to storage file / Шлях до файлу зберігання
            max_memory_size: Maximum number of memory entries /
            Максимальна кількість записів пам'яті
        """
        self.storage_path = Path(storage_path) if storage_path else None
        self.max_memory_size = max_memory_size
        self.memory: Dict[str, MemoryEntry] = {}
        self.indices: Dict[str, Dict[str, List[str]]] = {
            'session': {},
            'user': {},
            'type': {},
            'tags': {}
        }
        
        # Load existing memory if storage path is provided
        if self.storage_path and self.storage_path.exists():
            self.load_memory()
        
        logger.info(
            f"Memory system initialized with {len(self.memory)} entries")
    
    def add_memory(self, 
                   content: Any,
                   memory_type: MemoryType,
                   session_id: str,
                   user_id: str,
                   priority: MemoryPriority = MemoryPriority.NORMAL,
                   ttl: Optional[float] = None,
                   tags: Optional[List[str]] = None,
                   metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Add memory entry / Додати запис пам'яті
        
        Args:
            content: Memory content / Вміст пам'яті
            memory_type: Type of memory / Тип пам'яті
            session_id: Session ID / ID сесії
            user_id: User ID / ID користувача
            priority: Memory priority / Пріоритет пам'яті
            ttl: Time to live in seconds / Час життя в секундах
            tags: List of tags / Список тегів
            metadata: Additional metadata / Додаткові метадані
            
        Returns:
            Memory entry ID / ID запису пам'яті
        """
        # Check memory size limit
        if len(self.memory) >= self.max_memory_size:
            self._cleanup_memory()
        
        # Create memory entry
        memory_id = str(uuid4())
        entry = MemoryEntry(
            id=memory_id,
            type=memory_type,
            content=content,
            timestamp=time.time(),
            session_id=session_id,
            user_id=user_id,
            priority=priority,
            ttl=ttl,
            tags=tags or [],
            metadata=metadata or {}
        )
        
        # Store memory
        self.memory[memory_id] = entry
        
        # Update indices
        self._update_indices(entry)
        
        # Save to storage if path is provided
        if self.storage_path:
            self.save_memory()
        
        logger.debug(f"Added memory entry: {memory_id} ({memory_type.value})")
        return memory_id
    
    def get_memory(self, memory_id: str) -> Optional[MemoryEntry]:
        """
        Get memory entry by ID / Отримати запис пам'яті за ID
        
        Args:
            memory_id: Memory entry ID / ID запису пам'яті
            
        Returns:
            Memory entry or None / Запис пам'яті або None
        """
        entry = self.memory.get(memory_id)
        if entry and entry.is_expired():
            self.remove_memory(memory_id)
            return None
        return entry
    
    def remove_memory(self, memory_id: str) -> bool:
        """
        Remove memory entry / Видалити запис пам'яті
        
        Args:
            memory_id: Memory entry ID / ID запису пам'яті
            
        Returns:
            True if removed / True, якщо видалено
        """
        entry = self.memory.get(memory_id)
        if not entry:
            return False
        
        # Remove from memory
        del self.memory[memory_id]
        
        # Remove from indices
        self._remove_from_indices(entry)
        
        # Save to storage if path is provided
        if self.storage_path:
            self.save_memory()
        
        logger.debug(f"Removed memory entry: {memory_id}")
        return True
    
    def update_memory(self, 
                      memory_id: str,
                      content: Optional[Any] = None,
                      priority: Optional[MemoryPriority] = None,
                      tags: Optional[List[str]] = None,
                      metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Update memory entry / Оновити запис пам'яті
        
        Args:
            memory_id: Memory entry ID / ID запису пам'яті
            content: New content / Новий вміст
            priority: New priority / Новий пріоритет
            tags: New tags / Нові теги
            metadata: New metadata / Нові метадані
            
        Returns:
            True if updated / True, якщо оновлено
        """
        entry = self.memory.get(memory_id)
        if not entry:
            return False
        
        # Remove from indices before updating
        self._remove_from_indices(entry)
        
        # Update fields
        if content is not None:
            entry.content = content
        if priority is not None:
            entry.priority = priority
        if tags is not None:
            entry.tags = tags
        if metadata is not None:
            entry.metadata = metadata
        
        # Update timestamp
        entry.timestamp = time.time()
        
        # Update indices
        self._update_indices(entry)
        
        # Save to storage if path is provided
        if self.storage_path:
            self.save_memory()
        
        logger.debug(f"Updated memory entry: {memory_id}")
        return True
    
    def get_session_memory(self, session_id: str, 
                          memory_type: Optional[MemoryType] = None,
                          limit: Optional[int] = None) -> List[MemoryEntry]:
        """
        Get memory entries for a session / Отримати записи пам'яті для сесії
        
        Args:
            session_id: Session ID / ID сесії
            memory_type: Filter by memory type / Фільтрувати за типом пам'яті
            limit: Maximum number of entries / Максимальна кількість записів
            
        Returns:
            List of memory entries / Список записів пам'яті
        """
        memory_ids = self.indices['session'].get(session_id, [])
        entries = []
        
        for memory_id in memory_ids:
            entry = self.get_memory(memory_id)
            if entry and (memory_type is None or entry.type == memory_type):
                entries.append(entry)
        
        # Sort by timestamp (newest first)
        entries.sort(key=lambda x: x.timestamp, reverse=True)
        
        if limit:
            entries = entries[:limit]
        
        return entries
    
    def get_user_memory(self, user_id: str,
                       memory_type: Optional[MemoryType] = None,
                       limit: Optional[int] = None) -> List[MemoryEntry]:
        """
        Get memory entries for a user / Отримати записи пам'яті для користувача
        
        Args:
            user_id: User ID / ID користувача
            memory_type: Filter by memory type / Фільтрувати за типом пам'яті
            limit: Maximum number of entries / Максимальна кількість записів
            
        Returns:
            List of memory entries / Список записів пам'яті
        """
        memory_ids = self.indices['user'].get(user_id, [])
        entries = []
        
        for memory_id in memory_ids:
            entry = self.get_memory(memory_id)
            if entry and (memory_type is None or entry.type == memory_type):
                entries.append(entry)
        
        # Sort by timestamp (newest first)
        entries.sort(key=lambda x: x.timestamp, reverse=True)
        
        if limit:
            entries = entries[:limit]
        
        return entries
    
    def get_memory_by_tags(self, tags: List[str],
                          operator: str = "AND") -> List[MemoryEntry]:
        """
        Get memory entries by tags / Отримати записи пам'яті за тегами
        
        Args:
            tags: List of tags / Список тегів
            operator: "AND" or "OR" / "AND" або "OR"
            
        Returns:
            List of memory entries / Список записів пам'яті
        """
        if operator not in ["AND", "OR"]:
            raise ValueError("Operator must be 'AND' or 'OR'")
        
        matching_ids = set()
        
        for tag in tags:
            tag_ids = set(self.indices['tags'].get(tag, []))
            if operator == "AND":
                if not matching_ids:
                    matching_ids = tag_ids
                else:
                    matching_ids.intersection_update(tag_ids)
            else:  # OR
                matching_ids.update(tag_ids)
        
        entries = []
        for memory_id in matching_ids:
            entry = self.get_memory(memory_id)
            if entry:
                entries.append(entry)
        
        # Sort by timestamp (newest first)
        entries.sort(key=lambda x: x.timestamp, reverse=True)
        
        return entries
    
    def get_conversation_history(self, session_id: str, 
                                limit: Optional[int] = None
                                ) -> List[Dict[str, Any]]:
        """
        Get conversation history for a session /
        Отримати історію розмови для сесії
        
        Args:
            session_id: Session ID / ID сесії
            limit: Maximum number of entries / Максимальна кількість записів
            
        Returns:
            List of conversation entries / Список записів розмови
        """
        entries = self.get_session_memory(
            session_id, MemoryType.CONVERSATION, limit)
        
        history = []
        for entry in entries:
            history.append({
                'timestamp': entry.timestamp,
                'role': entry.metadata.get('role', 'unknown'),
                'content': entry.content
            })
        
        return history
    
    def add_conversation_turn(self,
                             session_id: str,
                             user_id: str,
                             role: str,
                             content: str) -> str:
        """
        Add conversation turn / Додати хід розмови
        
        Args:
            session_id: Session ID / ID сесії
            user_id: User ID / ID користувача
            role: Role (user, assistant, system) /
            Роль (користувач, асистент, система)
            content: Conversation content / Вміст розмови
            
        Returns:
            Memory entry ID / ID запису пам'яті
        """
        return self.add_memory(
            content=content,
            memory_type=MemoryType.CONVERSATION,
            session_id=session_id,
            user_id=user_id,
            priority=MemoryPriority.NORMAL,
            tags=['conversation', role],
            metadata={'role': role}
        )
    
    def get_context(self, session_id: str, 
                   context_type: Optional[str] = None
                   ) -> Dict[str, Any]:
        """
        Get context for a session / Отримати контекст для сесії
        
        Args:
            session_id: Session ID / ID сесії
            context_type: Type of context / Тип контексту
            
        Returns:
            Context dictionary / Словник контексту
        """
        entries = self.get_session_memory(session_id, MemoryType.CONTEXT)
        
        context = {}
        for entry in entries:
            if (context_type is None or
                entry.metadata.get('context_type') == context_type):
                context.update(entry.content)
        
        return context
    
    def update_context(self, session_id: str,
                      context_data: Dict[str, Any],
                      context_type: str = "general") -> bool:
        """
        Update context for a session / Оновити контекст для сесії
        
        Args:
            session_id: Session ID / ID сесії
            context_data: Context data / Дані контексту
            context_type: Type of context / Тип контексту
            
        Returns:
            True if updated / True, якщо оновлено
        """
        # Get existing context
        existing_context = self.get_context(session_id, context_type)
        
        # Update context data
        existing_context.update(context_data)
        
        # Check if context memory exists
        entries = self.get_session_memory(session_id, MemoryType.CONTEXT)
        context_entry = None
        
        for entry in entries:
            if entry.metadata.get('context_type') == context_type:
                context_entry = entry
                break
        
        if context_entry:
            # Update existing context
            return self.update_memory(
                context_entry.id,
                content=existing_context
            )
        else:
            # Create new context
            self.add_memory(
                content=existing_context,
                memory_type=MemoryType.CONTEXT,
                session_id=session_id,
                user_id="system",
                priority=MemoryPriority.HIGH,
                tags=['context', context_type],
                metadata={'context_type': context_type}
            )
            return True
    
    def _update_indices(self, entry: MemoryEntry):
        """Update indices for memory entry /
        Оновити індекси для запису пам'яті"""
        # Update session index
        if entry.session_id not in self.indices['session']:
            self.indices['session'][entry.session_id] = []
        if entry.id not in self.indices['session'][entry.session_id]:
            self.indices['session'][entry.session_id].append(entry.id)
        
        # Update user index
        if entry.user_id not in self.indices['user']:
            self.indices['user'][entry.user_id] = []
        if entry.id not in self.indices['user'][entry.user_id]:
            self.indices['user'][entry.user_id].append(entry.id)
        
        # Update type index
        type_name = entry.type.value
        if type_name not in self.indices['type']:
            self.indices['type'][type_name] = []
        if entry.id not in self.indices['type'][type_name]:
            self.indices['type'][type_name].append(entry.id)
        
        # Update tags index
        for tag in entry.tags:
            if tag not in self.indices['tags']:
                self.indices['tags'][tag] = []
            if entry.id not in self.indices['tags'][tag]:
                self.indices['tags'][tag].append(entry.id)
    
    def _remove_from_indices(self, entry: MemoryEntry):
        """Remove memory entry from indices /
        Видалити запис пам'яті з індексів"""
        # Remove from session index
        if entry.session_id in self.indices['session']:
            if entry.id in self.indices['session'][entry.session_id]:
                self.indices['session'][entry.session_id].remove(entry.id)
        
        # Remove from user index
        if entry.user_id in self.indices['user']:
            if entry.id in self.indices['user'][entry.user_id]:
                self.indices['user'][entry.user_id].remove(entry.id)
        
        # Remove from type index
        type_name = entry.type.value
        if type_name in self.indices['type']:
            if entry.id in self.indices['type'][type_name]:
                self.indices['type'][type_name].remove(entry.id)
        
        # Remove from tags index
        for tag in entry.tags:
            if tag in self.indices['tags']:
                if entry.id in self.indices['tags'][tag]:
                    self.indices['tags'][tag].remove(entry.id)
    
    def _cleanup_memory(self):
        """Clean up expired and low-priority memory /
        Очистити закінчену та низькопріоритетну пам'ять"""
        # Remove expired entries
        expired_ids = []
        for memory_id, entry in self.memory.items():
            if entry.is_expired():
                expired_ids.append(memory_id)
        
        for memory_id in expired_ids:
            self.remove_memory(memory_id)
        
        # If still over limit, remove low-priority entries
        if len(self.memory) >= self.max_memory_size:
            # Sort by priority and timestamp
            entries = sorted(
                self.memory.values(),
                key=lambda x: (x.priority.value, x.timestamp)
            )
            
            # Remove oldest low-priority entries
            to_remove = len(self.memory) - self.max_memory_size + 100
            for i in range(to_remove):
                if i < len(entries):
                    self.remove_memory(entries[i].id)
    
    def save_memory(self):
        """Save memory to storage / Зберегти пам'ять у сховище"""
        if not self.storage_path:
            return
        
        try:
            data = {
                'memory': {
                    mid: entry.to_dict()
                    for mid, entry in self.memory.items()
                },
                'indices': self.indices
            }
            
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Saved memory to: {self.storage_path}")
        except Exception as e:
            logger.error(f"Failed to save memory: {e}")
    
    def load_memory(self):
        """Load memory from storage / Завантажити пам'ять зі сховища"""
        if not self.storage_path or not self.storage_path.exists():
            return
        
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Load memory entries
            self.memory = {}
            for memory_id, entry_data in data.get('memory', {}).items():
                self.memory[memory_id] = MemoryEntry.from_dict(entry_data)
            
            # Load indices
            self.indices = data.get('indices', {
                'session': {},
                'user': {},
                'type': {},
                'tags': {}
            })
            
            logger.debug(f"Loaded memory from: {self.storage_path}")
        except Exception as e:
            logger.error(f"Failed to load memory: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get memory system statistics / Отримати статистику системи пам'яті
        
        Returns:
            Statistics dictionary / Словник статистики
        """
        stats = {
            'total_entries': len(self.memory),
            'entries_by_type': {},
            'entries_by_priority': {},
            'total_sessions': len(self.indices['session']),
            'total_users': len(self.indices['user']),
            'total_tags': len(self.indices['tags'])
        }
        
        # Count by type
        for type_name, memory_ids in self.indices['type'].items():
            stats['entries_by_type'][type_name] = len(memory_ids)
        
        # Count by priority
        priority_counts = {p.value: 0 for p in MemoryPriority}
        for entry in self.memory.values():
            priority_counts[entry.priority.value] += 1
        stats['entries_by_priority'] = priority_counts
        
        return stats
    
    def clear_session_memory(self, session_id: str):
        """Clear all memory for a session / Очистити всю пам'ять для сесії"""
        memory_ids = self.indices['session'].get(session_id, []).copy()
        
        for memory_id in memory_ids:
            self.remove_memory(memory_id)
        
        logger.info(f"Cleared memory for session: {session_id}")
    
    def clear_user_memory(self, user_id: str):
        """Clear all memory for a user /
        Очистити всю пам'ять для користувача"""
        memory_ids = self.indices['user'].get(user_id, []).copy()
        
        for memory_id in memory_ids:
            self.remove_memory(memory_id)
        
        logger.info(f"Cleared memory for user: {user_id}")


# Example usage / Приклад використання
if __name__ == "__main__":
    # Initialize memory system / Ініціалізація системи пам'яті
    memory_system = MemorySystem(storage_path="memory.json")
    
    # Add conversation turn / Додати хід розмови
    session_id = "test_session"
    user_id = "test_user"
    
    memory_system.add_conversation_turn(
        session_id=session_id,
        user_id=user_id,
        role="user",
        content="Привіт! Як справи?"
    )
    
    memory_system.add_conversation_turn(
        session_id=session_id,
        user_id=user_id,
        role="assistant",
        content="Привіт! У мене все добре, дякую! Як я можу вам допомогти?"
    )
    
    # Add context / Додати контекст
    memory_system.update_context(
        session_id=session_id,
        context_data={"user_name": "Іван", "language": "uk"},
        context_type="user_info"
    )
    
    # Get conversation history / Отримати історію розмови
    history = memory_system.get_conversation_history(session_id)
    print("Conversation History:")
    for turn in history:
        print(f"{turn['role']}: {turn['content']}")
    
    # Get context / Отримати контекст
    context = memory_system.get_context(session_id, "user_info")
    print(f"\nContext: {context}")
    
    # Get statistics / Отримати статистику
    stats = memory_system.get_statistics()
    print(f"\nStatistics: {stats}")