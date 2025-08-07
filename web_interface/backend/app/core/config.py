"""
Configuration settings for MOVA Web Interface
Конфігурація для веб-інтерфейсу MOVA
"""

import os
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Налаштування додатку"""
    
    # Основні налаштування
    APP_NAME: str = "MOVA Web Interface"
    VERSION: str = "2.2.0"
    DEBUG: bool = Field(default=True, env="DEBUG")
    
    # Сервер
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    
    # CORS
    ALLOWED_HOSTS: List[str] = Field(
        default=[
            "http://localhost:3000", 
            "http://localhost:5173",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
            "http://localhost:3001",
            "http://127.0.0.1:3001"
        ],
        env="ALLOWED_HOSTS"
    )
    
    # MOVA SDK налаштування
    MOVA_REDIS_URL: Optional[str] = Field(default=None, env="MOVA_REDIS_URL")
    MOVA_LLM_API_KEY: Optional[str] = Field(default=None, env="MOVA_LLM_API_KEY")
    MOVA_LLM_MODEL: str = Field(default="openai/gpt-3.5-turbo", env="MOVA_LLM_MODEL")
    
    # Файлова система
    UPLOAD_DIR: str = Field(default="uploads", env="UPLOAD_DIR")
    MAX_FILE_SIZE: int = Field(default=10 * 1024 * 1024, env="MAX_FILE_SIZE")  # 10MB
    
    # Безпека
    SECRET_KEY: str = Field(default="your-secret-key-change-in-production", env="SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # Логування
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FILE: Optional[str] = Field(default=None, env="LOG_FILE")
    
    # WebSocket
    WS_HEARTBEAT_INTERVAL: int = Field(default=30, env="WS_HEARTBEAT_INTERVAL")
    
    # Кешування
    CACHE_TTL: int = Field(default=3600, env="CACHE_TTL")  # 1 година
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Глобальний екземпляр налаштувань
settings = Settings()


def get_settings() -> Settings:
    """Отримання налаштувань"""
    return settings 