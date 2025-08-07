"""
JSON parser for MOVA language
JSON парсер для мови MOVA
"""

import json
import json5
from typing import Dict, List, Any, Optional
from loguru import logger

from ..core.models import (
    Intent, Protocol, ToolAPI, Instruction, Profile, 
    Session, Contract, ProtocolStep, Condition,
    IntentType, ActionType, ComparisonOperator
)


class MovaJsonParser:
    """
    JSON parser for MOVA language files
    JSON парсер для файлів мови MOVA
    """
    
    def __init__(self):
        """Initialize JSON parser / Ініціалізація JSON парсера"""
        self.supported_extensions = ['.json', '.json5']
        logger.info("MOVA JSON Parser initialized / MOVA JSON Parser ініціалізовано")
    
    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """
        Parse MOVA JSON file / Парсити MOVA JSON файл
        
        Args:
            file_path: Path to JSON file / Шлях до JSON файлу
            
        Returns:
            Dict[str, Any]: Parsed MOVA structure / Розпарсена структура MOVA
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Try JSON5 first, then fallback to standard JSON
            # Спочатку спробувати JSON5, потім стандартний JSON
            try:
                data = json5.loads(content)
            except:
                data = json.loads(content)
            
            logger.info(f"Successfully parsed file: {file_path}")
            return self._validate_and_transform(data)
            
        except Exception as e:
            logger.error(f"Failed to parse file {file_path}: {e}")
            raise
    
    def parse_string(self, json_string: str) -> Dict[str, Any]:
        """
        Parse MOVA JSON string / Парсити MOVA JSON рядок
        
        Args:
            json_string: JSON string content / Зміст JSON рядка
            
        Returns:
            Dict[str, Any]: Parsed MOVA structure / Розпарсена структура MOVA
        """
        try:
            # Try JSON5 first, then fallback to standard JSON
            try:
                data = json5.loads(json_string)
            except:
                data = json.loads(json_string)
            
            logger.info("Successfully parsed JSON string")
            return self._validate_and_transform(data)
            
        except Exception as e:
            logger.error(f"Failed to parse JSON string: {e}")
            raise
    
    def _validate_and_transform(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and transform parsed data / Валідувати та трансформувати розпарсені дані
        
        Args:
            data: Raw parsed data / Сирі розпарсені дані
            
        Returns:
            Dict[str, Any]: Validated and transformed data / Валідовані та трансформовані дані
        """
        result = {
            "version": data.get("version", "2.0"),
            "intents": [],
            "protocols": [],
            "tools": [],
            "instructions": [],
            "profiles": [],
            "sessions": [],
            "contracts": []
        }
        
        # Parse intents
        if "intents" in data:
            for intent_data in data["intents"]:
                intent = self._parse_intent(intent_data)
                if intent:
                    result["intents"].append(intent.model_dump())
        
        # Parse protocols
        if "protocols" in data:
            for protocol_data in data["protocols"]:
                protocol = self._parse_protocol(protocol_data)
                if protocol:
                    result["protocols"].append(protocol.model_dump())
        
        # Parse tools
        if "tools" in data:
            for tool_data in data["tools"]:
                tool = self._parse_tool(tool_data)
                if tool:
                    result["tools"].append(tool.model_dump())
        
        # Parse instructions
        if "instructions" in data:
            for instruction_data in data["instructions"]:
                instruction = self._parse_instruction(instruction_data)
                if instruction:
                    result["instructions"].append(instruction.model_dump())
        
        # Parse profiles
        if "profiles" in data:
            for profile_data in data["profiles"]:
                profile = self._parse_profile(profile_data)
                if profile:
                    result["profiles"].append(profile.model_dump())
        
        # Parse sessions
        if "sessions" in data:
            for session_data in data["sessions"]:
                session = self._parse_session(session_data)
                if session:
                    result["sessions"].append(session.model_dump())
        
        # Parse contracts
        if "contracts" in data:
            for contract_data in data["contracts"]:
                contract = self._parse_contract(contract_data)
                if contract:
                    result["contracts"].append(contract.model_dump())
        
        return result
    
    def _parse_intent(self, data: Dict[str, Any]) -> Optional[Intent]:
        """Parse intent from data / Парсити намір з даних"""
        try:
            return Intent(
                name=data["name"],
                patterns=data["patterns"],
                priority=data.get("priority", 0),
                response_template=data.get("response_template"),
                intent_type=IntentType(data.get("intent_type", "custom"))
            )
        except Exception as e:
            logger.error(f"Failed to parse intent: {e}")
            return None
    
    def _parse_protocol(self, data: Dict[str, Any]) -> Optional[Protocol]:
        """Parse protocol from data / Парсити протокол з даних"""
        try:
            steps = []
            for step_data in data.get("steps", []):
                step = self._parse_protocol_step(step_data)
                if step:
                    steps.append(step)
            
            return Protocol(
                name=data["name"],
                steps=steps,
                description=data.get("description")
            )
        except Exception as e:
            logger.error(f"Failed to parse protocol: {e}")
            return None
    
    def _parse_protocol_step(self, data: Dict[str, Any]) -> Optional[ProtocolStep]:
        """Parse protocol step from data / Парсити крок протоколу з даних"""
        try:
            conditions = []
            for condition_data in data.get("conditions", []):
                condition = self._parse_condition(condition_data)
                if condition:
                    conditions.append(condition)
            
            return ProtocolStep(
                id=data["id"],
                action=ActionType(data["action"]),
                prompt=data.get("prompt"),
                tool_api_id=data.get("tool_api_id"),
                conditions=conditions if conditions else None,
                next_step=data.get("next_step")
            )
        except Exception as e:
            logger.error(f"Failed to parse protocol step: {e}")
            return None
    
    def _parse_condition(self, data: Dict[str, Any]) -> Optional[Condition]:
        """Parse condition from data / Парсити умову з даних"""
        try:
            return Condition(
                variable=data["variable"],
                operator=ComparisonOperator(data["operator"]),
                value=data["value"]
            )
        except Exception as e:
            logger.error(f"Failed to parse condition: {e}")
            return None
    
    def _parse_tool(self, data: Dict[str, Any]) -> Optional[ToolAPI]:
        """Parse tool from data / Парсити інструмент з даних"""
        try:
            return ToolAPI(
                id=data["id"],
                name=data["name"],
                endpoint=data["endpoint"],
                method=data.get("method", "GET"),
                headers=data.get("headers"),
                parameters=data.get("parameters"),
                authentication=data.get("authentication")
            )
        except Exception as e:
            logger.error(f"Failed to parse tool: {e}")
            return None
    
    def _parse_instruction(self, data: Dict[str, Any]) -> Optional[Instruction]:
        """Parse instruction from data / Парсити інструкцію з даних"""
        try:
            return Instruction(
                id=data["id"],
                title=data["title"],
                content=data["content"],
                category=data.get("category"),
                tags=data.get("tags", [])
            )
        except Exception as e:
            logger.error(f"Failed to parse instruction: {e}")
            return None
    
    def _parse_profile(self, data: Dict[str, Any]) -> Optional[Profile]:
        """Parse profile from data / Парсити профіль з даних"""
        try:
            return Profile(
                user_id=data["user_id"],
                name=data.get("name"),
                preferences=data.get("preferences", {}),
                language=data.get("language", "en"),
                timezone=data.get("timezone")
            )
        except Exception as e:
            logger.error(f"Failed to parse profile: {e}")
            return None
    
    def _parse_session(self, data: Dict[str, Any]) -> Optional[Session]:
        """Parse session from data / Парсити сесію з даних"""
        try:
            return Session(
                session_id=data["session_id"],
                user_id=data["user_id"],
                start_time=data["start_time"],
                data=data.get("data", {}),
                context=data.get("context", {}),
                active=data.get("active", True)
            )
        except Exception as e:
            logger.error(f"Failed to parse session: {e}")
            return None
    
    def _parse_contract(self, data: Dict[str, Any]) -> Optional[Contract]:
        """Parse contract from data / Парсити контракт з даних"""
        try:
            conditions = []
            for condition_data in data.get("conditions", []):
                condition = self._parse_condition(condition_data)
                if condition:
                    conditions.append(condition)
            
            return Contract(
                contract_id=data["contract_id"],
                parties=data["parties"],
                terms=data["terms"],
                conditions=conditions,
                valid_from=data["valid_from"],
                valid_until=data.get("valid_until")
            )
        except Exception as e:
            logger.error(f"Failed to parse contract: {e}")
            return None
    
    def export_to_json(self, data: Dict[str, Any], file_path: str) -> bool:
        """
        Export MOVA data to JSON file / Експортувати дані MOVA до JSON файлу
        
        Args:
            data: MOVA data to export / Дані MOVA для експорту
            file_path: Output file path / Шлях до вихідного файлу
            
        Returns:
            bool: Success status / Статус успіху
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=2, ensure_ascii=False)
            
            logger.info(f"Successfully exported to: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to export to {file_path}: {e}")
            return False 