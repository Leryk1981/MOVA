// User Types
export interface User {
  id: string;
  email: string;
  username: string;
  firstName: string;
  lastName: string;
  avatar?: string;
  role: UserRole;
  permissions: Permission[];
  isActive: boolean;
  lastLogin: Date;
  createdAt: Date;
  updatedAt: Date;
  emailVerified: boolean;
  twoFactorEnabled: boolean;
}

export interface UserRole {
  id: string;
  name: string;
  description: string;
  permissions: Permission[];
  isSystem: boolean;
  createdAt: Date;
  updatedAt: Date;
}

export interface Permission {
  id: string;
  name: string;
  description: string;
  resource: string;
  action: string;
  createdAt: Date;
  updatedAt: Date;
}

// Authentication Types
export interface LoginCredentials {
  email: string;
  password: string;
  rememberMe?: boolean;
}

export interface RegisterData {
  email: string;
  username: string;
  firstName: string;
  lastName: string;
  password: string;
  confirmPassword: string;
  acceptTerms: boolean;
}

export interface AuthResponse {
  user: User;
  accessToken: string;
  refreshToken: string;
  expiresIn: number;
}

export interface TokenRefreshResponse {
  accessToken: string;
  refreshToken: string;
  expiresIn: number;
}

// Profile Management Types
export interface UserUpdateData {
  firstName?: string;
  lastName?: string;
  username?: string;
  avatar?: File;
}

export interface PasswordChangeData {
  currentPassword: string;
  newPassword: string;
  confirmPassword: string;
}

export interface PasswordResetRequest {
  email: string;
}

export interface PasswordResetData {
  token: string;
  newPassword: string;
  confirmPassword: string;
}

// Two-Factor Authentication Types
export interface TwoFactorSetup {
  secret: string;
  qrCode: string;
  backupCodes: string[];
}

export interface TwoFactorVerify {
  code: string;
}

export interface TwoFactorBackupCodes {
  codes: string[];
}

// Session Management Types
export interface UserSession {
  id: string;
  device: string;
  browser: string;
  ipAddress: string;
  location: string;
  lastActivity: Date;
  createdAt: Date;
  isCurrent: boolean;
}

// Security Types
export interface SecurityEvent {
  id: string;
  type: SecurityEventType;
  description: string;
  ipAddress: string;
  userAgent: string;
  location: string;
  timestamp: Date;
  severity: SecurityEventSeverity;
}

export enum SecurityEventType {
  LOGIN_SUCCESS = 'login_success',
  LOGIN_FAILED = 'login_failed',
  LOGOUT = 'logout',
  PASSWORD_CHANGE = 'password_change',
  PASSWORD_RESET = 'password_reset',
  PROFILE_UPDATE = 'profile_update',
  TWO_FACTOR_ENABLED = '2fa_enabled',
  TWO_FACTOR_DISABLED = '2fa_disabled',
  SESSION_TERMINATED = 'session_terminated',
  PERMISSION_DENIED = 'permission_denied',
  SUSPICIOUS_ACTIVITY = 'suspicious_activity'
}

export enum SecurityEventSeverity {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical'
}

// Admin Types
export interface UserListResponse {
  users: User[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
}

export interface UserCreateData {
  email: string;
  username: string;
  firstName: string;
  lastName: string;
  password: string;
  roleId: string;
  isActive: boolean;
}

export interface UserUpdateAdminData {
  firstName?: string;
  lastName?: string;
  username?: string;
  roleId?: string;
  isActive?: boolean;
  emailVerified?: boolean;
}

export interface RoleCreateData {
  name: string;
  description: string;
  permissions: string[];
}

export interface RoleUpdateData {
  name?: string;
  description?: string;
  permissions?: string[];
}

// Audit Types
export interface AuditLog {
  id: string;
  userId: string;
  userEmail: string;
  action: string;
  resource: string;
  resourceId?: string;
  details: Record<string, any>;
  ipAddress: string;
  userAgent: string;
  timestamp: Date;
}

export interface AuditLogResponse {
  logs: AuditLog[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
}

// Security Settings Types
export interface SecuritySettings {
  passwordMinLength: number;
  passwordRequireUppercase: boolean;
  passwordRequireLowercase: boolean;
  passwordRequireNumbers: boolean;
  passwordRequireSpecialChars: boolean;
  sessionTimeout: number;
  maxLoginAttempts: number;
  lockoutDuration: number;
  requireEmailVerification: boolean;
  requireTwoFactor: boolean;
  allowedLoginAttempts: number;
}

// API Response Types
export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
  errors?: Record<string, string[]>;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
}

// Error Types
export interface AuthError {
  code: string;
  message: string;
  field?: string;
}

export interface ValidationError {
  field: string;
  message: string;
}

// Context Types
export interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  isInitialized: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  updateProfile: (data: UserUpdateData) => Promise<void>;
  changePassword: (data: PasswordChangeData) => Promise<void>;
  refreshToken: () => Promise<void>;
  hasRole: (role: string) => boolean;
  hasPermission: (permission: string) => boolean;
  hasAnyRole: (roles: string[]) => boolean;
  hasAnyPermission: (permissions: string[]) => boolean;
  clearAuth: () => void;
}

// Hook Types
export interface UseAuthOptions {
  requireAuth?: boolean;
  redirectTo?: string;
  onSuccess?: () => void;
  onError?: (error: string) => void;
}

export interface UsePermissionOptions {
  permission: string;
  fallback?: React.ReactNode;
  onDenied?: () => void;
}

export interface UseRoleOptions {
  role: string;
  fallback?: React.ReactNode;
  onDenied?: () => void;
} 