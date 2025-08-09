"""
Configuration schemas for MOVA SDK
Схеми конфігурації для MOVA SDK
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class LLMProvider(str, Enum):
    """LLM provider options / Опції провайдера LLM"""
    OPENROUTER = "openrouter"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"
    CUSTOM = "custom"


class LLMConfig(BaseModel):
    """LLM configuration / Конфігурація LLM"""
    provider: LLMProvider = Field(
        default=LLMProvider.OPENROUTER,
        description="LLM provider"
    )
    api_key: Optional[str] = Field(
        default=None,
        description="API key"
    )
    api_key_env: str = Field(
        default="OPENROUTER_API_KEY",
        description="Environment variable for API key"
    )
    base_url: str = Field(
        default="https://openrouter.ai/api/v1",
        description="Base URL for API"
    )
    model: Optional[str] = Field(
        default=None,
        description="Model to use"
    )
    default_model: str = Field(
        default="openrouter/anthropic/claude-3-haiku",
        description="Default model to use"
    )
    max_tokens: Optional[int] = Field(
        default=None,
        description="Maximum tokens to generate"
    )
    temperature: Optional[float] = Field(
        default=None,
        description="Sampling temperature"
    )


class PresetProfile(BaseModel):
    """Preset profile configuration / Конфігурація профілю пресету"""
    name: str = Field(description="Preset name")
    description: Optional[str] = Field(
        default=None,
        description="Preset description"
    )
    llm_config: Optional[LLMConfig] = Field(
        default=None,
        description="LLM configuration"
    )
    model: str = Field(description="Model identifier")
    temperature: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        description="Sampling temperature"
    )
    max_tokens: int = Field(
        default=1024,
        description="Maximum tokens to generate"
    )
    system_prompt: Optional[str] = Field(
        default=None,
        description="System message"
    )
    tools: Optional[List[str]] = Field(
        default=None,
        description="Allowed tools for this preset"
    )


class ToolPolicy(BaseModel):
    """Tool policy configuration / Конфігурація політики інструменту"""
    default_action: str = Field(
        default="block",
        description="Default action for tools"
    )
    allowed_tools: Optional[List[str]] = Field(
        default=None,
        description="List of allowed tools"
    )
    blocked_tools: Optional[List[str]] = Field(
        default=None,
        description="List of blocked tools"
    )
    require_confirmation: Optional[List[str]] = Field(
        default=None,
        description="Tools requiring confirmation"
    )
    allow_models: List[str] = Field(
        default=["*"],
        description="Allowed models for this tool"
    )
    rate_limit_per_min: int = Field(
        default=60,
        description="Rate limit per minute"
    )


class ToolSchema(BaseModel):
    """Tool schema configuration / Конфігурація схеми інструменту"""
    name: str = Field(description="Tool name")
    description: str = Field(description="Tool description")
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Tool parameters"
    )
    schema_def: Dict[str, Any] = Field(
        alias="schema",
        description="Tool JSON schema"
    )
    policy: Optional[ToolPolicy] = Field(
        default=None,
        description="Tool policy"
    )


class MOVAConfigSchema(BaseModel):
    """Main MOVA configuration schema / Основна схема конфігурації MOVA"""
    llm: LLMConfig = Field(
        default_factory=LLMConfig,
        description="LLM configuration"
    )
    presets: Dict[str, PresetProfile] = Field(
        default_factory=dict,
        description="Preset profiles"
    )
    default_preset: str = Field(
        default="general",
        description="Default preset name"
    )
    tool_policy: ToolPolicy = Field(
        default_factory=ToolPolicy,
        description="Tool policy"
    )
    tools: List[ToolSchema] = Field(
        default_factory=list,
        description="Tool schemas"
    )
    cache: Dict[str, Any] = Field(
        default_factory=lambda: {"enabled": True, "ttl": 3600},
        description="Cache configuration"
    )
    redis: Dict[str, Any] = Field(
        default_factory=lambda: {
            "enabled": False,
            "url": "redis://localhost:6379"
        },
        description="Redis configuration"
    )
    webhook: Dict[str, Any] = Field(
        default_factory=lambda: {
            "enabled": False,
            "endpoints": []
        },
        description="Webhook configuration"
    )