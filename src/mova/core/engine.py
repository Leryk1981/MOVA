"""
MOVA Engine - Core processing engine
MOVA Engine - Основний обробний движок
"""

import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from loguru import logger

from .models import (
    Intent, Protocol, ToolAPI, Instruction, Profile,
    Session, Contract, ProtocolStep, Condition
)
from ..redis_manager import get_redis_manager, MovaRedisManager
from .llm_client import get_llm_client, LLMClient
from .tool_router import ToolRouter, ToolRegistry
from .tools.builtin import CalendarTool, CRMTool, NotifierTool
from .memory_system import MemorySystem, MemoryType, MemoryPriority


class MovaEngine:
    """
    Main MOVA language processing engine
    Основний обробний движок мови MOVA
    """
    
    def __init__(self, redis_url: Optional[str] = None,
                 llm_api_key: Optional[str] = None,
                 llm_model: str = "openrouter/anthropic/claude-3-haiku",
                 memory_storage_path: Optional[str] = None):
        """
        Initialize MOVA engine / Ініціалізація движка MOVA
        
        Args:
            redis_url: Redis connection URL (optional) /
                       URL підключення до Redis (опціонально)
            llm_api_key: OpenRouter API key (optional) /
                         OpenRouter API ключ (опціонально)
            llm_model: Default LLM model / Модель LLM за замовчуванням
            memory_storage_path: Path to memory storage file /
                                 Шлях до файлу зберігання пам'яті
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
                logger.info(
                    f"MOVA Engine initialized with Redis at {redis_url}")
            except Exception as e:
                logger.warning(
                    f"Failed to initialize Redis: {e}. Using in-memory storage.")
        else:
            logger.info("MOVA Engine initialized with in-memory storage")
        
        # Initialize LLM client with new implementation
        self.llm_client: Optional[LLMClient] = None
        try:
            self.llm_client = get_llm_client()
            logger.info("MOVA Engine initialized with new LLM client")
        except Exception as e:
            logger.warning(
                f"Failed to initialize LLM client: {e}. Using mock responses.")
        
        # Initialize ToolRouter and ToolRegistry
        self.tool_registry = ToolRegistry()
        self.tool_router = ToolRouter(self.tool_registry)
        
        # Initialize Memory System
        self.memory_system = MemorySystem(storage_path=memory_storage_path)
        logger.info("MOVA Engine initialized with Memory System")
        
        # Register built-in tools
        self._register_builtin_tools()
    
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
        Add API tool to engine / Додати API інструмент до движка
        
        Args:
            tool: ToolAPI object / Об'єкт ToolAPI
            
        Returns:
            bool: Success status / Статус успіху
        """
        try:
            self.tools[tool.id] = tool
            logger.info(f"Tool '{tool.name}' added / Інструмент '{tool.name}' додано")
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
            start_time=datetime.now().isoformat()
        )
        
        # Store session in memory
        self.sessions[session_id] = session
        
        # Store session data in Redis if available
        if self.redis_manager:
            initial_data = {
                "user_id": user_id,
                "start_time": session.start_time,
                "active": True
            }
            self.redis_manager.create_session(session_id, initial_data, ttl)
        
        logger.info(f"Session '{session_id}' created for user '{user_id}' / Сесію '{session_id}' створено для користувача '{user_id}'")
        return session
    
    def recognize_intent(self, text: str, session_id: str) -> Optional[Intent]:
        """
        Recognize intent from text / Розпізнати намір з тексту
        
        Args:
            text: Input text / Вхідний текст
            session_id: Session identifier / Ідентифікатор сесії
            
        Returns:
            Optional[Intent]: Recognized intent or None / Розпізнаний намір або None
        """
        if session_id not in self.sessions:
            logger.warning(f"Session '{session_id}' not found / Сесію '{session_id}' не знайдено")
            return None
        
        # Simple pattern matching (can be enhanced with ML)
        # Просте співпадіння шаблонів (можна покращити з ML)
        for intent in self.intents.values():
            for pattern in intent.patterns:
                if pattern.lower() in text.lower():
                    logger.info(f"Intent '{intent.name}' recognized / Намір '{intent.name}' розпізнано")
                    return intent
        
        logger.info("No intent recognized / Намір не розпізнано")
        return None
    
    def execute_protocol(self, protocol_name: str, session_id: str, **kwargs) -> Dict[str, Any]:
        """
        Execute protocol / Виконати протокол
        
        Args:
            protocol_name: Protocol name / Назва протоколу
            session_id: Session identifier / Ідентифікатор сесії
            **kwargs: Additional parameters / Додаткові параметри
            
        Returns:
            Dict[str, Any]: Execution result / Результат виконання
        """
        if protocol_name not in self.protocols:
            logger.error(f"Protocol '{protocol_name}' not found / Протокол '{protocol_name}' не знайдено")
            return {"error": "Protocol not found"}
        
        if session_id not in self.sessions:
            logger.error(f"Session '{session_id}' not found / Сесію '{session_id}' не знайдено")
            return {"error": "Session not found"}
        
        protocol = self.protocols[protocol_name]
        session = self.sessions[session_id]
        result = {"protocol": protocol_name, "steps_executed": [], "final_result": None}
        
        logger.info(f"Executing protocol '{protocol_name}' / Виконання протоколу '{protocol_name}'")
        
        # Execute steps sequentially
        # Виконання кроків послідовно
        for step in protocol.steps:
            step_result = self._execute_step(step, session, **kwargs)
            result["steps_executed"].append({
                "step_id": step.id,
                "action": step.action,
                "result": step_result
            })
            
            if step_result.get("error"):
                logger.error(f"Step '{step.id}' failed: {step_result['error']}")
                break
        
        return result
    
    def _execute_step(self, step: ProtocolStep, session: Session, **kwargs) -> Dict[str, Any]:
        """
        Execute single protocol step / Виконати один крок протоколу
        
        Args:
            step: Protocol step / Крок протоколу
            session: Current session / Поточна сесія
            **kwargs: Additional parameters / Додаткові параметри
            
        Returns:
            Dict[str, Any]: Step execution result / Результат виконання кроку
        """
        try:
            if step.action == "prompt":
                return self._execute_prompt_step(step, session, **kwargs)
            elif step.action == "tool_api":
                return self._execute_api_step(step, session, **kwargs)
            elif step.action == "condition":
                return self._execute_condition_step(step, session, **kwargs)
            elif step.action == "end":
                return self._execute_end_step(step, session, **kwargs)
            else:
                return {"error": f"Unknown action type: {step.action}"}
        except Exception as e:
            logger.error(f"Step execution failed: {e}")
            return {"error": str(e)}
    
    def _execute_prompt_step(self, step: ProtocolStep, session: Session, **kwargs) -> Dict[str, Any]:
        """Execute prompt step / Виконати крок промпту"""
        if not step.prompt:
            return {"error": "No prompt specified"}
        
        try:
            # Prepare prompt with session data substitution
            prompt = step.prompt
            session_data = session.data
            
            # Get conversation history from memory system
            conversation_history = []
            if self.memory_system:
                history = self.memory_system.get_conversation_history(
                    session.session_id, limit=10
                )
                conversation_history = history
            
            # Substitute session data placeholders
            for key, value in session_data.items():
                placeholder = f"{{session.data.{key}}}"
                if placeholder in prompt:
                    prompt = prompt.replace(placeholder, str(value))
            
            # Use new LLM client with presets and tools support
            if self.llm_client:
                logger.info(f"Using LLM client for prompt: {prompt[:100]}...")
                
                # Prepare messages for LLM
                messages = []
                
                # Add conversation history
                for turn in conversation_history:
                    messages.append({
                        "role": turn["role"],
                        "content": turn["content"]
                    })
                
                # Get system message from profile if available
                system_message = None
                if session.user_id in self.profiles:
                    profile = self.profiles[session.user_id]
                    if hasattr(profile, 'preferences') and profile.preferences:
                        system_message = f"User preferences: {profile.preferences}"
                
                # Add system message if available
                if system_message:
                    messages.append({
                        "role": "system",
                        "content": system_message
                    })
                
                # Add user prompt
                messages.append({
                    "role": "user",
                    "content": prompt
                })
                
                # Get preset from step or use default
                preset = step.preset if hasattr(step, 'preset') else None
                
                # Get tools if specified
                tools = []
                if hasattr(step, 'tools') and step.tools:
                    for tool_name in step.tools:
                        if tool_name in self.tools:
                            tool = self.tools[tool_name]
                            tools.append({
                                "type": "function",
                                "function": {
                                    "name": tool.id,
                                    "description": tool.description,
                                    "parameters": tool.parameters or {}
                                }
                            })
                
                # Call LLM with preset and tools support
                response_data = self.llm_client.chat(
                    messages=messages,
                    preset=preset,
                    tools=tools if tools else None
                )
                
                if response_data["success"]:
                    response = response_data["text"]
                    
                    # Store conversation turn in memory system
                    if self.memory_system:
                        self.memory_system.add_conversation_turn(
                            session_id=session.session_id,
                            user_id=session.user_id,
                            role="user",
                            content=prompt
                        )
                        self.memory_system.add_conversation_turn(
                            session_id=session.session_id,
                            user_id=session.user_id,
                            role="assistant",
                            content=response
                        )
                    
                    # Handle tool calls if any
                    if response_data.get("tool_calls"):
                        for tool_call in response_data["tool_calls"]:
                            tool_name = tool_call["name"]
                            # Execute tool call
                            if tool_name in self.tools:
                                tool = self.tools[tool_name]
                                try:
                                    tool_result = self._execute_api_call(tool, session.data)
                                    
                                    # Add tool result to session
                                    session.data[f"tool_{tool_name}_result"] = tool_result
                                    
                                    # Store tool result in memory system
                                    if self.memory_system:
                                        self.memory_system.add_memory(
                                            content=f"Tool {tool_name} result: {json.dumps(tool_result)}",
                                            memory_type=MemoryType.CONTEXT,
                                            session_id=session.session_id,
                                            user_id=session.user_id,
                                            priority=MemoryPriority.NORMAL,
                                            metadata={"tool_name": tool_name}
                                        )
                                    
                                    # If tool result needs to be sent back to LLM
                                    if hasattr(step, 'continue_after_tools') and step.continue_after_tools:
                                        messages.append({
                                            "role": "assistant",
                                            "content": response
                                        })
                                        messages.append({
                                            "role": "tool",
                                            "content": json.dumps(tool_result),
                                            "tool_call_id": tool_name
                                        })
                                        
                                        # Get follow-up response from LLM
                                        follow_up = self.llm_client.chat(
                                            messages=messages,
                                            preset=preset
                                        )
                                        
                                        if follow_up["success"]:
                                            response = follow_up["text"]
                                            
                                            # Store follow-up in memory system
                                            if self.memory_system:
                                                self.memory_system.add_conversation_turn(
                                                    session_id=session.session_id,
                                                    user_id=session.user_id,
                                                    role="assistant",
                                                    content=response
                                                )
                                except Exception as e:
                                    logger.error(f"Tool execution failed: {e}")
                else:
                    logger.error(f"LLM request failed: {response_data.get('error')}")
                    response = f"Error: {response_data.get('error')}"
            else:
                logger.info("Using mock LLM response")
                response = f"Mock LLM response for: {prompt}"
            
            # Store response in session
            session.data[f"step_{step.id}_response"] = response
            
            # Update session data in Redis if available
            if self.redis_manager:
                self.redis_manager.update_session_data(
                    session.session_id,
                    f"step_{step.id}_response",
                    response
                )
            
            return {"success": True, "response": response}
            
        except Exception as e:
            logger.error(f"Prompt step execution failed: {str(e)}")
            return {"error": f"Prompt execution failed: {str(e)}"}
    
    def _execute_api_step(self, step: ProtocolStep, session: Session, **kwargs) -> Dict[str, Any]:
        """Execute API step / Виконати крок API"""
        if not step.tool_api_id or step.tool_api_id not in self.tools:
            return {"error": "Tool not found"}
        
        tool = self.tools[step.tool_api_id]
        
        try:
            # Execute real API call
            response = self._execute_api_call(tool, session.data)
            session.data[f"step_{step.id}_api_response"] = response
            
            return {"success": True, "api_response": response}
            
        except Exception as e:
            logger.error(f"API step execution failed: {str(e)}")
            return {"error": f"API execution failed: {str(e)}"}
    
    def _execute_api_call(self, tool: ToolAPI, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute API call using HTTP client / Виконати API виклик через HTTP клієнт"""
        import requests
        
        try:
            
            # Prepare headers
            headers = tool.headers or {}
            if tool.authentication:
                auth_type = tool.authentication.get("type", "")
                if auth_type == "api_key":
                    api_key = tool.authentication.get("credentials", {}).get("key", "")
                    # Replace placeholders in API key
                    api_key = self._replace_placeholders(api_key, session_data)
                    headers["Authorization"] = f"Bearer {api_key}"
                elif auth_type == "basic":
                    username = tool.authentication.get("credentials", {}).get("username", "")
                    password = tool.authentication.get("credentials", {}).get("password", "")
                    import base64
                    credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
                    headers["Authorization"] = f"Basic {credentials}"
            
            # Prepare parameters
            params = {}
            if tool.parameters:
                for key, value in tool.parameters.items():
                    # Replace placeholders in parameters
                    if isinstance(value, str):
                        params[key] = self._replace_placeholders(value, session_data)
                    else:
                        params[key] = value
            
            # Make API call based on method
            method = tool.method.upper()
            endpoint = tool.endpoint
            
            logger.info(f"Making {method} request to {endpoint}")
            
            # Add retry mechanism
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    if method == "GET":
                        response = requests.get(endpoint, params=params, headers=headers, timeout=30)
                    elif method == "POST":
                        response = requests.post(endpoint, json=params, headers=headers, timeout=30)
                    elif method == "PUT":
                        response = requests.put(endpoint, json=params, headers=headers, timeout=30)
                    elif method == "DELETE":
                        response = requests.delete(endpoint, headers=headers, timeout=30)
                    else:
                        raise ValueError(f"Unsupported HTTP method: {method}")
                    
                    response.raise_for_status()
                    result = response.json()
                    
                    logger.info(f"API call successful (attempt {attempt + 1}): {result}")
                    return result
                    
                except requests.exceptions.RequestException as e:
                    logger.warning(f"API call failed (attempt {attempt + 1}/{max_retries}): {e}")
                    if attempt == max_retries - 1:
                        raise
                    continue
            
        except Exception as e:
            logger.error(f"API call failed: {str(e)}")
            raise
    
    def _replace_placeholders(self, text: str, session_data: Dict[str, Any]) -> str:
        """Replace placeholders in text with session data / Замінити плейсхолдери в тексті даними сесії"""
        import re
        
        # Find all placeholders like {session.data.key}
        pattern = r'\{session\.data\.(\w+)\}'
        
        def replace_placeholder(match):
            key = match.group(1)
            value = session_data.get(key, "")
            return str(value)
        
        return re.sub(pattern, replace_placeholder, text)
    
    def _execute_condition_step(self, step: ProtocolStep, session: Session, **kwargs) -> Dict[str, Any]:
        """Execute condition step / Виконати крок умови"""
        if not step.conditions:
            return {"success": True, "no_conditions": True}
        
        conditions_met = True
        for condition in step.conditions:
            # Simple condition evaluation
            # Проста оцінка умов
            variable_value = session.data.get(condition.variable)
            if not self._evaluate_condition(condition, variable_value):
                conditions_met = False
                break
        
        return {"success": True, "conditions_met": conditions_met}
    
    def _execute_end_step(self, step: ProtocolStep, session: Session, **kwargs) -> Dict[str, Any]:
        """Execute end step / Виконати крок завершення"""
        session.active = False
        return {"success": True, "session_ended": True}
    
    def _evaluate_condition(self, condition: Condition, value: Any) -> bool:
        """Evaluate condition / Оцінити умову"""
        if condition.operator == "equals":
            return value == condition.value
        elif condition.operator == "not_equals":
            return value != condition.value
        elif condition.operator == "contains":
            return condition.value in str(value)
        elif condition.operator == "greater_than":
            return value > condition.value
        elif condition.operator == "less_than":
            return value < condition.value
        return False
    
    def get_session_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session data / Отримати дані сесії
        
        Args:
            session_id: Session identifier / Ідентифікатор сесії
            
        Returns:
            Optional[Dict[str, Any]]: Session data or None / Дані сесії або None
        """
        # Try Redis first if available
        if self.redis_manager:
            redis_data = self.redis_manager.get_session_data(session_id)
            if redis_data:
                return redis_data
        
        # Fallback to memory
        if session_id in self.sessions:
            return self.sessions[session_id].data
        return None

    def update_session_data(self, session_id: str, data: Dict[str, Any]) -> bool:
        """
        Update session data / Оновити дані сесії
        
        Args:
            session_id: Session identifier / Ідентифікатор сесії
            data: Data to update / Дані для оновлення
            
        Returns:
            bool: Success status / Статус успіху
        """
        # Update Redis if available
        if self.redis_manager:
            success = self.redis_manager.update_session_data_batch(session_id, data)
            if not success:
                logger.warning(f"Failed to update session {session_id} in Redis")
        
        # Update memory
        if session_id in self.sessions:
            self.sessions[session_id].data.update(data)
            return True
        return False
    
    def _register_builtin_tools(self):
        """Register built-in tools in the registry"""
        try:
            # Register calendar tool
            calendar_tool = CalendarTool()
            self.tool_registry.register_tool(calendar_tool)
            logger.info(f"Tool '{calendar_tool.name}' registered")
            
            # Register CRM tool
            crm_tool = CRMTool()
            self.tool_registry.register_tool(crm_tool)
            logger.info(f"Tool '{crm_tool.name}' registered")
            
            # Register notifier tool
            notifier_tool = NotifierTool()
            self.tool_registry.register_tool(notifier_tool)
            logger.info(f"Tool '{notifier_tool.name}' registered")
            
            logger.info("All built-in tools registered successfully")
        except Exception as e:
            logger.error(f"Failed to register built-in tools: {e}")
    
    def get_memory_context(self, session_id: str, user_id: str,
                          context_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Get memory context for a session / Отримати контекст пам'яті для сесії
        
        Args:
            session_id: Session identifier / Ідентифікатор сесії
            user_id: User identifier / Ідентифікатор користувача
            context_type: Type of context to retrieve / Тип контексту для отримання
            
        Returns:
            Dict[str, Any]: Memory context / Контекст пам'яті
        """
        if not self.memory_system:
            return {}
        
        return self.memory_system.get_context(
            session_id=session_id,
            user_id=user_id,
            context_type=context_type
        )
    
    def add_memory(self, content: str, memory_type: MemoryType,
                  session_id: str, user_id: str,
                  priority: MemoryPriority = MemoryPriority.NORMAL,
                  metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Add memory entry / Додати запис пам'яті
        
        Args:
            content: Memory content / Вміст пам'яті
            memory_type: Type of memory / Тип пам'яті
            session_id: Session identifier / Ідентифікатор сесії
            user_id: User identifier / Ідентифікатор користувача
            priority: Memory priority / Пріоритет пам'яті
            metadata: Additional metadata / Додаткові метадані
            
        Returns:
            bool: Success status / Статус успіху
        """
        if not self.memory_system:
            return False
        
        try:
            self.memory_system.add_memory(
                content=content,
                memory_type=memory_type,
                session_id=session_id,
                user_id=user_id,
                priority=priority,
                metadata=metadata or {}
            )
            return True
        except Exception as e:
            logger.error(f"Failed to add memory: {e}")
            return False
    
    def search_memory(self, query: str, session_id: Optional[str] = None,
                     user_id: Optional[str] = None,
                     memory_type: Optional[MemoryType] = None,
                     limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Search memory entries / Пошук записів пам'яті
        
        Args:
            query: Search query / Запит пошуку
            session_id: Session identifier (optional) / Ідентифікатор сесії (опціонально)
            user_id: User identifier (optional) / Ідентифікатор користувача (опціонально)
            memory_type: Memory type filter (optional) / Фільтр типу пам'яті (опціонально)
            limit: Maximum number of results (optional) / Максимальна кількість результатів (опціонально)
            
        Returns:
            List[Dict[str, Any]]: Search results / Результати пошуку
        """
        if not self.memory_system:
            return []
        
        return self.memory_system.search_memory(
            query=query,
            session_id=session_id,
            user_id=user_id,
            memory_type=memory_type,
            limit=limit
        )
    
    def get_conversation_history(self, session_id: str,
                                limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get conversation history for a session / Отримати історію розмови для сесії
        
        Args:
            session_id: Session identifier / Ідентифікатор сесії
            limit: Maximum number of turns (optional) / Максимальна кількість ходів (опціонально)
            
        Returns:
            List[Dict[str, Any]]: Conversation history / Історія розмови
        """
        if not self.memory_system:
            return []
        
        return self.memory_system.get_conversation_history(
            session_id=session_id,
            limit=limit
        )