"""
YAML parser for MOVA language
YAML парсер для мови MOVA
"""

import yaml
from typing import Dict, List, Any, Optional
from loguru import logger

from .json_parser import MovaJsonParser


class MovaYamlParser(MovaJsonParser):
    """
    YAML parser for MOVA language files
    YAML парсер для файлів мови MOVA
    """
    
    def __init__(self):
        """Initialize YAML parser / Ініціалізація YAML парсера"""
        super().__init__()
        self.supported_extensions = ['.yaml', '.yml']
        logger.info("MOVA YAML Parser initialized / MOVA YAML Parser ініціалізовано")
    
    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """
        Parse MOVA YAML file / Парсити MOVA YAML файл
        
        Args:
            file_path: Path to YAML file / Шлях до YAML файлу
            
        Returns:
            Dict[str, Any]: Parsed MOVA structure / Розпарсена структура MOVA
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = yaml.safe_load(file)
            
            logger.info(f"Successfully parsed YAML file: {file_path}")
            return self._validate_and_transform(data)
            
        except Exception as e:
            logger.error(f"Failed to parse YAML file {file_path}: {e}")
            raise
    
    def parse_string(self, yaml_string: str) -> Dict[str, Any]:
        """
        Parse MOVA YAML string / Парсити MOVA YAML рядок
        
        Args:
            yaml_string: YAML string content / Зміст YAML рядка
            
        Returns:
            Dict[str, Any]: Parsed MOVA structure / Розпарсена структура MOVA
        """
        try:
            data = yaml.safe_load(yaml_string)
            
            logger.info("Successfully parsed YAML string")
            return self._validate_and_transform(data)
            
        except Exception as e:
            logger.error(f"Failed to parse YAML string: {e}")
            raise
    
    def export_to_yaml(self, data: Dict[str, Any], file_path: str) -> bool:
        """
        Export MOVA data to YAML file / Експортувати дані MOVA до YAML файлу
        
        Args:
            data: MOVA data to export / Дані MOVA для експорту
            file_path: Output file path / Шлях до вихідного файлу
            
        Returns:
            bool: Success status / Статус успіху
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                yaml.dump(data, file, default_flow_style=False, allow_unicode=True, indent=2)
            
            logger.info(f"Successfully exported to YAML: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to export to YAML {file_path}: {e}")
            return False 