import axios, { AxiosInstance } from 'axios';
import {
  LoginCredentials,
  RegisterData,
  AuthResponse,
  User,
  UserUpdateData,
  PasswordChangeData,
  PasswordResetRequest,
  PasswordResetData,
  TwoFactorSetup,
  TwoFactorVerify,
  UserSession,
  SecurityEvent,
  UserListResponse,
  UserCreateData,
  UserUpdateAdminData,
  RoleCreateData,
  RoleUpdateData,
  AuditLogResponse,
  SecuritySettings,
  ApiResponse,
  PaginatedResponse
} from '../types/auth';

class AuthService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: '/api/auth',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor для добавления токена
    this.api.interceptors.request.use(
      (config) => {
        const token = this.getAccessToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor для обработки ошибок
    this.api.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          try {
            const refreshToken = this.getRefreshToken();
            if (refreshToken) {
              const response = await this.refreshToken(refreshToken);
              this.setTokens(response.accessToken, response.refreshToken);
              originalRequest.headers.Authorization = `Bearer ${response.accessToken}`;
              return this.api(originalRequest);
            }
          } catch (refreshError) {
            this.clearTokens();
            window.location.href = '/login';
            return Promise.reject(refreshError);
          }
        }

        return Promise.reject(error);
      }
    );
  }

  // Token Management
  getAccessToken(): string | null {
    return localStorage.getItem('accessToken');
  }

  getRefreshToken(): string | null {
    return localStorage.getItem('refreshToken');
  }

  setTokens(accessToken: string, refreshToken: string): void {
    localStorage.setItem('accessToken', accessToken);
    localStorage.setItem('refreshToken', refreshToken);
  }

  clearTokens(): void {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
  }

  // Authentication Methods
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const response = await this.api.post<AuthResponse>('/login', credentials);
    this.setTokens(response.data.accessToken, response.data.refreshToken);
    return response.data;
  }

  async register(userData: RegisterData): Promise<AuthResponse> {
    const response = await this.api.post<AuthResponse>('/register', userData);
    this.setTokens(response.data.accessToken, response.data.refreshToken);
    return response.data;
  }

  async logout(): Promise<void> {
    try {
      await this.api.post('/logout');
    } finally {
      this.clearTokens();
    }
  }

  async refreshToken(refreshToken: string): Promise<{ accessToken: string; refreshToken: string; expiresIn: number }> {
    const response = await this.api.post<{ accessToken: string; refreshToken: string; expiresIn: number }>('/refresh', {
      refreshToken,
    });
    return response.data;
  }

  async getProfile(): Promise<User> {
    const response = await this.api.get<User>('/profile');
    return response.data;
  }

  async updateProfile(data: UserUpdateData): Promise<User> {
    const formData = new FormData();
    
    Object.entries(data).forEach(([key, value]) => {
      if (value !== undefined) {
        if (key === 'avatar' && value instanceof File) {
          formData.append(key, value);
        } else {
          formData.append(key, String(value));
        }
      }
    });

    const response = await this.api.put<ApiResponse<User>>('/profile', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data.data;
  }

  async changePassword(data: PasswordChangeData): Promise<void> {
    await this.api.post('/change-password', data);
  }

  async forgotPassword(data: PasswordResetRequest): Promise<void> {
    await this.api.post('/forgot-password', data);
  }

  async resetPassword(data: PasswordResetData): Promise<void> {
    await this.api.post('/reset-password', data);
  }

  async verifyEmail(token: string): Promise<void> {
    await this.api.post('/verify-email', { token });
  }

  // Two-Factor Authentication
  async setupTwoFactor(): Promise<TwoFactorSetup> {
    const response = await this.api.post<ApiResponse<TwoFactorSetup>>('/2fa/setup');
    return response.data.data;
  }

  async verifyTwoFactor(code: string): Promise<void> {
    await this.api.post('/2fa/verify', { code });
  }

  async disableTwoFactor(code: string): Promise<void> {
    await this.api.post('/2fa/disable', { code });
  }

  async getBackupCodes(): Promise<string[]> {
    const response = await this.api.get<ApiResponse<{ codes: string[] }>>('/2fa/backup-codes');
    return response.data.data.codes;
  }

  async generateBackupCodes(): Promise<string[]> {
    const response = await this.api.post<ApiResponse<{ codes: string[] }>>('/2fa/backup-codes');
    return response.data.data.codes;
  }

  // Session Management
  async getSessions(): Promise<UserSession[]> {
    const response = await this.api.get<ApiResponse<UserSession[]>>('/sessions');
    return response.data.data;
  }

  async terminateSession(sessionId: string): Promise<void> {
    await this.api.delete(`/sessions/${sessionId}`);
  }

  async terminateAllSessions(): Promise<void> {
    await this.api.delete('/sessions');
  }

  // Security
  async getSecurityEvents(page: number = 1, limit: number = 20): Promise<PaginatedResponse<SecurityEvent>> {
    const response = await this.api.get<ApiResponse<PaginatedResponse<SecurityEvent>>>('/security/events', {
      params: { page, limit },
    });
    return response.data.data;
  }

  async getLoginHistory(page: number = 1, limit: number = 20): Promise<PaginatedResponse<SecurityEvent>> {
    const response = await this.api.get<ApiResponse<PaginatedResponse<SecurityEvent>>>('/security/login-history', {
      params: { page, limit },
    });
    return response.data.data;
  }

  async getSecuritySettings(): Promise<SecuritySettings> {
    const response = await this.api.get<ApiResponse<SecuritySettings>>('/security/settings');
    return response.data.data;
  }

  async updateSecuritySettings(settings: Partial<SecuritySettings>): Promise<SecuritySettings> {
    const response = await this.api.put<ApiResponse<SecuritySettings>>('/security/settings', settings);
    return response.data.data;
  }

  // Admin Methods
  async getUsers(page: number = 1, limit: number = 20, search?: string): Promise<UserListResponse> {
    const response = await this.api.get<ApiResponse<UserListResponse>>('/admin/users', {
      params: { page, limit, search },
    });
    return response.data.data;
  }

  async createUser(userData: UserCreateData): Promise<User> {
    const response = await this.api.post<ApiResponse<User>>('/admin/users', userData);
    return response.data.data;
  }

  async updateUser(userId: string, userData: UserUpdateAdminData): Promise<User> {
    const response = await this.api.put<ApiResponse<User>>(`/admin/users/${userId}`, userData);
    return response.data.data;
  }

  async deleteUser(userId: string): Promise<void> {
    await this.api.delete(`/admin/users/${userId}`);
  }

  async assignRole(userId: string, roleId: string): Promise<void> {
    await this.api.post(`/admin/users/${userId}/roles`, { roleId });
  }

  async removeRole(userId: string, roleId: string): Promise<void> {
    await this.api.delete(`/admin/users/${userId}/roles/${roleId}`);
  }

  async getRoles(): Promise<{ id: string; name: string; description: string }[]> {
    const response = await this.api.get<ApiResponse<{ id: string; name: string; description: string }[]>>('/admin/roles');
    return response.data.data;
  }

  async createRole(roleData: RoleCreateData): Promise<{ id: string; name: string; description: string }> {
    const response = await this.api.post<ApiResponse<{ id: string; name: string; description: string }>>('/admin/roles', roleData);
    return response.data.data;
  }

  async updateRole(roleId: string, roleData: RoleUpdateData): Promise<{ id: string; name: string; description: string }> {
    const response = await this.api.put<ApiResponse<{ id: string; name: string; description: string }>>(`/admin/roles/${roleId}`, roleData);
    return response.data.data;
  }

  async deleteRole(roleId: string): Promise<void> {
    await this.api.delete(`/admin/roles/${roleId}`);
  }

  async getPermissions(): Promise<{ id: string; name: string; description: string; resource: string; action: string }[]> {
    const response = await this.api.get<ApiResponse<{ id: string; name: string; description: string; resource: string; action: string }[]>>('/admin/permissions');
    return response.data.data;
  }

  // Audit
  async getAuditLogs(page: number = 1, limit: number = 20, userId?: string): Promise<AuditLogResponse> {
    const response = await this.api.get<ApiResponse<AuditLogResponse>>('/admin/audit-logs', {
      params: { page, limit, userId },
    });
    return response.data.data;
  }

  // Utility Methods
  isAuthenticated(): boolean {
    return !!this.getAccessToken();
  }

  getTokenExpiration(): Date | null {
    const token = this.getAccessToken();
    if (!token) return null;

    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      return new Date(payload.exp * 1000);
    } catch {
      return null;
    }
  }

  isTokenExpired(): boolean {
    const expiration = this.getTokenExpiration();
    if (!expiration) return true;
    return expiration < new Date();
  }

  getTokenPayload(): any {
    const token = this.getAccessToken();
    if (!token) return null;

    try {
      return JSON.parse(atob(token.split('.')[1]));
    } catch {
      return null;
    }
  }
}

// Singleton instance
export const authService = new AuthService();
export default authService; 