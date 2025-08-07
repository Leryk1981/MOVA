"""
Async MOVA Engine - Core processing engine with async support
Асинхронний MOVA Engine - Основний обробний движок з асинхронною підтримкою
"""

import json
import uuid
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from loguru import logger

from .models import (
    Intent, Protocol, ToolAPI, Instruction, Profile, 
    Session, Contract, ProtocolStep, Condition
)
from ..redis_manager import get_redis_manager, MovaRedisManager
from ..async_llm_client import get_async_llm_client, AsyncMovaLLMClient
from ..http_client import create_async_http_client, AsyncMovaHTTPClient


class AsyncMovaEngine:
    """
    Async MOVA language processing engine
    Асинхронний обробний движок мови MOVA
    """
    
    def __init__(self, redis_url: Optional[str] = None, llm_api_key: Optional[str] = None, llm_model: str = "openai/gpt-3.5-turbo"):
        """
        Initialize async MOVA engine / Ініціалізація асинхронного движка MOVA
        
        Args:
            redis_url: Redis connection URL (optional) / URL підключення до Redis (опціонально)
            llm_api_key: OpenRouter API key (optional) / OpenRouter API ключ (опціонально)
            llm_model: Default LLM model / Модель LLM за замовчуванням
        """
        self.intents: Dict[str, Intent] = {}
        self.protocols: Dict[str, Protocol] = {}
        self.tools: Dict[str, ToolAPI] = {}
        self.instructions: Dict[str, Instruction] = {}
        self.profiles: Dict[str, Profile] = {}
        self.sessions: Dict[str, Session] = {}
        self.contracts: Dict[str, Contract] = {}
        
        # Initialize Redis manager if URL provided
        self.redis_manager: Optional[MovaRedisManager] = None
        if redis_url:
            try:
                self.redis_manager = get_redis_manager(redis_url)
                logger.info(f"Async MOVA Engine initialized with Redis at {redis_url}")
            except Exception as e:
                logger.warning(f"Failed to initialize Redis: {e}. Using in-memory storage.")
        else:
            logger.info("Async MOVA Engine initialized with in-memory storage")
        
        # Initialize async LLM client if API key provided
        self.llm_client: Optional[AsyncMovaLLMClient] = None
        if llm_api_key:
            try:
                # Note: We'll initialize this in an async context
                self.llm_api_key = llm_api_key
                self.llm_model = llm_model
                logger.info(f"Async MOVA Engine prepared for LLM model: {llm_model}")
            except Exception as e:
                logger.warning(f"Failed to prepare LLM client: {e}. Using mock responses.")
        else:
            logger.info("Async MOVA Engine initialized with mock LLM responses")
        
        # Initialize async HTTP client
        self.http_client: Optional[AsyncMovaHTTPClient] = None
    
    async def initialize_llm_client(self):
        """Initialize async LLM client / Ініціалізація асинхронного LLM клієнта"""
        if hasattr(self, 'llm_api_key') and self.llm_api_key:
            try:
                self.llm_client = await get_async_llm_client(self.llm_api_key, self.llm_model)
                logger.info(f"Async LLM client initialized with model: {self.llm_model}")
            except Exception as e:
                logger.warning(f"Failed to initialize async LLM client: {e}")
    
    async def initialize_http_client(self, base_url: str = "", headers: Optional[Dict[str, str]] = None):
        """Initialize async HTTP client / Ініціалізація асинхронного HTTP клієнта"""
        try:
            self.http_client = create_async_http_client(base_url, headers)
            await self.http_client.__aenter__()
            logger.info("Async HTTP client initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize async HTTP client: {e}")
    
    async def cleanup(self):
        """Cleanup async resources / Очищення асинхронних ресурсів"""
        if self.http_client:
            await self.http_client.__aexit__(None, None, None)
            logger.info("Async HTTP client cleaned up")
    
    def add_intent(self, intent: Intent) -> bool:
        """
        Add intent to engine / Додати намір до движка
        
        Args:
            intent: Intent object / Об'єкт наміру
            
        Returns:
            bool: Success status / Статус успіху
        """
        try:
            self.intents[intent.name] = intent
            logger.info(f"Intent '{intent.name}' added / Намір '{intent.name}' додано")
            return True
        except Exception as e:
            logger.error(f"Failed to add intent: {e} / Не вдалося додати намір: {e}")
            return False
    
    def add_protocol(self, protocol: Protocol) -> bool:
        """
        Add protocol to engine / Додати протокол до движка
        
        Args:
            protocol: Protocol object / Об'єкт протоколу
            
        Returns:
            bool: Success status / Статус успіху
        """
        try:
            self.protocols[protocol.name] = protocol
            logger.info(f"Protocol '{protocol.name}' added / Протокол '{protocol.name}' додано")
            return True
        except Exception as e:
            logger.error(f"Failed to add protocol: {e} / Не вдалося додати протокол: {e}")
            return False
    
    def add_tool(self, tool: ToolAPI) -> bool:
        """
        Add tool to engine / Додати інструмент до движка
        
        Args:
            tool: ToolAPI object / Об'єкт ToolAPI
            
        Returns:
            bool: Success status / Статус успіху
        """
        try:
            self.tools[tool.id] = tool
            logger.info(f"Tool '{tool.id}' added / Інструмент '{tool.id}' додано")
            return True
        except Exception as e:
            logger.error(f"Failed to add tool: {e} / Не вдалося додати інструмент: {e}")
            return False
    
    def create_session(self, user_id: str, ttl: int = 3600) -> Session:
        """
        Create new session / Створити нову сесію
        
        Args:
            user_id: User identifier / Ідентифікатор користувача
            ttl: Time to live in seconds / Час життя в секундах
            
        Returns:
            Session: Created session / Створена сесія
        """
        session_id = str(uuid.uuid4())
        session = Session(
            session_id=session_id,
            user_id=user_id,
            start_time=datetime.now().isoformat(),
            data={}
        )
        
        self.sessions[session_id] = session
        
        # Save to Redis if available
        if self.redis_manager:
            try:
                self.redis_manager.save_session(session_id, session.dict())
                logger.info(f"Session '{session_id}' saved to Redis")
            except Exception as e:
                logger.warning(f"Failed to save session to Redis: {e}")
        
        logger.info(f"Session '{session_id}' created for user '{user_id}'")
        return session
    
    async def recognize_intent(self, text: str, session_id: str) -> Optional[Intent]:
        """
        Recognize intent from text / Розпізнати намір з тексту
        
        Args:
            text: Input text / Вхідний текст
            session_id: Session identifier / Ідентифікатор сесії
            
        Returns:
            Optional[Intent]: Recognized intent or None / Розпізнаний намір або None
        """
        try:
            # Simple pattern matching for now
            # In the future, this could use LLM for better intent recognition
            text_lower = text.lower()
            
            for intent in self.intents.values():
                for pattern in intent.patterns:
                    if pattern.lower() in text_lower:
                        logger.info(f"Intent '{intent.name}' recognized from text")
                        return intent
            
            # If no pattern match, try LLM-based recognition
            if self.llm_client:
                try:
                    prompt = f"Classify the following text into one of these intents: {list(self.intents.keys())}\nText: {text}\nIntent:"
                    response = await self.llm_client.generate_response(prompt, max_tokens=50)
                    
                    # Parse response to find matching intent
                    for intent_name in self.intents.keys():
                        if intent_name.lower() in response.lower():
                            intent = self.intents[intent_name]
                            logger.info(f"LLM recognized intent '{intent.name}' from text")
                            return intent
                            
                except Exception as e:
                    logger.warning(f"LLM intent recognition failed: {e}")
            
            logger.info("No intent recognized from text")
            return None
            
        except Exception as e:
            logger.error(f"Intent recognition failed: {e}")
            return None
    
    async def execute_protocol(self, protocol_name: str, session_id: str, **kwargs) -> Dict[str, Any]:
        """
        Execute protocol asynchronously / Виконати протокол асинхронно
        
        Args:
            protocol_name: Name of protocol to execute / Назва протоколу для виконання
            session_id: Session identifier / Ідентифікатор сесії
            **kwargs: Additional parameters / Додаткові параметри
            
        Returns:
            Dict[str, Any]: Execution result / Результат виконання
        """
        try:
            if protocol_name not in self.protocols:
                raise ValueError(f"Protocol '{protocol_name}' not found")
            
            protocol = self.protocols[protocol_name]
            session = self.sessions.get(session_id)
            
            if not session:
                raise ValueError(f"Session '{session_id}' not found")
            
            logger.info(f"Executing protocol '{protocol_name}' for session '{session_id}'")
            
            result = {
                "protocol_name": protocol_name,
                "session_id": session_id,
                "steps_executed": [],
                "final_result": None,
                "success": True,
                "error": None
            }
            
            current_step_index = 0
            
            while current_step_index < len(protocol.steps):
                step = protocol.steps[current_step_index]
                
                try:
                    step_result = await self._execute_step(step, session, **kwargs)
                    result["steps_executed"].append({
                        "step_id": step.id,
                        "action": step.action,
                        "result": step_result
                    })
                    
                    # Check if step indicates end
                    if step.action == "end":
                        result["final_result"] = step_result
                        break
                    
                    # Move to next step
                    current_step_index += 1
                    
                except Exception as e:
                    logger.error(f"Step execution failed: {e}")
                    result["success"] = False
                    result["error"] = str(e)
                    break
            
            # Update session data
            self.update_session_data(session_id, session.data)
            
            logger.info(f"Protocol '{protocol_name}' execution completed")
            return result
            
        except Exception as e:
            logger.error(f"Protocol execution failed: {e}")
            return {
                "protocol_name": protocol_name,
                "session_id": session_id,
                "success": False,
                "error": str(e)
            }
    
    async def _execute_step(self, step: ProtocolStep, session: Session, **kwargs) -> Dict[str, Any]:
        """
        Execute single protocol step asynchronously / Виконати один крок протоколу асинхронно
        
        Args:
            step: Protocol step to execute / Крок протоколу для виконання
            session: Current session / Поточна сесія
            **kwargs: Additional parameters / Додаткові параметри
            
        Returns:
            Dict[str, Any]: Step execution result / Результат виконання кроку
        """
        try:
            logger.info(f"Executing step '{step.id}' with action '{step.action}'")
            
            if step.action == "prompt":
                return await self._execute_prompt_step(step, session, **kwargs)
            elif step.action == "tool_api":
                return await self._execute_api_step(step, session, **kwargs)
            elif step.action == "condition":
                return await self._execute_condition_step(step, session, **kwargs)
            elif step.action == "end":
                return await self._execute_end_step(step, session, **kwargs)
            else:
                raise ValueError(f"Unknown step action: {step.action}")
                
        except Exception as e:
            logger.error(f"Step execution failed: {e}")
            raise
    
    async def _execute_prompt_step(self, step: ProtocolStep, session: Session, **kwargs) -> Dict[str, Any]:
        """
        Execute prompt step asynchronously / Виконати крок запиту асинхронно
        
        Args:
            step: Prompt step / Крок запиту
            session: Current session / Поточна сесія
            **kwargs: Additional parameters / Додаткові параметри
            
        Returns:
            Dict[str, Any]: Prompt result / Результат запиту
        """
        try:
            prompt_text = self._replace_placeholders(step.prompt, session.data)
            
            if self.llm_client:
                # Use LLM to generate response
                try:
                    response = await self.llm_client.generate_response(prompt_text, **kwargs)
                    
                    # Store response in session
                    session.data[f"prompt_response_{step.id}"] = response
                    
                    return {
                        "action": "prompt",
                        "prompt": prompt_text,
                        "response": response,
                        "success": True
                    }
                    
                except Exception as e:
                    logger.warning(f"LLM prompt failed: {e}, using mock response")
                    # Fallback to mock response
                    response = f"Mock response for: {prompt_text}"
                    session.data[f"prompt_response_{step.id}"] = response
                    
                    return {
                        "action": "prompt",
                        "prompt": prompt_text,
                        "response": response,
                        "success": True
                    }
            else:
                # Mock response when no LLM client
                response = f"Mock response for: {prompt_text}"
                session.data[f"prompt_response_{step.id}"] = response
                
                return {
                    "action": "prompt",
                    "prompt": prompt_text,
                    "response": response,
                    "success": True
                }
                
        except Exception as e:
            logger.error(f"Prompt step execution failed: {e}")
            raise
    
    async def _execute_api_step(self, step: ProtocolStep, session: Session, **kwargs) -> Dict[str, Any]:
        """
        Execute API step asynchronously / Виконати крок API асинхронно
        
        Args:
            step: API step / Крок API
            session: Current session / Поточна сесія
            **kwargs: Additional parameters / Додаткові параметри
            
        Returns:
            Dict[str, Any]: API call result / Результат виклику API
        """
        try:
            if not step.tool_api_id or step.tool_api_id not in self.tools:
                raise ValueError(f"Tool API '{step.tool_api_id}' not found")
            
            tool = self.tools[step.tool_api_id]
            
            if self.http_client:
                return await self._execute_async_api_call(tool, session.data)
            else:
                # Mock API call when no HTTP client
                return self._execute_mock_api_call(tool, session.data)
                
        except Exception as e:
            logger.error(f"API step execution failed: {e}")
            raise
    
    async def _execute_async_api_call(self, tool: ToolAPI, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute async API call / Виконати асинхронний виклик API
        
        Args:
            tool: Tool API configuration / Конфігурація Tool API
            session_data: Session data / Дані сесії
            
        Returns:
            Dict[str, Any]: API response / Відповідь API
        """
        try:
            # Replace placeholders in parameters
            params = {}
            for key, value in tool.parameters.items():
                if isinstance(value, str):
                    params[key] = self._replace_placeholders(value, session_data)
                else:
                    params[key] = value
            
            # Replace placeholders in headers
            headers = {}
            for key, value in (tool.headers or {}).items():
                if isinstance(value, str):
                    headers[key] = self._replace_placeholders(value, session_data)
                else:
                    headers[key] = value
            
            logger.info(f"Making async API call to {tool.endpoint}")
            
            if tool.method.upper() == "GET":
                response = await self.http_client.get(tool.endpoint, params=params, headers=headers)
            elif tool.method.upper() == "POST":
                response = await self.http_client.post(tool.endpoint, json_data=params, headers=headers)
            elif tool.method.upper() == "PUT":
                response = await self.http_client.put(tool.endpoint, json_data=params, headers=headers)
            elif tool.method.upper() == "DELETE":
                response = await self.http_client.delete(tool.endpoint, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {tool.method}")
            
            return {
                "action": "tool_api",
                "tool_id": tool.id,
                "method": tool.method,
                "endpoint": tool.endpoint,
                "response": response,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Async API call failed: {e}")
            return {
                "action": "tool_api",
                "tool_id": tool.id,
                "error": str(e),
                "success": False
            }
    
    def _execute_mock_api_call(self, tool: ToolAPI, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute mock API call / Виконати мок виклик API
        
        Args:
            tool: Tool API configuration / Конфігурація Tool API
            session_data: Session data / Дані сесії
            
        Returns:
            Dict[str, Any]: Mock API response / Мок відповідь API
        """
        # Replace placeholders in parameters
        params = {}
        for key, value in tool.parameters.items():
            if isinstance(value, str):
                params[key] = self._replace_placeholders(value, session_data)
            else:
                params[key] = value
        
        mock_response = {
            "status": "success",
            "data": {
                "mock": True,
                "tool_id": tool.id,
                "method": tool.method,
                "endpoint": tool.endpoint,
                "parameters": params
            }
        }
        
        return {
            "action": "tool_api",
            "tool_id": tool.id,
            "method": tool.method,
            "endpoint": tool.endpoint,
            "response": mock_response,
            "success": True
        }
    
    def _replace_placeholders(self, text: str, session_data: Dict[str, Any]) -> str:
        """
        Replace placeholders in text / Замінити плейсхолдери в тексті
        
        Args:
            text: Text with placeholders / Текст з плейсхолдерами
            session_data: Session data / Дані сесії
            
        Returns:
            str: Text with replaced placeholders / Текст з заміненими плейсхолдерами
        """
        import re
        
        def replace_placeholder(match):
            placeholder = match.group(1)
            return str(session_data.get(placeholder, f"{{{placeholder}}}"))
        
        return re.sub(r'\{(\w+)\}', replace_placeholder, text)
    
    async def _execute_condition_step(self, step: ProtocolStep, session: Session, **kwargs) -> Dict[str, Any]:
        """
        Execute condition step asynchronously / Виконати крок умови асинхронно
        
        Args:
            step: Condition step / Крок умови
            session: Current session / Поточна сесія
            **kwargs: Additional parameters / Додаткові параметри
            
        Returns:
            Dict[str, Any]: Condition evaluation result / Результат оцінки умови
        """
        try:
            if not step.condition:
                raise ValueError("Condition step requires condition configuration")
            
            condition = step.condition
            value = session.data.get(condition.field)
            
            result = self._evaluate_condition(condition, value)
            
            return {
                "action": "condition",
                "condition": condition.dict(),
                "value": value,
                "result": result,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Condition step execution failed: {e}")
            raise
    
    async def _execute_end_step(self, step: ProtocolStep, session: Session, **kwargs) -> Dict[str, Any]:
        """
        Execute end step asynchronously / Виконати крок завершення асинхронно
        
        Args:
            step: End step / Крок завершення
            session: Current session / Поточна сесія
            **kwargs: Additional parameters / Додаткові параметри
            
        Returns:
            Dict[str, Any]: End step result / Результат кроку завершення
        """
        return {
            "action": "end",
            "message": "Protocol execution completed",
            "success": True
        }
    
    def _evaluate_condition(self, condition: Condition, value: Any) -> bool:
        """
        Evaluate condition / Оцінити умову
        
        Args:
            condition: Condition to evaluate / Умова для оцінки
            value: Value to compare / Значення для порівняння
            
        Returns:
            bool: Condition result / Результат умови
        """
        if condition.operator == "equals":
            return value == condition.value
        elif condition.operator == "not_equals":
            return value != condition.value
        elif condition.operator == "contains":
            return condition.value in str(value)
        elif condition.operator == "greater_than":
            return float(value) > float(condition.value)
        elif condition.operator == "less_than":
            return float(value) < float(condition.value)
        else:
            logger.warning(f"Unknown condition operator: {condition.operator}")
            return False
    
    def get_session_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session data / Отримати дані сесії
        
        Args:
            session_id: Session identifier / Ідентифікатор сесії
            
        Returns:
            Optional[Dict[str, Any]]: Session data or None / Дані сесії або None
        """
        try:
            if self.redis_manager:
                # Try to get from Redis first
                redis_data = self.redis_manager.get_session(session_id)
                if redis_data:
                    return redis_data
            
            # Fallback to in-memory storage
            session = self.sessions.get(session_id)
            return session.data if session else None
            
        except Exception as e:
            logger.error(f"Failed to get session data: {e}")
            return None
    
    def update_session_data(self, session_id: str, data: Dict[str, Any]) -> bool:
        """
        Update session data / Оновити дані сесії
        
        Args:
            session_id: Session identifier / Ідентифікатор сесії
            data: New session data / Нові дані сесії
            
        Returns:
            bool: Success status / Статус успіху
        """
        try:
            # Update in-memory storage
            if session_id in self.sessions:
                self.sessions[session_id].data.update(data)
            
            # Update Redis if available
            if self.redis_manager:
                self.redis_manager.save_session(session_id, data)
            
            logger.debug(f"Session data updated for session '{session_id}'")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update session data: {e}")
            return False


# Factory function for creating async engine
async def create_async_mova_engine(redis_url: Optional[str] = None, llm_api_key: Optional[str] = None, llm_model: str = "openai/gpt-3.5-turbo") -> AsyncMovaEngine:
    """
    Create async MOVA engine
    Створити асинхронний движок MOVA
    
    Args:
        redis_url: Redis connection URL (optional) / URL підключення до Redis (опціонально)
        llm_api_key: OpenRouter API key (optional) / OpenRouter API ключ (опціонально)
        llm_model: Default LLM model / Модель LLM за замовчуванням
        
    Returns:
        AsyncMovaEngine: Initialized async engine / Ініціалізований асинхронний движок
    """
    engine = AsyncMovaEngine(redis_url, llm_api_key, llm_model)
    
    # Initialize async components
    await engine.initialize_llm_client()
    await engine.initialize_http_client()
    
    return engine 