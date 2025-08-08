import { api } from './api';
import {
  Plugin,
  PluginCreate,
  PluginUpdate,
  PluginList,
  PluginInstall,
  PluginConfigUpdate,
  MarketplaceList,
  PluginApiResponse
} from '../types/plugin';

export class PluginApiService {
  private baseUrl = '/api/plugins';

  // Plugin CRUD operations
  async getPlugins(page: number = 1, perPage: number = 10): Promise<PluginList> {
    try {
      const response = await api.get<PluginList>(this.baseUrl, {
        params: { page, per_page: perPage }
      });
      return response;
    } catch (error) {
      console.error('Error fetching plugins:', error);
      throw error;
    }
  }

  async getPlugin(pluginId: string): Promise<Plugin> {
    try {
      const response = await api.get<Plugin>(`${this.baseUrl}/${pluginId}`);
      return response;
    } catch (error) {
      console.error('Error fetching plugin:', error);
      throw error;
    }
  }

  async installPlugin(pluginData: PluginInstall): Promise<Plugin> {
    try {
      const response = await api.post<Plugin>(`${this.baseUrl}/install`, pluginData);
      return response;
    } catch (error) {
      console.error('Error installing plugin:', error);
      throw error;
    }
  }

  async uninstallPlugin(pluginId: string): Promise<void> {
    try {
      await api.delete(`${this.baseUrl}/${pluginId}`);
    } catch (error) {
      console.error('Error uninstalling plugin:', error);
      throw error;
    }
  }

  async updatePlugin(pluginId: string, pluginData: PluginUpdate): Promise<Plugin> {
    try {
      const response = await api.put<Plugin>(`${this.baseUrl}/${pluginId}`, pluginData);
      return response;
    } catch (error) {
      console.error('Error updating plugin:', error);
      throw error;
    }
  }

  async configurePlugin(pluginId: string, configData: PluginConfigUpdate): Promise<Plugin> {
    try {
      const response = await api.put<Plugin>(`${this.baseUrl}/${pluginId}/config`, configData);
      return response;
    } catch (error) {
      console.error('Error configuring plugin:', error);
      throw error;
    }
  }

  // Marketplace operations
  async getMarketplace(
    page: number = 1,
    perPage: number = 10,
    category?: string,
    search?: string
  ): Promise<MarketplaceList> {
    try {
      const params: Record<string, any> = { page, per_page: perPage };
      if (category) params.category = category;
      if (search) params.search = search;

      const response = await api.get<MarketplaceList>(`${this.baseUrl}/marketplace`, {
        params
      });
      return response;
    } catch (error) {
      console.error('Error fetching marketplace:', error);
      throw error;
    }
  }

  async uploadCustomPlugin(pluginData: PluginCreate): Promise<Plugin> {
    try {
      const response = await api.post<Plugin>(`${this.baseUrl}/upload`, pluginData);
      return response;
    } catch (error) {
      console.error('Error uploading custom plugin:', error);
      throw error;
    }
  }

  // Plugin status and control
  async getPluginStatus(pluginId: string): Promise<Record<string, any>> {
    try {
      const response = await api.get<Record<string, any>>(`${this.baseUrl}/${pluginId}/status`);
      return response;
    } catch (error) {
      console.error('Error fetching plugin status:', error);
      throw error;
    }
  }

  async enablePlugin(pluginId: string): Promise<Plugin> {
    try {
      const response = await api.post<Plugin>(`${this.baseUrl}/${pluginId}/enable`);
      return response;
    } catch (error) {
      console.error('Error enabling plugin:', error);
      throw error;
    }
  }

  async disablePlugin(pluginId: string): Promise<Plugin> {
    try {
      const response = await api.post<Plugin>(`${this.baseUrl}/${pluginId}/disable`);
      return response;
    } catch (error) {
      console.error('Error disabling plugin:', error);
      throw error;
    }
  }

  // Batch operations
  async installMultiplePlugins(pluginIds: string[]): Promise<Plugin[]> {
    try {
      const plugins: Plugin[] = [];
      for (const pluginId of pluginIds) {
        const plugin = await this.installPlugin({ plugin_id: pluginId });
        plugins.push(plugin);
      }
      return plugins;
    } catch (error) {
      console.error('Error installing multiple plugins:', error);
      throw error;
    }
  }

  async uninstallMultiplePlugins(pluginIds: string[]): Promise<void> {
    try {
      for (const pluginId of pluginIds) {
        await this.uninstallPlugin(pluginId);
      }
    } catch (error) {
      console.error('Error uninstalling multiple plugins:', error);
      throw error;
    }
  }

  async enableMultiplePlugins(pluginIds: string[]): Promise<Plugin[]> {
    try {
      const plugins: Plugin[] = [];
      for (const pluginId of pluginIds) {
        const plugin = await this.enablePlugin(pluginId);
        plugins.push(plugin);
      }
      return plugins;
    } catch (error) {
      console.error('Error enabling multiple plugins:', error);
      throw error;
    }
  }

  async disableMultiplePlugins(pluginIds: string[]): Promise<Plugin[]> {
    try {
      const plugins: Plugin[] = [];
      for (const pluginId of pluginIds) {
        const plugin = await this.disablePlugin(pluginId);
        plugins.push(plugin);
      }
      return plugins;
    } catch (error) {
      console.error('Error disabling multiple plugins:', error);
      throw error;
    }
  }

  // Search and filter operations
  async searchPlugins(query: string, page: number = 1, perPage: number = 10): Promise<PluginList> {
    try {
      const response = await api.get<PluginList>(this.baseUrl, {
        params: { search: query, page, per_page: perPage }
      });
      return response;
    } catch (error) {
      console.error('Error searching plugins:', error);
      throw error;
    }
  }

  async getPluginsByCategory(category: string, page: number = 1, perPage: number = 10): Promise<PluginList> {
    try {
      const response = await api.get<PluginList>(this.baseUrl, {
        params: { category, page, per_page: perPage }
      });
      return response;
    } catch (error) {
      console.error('Error fetching plugins by category:', error);
      throw error;
    }
  }

  async getPluginsByType(type: string, page: number = 1, perPage: number = 10): Promise<PluginList> {
    try {
      const response = await api.get<PluginList>(this.baseUrl, {
        params: { type, page, per_page: perPage }
      });
      return response;
    } catch (error) {
      console.error('Error fetching plugins by type:', error);
      throw error;
    }
  }

  // Plugin validation
  async validatePlugin(pluginData: PluginCreate): Promise<{ valid: boolean; errors: string[] }> {
    try {
      // This would typically call a validation endpoint
      // For now, we'll do basic validation
      const errors: string[] = [];

      if (!pluginData.name || pluginData.name.trim().length === 0) {
        errors.push('Plugin name is required');
      }

      if (!pluginData.version || pluginData.version.trim().length === 0) {
        errors.push('Plugin version is required');
      }

      if (!pluginData.author || pluginData.author.trim().length === 0) {
        errors.push('Plugin author is required');
      }

      return {
        valid: errors.length === 0,
        errors
      };
    } catch (error) {
      console.error('Error validating plugin:', error);
      throw error;
    }
  }

  // Plugin dependencies
  async checkDependencies(pluginId: string): Promise<{ satisfied: boolean; missing: string[] }> {
    try {
      const plugin = await this.getPlugin(pluginId);
      const installedPlugins = await this.getPlugins(1, 1000);
      const installedPluginIds = installedPlugins.plugins.map(p => p.id);

      const missing = plugin.dependencies.filter(dep => !installedPluginIds.includes(dep));

      return {
        satisfied: missing.length === 0,
        missing
      };
    } catch (error) {
      console.error('Error checking dependencies:', error);
      throw error;
    }
  }
}

// Export singleton instance
export const pluginApi = new PluginApiService(); 