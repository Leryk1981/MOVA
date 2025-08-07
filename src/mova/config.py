"""
Configuration management for MOVA SDK
Управління конфігурацією для MOVA SDK
"""

import os
from typing import Dict, Any, Optional
from pathlib import Path
from pydantic import BaseModel, Field


class MovaConfig(BaseModel):
    """
    Configuration settings for MOVA SDK
    Налаштування конфігурації для MOVA SDK
    """
    
    # Logging settings
    log_level: str = Field(default="INFO", description="Logging level")
    log_file: Optional[str] = Field(default=None, description="Log file path")
    
    # API settings
    api_timeout: int = Field(default=30, description="API request timeout in seconds")
    api_retries: int = Field(default=3, description="Number of API retries")
    api_rate_limit: int = Field(default=100, description="API rate limit per minute")
    
    # Cache settings
    cache_enabled: bool = Field(default=True, description="Enable caching")
    cache_ttl: int = Field(default=3600, description="Cache TTL in seconds")
    cache_dir: str = Field(default=".mova_cache", description="Cache directory")
    
    # Security settings
    encryption_enabled: bool = Field(default=False, description="Enable data encryption")
    encryption_key: Optional[str] = Field(default=None, description="Encryption key")
    
    # Performance settings
    max_concurrent_requests: int = Field(default=10, description="Max concurrent requests")
    request_timeout: int = Field(default=30, description="Request timeout")
    
    # Development settings
    debug_mode: bool = Field(default=False, description="Enable debug mode")
    verbose_output: bool = Field(default=False, description="Enable verbose output")
    
    # Language settings
    default_language: str = Field(default="en", description="Default language")
    supported_languages: list = Field(default=["en", "uk"], description="Supported languages")
    
    # Webhook settings
    webhook_enabled: bool = Field(default=True, description="Enable webhook support")
    webhook_timeout: int = Field(default=30, description="Webhook request timeout in seconds")
    webhook_max_retries: int = Field(default=3, description="Webhook max retries")
    webhook_secret: Optional[str] = Field(default=None, description="Default webhook secret")
    
    model_config = {
        "env_prefix": "MOVA_",
        "case_sensitive": False
    }


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
            config_file: Path to configuration file / Шлях до файлу конфігурації
        """
        self.config_file = config_file
        self.config = self._load_config()
    
    def _load_config(self) -> MovaConfig:
        """Load configuration from file and environment / Завантажити конфігурацію з файлу та середовища"""
        # Load from environment variables first
        config = MovaConfig()
        
        # Load from config file if specified
        if self.config_file and Path(self.config_file).exists():
            # Here you could load from YAML/JSON config file
            pass
        
        return config
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value / Отримати значення конфігурації"""
        return getattr(self.config, key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value / Встановити значення конфігурації"""
        if hasattr(self.config, key):
            setattr(self.config, key, value)
    
    def update(self, **kwargs) -> None:
        """Update multiple configuration values / Оновити кілька значень конфігурації"""
        for key, value in kwargs.items():
            self.set(key, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary / Конвертувати конфігурацію в словник"""
        return self.config.model_dump()
    
    def validate(self) -> bool:
        """Validate configuration / Валідувати конфігурацію"""
        try:
            # Validate required settings
            if self.config.encryption_enabled and not self.config.encryption_key:
                raise ValueError("Encryption key required when encryption is enabled")
            
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