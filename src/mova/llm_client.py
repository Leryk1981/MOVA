"""
LLM Client for MOVA SDK - OpenRouter Integration
LLM клієнт для MOVA SDK - інтеграція з OpenRouter
"""

import json
import logging
import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import requests
from openai import OpenAI

logger = logging.getLogger(__name__)


@dataclass
class LLMConfig:
    """Configuration for LLM client / Конфігурація для LLM клієнта"""
    api_key: str
    base_url: str = "https://openrouter.ai/api/v1"
    default_model: str = "openai/gpt-3.5-turbo"
    max_tokens: int = 1000
    temperature: float = 0.7
    timeout: int = 30


@dataclass
class LLMRequest:
    """LLM request structure / Структура LLM запиту"""
    prompt: str
    model: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    system_message: Optional[str] = None
    messages: Optional[List[Dict[str, str]]] = None


@dataclass
class LLMResponse:
    """LLM response structure / Структура LLM відповіді"""
    content: str
    model: str
    usage: Dict[str, Any]
    finish_reason: str
    success: bool
    error: Optional[str] = None


class OpenRouterClient:
    """
    OpenRouter client for LLM interactions using OpenAI SDK
    OpenRouter клієнт для взаємодії з LLM через OpenAI SDK
    """
    
    def __init__(self, config: LLMConfig):
        """
        Initialize OpenRouter client
        Ініціалізація OpenRouter клієнта
        
        Args:
            config: LLM configuration / Конфігурація LLM
        """
        self.config = config
        
        # Initialize OpenAI client with OpenRouter configuration
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=config.api_key,
        )
        
        # Set default headers for attribution
        self.extra_headers = {
            "HTTP-Referer": "https://mova-sdk.github.io",
            "X-Title": "MOVA SDK"
        }
        
        logger.info(f"OpenRouter client initialized with model: {config.default_model}")
    
    def chat_completion(self, request: LLMRequest) -> LLMResponse:
        """
        Send chat completion request
        Відправити запит на завершення чату
        
        Args:
            request: LLM request / LLM запит
            
        Returns:
            LLMResponse: Response from LLM / Відповідь від LLM
        """
        try:
            # Prepare messages
            messages = self._prepare_messages(request)
            
            logger.info(f"Sending request to OpenRouter: model={request.model or self.config.default_model}")
            
            # Send request using OpenAI SDK
            response = self.client.chat.completions.create(
                model=request.model or self.config.default_model,
                messages=messages,
                max_tokens=request.max_tokens or self.config.max_tokens,
                temperature=request.temperature or self.config.temperature,
                extra_headers=self.extra_headers
            )
            
            return self._parse_success_response(response)
                
        except Exception as e:
            logger.error(f"Request failed: {str(e)}")
            return LLMResponse(
                content="",
                model=request.model or self.config.default_model,
                usage={},
                finish_reason="error",
                success=False,
                error=f"Request failed: {str(e)}"
            )
    
    def _prepare_messages(self, request: LLMRequest) -> List[Dict[str, str]]:
        """
        Prepare messages for OpenRouter API
        Підготувати повідомлення для OpenRouter API
        
        Args:
            request: LLM request / LLM запит
            
        Returns:
            List[Dict[str, str]]: Formatted messages / Форматовані повідомлення
        """
        messages = []
        
        # Add system message if provided
        if request.system_message:
            messages.append({
                "role": "system",
                "content": request.system_message
            })
        
        # Use provided messages or create from prompt
        if request.messages:
            messages.extend(request.messages)
        else:
            messages.append({
                "role": "user",
                "content": request.prompt
            })
        
        return messages
    
    def _parse_success_response(self, response) -> LLMResponse:
        """
        Parse successful response from OpenRouter
        Парсити успішну відповідь від OpenRouter
        
        Args:
            response: OpenAI response object / Об'єкт відповіді OpenAI
            
        Returns:
            LLMResponse: Parsed response / Розпарсена відповідь
        """
        try:
            choice = response.choices[0]
            message = choice.message
            
            llm_response = LLMResponse(
                content=message.content,
                model=response.model,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                    "total_tokens": response.usage.total_tokens if response.usage else 0
                },
                finish_reason=choice.finish_reason or "stop",
                success=True
            )
            
            logger.info(f"Received response: {len(llm_response.content)} characters, model: {llm_response.model}")
            return llm_response
            
        except Exception as e:
            logger.error(f"Failed to parse response: {str(e)}")
            return LLMResponse(
                content="",
                model=getattr(response, 'model', 'unknown'),
                usage={},
                finish_reason="error",
                success=False,
                error=f"Failed to parse response: {str(e)}"
            )
    
    def _parse_error_response(self, error: Exception) -> LLMResponse:
        """
        Parse error response from OpenRouter
        Парсити помилкову відповідь від OpenRouter
        
        Args:
            error: Exception object / Об'єкт винятку
            
        Returns:
            LLMResponse: Error response / Відповідь з помилкою
        """
        error_message = str(error)
        logger.error(f"OpenRouter error: {error_message}")
        
        return LLMResponse(
            content="",
            model="unknown",
            usage={},
            finish_reason="error",
            success=False,
            error=error_message
        )
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """
        Get list of available models
        Отримати список доступних моделей
        
        Returns:
            List[Dict[str, Any]]: Available models / Доступні моделі
        """
        try:
            response = self.client.models.list()
            models = []
            
            for model in response.data:
                models.append({
                    "id": model.id,
                    "name": model.name,
                    "context_length": getattr(model, 'context_length', None),
                    "pricing": getattr(model, 'pricing', None)
                })
            
            logger.info(f"Retrieved {len(models)} available models")
            return models
                
        except Exception as e:
            logger.error(f"Failed to get models: {str(e)}")
            return []
    
    def get_model_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about specific model
        Отримати інформацію про конкретну модель
        
        Args:
            model_id: Model identifier / Ідентифікатор моделі
            
        Returns:
            Optional[Dict[str, Any]]: Model information / Інформація про модель
        """
        try:
            model = self.client.models.retrieve(model_id)
            
            model_info = {
                "id": model.id,
                "name": model.name,
                "context_length": getattr(model, 'context_length', None),
                "pricing": getattr(model, 'pricing', None),
                "description": getattr(model, 'description', None)
            }
            
            logger.info(f"Retrieved info for model: {model_id}")
            return model_info
                
        except Exception as e:
            logger.error(f"Failed to get model info: {str(e)}")
            return None


class MovaLLMClient:
    """
    MOVA LLM client wrapper using OpenAI SDK
    Обгортка MOVA LLM клієнта з використанням OpenAI SDK
    """
    
    def __init__(self, api_key: str = None, model: str = "openai/gpt-3.5-turbo", **kwargs):
        """
        Initialize MOVA LLM client
        Ініціалізація MOVA LLM клієнта
        
        Args:
            api_key: OpenRouter API key / OpenRouter API ключ (optional, uses env var if not provided)
            model: Default model to use / Модель за замовчуванням
            **kwargs: Additional configuration / Додаткова конфігурація
        """
        # Use environment variable if api_key is not provided
        if not api_key:
            api_key = os.getenv("OPENROUTER_API_KEY")
            if not api_key:
                raise ValueError("OpenRouter API key is required. Set OPENROUTER_API_KEY environment variable or pass api_key parameter.")
        
        config = LLMConfig(
            api_key=api_key,
            default_model=model,
            **kwargs
        )
        
        self.client = OpenRouterClient(config)
        self.default_model = model
        
        logger.info(f"MOVA LLM client initialized with model: {model}")
    
    def generate_response(self, prompt: str, **kwargs) -> str:
        """
        Generate response for prompt
        Згенерувати відповідь на промпт
        
        Args:
            prompt: Input prompt / Вхідний промпт
            **kwargs: Additional parameters / Додаткові параметри
            
        Returns:
            str: Generated response / Згенерована відповідь
        """
        request = LLMRequest(
            prompt=prompt,
            model=kwargs.get("model", self.default_model),
            max_tokens=kwargs.get("max_tokens"),
            temperature=kwargs.get("temperature"),
            system_message=kwargs.get("system_message")
        )
        
        response = self.client.chat_completion(request)
        
        if response.success:
            return response.content
        else:
            logger.error(f"LLM generation failed: {response.error}")
            return f"Error: {response.error}"
    
    def generate_with_context(self, prompt: str, context: List[Dict[str, str]], **kwargs) -> str:
        """
        Generate response with conversation context
        Згенерувати відповідь з контекстом розмови
        
        Args:
            prompt: Current prompt / Поточний промпт
            context: Conversation context / Контекст розмови
            **kwargs: Additional parameters / Додаткові параметри
            
        Returns:
            str: Generated response / Згенерована відповідь
        """
        messages = context + [{"role": "user", "content": prompt}]
        
        request = LLMRequest(
            prompt="",  # Not used when messages are provided
            messages=messages,
            model=kwargs.get("model", self.default_model),
            max_tokens=kwargs.get("max_tokens"),
            temperature=kwargs.get("temperature")
        )
        
        response = self.client.chat_completion(request)
        
        if response.success:
            return response.content
        else:
            logger.error(f"LLM generation with context failed: {response.error}")
            return f"Error: {response.error}"
    
    def get_models(self) -> List[Dict[str, Any]]:
        """
        Get available models
        Отримати доступні моделі
        
        Returns:
            List[Dict[str, Any]]: Available models / Доступні моделі
        """
        return self.client.get_available_models()
    
    def test_connection(self) -> bool:
        """
        Test connection to OpenRouter
        Протестувати з'єднання з OpenRouter
        
        Returns:
            bool: Connection status / Статус з'єднання
        """
        try:
            models = self.get_models()
            return len(models) > 0
        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            return False


# Global LLM client instance
_llm_client = None


def get_llm_client(api_key: str, model: str = "openai/gpt-3.5-turbo", **kwargs) -> MovaLLMClient:
    """
    Get global LLM client instance
    Отримати глобальний екземпляр LLM клієнта
    
    Args:
        api_key: OpenRouter API key / OpenRouter API ключ
        model: Default model / Модель за замовчуванням
        **kwargs: Additional configuration / Додаткова конфігурація
        
    Returns:
        MovaLLMClient: LLM client instance / Екземпляр LLM клієнта
    """
    global _llm_client
    
    if _llm_client is None:
        _llm_client = MovaLLMClient(api_key, model, **kwargs)
    
    return _llm_client


def close_llm_client():
    """
    Close global LLM client
    Закрити глобальний LLM клієнт
    """
    global _llm_client
    
    if _llm_client:
        _llm_client = None 