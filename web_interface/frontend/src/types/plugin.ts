export enum PluginStatus {
  INSTALLED = "installed",
  ENABLED = "enabled",
  DISABLED = "disabled",
  ERROR = "error",
  UPDATING = "updating"
}

export enum PluginType {
  WIDGET = "widget",
  INTEGRATION = "integration",
  ANALYTICS = "analytics",
  AUTOMATION = "automation",
  CUSTOM = "custom"
}

export enum PluginCategory {
  PRODUCTIVITY = "productivity",
  ANALYTICS = "analytics",
  INTEGRATION = "integration",
  AUTOMATION = "automation",
  UTILITIES = "utilities",
  CUSTOM = "custom"
}

export interface PluginConfig {
  name: string;
  type: string;
  value: any;
  required: boolean;
  description?: string;
}

export interface Plugin {
  id: string;
  name: string;
  description?: string;
  version: string;
  author: string;
  type: PluginType;
  category: PluginCategory;
  status: PluginStatus;
  config: PluginConfig[];
  dependencies: string[];
  permissions: string[];
  icon_url?: string;
  homepage_url?: string;
  repository_url?: string;
  install_date: string;
  last_updated: string;
  is_custom: boolean;
}

export interface PluginCreate {
  name: string;
  description?: string;
  version: string;
  author: string;
  type: PluginType;
  category: PluginCategory;
  config?: PluginConfig[];
  dependencies?: string[];
  permissions?: string[];
  icon_url?: string;
  homepage_url?: string;
  repository_url?: string;
}

export interface PluginUpdate {
  name?: string;
  description?: string;
  status?: PluginStatus;
  config?: PluginConfig[];
}

export interface PluginInstall {
  plugin_id: string;
  config?: Record<string, any>;
}

export interface PluginConfigUpdate {
  config: Record<string, any>;
}

export interface PluginList {
  plugins: Plugin[];
  total: number;
  page: number;
  per_page: number;
}

export interface MarketplacePlugin {
  id: string;
  name: string;
  description?: string;
  version: string;
  author: string;
  type: PluginType;
  category: PluginCategory;
  downloads: number;
  rating: number;
  reviews: number;
  icon_url?: string;
  homepage_url?: string;
  repository_url?: string;
  is_installed: boolean;
  is_compatible: boolean;
}

export interface MarketplaceList {
  plugins: MarketplacePlugin[];
  total: number;
  page: number;
  per_page: number;
  categories: string[];
  filters: Record<string, any>;
}

export interface PluginApiResponse<T> {
  data: T;
  message?: string;
  error?: string;
} 