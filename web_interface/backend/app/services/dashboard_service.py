import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import HTTPException, status
from loguru import logger

from app.models.dashboards import (
    Dashboard, DashboardCreate, DashboardUpdate, DashboardList,
    Widget, WidgetCreate, WidgetUpdate, WidgetData,
    WidgetType, ChartType
)


class DashboardService:
    def __init__(self):
        # In-memory storage (in real project this would be a database)
        self.dashboards: Dict[str, Dashboard] = {}
        self.widget_data: Dict[str, List[WidgetData]] = {}
        logger.info("Dashboard service initialized")

    def create_dashboard(self, dashboard_data: DashboardCreate, user_id: str) -> Dashboard:
        """Create new dashboard"""
        dashboard_id = str(uuid.uuid4())
        
        dashboard = Dashboard(
            id=dashboard_id,
            user_id=user_id,
            name=dashboard_data.name,
            description=dashboard_data.description,
            is_public=dashboard_data.is_public,
            widgets=[],
            layout={},
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.dashboards[dashboard_id] = dashboard
        logger.info(f"Created dashboard {dashboard_id} for user {user_id}")
        return dashboard

    def get_dashboard(self, dashboard_id: str, user_id: str) -> Dashboard:
        """Get dashboard by ID"""
        if dashboard_id not in self.dashboards:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dashboard not found"
            )
        
        dashboard = self.dashboards[dashboard_id]
        
        # Check access
        if not dashboard.is_public and dashboard.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        return dashboard

    def get_user_dashboards(self, user_id: str, page: int = 1, per_page: int = 10) -> DashboardList:
        """Get user dashboards list"""
        user_dashboards = [
            dashboard for dashboard in self.dashboards.values()
            if dashboard.user_id == user_id or dashboard.is_public
        ]
        
        # Pagination
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_dashboards = user_dashboards[start_idx:end_idx]
        
        return DashboardList(
            dashboards=paginated_dashboards,
            total=len(user_dashboards),
            page=page,
            per_page=per_page
        )

    def update_dashboard(self, dashboard_id: str, dashboard_data: DashboardUpdate, user_id: str) -> Dashboard:
        """Update dashboard"""
        dashboard = self.get_dashboard(dashboard_id, user_id)
        
        # Check ownership
        if dashboard.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only owner can update dashboard"
            )
        
        # Update fields
        if dashboard_data.name is not None:
            dashboard.name = dashboard_data.name
        if dashboard_data.description is not None:
            dashboard.description = dashboard_data.description
        if dashboard_data.is_public is not None:
            dashboard.is_public = dashboard_data.is_public
        if dashboard_data.layout is not None:
            dashboard.layout = dashboard_data.layout
        
        dashboard.updated_at = datetime.now()
        
        logger.info(f"Updated dashboard {dashboard_id}")
        return dashboard

    def delete_dashboard(self, dashboard_id: str, user_id: str) -> bool:
        """Delete dashboard"""
        dashboard = self.get_dashboard(dashboard_id, user_id)
        
        # Check ownership
        if dashboard.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only owner can delete dashboard"
            )
        
        del self.dashboards[dashboard_id]
        
        # Delete widget data
        if dashboard_id in self.widget_data:
            del self.widget_data[dashboard_id]
        
        logger.info(f"Deleted dashboard {dashboard_id}")
        return True

    def add_widget(self, dashboard_id: str, widget_data: WidgetCreate, user_id: str) -> Widget:
        """Add widget to dashboard"""
        dashboard = self.get_dashboard(dashboard_id, user_id)
        
        # Check ownership
        if dashboard.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only owner can add widgets"
            )
        
        widget_id = str(uuid.uuid4())
        widget = Widget(
            id=widget_id,
            type=widget_data.type,
            position=widget_data.position,
            config=widget_data.config,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        dashboard.widgets.append(widget)
        dashboard.updated_at = datetime.now()
        
        logger.info(f"Added widget {widget_id} to dashboard {dashboard_id}")
        return widget

    def update_widget(self, dashboard_id: str, widget_id: str, widget_data: WidgetUpdate, user_id: str) -> Widget:
        """Update widget"""
        dashboard = self.get_dashboard(dashboard_id, user_id)
        
        # Check ownership
        if dashboard.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only owner can update widgets"
            )
        
        # Find widget
        widget = None
        for w in dashboard.widgets:
            if w.id == widget_id:
                widget = w
                break
        
        if not widget:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Widget not found"
            )
        
        # Update fields
        if widget_data.position is not None:
            widget.position = widget_data.position
        if widget_data.config is not None:
            widget.config = widget_data.config
        
        widget.updated_at = datetime.now()
        dashboard.updated_at = datetime.now()
        
        logger.info(f"Updated widget {widget_id} in dashboard {dashboard_id}")
        return widget

    def delete_widget(self, dashboard_id: str, widget_id: str, user_id: str) -> bool:
        """Delete widget"""
        dashboard = self.get_dashboard(dashboard_id, user_id)
        
        # Check ownership
        if dashboard.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only owner can delete widgets"
            )
        
        # Find and delete widget
        widget_found = False
        for i, widget in enumerate(dashboard.widgets):
            if widget.id == widget_id:
                del dashboard.widgets[i]
                widget_found = True
                break
        
        if not widget_found:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Widget not found"
            )
        
        dashboard.updated_at = datetime.now()
        
        logger.info(f"Deleted widget {widget_id} from dashboard {dashboard_id}")
        return True

    def get_widget_data(self, dashboard_id: str, widget_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get widget data"""
        dashboard = self.get_dashboard(dashboard_id, user_id)
        
        # Find widget
        widget = None
        for w in dashboard.widgets:
            if w.id == widget_id:
                widget = w
                break
        
        if not widget:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Widget not found"
            )
        
        # Return latest widget data
        if dashboard_id in self.widget_data:
            for data in reversed(self.widget_data[dashboard_id]):
                if data.widget_id == widget_id:
                    return data.data
        
        return widget.data

    def update_widget_data(self, dashboard_id: str, widget_id: str, data: Dict[str, Any], user_id: str) -> WidgetData:
        """Update widget data"""
        dashboard = self.get_dashboard(dashboard_id, user_id)
        
        # Find widget
        widget = None
        for w in dashboard.widgets:
            if w.id == widget_id:
                widget = w
                break
        
        if not widget:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Widget not found"
            )
        
        # Create data record
        widget_data = WidgetData(
            widget_id=widget_id,
            data=data,
            timestamp=datetime.now()
        )
        
        # Save data
        if dashboard_id not in self.widget_data:
            self.widget_data[dashboard_id] = []
        
        self.widget_data[dashboard_id].append(widget_data)
        
        # Limit data history (last 100 records)
        if len(self.widget_data[dashboard_id]) > 100:
            self.widget_data[dashboard_id] = self.widget_data[dashboard_id][-100:]
        
        logger.info(f"Updated data for widget {widget_id} in dashboard {dashboard_id}")
        return widget_data

    def get_sample_data(self, widget_type: WidgetType) -> Dict[str, Any]:
        """Get sample data for widget"""
        if widget_type == WidgetType.METRIC:
            return {
                "value": 1234,
                "change": 5.2,
                "trend": "up"
            }
        elif widget_type == WidgetType.CHART:
            return {
                "labels": ["Jan", "Feb", "Mar", "Apr", "May"],
                "datasets": [
                    {
                        "label": "Sales",
                        "data": [12, 19, 3, 5, 2]
                    }
                ]
            }
        elif widget_type == WidgetType.TABLE:
            return {
                "headers": ["Name", "Value", "Status"],
                "rows": [
                    ["Item 1", "100", "Active"],
                    ["Item 2", "200", "Inactive"],
                    ["Item 3", "150", "Active"]
                ]
            }
        elif widget_type == WidgetType.TEXT:
            return {
                "content": "Sample text content for the widget"
            }
        else:
            return {
                "message": "Sample data for custom widget"
            }


# Global service instance
dashboard_service = DashboardService() 