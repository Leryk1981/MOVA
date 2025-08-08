import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import HTTPException, status
from loguru import logger

from app.models.plugins import (
    Plugin, PluginCreate, PluginUpdate, PluginList,
    PluginInstall, PluginConfigUpdate, PluginConfig,
    MarketplacePlugin, MarketplaceList,
    PluginStatus, PluginType, PluginCategory
)


class PluginService:
    def __init__(self):
        # In-memory storage (in real project this would be a database)
        self.plugins: Dict[str, Plugin] = {}
        self.marketplace_plugins: Dict[str, MarketplacePlugin] = {}
        self._initialize_marketplace()
        logger.info("Plugin service initialized")

    def _initialize_marketplace(self):
        """Initialize marketplace with sample plugins"""
        sample_plugins = [
            {
                "id": "analytics-dashboard",
                "name": "Analytics Dashboard",
                "description": "Advanced analytics and reporting dashboard",
                "version": "1.0.0",
                "author": "MOVA Team",
                "type": PluginType.ANALYTICS,
                "category": PluginCategory.ANALYTICS,
                "downloads": 1250,
                "rating": 4.8,
                "reviews": 45,
                "icon_url": "https://example.com/icons/analytics.png",
                "homepage_url": "https://example.com/analytics-dashboard",
                "repository_url": "https://github.com/mova/analytics-dashboard"
            },
            {
                "id": "data-export",
                "name": "Data Export",
                "description": "Export data in various formats (CSV, JSON, Excel)",
                "version": "1.2.0",
                "author": "MOVA Team",
                "type": PluginType.CUSTOM,
                "category": PluginCategory.UTILITIES,
                "downloads": 890,
                "rating": 4.6,
                "reviews": 32,
                "icon_url": "https://example.com/icons/export.png",
                "homepage_url": "https://example.com/data-export",
                "repository_url": "https://github.com/mova/data-export"
            },
            {
                "id": "slack-integration",
                "name": "Slack Integration",
                "description": "Send notifications and reports to Slack",
                "version": "1.1.0",
                "author": "MOVA Team",
                "type": PluginType.INTEGRATION,
                "category": PluginCategory.INTEGRATION,
                "downloads": 567,
                "rating": 4.4,
                "reviews": 28,
                "icon_url": "https://example.com/icons/slack.png",
                "homepage_url": "https://example.com/slack-integration",
                "repository_url": "https://github.com/mova/slack-integration"
            },
            {
                "id": "automated-reports",
                "name": "Automated Reports",
                "description": "Schedule and automate report generation",
                "version": "1.3.0",
                "author": "MOVA Team",
                "type": PluginType.AUTOMATION,
                "category": PluginCategory.AUTOMATION,
                "downloads": 432,
                "rating": 4.7,
                "reviews": 19,
                "icon_url": "https://example.com/icons/automation.png",
                "homepage_url": "https://example.com/automated-reports",
                "repository_url": "https://github.com/mova/automated-reports"
            }
        ]

        for plugin_data in sample_plugins:
            marketplace_plugin = MarketplacePlugin(**plugin_data)
            self.marketplace_plugins[plugin_data["id"]] = marketplace_plugin

    def get_plugins(self, user_id: str, page: int = 1, per_page: int = 10) -> PluginList:
        """Get user plugins list"""
        user_plugins = [
            plugin for plugin in self.plugins.values()
            if plugin.id in self.plugins  # In real app, filter by user_id
        ]
        
        # Pagination
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_plugins = user_plugins[start_idx:end_idx]
        
        return PluginList(
            plugins=paginated_plugins,
            total=len(user_plugins),
            page=page,
            per_page=per_page
        )

    def get_plugin(self, plugin_id: str, user_id: str) -> Plugin:
        """Get plugin by ID"""
        if plugin_id not in self.plugins:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plugin not found"
            )
        
        return self.plugins[plugin_id]

    def install_plugin(self, plugin_data: PluginInstall, user_id: str) -> Plugin:
        """Install plugin from marketplace"""
        plugin_id = plugin_data.plugin_id
        
        if plugin_id not in self.marketplace_plugins:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plugin not found in marketplace"
            )
        
        if plugin_id in self.plugins:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Plugin already installed"
            )
        
        marketplace_plugin = self.marketplace_plugins[plugin_id]
        
        # Create plugin instance
        plugin = Plugin(
            id=plugin_id,
            name=marketplace_plugin.name,
            description=marketplace_plugin.description,
            version=marketplace_plugin.version,
            author=marketplace_plugin.author,
            type=marketplace_plugin.type,
            category=marketplace_plugin.category,
            status=PluginStatus.INSTALLED,
            config=[],
            dependencies=[],
            permissions=[],
            icon_url=marketplace_plugin.icon_url,
            homepage_url=marketplace_plugin.homepage_url,
            repository_url=marketplace_plugin.repository_url,
            install_date=datetime.now(),
            last_updated=datetime.now(),
            is_custom=False
        )
        
        self.plugins[plugin_id] = plugin
        
        # Update marketplace plugin
        marketplace_plugin.is_installed = True
        marketplace_plugin.downloads += 1
        
        logger.info(f"Installed plugin {plugin_id} for user {user_id}")
        return plugin

    def uninstall_plugin(self, plugin_id: str, user_id: str) -> bool:
        """Uninstall plugin"""
        if plugin_id not in self.plugins:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plugin not found"
            )
        
        del self.plugins[plugin_id]
        
        # Update marketplace plugin
        if plugin_id in self.marketplace_plugins:
            self.marketplace_plugins[plugin_id].is_installed = False
        
        logger.info(f"Uninstalled plugin {plugin_id} for user {user_id}")
        return True

    def update_plugin(self, plugin_id: str, plugin_data: PluginUpdate, user_id: str) -> Plugin:
        """Update plugin"""
        if plugin_id not in self.plugins:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plugin not found"
            )
        
        plugin = self.plugins[plugin_id]
        
        # Update fields
        if plugin_data.name is not None:
            plugin.name = plugin_data.name
        if plugin_data.description is not None:
            plugin.description = plugin_data.description
        if plugin_data.status is not None:
            plugin.status = plugin_data.status
        if plugin_data.config is not None:
            plugin.config = plugin_data.config
        
        plugin.last_updated = datetime.now()
        
        logger.info(f"Updated plugin {plugin_id}")
        return plugin

    def configure_plugin(self, plugin_id: str, config_data: PluginConfigUpdate, user_id: str) -> Plugin:
        """Configure plugin"""
        if plugin_id not in self.plugins:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plugin not found"
            )
        
        plugin = self.plugins[plugin_id]
        
        # Update configuration
        for config_item in plugin.config:
            if config_item.name in config_data.config:
                config_item.value = config_data.config[config_item.name]
        
        plugin.last_updated = datetime.now()
        
        logger.info(f"Configured plugin {plugin_id}")
        return plugin

    def get_marketplace(self, page: int = 1, per_page: int = 10, 
                       category: Optional[str] = None, 
                       search: Optional[str] = None) -> MarketplaceList:
        """Get marketplace plugins"""
        plugins = list(self.marketplace_plugins.values())
        
        # Apply filters
        if category:
            plugins = [p for p in plugins if p.category.value == category]
        
        if search:
            search_lower = search.lower()
            plugins = [p for p in plugins if 
                      search_lower in p.name.lower() or 
                      search_lower in p.description.lower()]
        
        # Pagination
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_plugins = plugins[start_idx:end_idx]
        
        # Get available categories
        categories = list(set(p.category.value for p in self.marketplace_plugins.values()))
        
        return MarketplaceList(
            plugins=paginated_plugins,
            total=len(plugins),
            page=page,
            per_page=per_page,
            categories=categories,
            filters={
                "category": category,
                "search": search
            }
        )

    def upload_custom_plugin(self, plugin_data: PluginCreate, user_id: str) -> Plugin:
        """Upload custom plugin"""
        plugin_id = str(uuid.uuid4())
        
        plugin = Plugin(
            id=plugin_id,
            name=plugin_data.name,
            description=plugin_data.description,
            version=plugin_data.version,
            author=plugin_data.author,
            type=plugin_data.type,
            category=plugin_data.category,
            status=PluginStatus.INSTALLED,
            config=plugin_data.config or [],
            dependencies=plugin_data.dependencies or [],
            permissions=plugin_data.permissions or [],
            icon_url=plugin_data.icon_url,
            homepage_url=plugin_data.homepage_url,
            repository_url=plugin_data.repository_url,
            install_date=datetime.now(),
            last_updated=datetime.now(),
            is_custom=True
        )
        
        self.plugins[plugin_id] = plugin
        
        logger.info(f"Uploaded custom plugin {plugin_id} for user {user_id}")
        return plugin

    def get_plugin_status(self, plugin_id: str, user_id: str) -> Dict[str, Any]:
        """Get plugin status and health"""
        if plugin_id not in self.plugins:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plugin not found"
            )
        
        plugin = self.plugins[plugin_id]
        
        return {
            "plugin_id": plugin_id,
            "status": plugin.status,
            "is_enabled": plugin.status == PluginStatus.ENABLED,
            "last_updated": plugin.last_updated,
            "health": "healthy",  # In real app, check actual health
            "version": plugin.version,
            "dependencies_met": True  # In real app, check dependencies
        }

    def enable_plugin(self, plugin_id: str, user_id: str) -> Plugin:
        """Enable plugin"""
        if plugin_id not in self.plugins:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plugin not found"
            )
        
        plugin = self.plugins[plugin_id]
        plugin.status = PluginStatus.ENABLED
        plugin.last_updated = datetime.now()
        
        logger.info(f"Enabled plugin {plugin_id}")
        return plugin

    def disable_plugin(self, plugin_id: str, user_id: str) -> Plugin:
        """Disable plugin"""
        if plugin_id not in self.plugins:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plugin not found"
            )
        
        plugin = self.plugins[plugin_id]
        plugin.status = PluginStatus.DISABLED
        plugin.last_updated = datetime.now()
        
        logger.info(f"Disabled plugin {plugin_id}")
        return plugin


# Global service instance
plugin_service = PluginService() 