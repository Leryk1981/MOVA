"""
LLM Client with Presets and Tool-Calling support for MOVA SDK
LLM клієнт з підтримкою Presets та Tool-Calling для MOVA SDK
"""

import json
import logging
from typing import Dict, Any, Optional, List, TypedDict
from openai import OpenAI

from ..config import MOVAConfigSchema, load_config

logger = logging.getLogger(__name__)


class ToolSpec(TypedDict, total=False):
    """Tool specification for LLM / Специфікація інструменту для LLM"""
    type: str  # "function"
    function: Dict[str, Any]  # {name, description, parameters(JSON schema)}


class ToolCall(TypedDict, total=False):
    """Tool call from LLM / Виклик інструменту від LLM"""
    name: str
    arguments: Dict[str, Any]


class LLMResponse(TypedDict, total=False):
    """LLM response structure / Структура відповіді LLM"""
    text: str
    tool_calls: List[ToolCall]
    model: str
    usage: Dict[str, Any]
    finish_reason: str
    success: bool
    error: Optional[str]


class LLMClient:
    """
    LLM Client with Presets and Tool-Calling support
    LLM клієнт з підтримкою Presets та Tool-Calling
    """
    
    def __init__(self, config: Optional[MOVAConfigSchema] = None):
        """
        Initialize LLM client
        Ініціалізація LLM клієнта
        
        Args:
            config: Configuration object / Об'єкт конфігурації
        """
        self.config = config or load_config()
        
        # Initialize OpenAI client with OpenRouter configuration
        self.client = OpenAI(
            base_url=self.config.llm.base_url,
            api_key=self._get_api_key(),
        )
        
        # Set default headers for attribution
        self.extra_headers = {
            "HTTP-Referer": "https://mova-sdk.github.io",
            "X-Title": "MOVA SDK"
        }
        
        logger.info(
            f"LLM client initialized with provider: {self.config.llm.provider}"
        )
    
    def _get_api_key(self) -> str:
        """Get API key from environment / Отримати API ключ з оточення"""
        api_key_env = self.config.llm.api_key_env
        api_key = api_key_env
        
        # If api_key_env is not an actual API key but an environment
        # variable name
        if not api_key.startswith(('sk-', 'org-')):
            import os
            api_key = os.getenv(api_key_env)
        
        if not api_key:
            raise ValueError(
                f"API key not found. Set {api_key_env} environment variable."
            )
        
        return api_key
    
    def _get_preset_config(
        self, preset: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get preset configuration
        Отримати конфігурацію пресету
        
        Args:
            preset: Preset name / Назва пресету
            
        Returns:
            Dict[str, Any]: Preset configuration / Конфігурація пресету
        """
        if not preset:
            preset = self.config.default_preset or "default"
        
        # Find preset in profiles
        for profile_name, profile in self.config.presets.profiles.items():
            if profile_name == preset:
                return {
                    "model": profile.model,
                    "temperature": profile.temperature,
                    "max_tokens": profile.max_tokens,
                    "system": profile.system,
                    "tools": profile.tools
                }
        
        # Return default preset if not found
        return {
            "model": self.config.llm.default_model,
            "temperature": 0.7,
            "max_tokens": 1024,
            "system": "You are MOVA assistant.",
            "tools": None
        }
    
    def chat(self, messages: List[Dict[str, str]], *,
             preset: Optional[str] = None,
             tools: Optional[List[ToolSpec]] = None) -> LLMResponse:
        """
        Send chat completion request with preset and tools support
        Відправити запит на завершення чату з підтримкою пресетів та
        інструментів
        
        Args:
            messages: List of messages / Список повідомлень
            preset: Preset name / Назва пресету
            tools: List of available tools / Список доступних інструментів
            
        Returns:
            LLMResponse: Response from LLM / Відповідь від LLM
        """
        try:
            # Get preset configuration
            preset_config = self._get_preset_config(preset)
            
            # Prepare messages with system message
            prepared_messages = self._prepare_messages(
                messages, preset_config["system"]
            )
            
            # Prepare tools for LLM
            llm_tools = self._prepare_tools(
                tools or preset_config.get("tools")
            )
            
            logger.info(
                f"Sending request to {self.config.llm.provider}: "
                f"model={preset_config['model']}, "
                f"tools={len(llm_tools) if llm_tools else 0}"
            )
            
            # Send request using OpenAI SDK
            response = self.client.chat.completions.create(
                model=preset_config["model"],
                messages=prepared_messages,
                max_tokens=preset_config["max_tokens"],
                temperature=preset_config["temperature"],
                tools=llm_tools if llm_tools else None,
                tool_choice="auto" if llm_tools else None,
                extra_headers=self.extra_headers
            )
            
            return self._parse_success_response(response)
                
        except Exception as e:
            logger.error(f"Request failed: {str(e)}")
            return LLMResponse(
                text="",
                model=preset_config.get(
                    "model", self.config.llm.default_model
                ),
                tool_calls=[],
                usage={},
                finish_reason="error",
                success=False,
                error=f"Request failed: {str(e)}"
            )
    
    def _prepare_messages(
        self, messages: List[Dict[str, str]],
        system_message: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        Prepare messages with system message
        Підготувати повідомлення з системним повідомленням
        
        Args:
            messages: Original messages / Оригінальні повідомлення
            system_message: System message / Системне повідомлення
            
        Returns:
            List[Dict[str, str]]: Prepared messages / Підготовані повідомлення
        """
        prepared = []
        
        # Add system message if provided
        if system_message:
            prepared.append({
                "role": "system",
                "content": system_message
            })
        
        # Add existing messages
        prepared.extend(messages)
        
        return prepared
    
    def _prepare_tools(
        self, tool_names: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Prepare tools for LLM
        Підготувати інструменти для LLM
        
        Args:
            tool_names: List of tool names / Список назв інструментів
            
        Returns:
            List[Dict[str, Any]]: Formatted tools / Форматовані інструменти
        """
        if not tool_names:
            return []
        
        tools = []
        
        # Get tool schemas from config
        for tool_name in tool_names:
            for tool in self.config.tools:
                if tool.name == tool_name:
                    tools.append({
                        "type": "function",
                        "function": {
                            "name": tool.name,
                            "description": tool.description,
                            "parameters": tool.schema
                        }
                    })
                    break
        
        return tools
    
    def _parse_success_response(self, response) -> LLMResponse:
        """
        Parse successful response from LLM
        Парсити успішну відповідь від LLM
        
        Args:
            response: OpenAI response object / Об'єкт відповіді OpenAI
            
        Returns:
            LLMResponse: Parsed response / Розпарсена відповідь
        """
        try:
            choice = response.choices[0]
            message = choice.message
            
            # Parse tool calls
            tool_calls = []
            if message.tool_calls:
                for tool_call in message.tool_calls:
                    tool_calls.append({
                        "name": tool_call.function.name,
                        "arguments": json.loads(
                            tool_call.function.arguments
                        )
                    })
            
            llm_response = LLMResponse(
                text=message.content or "",
                tool_calls=tool_calls,
                model=response.model,
                usage={
                    "prompt_tokens": (
                        response.usage.prompt_tokens
                        if response.usage else 0
                    ),
                    "completion_tokens": (
                        response.usage.completion_tokens
                        if response.usage else 0
                    ),
                    "total_tokens": (
                        response.usage.total_tokens
                        if response.usage else 0
                    )
                },
                finish_reason=choice.finish_reason or "stop",
                success=True,
                error=None
            )
            
            logger.info(
                f"Received response: {len(llm_response['text'])} characters, "
                f"model: {llm_response['model']}, "
                f"tool_calls: {len(llm_response['tool_calls'])}"
            )
            return llm_response
            
        except Exception as e:
            logger.error(f"Failed to parse response: {str(e)}")
            return LLMResponse(
                text="",
                model=getattr(response, 'model', 'unknown'),
                tool_calls=[],
                usage={},
                finish_reason="error",
                success=False,
                error=f"Failed to parse response: {str(e)}"
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
                    "name": getattr(model, 'name', model.id),
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
                "name": getattr(model, 'name', model.id),
                "context_length": getattr(model, 'context_length', None),
                "pricing": getattr(model, 'pricing', None),
                "description": getattr(model, 'description', None)
            }
            
            logger.info(f"Retrieved info for model: {model_id}")
            return model_info
                
        except Exception as e:
            logger.error(f"Failed to get model info: {str(e)}")
            return None
    
    def test_connection(self) -> bool:
        """
        Test connection to LLM provider
        Протестувати з'єднання з LLM провайдером
        
        Returns:
            bool: Connection status / Статус з'єднання
        """
        try:
            models = self.get_available_models()
            return len(models) > 0
        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            return False


# Global LLM client instance
_llm_client = None


def get_llm_client(config: Optional[MOVAConfigSchema] = None) -> LLMClient:
    """
    Get global LLM client instance
    Отримати глобальний екземпляр LLM клієнта
    
    Args:
        config: Configuration object / Об'єкт конфігурації
        
    Returns:
        LLMClient: LLM client instance / Екземпляр LLM клієнта
    """
    global _llm_client
    
    if _llm_client is None:
        _llm_client = LLMClient(config)
    
    return _llm_client


def reset_llm_client():
    """
    Reset global LLM client
    Скинути глобальний LLM клієнт
    """
    global _llm_client
    
    if _llm_client:
        _llm_client = None