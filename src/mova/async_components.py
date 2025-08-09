"""
Asynchronous components for MOVA SDK
Асинхронні компоненти для MOVA SDK
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from concurrent.futures import ThreadPoolExecutor
from functools import wraps
from loguru import logger

from .config import get_config_value
from .cache import get_async_cache
from .http_client import get_async_http_client, close_http_clients
from .redis_manager import get_redis_manager
from .webhook import get_webhook_manager


class AsyncTaskStatus(str, Enum):
    """Status of async tasks / Статус асинхронних завдань"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class AsyncTaskResult:
    """Result of an async task / Результат асинхронного завдання"""
    task_id: str
    status: AsyncTaskStatus
    result: Any = None
    error: Optional[Exception] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class AsyncTaskManager:
    """
    Manager for asynchronous tasks
    Менеджер для асинхронних завдань
    """
    
    def __init__(self, max_concurrent_tasks: int = 10):
        """
        Initialize async task manager
        Ініціалізувати менеджер асинхронних завдань
        
        Args:
            max_concurrent_tasks: Maximum number of concurrent tasks
                Максимальна кількість одночасних завдань
        """
        self.max_concurrent_tasks = max_concurrent_tasks
        self.tasks: Dict[str, asyncio.Task] = {}
        self.results: Dict[str, AsyncTaskResult] = {}
        self.semaphore = asyncio.Semaphore(max_concurrent_tasks)
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent_tasks)
        self.logger = logging.getLogger(__name__)
        
        # Performance tracking
        self.stats = {
            "tasks_created": 0,
            "tasks_completed": 0,
            "tasks_failed": 0,
            "avg_execution_time": 0.0
        }
    
    async def create_task(
        self, 
        coro, 
        task_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a new async task
        Створити нове асинхронне завдання
        
        Args:
            coro: Coroutine to execute / Корутина для виконання
            task_id: Optional task ID / Опціональний ID завдання
            metadata: Optional metadata / Опціональні метадані
            
        Returns:
            Task ID / ID завдання
        """
        if task_id is None:
            task_id = f"task_{asyncio.get_event_loop().time()}"
        
        if task_id in self.tasks:
            raise ValueError(f"Task with ID {task_id} already exists")
        
        # Create initial result
        self.results[task_id] = AsyncTaskResult(
            task_id=task_id,
            status=AsyncTaskStatus.PENDING,
            metadata=metadata or {}
        )
        
        # Create and store task
        task = asyncio.create_task(self._run_task(coro, task_id))
        self.tasks[task_id] = task
        
        # Update stats
        self.stats["tasks_created"] += 1
        
        self.logger.info(f"Created async task: {task_id}")
        return task_id
    
    async def _run_task(self, coro, task_id: str) -> Any:
        """
        Run a task with semaphore and error handling
        Виконати завдання з семафором та обробкою помилок
        
        Args:
            coro: Coroutine to execute / Корутина для виконання
            task_id: Task ID / ID завдання
        """
        async with self.semaphore:
            start_time = asyncio.get_event_loop().time()
            
            try:
                # Update status to running
                self.results[task_id].status = AsyncTaskStatus.RUNNING
                
                # Execute the coroutine
                result = await coro
                
                # Update result
                execution_time = asyncio.get_event_loop().time() - start_time
                self.results[task_id] = AsyncTaskResult(
                    task_id=task_id,
                    status=AsyncTaskStatus.COMPLETED,
                    result=result,
                    execution_time=execution_time,
                    metadata=self.results[task_id].metadata
                )
                
                # Update stats
                self.stats["tasks_completed"] += 1
                self.stats["avg_execution_time"] = (
                    (self.stats["avg_execution_time"] * 
                     (self.stats["tasks_completed"] - 1) + execution_time) 
                    / self.stats["tasks_completed"]
                )
                
                self.logger.info(f"Task {task_id} completed successfully")
                return result
                
            except asyncio.CancelledError:
                # Handle task cancellation
                self.results[task_id].status = AsyncTaskStatus.CANCELLED
                self.logger.info(f"Task {task_id} was cancelled")
                raise
                
            except Exception as e:
                # Handle task failure
                execution_time = asyncio.get_event_loop().time() - start_time
                self.results[task_id] = AsyncTaskResult(
                    task_id=task_id,
                    status=AsyncTaskStatus.FAILED,
                    error=e,
                    execution_time=execution_time,
                    metadata=self.results[task_id].metadata
                )
                
                # Update stats
                self.stats["tasks_failed"] += 1
                
                self.logger.error(f"Task {task_id} failed: {e}")
                raise
    
    async def get_result(self, task_id: str, timeout: Optional[float] = None) -> AsyncTaskResult:
        """
        Get task result, optionally waiting for completion
        Отримати результат завдання, опціонально чекаючи завершення
        
        Args:
            task_id: Task ID / ID завдання
            timeout: Optional timeout in seconds / Опціональний таймаут в секундах
            
        Returns:
            Task result / Результат завдання
        """
        if task_id not in self.results:
            raise ValueError(f"Task {task_id} not found")
        
        result = self.results[task_id]
        
        # If task is still running and timeout is specified, wait
        if (result.status == AsyncTaskStatus.RUNNING and 
                timeout is not None and task_id in self.tasks):
            try:
                await asyncio.wait_for(self.tasks[task_id], timeout)
                result = self.results[task_id]
            except asyncio.TimeoutError:
                self.logger.warning(f"Timeout waiting for task {task_id}")
        
        return result
    
    async def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a running task
        Скасувати запущене завдання
        
        Args:
            task_id: Task ID / ID завдання
            
        Returns:
            True if task was cancelled / True якщо завдання було скасовано
        """
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        
        if task.done():
            return False
        
        task.cancel()
        
        try:
            await task
        except asyncio.CancelledError:
            pass
        
        self.logger.info(f"Cancelled task: {task_id}")
        return True
    
    async def get_all_results(self) -> Dict[str, AsyncTaskResult]:
        """
        Get all task results
        Отримати всі результати завдань
        
        Returns:
            Dictionary of task results / Словник результатів завдань
        """
        return self.results.copy()
    
    async def cleanup_completed_tasks(self) -> None:
        """Clean up completed tasks / Очистити завершені завдання"""
        completed_tasks = [
            task_id for task_id, result in self.results.items()
            if result.status in [AsyncTaskStatus.COMPLETED, AsyncTaskStatus.FAILED]
        ]
        
        for task_id in completed_tasks:
            if task_id in self.tasks:
                del self.tasks[task_id]
        
        if completed_tasks:
            self.logger.info(f"Cleaned up {len(completed_tasks)} completed tasks")
    
    async def wait_for_all_tasks(self, timeout: Optional[float] = None) -> None:
        """
        Wait for all tasks to complete
        Чекати завершення всіх завдань
        
        Args:
            timeout: Optional timeout in seconds / Опціональний таймаут в секундах
        """
        if not self.tasks:
            return
        
        tasks = list(self.tasks.values())
        try:
            await asyncio.wait_for(asyncio.gather(*tasks, return_exceptions=True), timeout)
        except asyncio.TimeoutError:
            self.logger.warning("Timeout waiting for all tasks to complete")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get task statistics
        Отримати статистику завдань
        
        Returns:
            Task statistics / Статистика завдань
        """
        return self.stats.copy()
    
    async def shutdown(self) -> None:
        """Shutdown the task manager / Вимкнути менеджер завдань"""
        # Cancel all running tasks
        for task_id, task in self.tasks.items():
            if not task.done():
                task.cancel()
        
        # Wait for all tasks to complete
        if self.tasks:
            await asyncio.gather(*self.tasks.values(), return_exceptions=True)
        
        # Shutdown executor
        self.executor.shutdown(wait=True)
        
        self.logger.info("Async task manager shutdown complete")


class AsyncBatchProcessor:
    """
    Batch processor for async operations
    Пакетний процесор для асинхронних операцій
    """
    
    def __init__(self, batch_size: int = 10, max_concurrent_batches: int = 3):
        """
        Initialize batch processor
        Ініціалізувати пакетний процесор
        
        Args:
            batch_size: Size of each batch / Розмір кожного пакету
            max_concurrent_batches: Maximum concurrent batches
                Максимальна кількість одночасних пакетів
        """
        self.batch_size = batch_size
        self.max_concurrent_batches = max_concurrent_batches
        self.semaphore = asyncio.Semaphore(max_concurrent_batches)
        self.logger = logging.getLogger(__name__)
    
    async def process_batch(
        self, 
        items: List[Any], 
        process_func: Callable[[Any], Any],
        **kwargs
    ) -> List[Any]:
        """
        Process items in batches
        Обробити елементи пакетами
        
        Args:
            items: Items to process / Елементи для обробки
            process_func: Function to process each item / Функція для обробки кожного елемента
            **kwargs: Additional arguments for process_func
                Додаткові аргументи для process_func
            
        Returns:
            List of results / Список результатів
        """
        if not items:
            return []
        
        # Split items into batches
        batches = [
            items[i:i + self.batch_size] 
            for i in range(0, len(items), self.batch_size)
        ]
        
        results = []
        
        # Process batches concurrently
        async def process_single_batch(batch):
            async with self.semaphore:
                batch_results = []
                for item in batch:
                    try:
                        if asyncio.iscoroutinefunction(process_func):
                            result = await process_func(item, **kwargs)
                        else:
                            # Run synchronous function in executor
                            loop = asyncio.get_event_loop()
                            result = await loop.run_in_executor(
                                None, process_func, item, **kwargs
                            )
                        batch_results.append(result)
                    except Exception as e:
                        self.logger.error(f"Error processing item {item}: {e}")
                        batch_results.append(None)
                return batch_results
        
        batch_tasks = [process_single_batch(batch) for batch in batches]
        batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
        
        # Flatten results
        for batch_result in batch_results:
            if isinstance(batch_result, Exception):
                self.logger.error(f"Batch processing error: {batch_result}")
            else:
                results.extend(batch_result)
        
        return results


class AsyncEventEmitter:
    """
    Async event emitter for MOVA SDK
    Асинхронний генератор подій для MOVA SDK
    """
    
    def __init__(self):
        """Initialize event emitter / Ініціалізувати генератор подій"""
        self.listeners: Dict[str, List[Callable]] = {}
        self.logger = logging.getLogger(__name__)
    
    def on(self, event: str, callback: Callable) -> None:
        """
        Register event listener
        Зареєструвати слухача подій
        
        Args:
            event: Event name / Назва події
            callback: Callback function / Функція зворотного виклику
        """
        if event not in self.listeners:
            self.listeners[event] = []
        self.listeners[event].append(callback)
        self.logger.debug(f"Registered listener for event: {event}")
    
    def off(self, event: str, callback: Callable) -> bool:
        """
        Unregister event listener
        Видалити слухача подій
        
        Args:
            event: Event name / Назва події
            callback: Callback function / Функція зворотного виклику
            
        Returns:
            True if listener was removed / True якщо слухача було видалено
        """
        if event in self.listeners and callback in self.listeners[event]:
            self.listeners[event].remove(callback)
            self.logger.debug(f"Removed listener for event: {event}")
            return True
        return False
    
    async def emit(self, event: str, *args, **kwargs) -> None:
        """
        Emit event to all listeners
        Надіслати подію всім слухачам
        
        Args:
            event: Event name / Назва події
            *args: Positional arguments for callbacks
                Позиційні аргументи для функцій зворотного виклику
            **kwargs: Keyword arguments for callbacks
                Іменовані аргументи для функцій зворотного виклику
        """
        if event not in self.listeners:
            return
        
        tasks = []
        for callback in self.listeners[event]:
            try:
                if asyncio.iscoroutinefunction(callback):
                    task = callback(event, *args, **kwargs)
                else:
                    # Run synchronous callback in executor
                    loop = asyncio.get_event_loop()
                    task = loop.run_in_executor(
                        None, callback, event, *args, **kwargs
                    )
                tasks.append(task)
            except Exception as e:
                self.logger.error(f"Error emitting event {event}: {e}")
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    def listener_count(self, event: str) -> int:
        """
        Get number of listeners for event
        Отримати кількість слухачів події
        
        Args:
            event: Event name / Назва події
            
        Returns:
            Number of listeners / Кількість слухачів
        """
        return len(self.listeners.get(event, []))
    
    def event_names(self) -> List[str]:
        """
        Get all event names
        Отримати всі назви подій
        
        Returns:
            List of event names / Список назв подій
        """
        return list(self.listeners.keys())


# Global instances
_task_manager = None
_batch_processor = None
_event_emitter = None


def get_async_task_manager(max_concurrent_tasks: int = 10) -> AsyncTaskManager:
    """
    Get global async task manager
    Отримати глобальний асинхронний менеджер завдань
    
    Args:
        max_concurrent_tasks: Maximum concurrent tasks
            Максимальна кількість одночасних завдань
            
    Returns:
        Async task manager instance / Екземпляр асинхронного менеджера завдань
    """
    global _task_manager
    if _task_manager is None:
        _task_manager = AsyncTaskManager(max_concurrent_tasks)
    return _task_manager


def get_async_batch_processor(
    batch_size: int = 10, 
    max_concurrent_batches: int = 3
) -> AsyncBatchProcessor:
    """
    Get global async batch processor
    Отримати глобальний асинхронний пакетний процесор
    
    Args:
        batch_size: Size of each batch / Розмір кожного пакету
        max_concurrent_batches: Maximum concurrent batches
            Максимальна кількість одночасних пакетів
            
    Returns:
        Async batch processor instance / Екземпляр асинхронного пакетного процесора
    """
    global _batch_processor
    if _batch_processor is None:
        _batch_processor = AsyncBatchProcessor(batch_size, max_concurrent_batches)
    return _batch_processor


def get_async_event_emitter() -> AsyncEventEmitter:
    """
    Get global async event emitter
    Отримати глобальний асинхронний генератор подій
    
    Returns:
        Async event emitter instance / Екземпляр асинхронного генератора подій
    """
    global _event_emitter
    if _event_emitter is None:
        _event_emitter = AsyncEventEmitter()
    return _event_emitter


async def shutdown_async_components() -> None:
    """
    Shutdown all async components
    Вимкнути всі асинхронні компоненти
    """
    global _task_manager, _batch_processor
    
    # Shutdown task manager
    if _task_manager:
        await _task_manager.shutdown()
        _task_manager = None
    
    # Close HTTP clients
    await close_http_clients()
    
    # Close Redis manager
    redis_manager = get_redis_manager()
    redis_manager.close()
    
    logger.info("All async components shutdown complete")


def run_async(coro):
    """
    Decorator to run async function from sync code
    Декоратор для запуску асинхронної функції з синхронного коду
    
    Args:
        coro: Coroutine function / Функція-корутина
    """
    @wraps(coro)
    def wrapper(*args, **kwargs):
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(coro(*args, **kwargs))
    
    return wrapper


def async_to_sync(coro):
    """
    Convert async function to sync function
    Перетворити асинхронну функцію на синхронну
    
    Args:
        coro: Coroutine function / Функція-корутина
        
    Returns:
        Sync function / Синхронна функція
    """
    @wraps(coro)
    def wrapper(*args, **kwargs):
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(coro(*args, **kwargs))
    
    return wrapper