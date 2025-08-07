"""
Webhook integration with MOVA SDK components
Інтеграція webhook з компонентами MOVA SDK
"""

import logging
from typing import Dict, Any, Optional
from .webhook import (
    WebhookEventType, 
    trigger_webhook_event, 
    get_webhook_manager,
    WebhookReceiver
)
from .config import get_config_value


class WebhookIntegration:
    """Webhook integration manager / Менеджер інтеграції webhook"""
    
    def __init__(self):
        """Initialize webhook integration / Ініціалізувати інтеграцію webhook"""
        self.logger = logging.getLogger(__name__)
        self.webhook_manager = get_webhook_manager()
        self._enabled = get_config_value("webhook_enabled", True)
        
        if self._enabled:
            self._setup_integrations()
    
    def _setup_integrations(self) -> None:
        """Setup webhook integrations / Налаштувати інтеграції webhook"""
        self.logger.info("Setting up webhook integrations")
        
        # Integration will be set up when components are initialized
        # Інтеграція буде налаштована коли компоненти ініціалізовані
    
    def trigger_validation_event(
        self, 
        event_type: str, 
        data: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Trigger validation webhook event
        Запустити webhook подію валідації
        
        Args:
            event_type: Event type (started/completed/failed) / Тип події
            data: Event data / Дані події
        """
        if not self._enabled:
            return
        
        event_map = {
            "started": WebhookEventType.VALIDATION_STARTED,
            "completed": WebhookEventType.VALIDATION_COMPLETED,
            "failed": WebhookEventType.VALIDATION_FAILED
        }
        
        webhook_event = event_map.get(event_type)
        if webhook_event:
            trigger_webhook_event(webhook_event, data)
    
    def trigger_cache_event(
        self, 
        event_type: str, 
        data: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Trigger cache webhook event
        Запустити webhook подію кешу
        
        Args:
            event_type: Event type (updated/cleared) / Тип події
            data: Event data / Дані події
        """
        if not self._enabled:
            return
        
        event_map = {
            "updated": WebhookEventType.CACHE_UPDATED,
            "cleared": WebhookEventType.CACHE_CLEARED
        }
        
        webhook_event = event_map.get(event_type)
        if webhook_event:
            trigger_webhook_event(webhook_event, data)
    
    def trigger_redis_event(
        self, 
        event_type: str, 
        data: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Trigger Redis webhook event
        Запустити webhook подію Redis
        
        Args:
            event_type: Event type (connected/disconnected) / Тип події
            data: Event data / Дані події
        """
        if not self._enabled:
            return
        
        event_map = {
            "connected": WebhookEventType.REDIS_CONNECTED,
            "disconnected": WebhookEventType.REDIS_DISCONNECTED
        }
        
        webhook_event = event_map.get(event_type)
        if webhook_event:
            trigger_webhook_event(webhook_event, data)
    
    def trigger_llm_event(
        self, 
        event_type: str, 
        data: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Trigger LLM webhook event
        Запустити webhook подію LLM
        
        Args:
            event_type: Event type (started/completed/failed) / Тип події
            data: Event data / Дані події
        """
        if not self._enabled:
            return
        
        event_map = {
            "started": WebhookEventType.LLM_REQUEST_STARTED,
            "completed": WebhookEventType.LLM_REQUEST_COMPLETED,
            "failed": WebhookEventType.LLM_REQUEST_FAILED
        }
        
        webhook_event = event_map.get(event_type)
        if webhook_event:
            trigger_webhook_event(webhook_event, data)
    
    def trigger_config_event(
        self, 
        data: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Trigger config webhook event
        Запустити webhook подію конфігурації
        
        Args:
            data: Event data / Дані події
        """
        if not self._enabled:
            return
        
        trigger_webhook_event(WebhookEventType.CONFIG_UPDATED, data)
    
    def trigger_error_event(
        self, 
        error: Exception, 
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Trigger error webhook event
        Запустити webhook подію помилки
        
        Args:
            error: Exception / Виняток
            context: Error context / Контекст помилки
        """
        if not self._enabled:
            return
        
        data = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context or {}
        }
        
        trigger_webhook_event(WebhookEventType.ERROR_OCCURRED, data)
    
    def trigger_ml_event(
        self, 
        event_type: str, 
        data: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Trigger ML webhook event
        Запустити webhook подію ML
        
        Args:
            event_type: Event type (intent_recognized/entity_extracted/context_updated/model_trained/prediction_made)
            data: Event data / Дані події
        """
        if not self._enabled:
            return
        
        event_map = {
            "intent_recognized": WebhookEventType.ML_INTENT_RECOGNIZED,
            "entity_extracted": WebhookEventType.ML_ENTITY_EXTRACTED, 
            "context_updated": WebhookEventType.ML_CONTEXT_UPDATED,
            "model_trained": WebhookEventType.ML_MODEL_TRAINED,
            "prediction_made": WebhookEventType.ML_PREDICTION_MADE
        }
        
        webhook_event = event_map.get(event_type)
        if webhook_event:
            trigger_webhook_event(webhook_event, data)


# Global webhook integration instance
webhook_integration = WebhookIntegration()


def get_webhook_integration() -> WebhookIntegration:
    """Get global webhook integration / Отримати глобальну інтеграцію webhook"""
    return webhook_integration


# Convenience functions for triggering events
def trigger_validation_started(data: Optional[Dict[str, Any]] = None) -> None:
    """Trigger validation started event / Запустити подію початку валідації"""
    webhook_integration.trigger_validation_event("started", data)


def trigger_validation_completed(data: Optional[Dict[str, Any]] = None) -> None:
    """Trigger validation completed event / Запустити подію завершення валідації"""
    webhook_integration.trigger_validation_event("completed", data)


def trigger_validation_failed(data: Optional[Dict[str, Any]] = None) -> None:
    """Trigger validation failed event / Запустити подію помилки валідації"""
    webhook_integration.trigger_validation_event("failed", data)


def trigger_cache_updated(data: Optional[Dict[str, Any]] = None) -> None:
    """Trigger cache updated event / Запустити подію оновлення кешу"""
    webhook_integration.trigger_cache_event("updated", data)


def trigger_cache_cleared(data: Optional[Dict[str, Any]] = None) -> None:
    """Trigger cache cleared event / Запустити подію очищення кешу"""
    webhook_integration.trigger_cache_event("cleared", data)


def trigger_redis_connected(data: Optional[Dict[str, Any]] = None) -> None:
    """Trigger Redis connected event / Запустити подію підключення Redis"""
    webhook_integration.trigger_redis_event("connected", data)


def trigger_redis_disconnected(data: Optional[Dict[str, Any]] = None) -> None:
    """Trigger Redis disconnected event / Запустити подію відключення Redis"""
    webhook_integration.trigger_redis_event("disconnected", data)


def trigger_llm_request_started(data: Optional[Dict[str, Any]] = None) -> None:
    """Trigger LLM request started event / Запустити подію початку запиту LLM"""
    webhook_integration.trigger_llm_event("started", data)


def trigger_llm_request_completed(data: Optional[Dict[str, Any]] = None) -> None:
    """Trigger LLM request completed event / Запустити подію завершення запиту LLM"""
    webhook_integration.trigger_llm_event("completed", data)


def trigger_llm_request_failed(data: Optional[Dict[str, Any]] = None) -> None:
    """Trigger LLM request failed event / Запустити подію помилки запиту LLM"""
    webhook_integration.trigger_llm_event("failed", data)


def trigger_config_updated(data: Optional[Dict[str, Any]] = None) -> None:
    """Trigger config updated event / Запустити подію оновлення конфігурації"""
    webhook_integration.trigger_config_event(data)


def trigger_error_occurred(error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
    """Trigger error occurred event / Запустити подію виникнення помилки"""
    webhook_integration.trigger_error_event(error, context)


# ML Webhook convenience functions
def trigger_ml_intent_recognized(data: Optional[Dict[str, Any]] = None) -> None:
    """Convenience function to trigger ML intent recognized event"""
    webhook_integration.trigger_ml_event("intent_recognized", data)


def trigger_ml_entity_extracted(data: Optional[Dict[str, Any]] = None) -> None:
    """Convenience function to trigger ML entity extracted event"""
    webhook_integration.trigger_ml_event("entity_extracted", data)


def trigger_ml_context_updated(data: Optional[Dict[str, Any]] = None) -> None:
    """Convenience function to trigger ML context updated event"""
    webhook_integration.trigger_ml_event("context_updated", data)


def trigger_ml_model_trained(data: Optional[Dict[str, Any]] = None) -> None:
    """Convenience function to trigger ML model trained event"""
    webhook_integration.trigger_ml_event("model_trained", data)


def trigger_ml_prediction_made(data: Optional[Dict[str, Any]] = None) -> None:
    """Convenience function to trigger ML prediction made event"""
    webhook_integration.trigger_ml_event("prediction_made", data) 