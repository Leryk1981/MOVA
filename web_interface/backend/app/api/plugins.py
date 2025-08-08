from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from loguru import logger

from app.models.plugins import (
    Plugin, PluginCreate, PluginUpdate, PluginList,
    PluginInstall, PluginConfigUpdate,
    MarketplaceList
)
from app.services.plugin_service import plugin_service
from app.api.auth import get_current_user
# User is returned as dict from get_current_user function

router = APIRouter(prefix="/api/plugins", tags=["plugins"])


@router.get("/", response_model=PluginList)
async def get_plugins(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    current_user: dict = Depends(get_current_user)
):
    """Get user plugins list"""
    try:
        return plugin_service.get_plugins(
            user_id=current_user["id"],
            page=page,
            per_page=per_page
        )
    except Exception as e:
        logger.error(f"Error getting plugins: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/{plugin_id}", response_model=Plugin)
async def get_plugin(
    plugin_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get plugin by ID"""
    try:
        return plugin_service.get_plugin(
            plugin_id=plugin_id,
            user_id=current_user["id"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting plugin {plugin_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/install", response_model=Plugin)
async def install_plugin(
    plugin_data: PluginInstall,
    current_user: dict = Depends(get_current_user)
):
    """Install plugin from marketplace"""
    try:
        return plugin_service.install_plugin(
            plugin_data=plugin_data,
            user_id=current_user["id"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error installing plugin: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete("/{plugin_id}")
async def uninstall_plugin(
    plugin_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Uninstall plugin"""
    try:
        success = plugin_service.uninstall_plugin(
            plugin_id=plugin_id,
            user_id=current_user["id"]
        )
        return {"message": "Plugin uninstalled successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uninstalling plugin {plugin_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.put("/{plugin_id}", response_model=Plugin)
async def update_plugin(
    plugin_id: str,
    plugin_data: PluginUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update plugin"""
    try:
        return plugin_service.update_plugin(
            plugin_id=plugin_id,
            plugin_data=plugin_data,
            user_id=current_user["id"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating plugin {plugin_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.put("/{plugin_id}/config", response_model=Plugin)
async def configure_plugin(
    plugin_id: str,
    config_data: PluginConfigUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Configure plugin"""
    try:
        return plugin_service.configure_plugin(
            plugin_id=plugin_id,
            config_data=config_data,
            user_id=current_user["id"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error configuring plugin {plugin_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/marketplace", response_model=MarketplaceList)
async def get_marketplace(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search query"),
    current_user: dict = Depends(get_current_user)
):
    """Get plugin marketplace"""
    try:
        return plugin_service.get_marketplace(
            page=page,
            per_page=per_page,
            category=category,
            search=search
        )
    except Exception as e:
        logger.error(f"Error getting marketplace: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/upload", response_model=Plugin)
async def upload_custom_plugin(
    plugin_data: PluginCreate,
    current_user: dict = Depends(get_current_user)
):
    """Upload custom plugin"""
    try:
        return plugin_service.upload_custom_plugin(
            plugin_data=plugin_data,
            user_id=current_user["id"]
        )
    except Exception as e:
        logger.error(f"Error uploading custom plugin: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/{plugin_id}/status")
async def get_plugin_status(
    plugin_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get plugin status and health"""
    try:
        return plugin_service.get_plugin_status(
            plugin_id=plugin_id,
            user_id=current_user["id"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting plugin status {plugin_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/{plugin_id}/enable", response_model=Plugin)
async def enable_plugin(
    plugin_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Enable plugin"""
    try:
        return plugin_service.enable_plugin(
            plugin_id=plugin_id,
            user_id=current_user["id"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error enabling plugin {plugin_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/{plugin_id}/disable", response_model=Plugin)
async def disable_plugin(
    plugin_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Disable plugin"""
    try:
        return plugin_service.disable_plugin(
            plugin_id=plugin_id,
            user_id=current_user["id"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error disabling plugin {plugin_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) 