from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class PluginStatus(str, Enum):
    INSTALLED = "installed"
    ENABLED = "enabled"
    DISABLED = "disabled"
    ERROR = "error"
    UPDATING = "updating"


class PluginType(str, Enum):
    WIDGET = "widget"
    INTEGRATION = "integration"
    ANALYTICS = "analytics"
    AUTOMATION = "automation"
    CUSTOM = "custom"


class PluginCategory(str, Enum):
    PRODUCTIVITY = "productivity"
    ANALYTICS = "analytics"
    INTEGRATION = "integration"
    AUTOMATION = "automation"
    UTILITIES = "utilities"
    CUSTOM = "custom"


class PluginVersion(BaseModel):
    version: str = Field(..., description="Plugin version")
    release_date: datetime = Field(..., description="Release date")
    changelog: Optional[str] = Field(None, description="Changelog")
    compatibility: List[str] = Field(default_factory=list, description="Compatible versions")


class PluginConfig(BaseModel):
    name: str = Field(..., description="Configuration name")
    type: str = Field(..., description="Configuration type")
    value: Any = Field(..., description="Configuration value")
    required: bool = Field(default=False, description="Required configuration")
    description: Optional[str] = Field(None, description="Configuration description")


class Plugin(BaseModel):
    id: str = Field(..., description="Unique plugin ID")
    name: str = Field(..., description="Plugin name")
    description: Optional[str] = Field(None, description="Plugin description")
    version: str = Field(..., description="Plugin version")
    author: str = Field(..., description="Plugin author")
    type: PluginType = Field(..., description="Plugin type")
    category: PluginCategory = Field(..., description="Plugin category")
    status: PluginStatus = Field(default=PluginStatus.INSTALLED, description="Plugin status")
    config: List[PluginConfig] = Field(default_factory=list, description="Plugin configuration")
    dependencies: List[str] = Field(default_factory=list, description="Plugin dependencies")
    permissions: List[str] = Field(default_factory=list, description="Required permissions")
    icon_url: Optional[str] = Field(None, description="Plugin icon URL")
    homepage_url: Optional[str] = Field(None, description="Plugin homepage URL")
    repository_url: Optional[str] = Field(None, description="Plugin repository URL")
    install_date: datetime = Field(default_factory=datetime.now, description="Install date")
    last_updated: datetime = Field(default_factory=datetime.now, description="Last updated")
    is_custom: bool = Field(default=False, description="Custom plugin")


class PluginCreate(BaseModel):
    name: str = Field(..., description="Plugin name")
    description: Optional[str] = Field(None, description="Plugin description")
    version: str = Field(..., description="Plugin version")
    author: str = Field(..., description="Plugin author")
    type: PluginType = Field(..., description="Plugin type")
    category: PluginCategory = Field(..., description="Plugin category")
    config: Optional[List[PluginConfig]] = Field(None, description="Plugin configuration")
    dependencies: Optional[List[str]] = Field(None, description="Plugin dependencies")
    permissions: Optional[List[str]] = Field(None, description="Required permissions")
    icon_url: Optional[str] = Field(None, description="Plugin icon URL")
    homepage_url: Optional[str] = Field(None, description="Plugin homepage URL")
    repository_url: Optional[str] = Field(None, description="Plugin repository URL")


class PluginUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Plugin name")
    description: Optional[str] = Field(None, description="Plugin description")
    status: Optional[PluginStatus] = Field(None, description="Plugin status")
    config: Optional[List[PluginConfig]] = Field(None, description="Plugin configuration")


class PluginInstall(BaseModel):
    plugin_id: str = Field(..., description="Plugin ID to install")
    config: Optional[Dict[str, Any]] = Field(None, description="Installation configuration")


class PluginConfigUpdate(BaseModel):
    config: Dict[str, Any] = Field(..., description="Plugin configuration")


class PluginList(BaseModel):
    plugins: List[Plugin] = Field(..., description="Plugin list")
    total: int = Field(..., description="Total count")
    page: int = Field(..., description="Page number")
    per_page: int = Field(..., description="Items per page")


class MarketplacePlugin(BaseModel):
    id: str = Field(..., description="Plugin ID")
    name: str = Field(..., description="Plugin name")
    description: Optional[str] = Field(None, description="Plugin description")
    version: str = Field(..., description="Plugin version")
    author: str = Field(..., description="Plugin author")
    type: PluginType = Field(..., description="Plugin type")
    category: PluginCategory = Field(..., description="Plugin category")
    downloads: int = Field(default=0, description="Download count")
    rating: float = Field(default=0.0, description="Plugin rating")
    reviews: int = Field(default=0, description="Review count")
    icon_url: Optional[str] = Field(None, description="Plugin icon URL")
    homepage_url: Optional[str] = Field(None, description="Plugin homepage URL")
    repository_url: Optional[str] = Field(None, description="Plugin repository URL")
    is_installed: bool = Field(default=False, description="Is plugin installed")
    is_compatible: bool = Field(default=True, description="Is plugin compatible")


class MarketplaceList(BaseModel):
    plugins: List[MarketplacePlugin] = Field(..., description="Marketplace plugin list")
    total: int = Field(..., description="Total count")
    page: int = Field(..., description="Page number")
    per_page: int = Field(..., description="Items per page")
    categories: List[str] = Field(..., description="Available categories")
    filters: Dict[str, Any] = Field(..., description="Applied filters") 