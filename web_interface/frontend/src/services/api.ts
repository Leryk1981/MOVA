import axios, { AxiosInstance, AxiosResponse } from 'axios';
import type {
  ApiResponse,
  SystemStatus,
  FileListResponse,
  FileUploadResponse,
  CLIRunRequest,
  CLIRunResponse,
  MLStatus,
  MLModel,
  Recommendation,
  RedisSession,
  CacheStats,
  WebhookStatus,
  MetricsResponse,
} from '@/types/api';

class ApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: '/api',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor
    this.api.interceptors.request.use(
      (config) => {
        // Add auth token if available
        const token = localStorage.getItem('auth_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.api.interceptors.response.use(
      (response: AxiosResponse) => {
        return response;
      },
      (error) => {
        // Handle common errors
        if (error.response?.status === 401) {
          // Handle unauthorized
          localStorage.removeItem('auth_token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // System API
  async getSystemStatus(): Promise<SystemStatus> {
    const response = await this.api.get<SystemStatus>('/system/status');
    return response.data;
  }

  async getSystemInfo(): Promise<ApiResponse> {
    const response = await this.api.get<ApiResponse>('/system/info');
    return response.data;
  }

  async getSystemMetrics(timeRange: string = '1h'): Promise<ApiResponse<MetricsResponse>> {
    const response = await this.api.get<ApiResponse<MetricsResponse>>(`/system/metrics?time_range=${timeRange}`);
    return response.data;
  }

  async cleanupSystem(): Promise<ApiResponse> {
    const response = await this.api.post<ApiResponse>('/system/cleanup');
    return response.data;
  }

  async healthCheck(): Promise<ApiResponse> {
    const response = await this.api.get<ApiResponse>('/system/health');
    return response.data;
  }

  // File API
  async uploadFile(file: File, subdirectory: string = 'mova'): Promise<FileUploadResponse> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('subdirectory', subdirectory);

    const response = await this.api.post<FileUploadResponse>('/files/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  async listFiles(directory: string = 'mova', pattern: string = '*'): Promise<FileListResponse> {
    const response = await this.api.get<FileListResponse>(`/files/list?directory=${directory}&pattern=${pattern}`);
    return response.data;
  }

  async readFile(filename: string, directory: string = 'mova'): Promise<ApiResponse> {
    const response = await this.api.get<ApiResponse>(`/files/read/${filename}?directory=${directory}`);
    return response.data;
  }

  async writeFile(filename: string, content: string, directory: string = 'mova'): Promise<ApiResponse> {
    const response = await this.api.post<ApiResponse>(`/files/write/${filename}`, {
      content,
      directory,
    });
    return response.data;
  }

  async deleteFile(filename: string, directory: string = 'mova'): Promise<ApiResponse> {
    const response = await this.api.delete<ApiResponse>(`/files/delete/${filename}?directory=${directory}`);
    return response.data;
  }

  // CLI API
  async executeCLICommand(request: CLIRunRequest): Promise<CLIRunResponse> {
    const response = await this.api.post<CLIRunResponse>('/cli/execute', request);
    return response.data;
  }

  async parseFile(filePath: string, validate: boolean = false): Promise<ApiResponse> {
    const response = await this.api.post<ApiResponse>('/cli/parse', {
      file_path: filePath,
      validate,
    });
    return response.data;
  }

  async validateFile(filePath: string, advanced: boolean = false): Promise<ApiResponse> {
    const response = await this.api.post<ApiResponse>('/cli/validate', {
      file_path: filePath,
      advanced,
    });
    return response.data;
  }

  async runProtocol(filePath: string, options: Record<string, any> = {}): Promise<ApiResponse> {
    const response = await this.api.post<ApiResponse>('/cli/run', {
      file_path: filePath,
      ...options,
    });
    return response.data;
  }

  async analyzeFile(filePath: string, sessionId: string = 'web_session'): Promise<ApiResponse> {
    const response = await this.api.post<ApiResponse>('/cli/analyze', {
      file_path: filePath,
      session_id: sessionId,
    });
    return response.data;
  }

  async diagnoseError(errorMessage: string, sessionId: string = 'web_session'): Promise<ApiResponse> {
    const response = await this.api.post<ApiResponse>('/cli/diagnose', {
      error_message: errorMessage,
      session_id: sessionId,
    });
    return response.data;
  }

  // Redis API
  async getRedisSessions(redisUrl: string = 'redis://localhost:6379', sessionId?: string): Promise<ApiResponse> {
    const response = await this.api.post<ApiResponse>('/cli/redis/sessions', {
      redis_url: redisUrl,
      session_id: sessionId,
    });
    return response.data;
  }

  async clearRedis(redisUrl: string = 'redis://localhost:6379', sessionId?: string): Promise<ApiResponse> {
    const response = await this.api.post<ApiResponse>('/cli/redis/clear', {
      redis_url: redisUrl,
      session_id: sessionId,
      confirm: true,
    });
    return response.data;
  }

  // Cache API
  async getCacheInfo(key?: string): Promise<ApiResponse<CacheStats>> {
    const response = await this.api.post<ApiResponse<CacheStats>>('/cli/cache/info', {
      key,
      stats: !key,
    });
    return response.data;
  }

  async clearCache(key?: string): Promise<ApiResponse> {
    const response = await this.api.post<ApiResponse>('/cli/cache/clear', {
      key,
      confirm: true,
    });
    return response.data;
  }

  // Webhook API
  async testWebhook(url: string, eventType: string, data?: Record<string, any>): Promise<ApiResponse> {
    const response = await this.api.post<ApiResponse>('/cli/webhook/test', {
      url,
      event_type: eventType,
      data,
    });
    return response.data;
  }

  // ML API
  async getMLStatus(): Promise<ApiResponse<MLStatus>> {
    const response = await this.api.get<ApiResponse<MLStatus>>('/ml/status');
    return response.data;
  }

  async getMLModels(): Promise<ApiResponse<{ models: MLModel[] }>> {
    const response = await this.api.get<ApiResponse<{ models: MLModel[] }>>('/ml/models');
    return response.data;
  }

  async getMLModel(modelId: string): Promise<ApiResponse<MLModel>> {
    const response = await this.api.get<ApiResponse<MLModel>>(`/ml/models/${modelId}`);
    return response.data;
  }

  async evaluateMLModel(modelId: string, testData: Record<string, any>): Promise<ApiResponse> {
    const response = await this.api.post<ApiResponse>(`/ml/models/${modelId}/evaluate`, {
      test_data: JSON.stringify(testData),
    });
    return response.data;
  }

  async trainMLModel(modelId: string, trainingConfig: Record<string, any>): Promise<ApiResponse> {
    const response = await this.api.post<ApiResponse>(`/ml/models/${modelId}/train`, trainingConfig);
    return response.data;
  }

  async analyzeIntent(text: string): Promise<ApiResponse> {
    const response = await this.api.post<ApiResponse>('/ml/analyze/intent', { text });
    return response.data;
  }

  async extractEntities(text: string): Promise<ApiResponse> {
    const response = await this.api.post<ApiResponse>('/ml/analyze/entities', { text });
    return response.data;
  }

  async analyzeSentiment(text: string): Promise<ApiResponse> {
    const response = await this.api.post<ApiResponse>('/ml/analyze/sentiment', { text });
    return response.data;
  }

  async generateRecommendations(filePath: string, sessionId: string = 'web_session'): Promise<ApiResponse> {
    const response = await this.api.post<ApiResponse>('/ml/recommendations/generate', {
      file_path: filePath,
      session_id: sessionId,
    });
    return response.data;
  }

  async getRecommendationsSummary(sessionId: string = 'web_session'): Promise<ApiResponse> {
    const response = await this.api.get<ApiResponse>(`/ml/recommendations/summary?session_id=${sessionId}`);
    return response.data;
  }

  async exportRecommendations(sessionId: string = 'web_session', format: string = 'json'): Promise<ApiResponse> {
    const response = await this.api.post<ApiResponse>('/ml/recommendations/export', {
      session_id: sessionId,
      format,
    });
    return response.data;
  }

  async getMLMetrics(): Promise<ApiResponse> {
    const response = await this.api.get<ApiResponse>('/ml/metrics');
    return response.data;
  }
}

// Export singleton instance
export const apiService = new ApiService();
export default apiService; 