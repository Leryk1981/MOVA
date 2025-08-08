export enum WidgetType {
  METRIC = "metric",
  CHART = "chart",
  TABLE = "table",
  TEXT = "text",
  IMAGE = "image",
  CUSTOM = "custom"
}

export enum ChartType {
  LINE = "line",
  BAR = "bar",
  PIE = "pie",
  AREA = "area",
  SCATTER = "scatter"
}

export interface WidgetPosition {
  x: number;
  y: number;
  w: number;
  h: number;
}

export interface WidgetConfig {
  title: string;
  description?: string;
  data_source?: string;
  refresh_interval?: number;
  chart_type?: ChartType;
  custom_config?: Record<string, any>;
}

export interface Widget {
  id: string;
  type: WidgetType;
  position: WidgetPosition;
  config: WidgetConfig;
  data?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface Dashboard {
  id: string;
  name: string;
  description?: string;
  user_id: string;
  widgets: Widget[];
  layout: Record<string, any>;
  is_public: boolean;
  created_at: string;
  updated_at: string;
}

export interface DashboardCreate {
  name: string;
  description?: string;
  is_public: boolean;
}

export interface DashboardUpdate {
  name?: string;
  description?: string;
  is_public?: boolean;
  layout?: Record<string, any>;
}

export interface WidgetCreate {
  type: WidgetType;
  position: WidgetPosition;
  config: WidgetConfig;
}

export interface WidgetUpdate {
  position?: WidgetPosition;
  config?: WidgetConfig;
}

export interface DashboardList {
  dashboards: Dashboard[];
  total: number;
  page: number;
  per_page: number;
}

export interface WidgetData {
  widget_id: string;
  data: Record<string, any>;
  timestamp: string;
}

export interface DashboardApiResponse<T> {
  data: T;
  message?: string;
  error?: string;
} 