from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from loguru import logger

from app.models.dashboards import (
    Dashboard, DashboardCreate, DashboardUpdate, DashboardList,
    Widget, WidgetCreate, WidgetUpdate, WidgetData,
    WidgetType
)
from app.services.dashboard_service import dashboard_service
from app.api.auth import get_current_user
# User is returned as dict from get_current_user function

router = APIRouter(prefix="/dashboards", tags=["dashboards"])


@router.get("/", response_model=DashboardList)
async def get_dashboards(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    current_user: dict = Depends(get_current_user)
):
    """Get user dashboards list"""
    try:
        return dashboard_service.get_user_dashboards(
            user_id=current_user["id"],
            page=page,
            per_page=per_page
        )
    except Exception as e:
        logger.error(f"Error getting dashboards: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/", response_model=Dashboard)
async def create_dashboard(
    dashboard_data: DashboardCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create new dashboard"""
    try:
        return dashboard_service.create_dashboard(
            dashboard_data=dashboard_data,
            user_id=current_user["id"]
        )
    except Exception as e:
        logger.error(f"Error creating dashboard: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/{dashboard_id}", response_model=Dashboard)
async def get_dashboard(
    dashboard_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get dashboard by ID"""
    try:
        return dashboard_service.get_dashboard(
            dashboard_id=dashboard_id,
            user_id=current_user["id"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting dashboard {dashboard_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.put("/{dashboard_id}", response_model=Dashboard)
async def update_dashboard(
    dashboard_id: str,
    dashboard_data: DashboardUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update dashboard"""
    try:
        return dashboard_service.update_dashboard(
            dashboard_id=dashboard_id,
            dashboard_data=dashboard_data,
            user_id=current_user["id"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating dashboard {dashboard_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete("/{dashboard_id}")
async def delete_dashboard(
    dashboard_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete dashboard"""
    try:
        dashboard_service.delete_dashboard(
            dashboard_id=dashboard_id,
            user_id=current_user["id"]
        )
        return {"message": "Dashboard deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting dashboard {dashboard_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/{dashboard_id}/widgets", response_model=List[Widget])
async def get_dashboard_widgets(
    dashboard_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get dashboard widgets"""
    try:
        dashboard = dashboard_service.get_dashboard(
            dashboard_id=dashboard_id,
            user_id=current_user["id"]
        )
        return dashboard.widgets
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error getting widgets for dashboard {dashboard_id}: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/{dashboard_id}/widgets", response_model=Widget)
async def add_widget(
    dashboard_id: str,
    widget_data: WidgetCreate,
    current_user: dict = Depends(get_current_user)
):
    """Add widget to dashboard"""
    try:
        return dashboard_service.add_widget(
            dashboard_id=dashboard_id,
            widget_data=widget_data,
            user_id=current_user["id"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding widget to dashboard {dashboard_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.put("/{dashboard_id}/widgets/{widget_id}", response_model=Widget)
async def update_widget(
    dashboard_id: str,
    widget_id: str,
    widget_data: WidgetUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update widget"""
    try:
        return dashboard_service.update_widget(
            dashboard_id=dashboard_id,
            widget_id=widget_id,
            widget_data=widget_data,
            user_id=current_user["id"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating widget {widget_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete("/{dashboard_id}/widgets/{widget_id}")
async def delete_widget(
    dashboard_id: str,
    widget_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete widget"""
    try:
        dashboard_service.delete_widget(
            dashboard_id=dashboard_id,
            widget_id=widget_id,
            user_id=current_user["id"]
        )
        return {"message": "Widget deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting widget {widget_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/{dashboard_id}/widgets/{widget_id}/data")
async def get_widget_data(
    dashboard_id: str,
    widget_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get widget data"""
    try:
        data = dashboard_service.get_widget_data(
            dashboard_id=dashboard_id,
            widget_id=widget_id,
            user_id=current_user["id"]
        )
        return {"data": data}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting widget data for {widget_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post(
    "/{dashboard_id}/widgets/{widget_id}/data",
    response_model=WidgetData
)
async def update_widget_data(
    dashboard_id: str,
    widget_id: str,
    data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Update widget data"""
    try:
        return dashboard_service.update_widget_data(
            dashboard_id=dashboard_id,
            widget_id=widget_id,
            data=data,
            user_id=current_user["id"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating widget data for {widget_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/widgets/sample-data/{widget_type}")
async def get_sample_data(widget_type: WidgetType):
    """Get sample data for widget"""
    try:
        data = dashboard_service.get_sample_data(widget_type=widget_type)
        return {"data": data}
    except Exception as e:
        logger.error(f"Error getting sample data for {widget_type}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) 