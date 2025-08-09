"""
Configuration loader for MOVA SDK
Завантажувач конфігурації для MOVA SDK
"""

import os
from typing import Dict, Any, Optional
from pathlib import Path
import yaml
import json
from .schema import MOVAConfigSchema


def load_config_from_file(config_path: str) -> MOVAConfigSchema:
    """
    Load configuration from file
    Завантажити конфігурацію з файлу
    
    Args:
        config_path: Path to configuration file / Шлях до файлу конфігурації
        
    Returns:
        MOVAConfigSchema: Loaded configuration / Завантажена конфігурація
    """
    config_path = Path(config_path)
    
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        if config_path.suffix.lower() in ['.yml', '.yaml']:
            config_data = yaml.safe_load(f)
        elif config_path.suffix.lower() == '.json':
            config_data = json.load(f)
        else:
            raise ValueError(
                f"Unsupported configuration file format: {config_path.suffix}"
            )
    
    # Validate and return configuration
    return MOVAConfigSchema(**config_data)


def load_config_from_env() -> Dict[str, Any]:
    """
    Load configuration from environment variables
    Завантажити конфігурацію з змінних оточення
    
    Returns:
        Dict[str, Any]: Configuration from environment /
        Конфігурація з оточення
    """
    config = {}
    
    # LLM configuration
    if os.getenv("MOVA_LLM_PROVIDER") or os.getenv("MOVA_LLM_API_KEY") or os.getenv("MOVA_LLM_MODEL") or os.getenv("MOVA_LLM_DEFAULT_MODEL"):
        llm_config = {}
        
        if os.getenv("MOVA_LLM_PROVIDER"):
            llm_config["provider"] = os.getenv("MOVA_LLM_PROVIDER")
        
        if os.getenv("MOVA_LLM_API_KEY"):
            llm_config["api_key"] = os.getenv("MOVA_LLM_API_KEY")
        
        if os.getenv("MOVA_LLM_API_KEY_ENV"):
            llm_config["api_key_env"] = os.getenv("MOVA_LLM_API_KEY_ENV")
        
        if os.getenv("MOVA_LLM_BASE_URL"):
            llm_config["base_url"] = os.getenv("MOVA_LLM_BASE_URL")
        
        if os.getenv("MOVA_LLM_MODEL"):
            llm_config["model"] = os.getenv("MOVA_LLM_MODEL")
        
        if os.getenv("MOVA_LLM_DEFAULT_MODEL"):
            llm_config["default_model"] = os.getenv("MOVA_LLM_DEFAULT_MODEL")
        
        if os.getenv("MOVA_LLM_MAX_TOKENS"):
            llm_config["max_tokens"] = int(os.getenv("MOVA_LLM_MAX_TOKENS"))
        
        if os.getenv("MOVA_LLM_TEMPERATURE"):
            llm_config["temperature"] = float(os.getenv("MOVA_LLM_TEMPERATURE"))
        
        if llm_config:
            config["llm"] = llm_config
    
    # Cache configuration
    if os.getenv("MOVA_CACHE_ENABLED"):
        config["cache"] = {
            "enabled": os.getenv("MOVA_CACHE_ENABLED", "true").lower()
            in ("true", "1", "yes"),
            "ttl": int(os.getenv("MOVA_CACHE_TTL", "3600"))
        }
    
    # Redis configuration
    if os.getenv("MOVA_REDIS_ENABLED"):
        config["redis"] = {
            "enabled": os.getenv("MOVA_REDIS_ENABLED", "false").lower()
            in ("true", "1", "yes"),
            "url": os.getenv("MOVA_REDIS_URL", "redis://localhost:6379"),
            "password": os.getenv("MOVA_REDIS_PASSWORD")
        }
    
    # Webhook configuration
    if os.getenv("MOVA_WEBHOOK_ENABLED"):
        config["webhook"] = {
            "enabled": os.getenv("MOVA_WEBHOOK_ENABLED", "false").lower()
            in ("true", "1", "yes")
        }
    
    # Tool policy configuration
    if os.getenv("MOVA_TOOL_POLICY_DEFAULT_ACTION"):
        config["tool_policy"] = {
            "default_action": os.getenv(
                "MOVA_TOOL_POLICY_DEFAULT_ACTION", "block"
            ),
            "allowed_tools": os.getenv(
                "MOVA_TOOL_POLICY_ALLOWED_TOOLS", ""
            ).split(",")
            if os.getenv("MOVA_TOOL_POLICY_ALLOWED_TOOLS") else None,
            "blocked_tools": os.getenv(
                "MOVA_TOOL_POLICY_BLOCKED_TOOLS", ""
            ).split(",")
            if os.getenv("MOVA_TOOL_POLICY_BLOCKED_TOOLS") else None,
            "require_confirmation": os.getenv(
                "MOVA_TOOL_POLICY_REQUIRE_CONFIRMATION", ""
            ).split(",")
            if os.getenv("MOVA_TOOL_POLICY_REQUIRE_CONFIRMATION") else None
        }
    
    # Preset configuration
    preset_names = os.getenv("MOVA_PRESETS", "")
    if preset_names:
        config["presets"] = {}
        for preset_name in preset_names.split(","):
            preset_name = preset_name.strip()
            model = os.getenv(f"MOVA_PRESETS_{preset_name.upper()}_MODEL")
            if model:
                preset_config = {
                    "name": preset_name,
                    "description": os.getenv(
                        f"MOVA_PRESETS_{preset_name.upper()}_DESCRIPTION"
                    ),
                    "model": model,
                    "temperature": float(os.getenv(
                        f"MOVA_PRESETS_{preset_name.upper()}_TEMPERATURE",
                        "0.3"
                    )),
                    "max_tokens": int(os.getenv(
                        f"MOVA_PRESETS_{preset_name.upper()}_MAX_TOKENS",
                        "1024"
                    )),
                    "system_prompt": os.getenv(
                        f"MOVA_PRESETS_{preset_name.upper()}_SYSTEM_PROMPT"
                    ),
                    "tools": os.getenv(
                        f"MOVA_PRESETS_{preset_name.upper()}_TOOLS", ""
                    ).split(",") if os.getenv(
                        f"MOVA_PRESETS_{preset_name.upper()}_TOOLS"
                    ) else None
                }
                
                # Add LLM config if provided
                llm_provider = os.getenv(
                    f"MOVA_PRESETS_{preset_name.upper()}_LLM_PROVIDER"
                )
                if llm_provider:
                    preset_config["llm_config"] = {
                        "provider": llm_provider,
                        "api_key": os.getenv(
                            f"MOVA_PRESETS_{preset_name.upper()}_LLM_API_KEY"
                        ),
                        "model": os.getenv(
                            f"MOVA_PRESETS_{preset_name.upper()}_LLM_MODEL"
                        )
                    }
                
                config["presets"][preset_name] = preset_config
    
    # Default preset
    default_preset = os.getenv("MOVA_DEFAULT_PRESET")
    if default_preset:
        config["default_preset"] = default_preset
    
    return config


def load_config(
    config_path: Optional[str] = None,
    env_file: Optional[str] = None,
    schema=None
) -> MOVAConfigSchema:
    """
    Load configuration from file or environment
    Завантажити конфігурацію з файлу або оточення
    
    Args:
        config_path: Optional path to configuration file /
        Необов'язковий шлях до файлу конфігурації
        env_file: Optional path to .env file /
        Необов'язковий шлях до .env файлу
        schema: Optional custom schema for validation /
        Необов'язкова користувацька схема для валідації
        
    Returns:
        MOVAConfigSchema: Loaded configuration / Завантажена конфігурація
    """
    # Load from .env file if provided
    if env_file:
        try:
            from dotenv import load_dotenv
            load_dotenv(env_file)
        except ImportError:
            print(
                "Warning: python-dotenv not installed, "
                "skipping .env file loading"
            )
    
    # Try to load from file first
    file_config = None
    if config_path and Path(config_path).exists():
        try:
            file_config = load_config_from_file(config_path)
            if schema:
                return schema(file_config.model_dump())
        except Exception as e:
            print(f"Warning: Failed to load config from file: {e}")
    
    # Load from environment
    env_config = load_config_from_env()
    
    # If we have both file and environment config, merge them
    if file_config and env_config:
        # Convert file config to dict for merging
        file_dict = file_config.model_dump()
        
        # Deep merge environment config over file config
        def deep_merge(base_dict, update_dict):
            result = base_dict.copy()
            for key, value in update_dict.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = deep_merge(result[key], value)
                else:
                    result[key] = value
            return result
        
        # Merge configs
        merged_dict = deep_merge(file_dict, env_config)
        
        if schema:
            return schema(merged_dict)
        return MOVAConfigSchema(**merged_dict)
    
    # If we have only file config
    if file_config:
        return file_config
    
    # If we have only environment config
    if env_config:
        if schema:
            return schema(env_config)
        return MOVAConfigSchema(**env_config)
    
    # Return default configuration
    if schema:
        return schema({})
    return MOVAConfigSchema()


# Global configuration instance
_global_config = None


def get_config_value(key: str, default=None):
    """
    Get configuration value from global configuration
    Отримати значення конфігурації з глобальної конфігурації
    
    Args:
        key: Configuration key / Ключ конфігурації
        default: Default value if key not found /
        Значення за замовчуванням, якщо ключ не знайдено
        
    Returns:
        Configuration value or default /
        Значення конфігурації або значення за замовчуванням
    """
    global _global_config
    
    if _global_config is None:
        try:
            _global_config = load_config()
        except Exception:
            _global_config = MOVAConfigSchema()
    
    # Navigate through nested keys using dot notation
    keys = key.split('.')
    value = _global_config
    
    try:
        for k in keys:
            if hasattr(value, k):
                value = getattr(value, k)
            elif isinstance(value, dict) and k in value:
                value = value[k]
            elif k.isdigit() and isinstance(value, list):
                # Handle array indices
                index = int(k)
                if 0 <= index < len(value):
                    value = value[index]
                else:
                    return default
            else:
                return default
        
        return value
    except (AttributeError, KeyError, IndexError, ValueError):
        return default