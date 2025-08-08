from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class WidgetType(str, Enum):
    METRIC = "metric"
    CHART = "chart"
    TABLE = "table"
    TEXT = "text"
    IMAGE = "image"
    CUSTOM = "custom"


class ChartType(str, Enum):
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    AREA = "area"
    SCATTER = "scatter"


class WidgetPosition(BaseModel):
    x: int = Field(ge=0, description="X coordinate")
    y: int = Field(ge=0, description="Y coordinate")
    w: int = Field(ge=1, le=12, description="Width (1-12)")
    h: int = Field(ge=1, le=12, description="Height (1-12)")


class WidgetConfig(BaseModel):
    title: str = Field(..., description="Widget title")
    description: Optional[str] = Field(None, description="Widget description")
    data_source: Optional[str] = Field(None, description="Data source")
    refresh_interval: Optional[int] = Field(None, description="Refresh interval (seconds)")
    chart_type: Optional[ChartType] = Field(None, description="Chart type")
    custom_config: Optional[Dict[str, Any]] = Field(None, description="Custom configuration")


class Widget(BaseModel):
    id: str = Field(..., description="Unique widget ID")
    type: WidgetType = Field(..., description="Widget type")
    position: WidgetPosition = Field(..., description="Position and size")
    config: WidgetConfig = Field(..., description="Widget configuration")
    data: Optional[Dict[str, Any]] = Field(None, description="Widget data")
    created_at: datetime = Field(default_factory=datetime.now, description="Created at")
    updated_at: datetime = Field(default_factory=datetime.now, description="Updated at")


class Dashboard(BaseModel):
    id: str = Field(..., description="Unique dashboard ID")
    name: str = Field(..., description="Dashboard name")
    description: Optional[str] = Field(None, description="Dashboard description")
    user_id: str = Field(..., description="User ID")
    widgets: List[Widget] = Field(default_factory=list, description="Widget list")
    layout: Dict[str, Any] = Field(default_factory=dict, description="Layout settings")
    is_public: bool = Field(default=False, description="Public dashboard")
    created_at: datetime = Field(default_factory=datetime.now, description="Created at")
    updated_at: datetime = Field(default_factory=datetime.now, description="Updated at")


class DashboardCreate(BaseModel):
    name: str = Field(..., description="Dashboard name")
    description: Optional[str] = Field(None, description="Dashboard description")
    is_public: bool = Field(default=False, description="Public dashboard")


class DashboardUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Dashboard name")
    description: Optional[str] = Field(None, description="Dashboard description")
    is_public: Optional[bool] = Field(None, description="Public dashboard")
    layout: Optional[Dict[str, Any]] = Field(None, description="Layout settings")


class WidgetCreate(BaseModel):
    type: WidgetType = Field(..., description="Widget type")
    position: WidgetPosition = Field(..., description="Position and size")
    config: WidgetConfig = Field(..., description="Widget configuration")


class WidgetUpdate(BaseModel):
    position: Optional[WidgetPosition] = Field(None, description="Position and size")
    config: Optional[WidgetConfig] = Field(None, description="Widget configuration")


class DashboardList(BaseModel):
    dashboards: List[Dashboard] = Field(..., description="Dashboard list")
    total: int = Field(..., description="Total count")
    page: int = Field(..., description="Page number")
    per_page: int = Field(..., description="Items per page")


class WidgetData(BaseModel):
    widget_id: str = Field(..., description="Widget ID")
    data: Dict[str, Any] = Field(..., description="Widget data")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp") 