"""
MOVA Engine - Core processing engine
MOVA Engine - Основний обробний движок
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from loguru import logger

from .models import (
    Intent, Protocol, ToolAPI, Instruction, Profile, 
    Session, Contract, ProtocolStep, Condition
)
from ..redis_manager import get_redis_manager, MovaRedisManager
from ..llm_client import get_llm_client, MovaLLMClient


class MovaEngine:
    """
    Main MOVA language processing engine
    Основний обробний движок мови MOVA
    """
    
    def __init__(self, redis_url: Optional[str] = None, llm_api_key: Optional[str] = None, llm_model: str = "openai/gpt-3.5-turbo"):
        """
        Initialize MOVA engine / Ініціалізація движка MOVA
        
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
                logger.info(f"MOVA Engine initialized with Redis at {redis_url}")
            except Exception as e:
                logger.warning(f"Failed to initialize Redis: {e}. Using in-memory storage.")
        else:
            logger.info("MOVA Engine initialized with in-memory storage")
        
        # Initialize LLM client if API key provided
        self.llm_client: Optional[MovaLLMClient] = None
        if llm_api_key:
            try:
                self.llm_client = get_llm_client(llm_api_key, llm_model)
                logger.info(f"MOVA Engine initialized with LLM model: {llm_model}")
            except Exception as e:
                logger.warning(f"Failed to initialize LLM client: {e}. Using mock responses.")
        else:
            logger.info("MOVA Engine initialized with mock LLM responses")
    
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
            
            # Substitute session data placeholders
            for key, value in session_data.items():
                placeholder = f"{{session.data.{key}}}"
                if placeholder in prompt:
                    prompt = prompt.replace(placeholder, str(value))
            
            # Use LLM client if available, otherwise use mock
            if self.llm_client:
                logger.info(f"Using LLM client for prompt: {prompt[:100]}...")
                
                # Get system message from profile if available
                system_message = None
                if session.user_id in self.profiles:
                    profile = self.profiles[session.user_id]
                    if hasattr(profile, 'preferences') and profile.preferences:
                        system_message = f"User preferences: {profile.preferences}"
                
                response = self.llm_client.generate_response(
                    prompt=prompt,
                    system_message=system_message,
                    **kwargs
                )
            else:
                logger.info("Using mock LLM response")
                response = f"Mock LLM response for: {prompt}"
            
            # Store response in session
            session.data[f"step_{step.id}_response"] = response
            
            # Update session data in Redis if available
            if self.redis_manager:
                self.redis_manager.update_session_data(session.session_id, f"step_{step.id}_response", response)
            
            return {"success": True, "response": response}
            
        except Exception as e:
            logger.error(f"Prompt step execution failed: {str(e)}")
            return {"error": f"Prompt execution failed: {str(e)}"}
    
    def _execute_api_step(self, step: ProtocolStep, session: Session, **kwargs) -> Dict[str, Any]:
        """Execute API step / Виконати крок API"""
        if not step.tool_api_id or step.tool_api_id not in self.tools:
            return {"error": "Tool not found"}
        
        tool = self.tools[step.tool_api_id]
        # Here would be actual API call
        # Тут буде реальний виклик API
        response = f"API call to {tool.endpoint}"
        session.data[f"step_{step.id}_api_response"] = response
        
        return {"success": True, "api_response": response}
    
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