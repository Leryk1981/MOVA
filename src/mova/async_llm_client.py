"""
Async LLM Client for MOVA SDK
Асинхронний LLM клієнт для MOVA SDK
"""

import json
import logging
import asyncio
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import aiohttp
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


@dataclass
class AsyncLLMConfig:
    """Configuration for async LLM client / Конфігурація для асинхронного LLM клієнта"""
    api_key: str
    base_url: str = "https://openrouter.ai/api/v1"
    default_model: str = "openai/gpt-3.5-turbo"
    max_tokens: int = 1000
    temperature: float = 0.7
    timeout: int = 30


@dataclass
class AsyncLLMRequest:
    """Async LLM request structure / Структура асинхронного LLM запиту"""
    prompt: str
    model: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    system_message: Optional[str] = None
    messages: Optional[List[Dict[str, str]]] = None


@dataclass
class AsyncLLMResponse:
    """Async LLM response structure / Структура асинхронної LLM відповіді"""
    content: str
    model: str
    usage: Dict[str, Any]
    finish_reason: str
    success: bool
    error: Optional[str] = None


class AsyncOpenRouterClient:
    """
    Async OpenRouter client for LLM interactions
    Асинхронний OpenRouter клієнт для взаємодії з LLM
    """
    
    def __init__(self, config: AsyncLLMConfig):
        """
        Initialize async OpenRouter client
        Ініціалізація асинхронного OpenRouter клієнта
        
        Args:
            config: Async LLM configuration / Конфігурація асинхронного LLM
        """
        self.config = config
        
        # Initialize async OpenAI client with OpenRouter configuration
        self.client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=config.api_key,
        )
        
        # Set default headers for attribution
        self.extra_headers = {
            "HTTP-Referer": "https://mova-sdk.github.io",
            "X-Title": "MOVA SDK"
        }
        
        logger.info(f"Async OpenRouter client initialized with model: {config.default_model}")
    
    async def chat_completion(self, request: AsyncLLMRequest) -> AsyncLLMResponse:
        """
        Send async chat completion request
        Відправити асинхронний запит на завершення чату
        
        Args:
            request: Async LLM request / Асинхронний LLM запит
            
        Returns:
            AsyncLLMResponse: Response from LLM / Відповідь від LLM
        """
        try:
            # Prepare messages
            messages = self._prepare_messages(request)
            
            logger.info(f"Sending async request to OpenRouter: model={request.model or self.config.default_model}")
            
            # Send async request using OpenAI SDK
            response = await self.client.chat.completions.create(
                model=request.model or self.config.default_model,
                messages=messages,
                max_tokens=request.max_tokens or self.config.max_tokens,
                temperature=request.temperature or self.config.temperature,
                extra_headers=self.extra_headers
            )
            
            return self._parse_success_response(response)
            
        except Exception as e:
            logger.error(f"Async OpenRouter request failed: {e}")
            return self._parse_error_response(e)
    
    def _prepare_messages(self, request: AsyncLLMRequest) -> List[Dict[str, str]]:
        """
        Prepare messages for LLM request
        Підготувати повідомлення для LLM запиту
        
        Args:
            request: Async LLM request / Асинхронний LLM запит
            
        Returns:
            List of messages / Список повідомлень
        """
        messages = []
        
        # Add system message if provided
        if request.system_message:
            messages.append({"role": "system", "content": request.system_message})
        
        # Add existing messages if provided
        if request.messages:
            messages.extend(request.messages)
        
        # Add user prompt
        messages.append({"role": "user", "content": request.prompt})
        
        return messages
    
    def _parse_success_response(self, response) -> AsyncLLMResponse:
        """
        Parse successful response from LLM
        Парсити успішну відповідь від LLM
        
        Args:
            response: Raw response from LLM / Сирова відповідь від LLM
            
        Returns:
            AsyncLLMResponse: Parsed response / Парсена відповідь
        """
        try:
            content = response.choices[0].message.content
            model = response.model
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
            finish_reason = response.choices[0].finish_reason
            
            logger.info(f"Async LLM response received: model={model}, tokens={usage['total_tokens']}")
            
            return AsyncLLMResponse(
                content=content,
                model=model,
                usage=usage,
                finish_reason=finish_reason,
                success=True
            )
            
        except Exception as e:
            logger.error(f"Failed to parse async LLM response: {e}")
            return AsyncLLMResponse(
                content="",
                model="",
                usage={},
                finish_reason="",
                success=False,
                error=f"Response parsing failed: {str(e)}"
            )
    
    def _parse_error_response(self, error: Exception) -> AsyncLLMResponse:
        """
        Parse error response from LLM
        Парсити помилку від LLM
        
        Args:
            error: Exception from LLM / Виняток від LLM
            
        Returns:
            AsyncLLMResponse: Error response / Відповідь з помилкою
        """
        return AsyncLLMResponse(
            content="",
            model="",
            usage={},
            finish_reason="",
            success=False,
            error=str(error)
        )
    
    async def get_available_models(self) -> List[Dict[str, Any]]:
        """
        Get available models from OpenRouter
        Отримати доступні моделі з OpenRouter
        
        Returns:
            List of available models / Список доступних моделей
        """
        try:
            response = await self.client.models.list()
            models = []
            
            for model in response.data:
                models.append({
                    "id": model.id,
                    "name": model.id,
                    "description": getattr(model, 'description', ''),
                    "context_length": getattr(model, 'context_length', 0)
                })
            
            logger.info(f"Retrieved {len(models)} available models from OpenRouter")
            return models
            
        except Exception as e:
            logger.error(f"Failed to get available models: {e}")
            return []
    
    async def get_model_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        """
        Get specific model information
        Отримати інформацію про конкретну модель
        
        Args:
            model_id: Model ID / ID моделі
            
        Returns:
            Model information or None / Інформація про модель або None
        """
        try:
            response = await self.client.models.retrieve(model_id)
            
            return {
                "id": response.id,
                "name": response.id,
                "description": getattr(response, 'description', ''),
                "context_length": getattr(response, 'context_length', 0)
            }
            
        except Exception as e:
            logger.error(f"Failed to get model info for {model_id}: {e}")
            return None


class AsyncMovaLLMClient:
    """
    Async MOVA LLM client wrapper
    Асинхронний обгортка MOVA LLM клієнта
    """
    
    def __init__(self, api_key: str = None, model: str = "openai/gpt-3.5-turbo", **kwargs):
        """
        Initialize async MOVA LLM client
        Ініціалізація асинхронного MOVA LLM клієнта
        
        Args:
            api_key: API key for LLM service / API ключ для LLM сервісу
            model: Default model to use / Модель за замовчуванням
            **kwargs: Additional configuration / Додаткова конфігурація
        """
        self.api_key = api_key or kwargs.get('api_key')
        if not self.api_key:
            raise ValueError("API key is required for LLM client")
        
        config = AsyncLLMConfig(
            api_key=self.api_key,
            default_model=model,
            max_tokens=kwargs.get('max_tokens', 1000),
            temperature=kwargs.get('temperature', 0.7),
            timeout=kwargs.get('timeout', 30)
        )
        
        self.client = AsyncOpenRouterClient(config)
        self.default_model = model
        
        logger.info(f"Async MOVA LLM client initialized with model: {model}")
    
    async def generate_response(self, prompt: str, **kwargs) -> str:
        """
        Generate async response from LLM
        Згенерувати асинхронну відповідь від LLM
        
        Args:
            prompt: User prompt / Користувацький запит
            **kwargs: Additional parameters / Додаткові параметри
            
        Returns:
            Generated response / Згенерована відповідь
        """
        request = AsyncLLMRequest(
            prompt=prompt,
            model=kwargs.get('model', self.default_model),
            max_tokens=kwargs.get('max_tokens'),
            temperature=kwargs.get('temperature'),
            system_message=kwargs.get('system_message')
        )
        
        response = await self.client.chat_completion(request)
        
        if response.success:
            return response.content
        else:
            raise Exception(f"LLM request failed: {response.error}")
    
    async def generate_with_context(self, prompt: str, context: List[Dict[str, str]], **kwargs) -> str:
        """
        Generate async response with conversation context
        Згенерувати асинхронну відповідь з контекстом діалогу
        
        Args:
            prompt: User prompt / Користувацький запит
            context: Conversation context / Контекст діалогу
            **kwargs: Additional parameters / Додаткові параметри
            
        Returns:
            Generated response / Згенерована відповідь
        """
        request = AsyncLLMRequest(
            prompt=prompt,
            model=kwargs.get('model', self.default_model),
            max_tokens=kwargs.get('max_tokens'),
            temperature=kwargs.get('temperature'),
            system_message=kwargs.get('system_message'),
            messages=context
        )
        
        response = await self.client.chat_completion(request)
        
        if response.success:
            return response.content
        else:
            raise Exception(f"LLM request failed: {response.error}")
    
    async def get_models(self) -> List[Dict[str, Any]]:
        """
        Get available models
        Отримати доступні моделі
        
        Returns:
            List of available models / Список доступних моделей
        """
        return await self.client.get_available_models()
    
    async def test_connection(self) -> bool:
        """
        Test async connection to LLM service
        Протестувати асинхронне з'єднання з LLM сервісом
        
        Returns:
            True if connection successful / True якщо з'єднання успішне
        """
        try:
            await self.generate_response("Test", max_tokens=10)
            logger.info("Async LLM connection test successful")
            return True
        except Exception as e:
            logger.error(f"Async LLM connection test failed: {e}")
            return False


# Factory function for creating async LLM client
async def get_async_llm_client(api_key: str, model: str = "openai/gpt-3.5-turbo", **kwargs) -> AsyncMovaLLMClient:
    """
    Create async LLM client
    Створити асинхронний LLM клієнт
    
    Args:
        api_key: API key for LLM service / API ключ для LLM сервісу
        model: Default model to use / Модель за замовчуванням
        **kwargs: Additional configuration / Додаткова конфігурація
        
    Returns:
        AsyncMovaLLMClient: Async LLM client / Асинхронний LLM клієнт
    """
    return AsyncMovaLLMClient(api_key, model, **kwargs) 