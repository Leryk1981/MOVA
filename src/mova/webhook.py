"""
Webhook support for MOVA SDK
Підтримка webhook для MOVA SDK
"""

import hashlib
import hmac
import json
import time
from typing import Dict, Any, Optional, Callable, List, Union
from dataclasses import dataclass, field
from enum import Enum
import asyncio
from datetime import datetime, timedelta
import logging

from pydantic import BaseModel, Field, validator
from .config import get_config_value


class WebhookEventType(str, Enum):
    """Webhook event types / Типи подій webhook"""
    VALIDATION_STARTED = "validation.started"
    VALIDATION_COMPLETED = "validation.completed"
    VALIDATION_FAILED = "validation.failed"
    CACHE_UPDATED = "cache.updated"
    CACHE_CLEARED = "cache.cleared"
    REDIS_CONNECTED = "redis.connected"
    REDIS_DISCONNECTED = "redis.disconnected"
    LLM_REQUEST_STARTED = "llm.request.started"
    LLM_REQUEST_COMPLETED = "llm.request.completed"
    LLM_REQUEST_FAILED = "llm.request.failed"
    CONFIG_UPDATED = "config.updated"
    ERROR_OCCURRED = "error.occurred"
    # ML Events
    ML_INTENT_RECOGNIZED = "ml.intent.recognized"
    ML_ENTITY_EXTRACTED = "ml.entity.extracted"
    ML_CONTEXT_UPDATED = "ml.context.updated"
    ML_MODEL_TRAINED = "ml.model.trained"
    ML_PREDICTION_MADE = "ml.prediction.made"


class WebhookPayload(BaseModel):
    """Webhook payload structure / Структура payload webhook"""
    event_type: WebhookEventType = Field(..., description="Event type")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Event timestamp")
    data: Dict[str, Any] = Field(default_factory=dict, description="Event data")
    source: str = Field(default="mova_sdk", description="Event source")
    version: str = Field(default="2.2", description="SDK version")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


@dataclass
class WebhookEndpoint:
    """Webhook endpoint configuration / Конфігурація webhook endpoint"""
    url: str
    secret: str
    headers: Dict[str, str] = field(default_factory=dict)
    timeout: int = 30
    retries: int = 3
    enabled: bool = True
    event_types: List[WebhookEventType] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.event_types:
            self.event_types = list(WebhookEventType)


class WebhookSignatureValidator:
    """Webhook signature validator / Валідатор підпису webhook"""
    
    @staticmethod
    def generate_signature(payload: str, secret: str, algorithm: str = "sha256") -> str:
        """
        Generate HMAC signature for payload
        Генерувати HMAC підпис для payload
        
        Args:
            payload: Payload string / Рядок payload
            secret: Signing secret / Секрет для підпису
            algorithm: Hash algorithm / Алгоритм хешування
            
        Returns:
            Generated signature / Згенерований підпис
        """
        if algorithm == "sha256":
            return hmac.new(
                secret.encode('utf-8'),
                payload.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
        elif algorithm == "sha1":
            return hmac.new(
                secret.encode('utf-8'),
                payload.encode('utf-8'),
                hashlib.sha1
            ).hexdigest()
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
    
    @staticmethod
    def verify_signature(
        payload: str, 
        signature: str, 
        secret: str, 
        algorithm: str = "sha256"
    ) -> bool:
        """
        Verify webhook signature
        Верифікувати підпис webhook
        
        Args:
            payload: Request payload / Payload запиту
            signature: Received signature / Отриманий підпис
            secret: Signing secret / Секрет для підпису
            algorithm: Hash algorithm / Алгоритм хешування
            
        Returns:
            True if signature is valid / True якщо підпис валідний
        """
        expected_signature = WebhookSignatureValidator.generate_signature(
            payload, secret, algorithm
        )
        return hmac.compare_digest(expected_signature, signature)


class WebhookManager:
    """Webhook manager for MOVA SDK / Менеджер webhook для MOVA SDK"""
    
    def __init__(self):
        """Initialize webhook manager / Ініціалізувати менеджер webhook"""
        self.endpoints: List[WebhookEndpoint] = []
        self.event_handlers: Dict[WebhookEventType, List[Callable]] = {}
        self.logger = logging.getLogger(__name__)
        self._enabled = get_config_value("webhook_enabled", True)
        self._max_retries = get_config_value("webhook_max_retries", 3)
        self._timeout = get_config_value("webhook_timeout", 30)
        
        # Initialize event handlers
        for event_type in WebhookEventType:
            self.event_handlers[event_type] = []
    
    def add_endpoint(self, endpoint: WebhookEndpoint) -> None:
        """
        Add webhook endpoint
        Додати webhook endpoint
        
        Args:
            endpoint: Webhook endpoint configuration / Конфігурація webhook endpoint
        """
        self.endpoints.append(endpoint)
        self.logger.info(f"Added webhook endpoint: {endpoint.url}")
    
    def remove_endpoint(self, url: str) -> bool:
        """
        Remove webhook endpoint
        Видалити webhook endpoint
        
        Args:
            url: Endpoint URL / URL endpoint
            
        Returns:
            True if endpoint was removed / True якщо endpoint був видалений
        """
        for i, endpoint in enumerate(self.endpoints):
            if endpoint.url == url:
                del self.endpoints[i]
                self.logger.info(f"Removed webhook endpoint: {url}")
                return True
        return False
    
    def add_event_handler(
        self, 
        event_type: WebhookEventType, 
        handler: Callable[[WebhookPayload], None]
    ) -> None:
        """
        Add event handler
        Додати обробник подій
        
        Args:
            event_type: Event type / Тип події
            handler: Event handler function / Функція обробника подій
        """
        self.event_handlers[event_type].append(handler)
        self.logger.debug(f"Added handler for event: {event_type}")
    
    def remove_event_handler(
        self, 
        event_type: WebhookEventType, 
        handler: Callable[[WebhookPayload], None]
    ) -> bool:
        """
        Remove event handler
        Видалити обробник подій
        
        Args:
            event_type: Event type / Тип події
            handler: Event handler function / Функція обробника подій
            
        Returns:
            True if handler was removed / True якщо обробник був видалений
        """
        if handler in self.event_handlers[event_type]:
            self.event_handlers[event_type].remove(handler)
            self.logger.debug(f"Removed handler for event: {event_type}")
            return True
        return False
    
    async def send_webhook(
        self, 
        endpoint: WebhookEndpoint, 
        payload: WebhookPayload
    ) -> bool:
        """
        Send webhook to endpoint
        Відправити webhook до endpoint
        
        Args:
            endpoint: Webhook endpoint / Webhook endpoint
            payload: Webhook payload / Webhook payload
            
        Returns:
            True if webhook was sent successfully / True якщо webhook був успішно відправлений
        """
        if not endpoint.enabled:
            return False
        
        try:
            import aiohttp
            
            # Prepare payload
            payload_dict = payload.model_dump()
            payload_json = json.dumps(payload_dict, default=str)
            
            # Generate signature
            signature = WebhookSignatureValidator.generate_signature(
                payload_json, endpoint.secret
            )
            
            # Prepare headers
            headers = {
                "Content-Type": "application/json",
                "X-Mova-Signature": signature,
                "X-Mova-Event": payload.event_type.value,
                "X-Mova-Timestamp": str(int(time.time())),
                "User-Agent": "MOVA-SDK/2.2"
            }
            headers.update(endpoint.headers)
            
            # Send webhook
            async with aiohttp.ClientSession() as session:
                for attempt in range(endpoint.retries + 1):
                    try:
                        async with session.post(
                            endpoint.url,
                            data=payload_json,
                            headers=headers,
                            timeout=aiohttp.ClientTimeout(total=endpoint.timeout)
                        ) as response:
                            if response.status in [200, 201, 202]:
                                self.logger.debug(
                                    f"Webhook sent successfully to {endpoint.url}: {response.status}"
                                )
                                return True
                            else:
                                self.logger.warning(
                                    f"Webhook failed with status {response.status}: {endpoint.url}"
                                )
                    except Exception as e:
                        if attempt == endpoint.retries:
                            self.logger.error(
                                f"Webhook failed after {endpoint.retries} retries: {endpoint.url}, error: {e}"
                            )
                        else:
                            await asyncio.sleep(2 ** attempt)  # Exponential backoff
                
                return False
                
        except ImportError:
            self.logger.error("aiohttp is required for webhook support")
            return False
        except Exception as e:
            self.logger.error(f"Failed to send webhook to {endpoint.url}: {e}")
            return False
    
    async def trigger_event(
        self, 
        event_type: WebhookEventType, 
        data: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Trigger webhook event
        Запустити webhook подію
        
        Args:
            event_type: Event type / Тип події
            data: Event data / Дані події
        """
        if not self._enabled:
            return
        
        # Create payload
        payload = WebhookPayload(
            event_type=event_type,
            data=data or {}
        )
        
        # Call local event handlers
        for handler in self.event_handlers[event_type]:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(payload)
                else:
                    handler(payload)
            except Exception as e:
                self.logger.error(f"Event handler failed for {event_type}: {e}")
        
        # Send to webhook endpoints
        tasks = []
        for endpoint in self.endpoints:
            if event_type in endpoint.event_types:
                task = asyncio.create_task(
                    self.send_webhook(endpoint, payload)
                )
                tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    def trigger_event_sync(
        self, 
        event_type: WebhookEventType, 
        data: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Trigger webhook event synchronously
        Запустити webhook подію синхронно
        
        Args:
            event_type: Event type / Тип події
            data: Event data / Дані події
        """
        asyncio.create_task(self.trigger_event(event_type, data))
    
    def get_endpoints(self) -> List[WebhookEndpoint]:
        """
        Get all webhook endpoints
        Отримати всі webhook endpoints
        
        Returns:
            List of webhook endpoints / Список webhook endpoints
        """
        return self.endpoints.copy()
    
    def is_enabled(self) -> bool:
        """
        Check if webhooks are enabled
        Перевірити чи webhook увімкнені
        
        Returns:
            True if webhooks are enabled / True якщо webhook увімкнені
        """
        return self._enabled
    
    def set_enabled(self, enabled: bool) -> None:
        """
        Enable or disable webhooks
        Увімкнути або вимкнути webhook
        
        Args:
            enabled: Enable webhooks / Увімкнути webhook
        """
        self._enabled = enabled
        self.logger.info(f"Webhooks {'enabled' if enabled else 'disabled'}")


class WebhookReceiver:
    """Webhook receiver for handling incoming webhooks / Отримувач webhook для обробки вхідних webhook"""
    
    def __init__(self, secret: str):
        """
        Initialize webhook receiver
        Ініціалізувати отримувач webhook
        
        Args:
            secret: Webhook secret / Секрет webhook
        """
        self.secret = secret
        self.logger = logging.getLogger(__name__)
        self.handlers: Dict[str, Callable] = {}
    
    def add_handler(self, event_type: str, handler: Callable[[Dict[str, Any]], None]) -> None:
        """
        Add webhook handler
        Додати обробник webhook
        
        Args:
            event_type: Event type / Тип події
            handler: Handler function / Функція обробника
        """
        self.handlers[event_type] = handler
        self.logger.debug(f"Added handler for event: {event_type}")
    
    def verify_signature(self, payload: str, signature: str) -> bool:
        """
        Verify webhook signature
        Верифікувати підпис webhook
        
        Args:
            payload: Request payload / Payload запиту
            signature: Received signature / Отриманий підпис
            
        Returns:
            True if signature is valid / True якщо підпис валідний
        """
        return WebhookSignatureValidator.verify_signature(payload, signature, self.secret)
    
    async def handle_webhook(
        self, 
        payload: str, 
        signature: str, 
        event_type: Optional[str] = None
    ) -> bool:
        """
        Handle incoming webhook
        Обробити вхідний webhook
        
        Args:
            payload: Webhook payload / Webhook payload
            signature: Webhook signature / Підпис webhook
            event_type: Event type header / Заголовок типу події
            
        Returns:
            True if webhook was handled successfully / True якщо webhook був успішно оброблений
        """
        try:
            # Verify signature
            if not self.verify_signature(payload, signature):
                self.logger.warning("Invalid webhook signature")
                return False
            
            # Parse payload
            data = json.loads(payload)
            
            # Determine event type
            if not event_type:
                event_type = data.get("event_type", "unknown")
            
            # Call handler
            if event_type in self.handlers:
                handler = self.handlers[event_type]
                if asyncio.iscoroutinefunction(handler):
                    await handler(data)
                else:
                    handler(data)
                self.logger.info(f"Webhook handled successfully: {event_type}")
                return True
            else:
                self.logger.warning(f"No handler found for event: {event_type}")
                return False
                
        except json.JSONDecodeError:
            self.logger.error("Invalid JSON payload")
            return False
        except Exception as e:
            self.logger.error(f"Failed to handle webhook: {e}")
            return False


# Global webhook manager instance
webhook_manager = WebhookManager()


def get_webhook_manager() -> WebhookManager:
    """Get global webhook manager / Отримати глобальний менеджер webhook"""
    return webhook_manager


def add_webhook_endpoint(endpoint: WebhookEndpoint) -> None:
    """Add webhook endpoint / Додати webhook endpoint"""
    webhook_manager.add_endpoint(endpoint)


def remove_webhook_endpoint(url: str) -> bool:
    """Remove webhook endpoint / Видалити webhook endpoint"""
    return webhook_manager.remove_endpoint(url)


def trigger_webhook_event(
    event_type: WebhookEventType, 
    data: Optional[Dict[str, Any]] = None
) -> None:
    """Trigger webhook event / Запустити webhook подію"""
    webhook_manager.trigger_event_sync(event_type, data) 