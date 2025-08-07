// API Response Types
export interface ApiResponse<T = any> {
  status: 'success' | 'error';
  message: string;
  data?: T;
  timestamp: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  pagination: {
    page: number;
    size: number;
    total: number;
    pages: number;
  };
}

// System Types
export interface SystemStatus {
  overall_status: 'success' | 'error' | 'pending' | 'running';
  version: string;
  uptime: number;
  components: ComponentStatus[];
  timestamp: string;
}

export interface ComponentStatus {
  name: string;
  status: 'success' | 'error' | 'pending' | 'running';
  version?: string;
  uptime?: number;
  details?: Record<string, any>;
}

// File Types
export interface FileInfo {
  name: string;
  size: number;
  type: string;
  modified: string;
  path: string;
}

export interface FileListResponse {
  files: FileInfo[];
  total: number;
  directory: string;
}

export interface FileUploadResponse {
  filename: string;
  size: number;
  path: string;
  uploaded_at: string;
}

// CLI Types
export interface CLIRunRequest {
  command: string;
  file_path?: string;
  options?: Record<string, any>;
  session_id?: string;
}

export interface CLIRunResponse {
  command: string;
  status: 'success' | 'error' | 'pending' | 'running';
  output?: string;
  error?: string;
  execution_time?: number;
  session_id?: string;
}

// ML Types
export interface MLModel {
  id: string;
  name: string;
  type: string;
  version: string;
  accuracy?: number;
  active: boolean;
  created_at: string;
  updated_at: string;
}

export interface MLStatus {
  enabled: boolean;
  models_count: number;
  active_models: string[];
  last_training?: string;
  accuracy?: number;
}

export interface Recommendation {
  id: string;
  type: 'performance' | 'security' | 'optimization' | 'error';
  title: string;
  description: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  category: string;
  confidence: number;
  created_at: string;
}

// Redis Types
export interface RedisSession {
  id: string;
  data: Record<string, any>;
  created_at: string;
  updated_at: string;
  ttl?: number;
}

// Cache Types
export interface CacheStats {
  total_files: number;
  total_size: number;
  hit_rate: number;
  miss_rate: number;
}

// Webhook Types
export interface WebhookEndpoint {
  id: string;
  url: string;
  events: string[];
  active: boolean;
  created_at: string;
}

export interface WebhookStatus {
  enabled: boolean;
  endpoints_count: number;
  last_event?: string;
  error_rate?: number;
}

// Metrics Types
export interface MetricData {
  timestamp: string;
  value: number;
  label: string;
  category: string;
}

export interface MetricsResponse {
  metrics: MetricData[];
  time_range: string;
  aggregation: string;
  cpu?: number;
  memory?: number;
  disk?: number;
  mova?: {
    requests_total: number;
    requests_success: number;
    requests_error: number;
    average_response_time: number;
    cache_hit_rate: number;
  };
} 