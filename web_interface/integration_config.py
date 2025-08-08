"""
Integration Configuration for MOVA Web Interface
Конфігурація інтеграції для веб-інтерфейсу MOVA
"""

import os
from pathlib import Path
from typing import Dict, Any

class IntegrationConfig:
    """Конфігурація інтеграції"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.backend_dir = self.project_root / "web_interface" / "backend"
        self.frontend_dir = self.project_root / "web_interface" / "frontend"
        
    @property
    def backend_config(self) -> Dict[str, Any]:
        """Конфігурація бекенда"""
        return {
            "host": "0.0.0.0",
            "port": 8000,
            "debug": True,
            "reload": True,
            "allowed_hosts": [
                "http://localhost:3000",
                "http://localhost:5173", 
                "http://127.0.0.1:3000",
                "http://127.0.0.1:5173",
                "http://localhost:3001",
                "http://127.0.0.1:3001"
            ],
            "cors_origins": [
                "http://localhost:3000",
                "http://localhost:5173",
                "http://127.0.0.1:3000", 
                "http://127.0.0.1:5173",
                "http://localhost:3001",
                "http://127.0.0.1:3001"
            ],
            "upload_dir": str(self.backend_dir / "uploads"),
            "max_file_size": 10 * 1024 * 1024,  # 10MB
            "secret_key": "mova-web-interface-secret-key-2024",
            "access_token_expire_minutes": 30,
            "log_level": "INFO"
        }
        
    @property
    def frontend_config(self) -> Dict[str, Any]:
        """Конфігурація фронтенда"""
        return {
            "port": 3000,
            "api_base_url": "http://localhost:8000",
            "api_timeout": 10000,
            "websocket_url": "ws://localhost:8000/ws",
            "build_dir": str(self.frontend_dir / "dist"),
            "public_dir": str(self.frontend_dir / "public"),
            "dev_server": {
                "port": 3000,
                "host": "localhost",
                "proxy": {
                    "/api": {
                        "target": "http://localhost:8000",
                        "changeOrigin": True,
                        "secure": False
                    }
                }
            }
        }
        
    @property
    def database_config(self) -> Dict[str, Any]:
        """Конфігурація бази даних"""
        return {
            "redis_url": os.getenv("MOVA_REDIS_URL", "redis://localhost:6379"),
            "cache_ttl": 3600,
            "session_ttl": 1800
        }
        
    @property
    def ml_config(self) -> Dict[str, Any]:
        """Конфігурація ML"""
        return {
            "models_dir": str(self.project_root / "models"),
            "llm_api_key": os.getenv("MOVA_LLM_API_KEY"),
            "llm_model": os.getenv("MOVA_LLM_MODEL", "openai/gpt-3.5-turbo"),
            "max_tokens": 4000,
            "temperature": 0.7
        }
        
    @property
    def webhook_config(self) -> Dict[str, Any]:
        """Конфігурація webhook"""
        return {
            "enabled": True,
            "endpoint": "/api/webhook",
            "secret": os.getenv("WEBHOOK_SECRET", "mova-webhook-secret"),
            "timeout": 30
        }
        
    def get_full_config(self) -> Dict[str, Any]:
        """Повна конфігурація"""
        return {
            "backend": self.backend_config,
            "frontend": self.frontend_config,
            "database": self.database_config,
            "ml": self.ml_config,
            "webhook": self.webhook_config,
            "project": {
                "name": "MOVA Web Interface",
                "version": "2.2.0",
                "description": "Веб-інтерфейс для управління MOVA 2.2"
            }
        }
        
    def validate_config(self) -> bool:
        """Валідація конфігурації"""
        errors = []
        
        # Перевірка директорій
        if not self.backend_dir.exists():
            errors.append(f"Backend directory not found: {self.backend_dir}")
            
        if not self.frontend_dir.exists():
            errors.append(f"Frontend directory not found: {self.frontend_dir}")
            
        # Перевірка портів
        if self.backend_config["port"] == self.frontend_config["port"]:
            errors.append("Backend and frontend ports cannot be the same")
            
        # Перевірка API ключів
        if not self.ml_config["llm_api_key"]:
            errors.append("MOVA_LLM_API_KEY environment variable not set")
            
        if errors:
            print("Configuration validation errors:")
            for error in errors:
                print(f"  - {error}")
            return False
            
        return True


# Глобальний екземпляр конфігурації
config = IntegrationConfig()


def get_config() -> IntegrationConfig:
    """Отримання конфігурації"""
    return config


def validate_and_get_config() -> Dict[str, Any]:
    """Валідація та отримання конфігурації"""
    if not config.validate_config():
        raise ValueError("Invalid configuration")
    return config.get_full_config() 