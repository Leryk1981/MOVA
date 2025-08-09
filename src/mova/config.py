"""
Configuration management for MOVA SDK
Управління конфігурацією для MOVA SDK
"""

from typing import Dict, Any, Optional
from pathlib import Path

# Import new configuration components
from .config import (
    MOVAConfigSchema,
    load_config
)


class MovaConfig(MOVAConfigSchema):
    """
    Legacy configuration class for backward compatibility
    Клас конфігурації для зворотної сумісності
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Initialize with default values
        self._config_data = load_config()
    
    def __getattr__(self, name):
        # Delegate to new configuration system
        if hasattr(self._config_data, name):
            return getattr(self._config_data, name)
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{name}'"
        )
    
    def __setattr__(self, name, value):
        # Handle internal attributes
        if name.startswith('_'):
            super().__setattr__(name, value)
        else:
            # Delegate to new configuration system
            if hasattr(self._config_data, name):
                setattr(self._config_data, name, value)
            else:
                super().__setattr__(name, value)


class ConfigManager:
    """
    Configuration manager for MOVA SDK
    Менеджер конфігурації для MOVA SDK
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration manager
        Ініціалізація менеджера конфігурації
        
        Args:
            config_file: Path to configuration file /
                         Шлях до файлу конфігурації
        """
        self.config_file = config_file
        self.config = self._load_config()
    
    def _load_config(self) -> MovaConfig:
        """Load configuration from file and environment /
           Завантажити конфігурацію з файлу та середовища"""
        # Use new configuration loader
        config_data = load_config(self.config_file)
        return MovaConfig(**config_data.model_dump())
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value / Отримати значення конфігурації"""
        return getattr(self.config, key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value / Встановити значення конфігурації"""
        if hasattr(self.config, key):
            setattr(self.config, key, value)
    
    def update(self, **kwargs) -> None:
        """Update multiple configuration values /
           Оновити кілька значень конфігурації"""
        for key, value in kwargs.items():
            self.set(key, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary /
           Конвертувати конфігурацію в словник"""
        return self.config._config_data.model_dump()
    
    def validate(self) -> bool:
        """Validate configuration / Валідувати конфігурацію"""
        try:
            # Validate required settings
            if (self.config.encryption_enabled and
                    not self.config.encryption_key):
                raise ValueError(
                    "Encryption key required when encryption is enabled"
                )
            
            # Validate cache directory
            if self.config.cache_enabled:
                cache_path = Path(self.config.cache_dir)
                cache_path.mkdir(parents=True, exist_ok=True)
            
            return True
        except Exception as e:
            print(f"Configuration validation failed: {e}")
            return False


# Global configuration instance
config_manager = ConfigManager()


def get_config() -> MovaConfig:
    """Get global configuration / Отримати глобальну конфігурацію"""
    return config_manager.config


def get_config_value(key: str, default: Any = None) -> Any:
    """Get configuration value / Отримати значення конфігурації"""
    return config_manager.get(key, default)


def set_config_value(key: str, value: Any) -> None:
    """Set configuration value / Встановити значення конфігурації"""
    config_manager.set(key, value)