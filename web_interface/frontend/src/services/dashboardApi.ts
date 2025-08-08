import { api } from './api';
import {
  Dashboard,
  DashboardCreate,
  DashboardUpdate,
  DashboardList,
  Widget,
  WidgetCreate,
  WidgetUpdate,
  WidgetData,
  DashboardApiResponse
} from '../types/dashboard';

export class DashboardApiService {
  private baseUrl = '/api/dashboards';

  // Dashboard CRUD operations
  async getDashboards(page: number = 1, perPage: number = 10): Promise<DashboardList> {
    try {
      const response = await api.get<DashboardList>(this.baseUrl, {
        params: { page, per_page: perPage }
      });
      return response;
    } catch (error) {
      console.error('Error fetching dashboards:', error);
      throw error;
    }
  }

  async createDashboard(dashboardData: DashboardCreate): Promise<Dashboard> {
    try {
      const response = await api.post<Dashboard>(this.baseUrl, dashboardData);
      return response;
    } catch (error) {
      console.error('Error creating dashboard:', error);
      throw error;
    }
  }

  async getDashboard(dashboardId: string): Promise<Dashboard> {
    try {
      const response = await api.get<Dashboard>(`${this.baseUrl}/${dashboardId}`);
      return response;
    } catch (error) {
      console.error('Error fetching dashboard:', error);
      throw error;
    }
  }

  async updateDashboard(dashboardId: string, dashboardData: DashboardUpdate): Promise<Dashboard> {
    try {
      const response = await api.put<Dashboard>(`${this.baseUrl}/${dashboardId}`, dashboardData);
      return response;
    } catch (error) {
      console.error('Error updating dashboard:', error);
      throw error;
    }
  }

  async deleteDashboard(dashboardId: string): Promise<void> {
    try {
      await api.delete(`${this.baseUrl}/${dashboardId}`);
    } catch (error) {
      console.error('Error deleting dashboard:', error);
      throw error;
    }
  }

  // Widget operations
  async getDashboardWidgets(dashboardId: string): Promise<Widget[]> {
    try {
      const response = await api.get<Widget[]>(`${this.baseUrl}/${dashboardId}/widgets`);
      return response;
    } catch (error) {
      console.error('Error fetching dashboard widgets:', error);
      throw error;
    }
  }

  async addWidget(dashboardId: string, widgetData: WidgetCreate): Promise<Widget> {
    try {
      const response = await api.post<Widget>(`${this.baseUrl}/${dashboardId}/widgets`, widgetData);
      return response;
    } catch (error) {
      console.error('Error adding widget:', error);
      throw error;
    }
  }

  async updateWidget(dashboardId: string, widgetId: string, widgetData: WidgetUpdate): Promise<Widget> {
    try {
      const response = await api.put<Widget>(`${this.baseUrl}/${dashboardId}/widgets/${widgetId}`, widgetData);
      return response;
    } catch (error) {
      console.error('Error updating widget:', error);
      throw error;
    }
  }

  async deleteWidget(dashboardId: string, widgetId: string): Promise<void> {
    try {
      await api.delete(`${this.baseUrl}/${dashboardId}/widgets/${widgetId}`);
    } catch (error) {
      console.error('Error deleting widget:', error);
      throw error;
    }
  }

  // Widget data operations
  async getWidgetData(dashboardId: string, widgetId: string): Promise<WidgetData> {
    try {
      const response = await api.get<{ data: any }>(`${this.baseUrl}/${dashboardId}/widgets/${widgetId}/data`);
      return {
        widget_id: widgetId,
        data: response.data,
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      console.error('Error fetching widget data:', error);
      throw error;
    }
  }

  async updateWidgetData(dashboardId: string, widgetId: string, data: Record<string, any>): Promise<WidgetData> {
    try {
      const response = await api.post<WidgetData>(`${this.baseUrl}/${dashboardId}/widgets/${widgetId}/data`, data);
      return response;
    } catch (error) {
      console.error('Error updating widget data:', error);
      throw error;
    }
  }

  // Sample data for widget types
  async getSampleData(widgetType: string): Promise<Record<string, any>> {
    try {
      const response = await api.get<{ data: Record<string, any> }>(`${this.baseUrl}/widgets/sample-data/${widgetType}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching sample data:', error);
      // Return default sample data
      return this.getDefaultSampleData(widgetType);
    }
  }

  private getDefaultSampleData(widgetType: string): Record<string, any> {
    switch (widgetType) {
      case 'metric':
        return {
          value: 1234,
          change: 5.2,
          trend: 'up',
          unit: 'users'
        };
      case 'chart':
        return {
          labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
          datasets: [
            {
              label: 'Data',
              data: [12, 19, 3, 5, 2]
            }
          ]
        };
      case 'table':
        return {
          columns: ['Name', 'Value', 'Status'],
          rows: [
            ['Item 1', '100', 'Active'],
            ['Item 2', '200', 'Inactive'],
            ['Item 3', '150', 'Active']
          ]
        };
      default:
        return {
          message: 'Sample data not available for this widget type'
        };
    }
  }

  // Dashboard operations
  async duplicateDashboard(dashboardId: string, name?: string): Promise<Dashboard> {
    try {
      const response = await api.post<Dashboard>(`${this.baseUrl}/${dashboardId}/duplicate`, { name });
      return response;
    } catch (error) {
      console.error('Error duplicating dashboard:', error);
      throw error;
    }
  }

  async exportDashboard(dashboardId: string): Promise<Record<string, any>> {
    try {
      const response = await api.get<Record<string, any>>(`${this.baseUrl}/${dashboardId}/export`);
      return response;
    } catch (error) {
      console.error('Error exporting dashboard:', error);
      throw error;
    }
  }

  async importDashboard(exportData: Record<string, any>): Promise<Dashboard> {
    try {
      const response = await api.post<Dashboard>(`${this.baseUrl}/import`, exportData);
      return response;
    } catch (error) {
      console.error('Error importing dashboard:', error);
      throw error;
    }
  }

  // Search and filter operations
  async searchDashboards(query: string, page: number = 1, perPage: number = 10): Promise<DashboardList> {
    try {
      const response = await api.get<DashboardList>(this.baseUrl, {
        params: { search: query, page, per_page: perPage }
      });
      return response;
    } catch (error) {
      console.error('Error searching dashboards:', error);
      throw error;
    }
  }

  async getPublicDashboards(page: number = 1, perPage: number = 10): Promise<DashboardList> {
    try {
      const response = await api.get<DashboardList>(this.baseUrl, {
        params: { public: true, page, per_page: perPage }
      });
      return response;
    } catch (error) {
      console.error('Error fetching public dashboards:', error);
      throw error;
    }
  }

  // Batch operations
  async deleteMultipleDashboards(dashboardIds: string[]): Promise<void> {
    try {
      for (const dashboardId of dashboardIds) {
        await this.deleteDashboard(dashboardId);
      }
    } catch (error) {
      console.error('Error deleting multiple dashboards:', error);
      throw error;
    }
  }

  async duplicateMultipleDashboards(dashboardIds: string[]): Promise<Dashboard[]> {
    try {
      const dashboards: Dashboard[] = [];
      for (const dashboardId of dashboardIds) {
        const dashboard = await this.duplicateDashboard(dashboardId);
        dashboards.push(dashboard);
      }
      return dashboards;
    } catch (error) {
      console.error('Error duplicating multiple dashboards:', error);
      throw error;
    }
  }
}

// Export singleton instance
export const dashboardApi = new DashboardApiService(); 