import {
  LoginCredentials,
  RegisterData,
  AuthResponse,
  User,
  UserUpdateData,
  PasswordChangeData,
  UserRole,
  Permission,
} from '../types/auth';

// Mock data
const mockUser: User = {
  id: '1',
  email: 'admin@mova.com',
  username: 'admin',
  firstName: 'Admin',
  lastName: 'User',
  avatar: undefined,
  role: {
    id: '1',
    name: 'admin',
    description: 'Administrator',
    permissions: [
      { id: '1', name: 'dashboard:read', description: 'Read dashboard', resource: 'dashboard', action: 'read', createdAt: new Date(), updatedAt: new Date() },
      { id: '2', name: 'files:manage', description: 'Manage files', resource: 'files', action: 'manage', createdAt: new Date(), updatedAt: new Date() },
      { id: '3', name: 'ml:manage', description: 'Manage ML models', resource: 'ml', action: 'manage', createdAt: new Date(), updatedAt: new Date() },
    ],
    isSystem: true,
    createdAt: new Date(),
    updatedAt: new Date(),
  },
  permissions: [
    { id: '1', name: 'dashboard:read', description: 'Read dashboard', resource: 'dashboard', action: 'read', createdAt: new Date(), updatedAt: new Date() },
    { id: '2', name: 'files:manage', description: 'Manage files', resource: 'files', action: 'manage', createdAt: new Date(), updatedAt: new Date() },
    { id: '3', name: 'ml:manage', description: 'Manage ML models', resource: 'ml', action: 'manage', createdAt: new Date(), updatedAt: new Date() },
  ],
  isActive: true,
  lastLogin: new Date(),
  createdAt: new Date(),
  updatedAt: new Date(),
  emailVerified: true,
  twoFactorEnabled: false,
};

class MockAuthService {
  private isLoggedIn = false;
  private currentUser: User | null = null;

  // Token Management
  getAccessToken(): string | null {
    return this.isLoggedIn ? 'mock-access-token' : null;
  }

  getRefreshToken(): string | null {
    return this.isLoggedIn ? 'mock-refresh-token' : null;
  }

  setTokens(accessToken: string, refreshToken: string): void {
    localStorage.setItem('accessToken', accessToken);
    localStorage.setItem('refreshToken', refreshToken);
    this.isLoggedIn = true;
  }

  clearTokens(): void {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    this.isLoggedIn = false;
    this.currentUser = null;
  }

  // Authentication Methods
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1000));

    // Mock validation
    if (credentials.email === 'admin@mova.com' && credentials.password === 'password') {
      this.isLoggedIn = true;
      this.currentUser = mockUser;
      
      const response: AuthResponse = {
        user: mockUser,
        accessToken: 'mock-access-token',
        refreshToken: 'mock-refresh-token',
        expiresIn: 3600,
      };

      this.setTokens(response.accessToken, response.refreshToken);
      return response;
    } else {
      throw new Error('Invalid credentials');
    }
  }

  async register(userData: RegisterData): Promise<AuthResponse> {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1000));

    // Mock registration
    const newUser: User = {
      ...mockUser,
      id: '2',
      email: userData.email,
      username: userData.username,
      firstName: userData.firstName,
      lastName: userData.lastName,
      role: {
        id: '2',
        name: 'user',
        description: 'Regular User',
        permissions: [
          { id: '1', name: 'dashboard:read', description: 'Read dashboard', resource: 'dashboard', action: 'read', createdAt: new Date(), updatedAt: new Date() },
        ],
        isSystem: true,
        createdAt: new Date(),
        updatedAt: new Date(),
      },
      permissions: [
        { id: '1', name: 'dashboard:read', description: 'Read dashboard', resource: 'dashboard', action: 'read', createdAt: new Date(), updatedAt: new Date() },
      ],
    };

    this.isLoggedIn = true;
    this.currentUser = newUser;

    const response: AuthResponse = {
      user: newUser,
      accessToken: 'mock-access-token',
      refreshToken: 'mock-refresh-token',
      expiresIn: 3600,
    };

    this.setTokens(response.accessToken, response.refreshToken);
    return response;
  }

  async logout(): Promise<void> {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 500));
    this.clearTokens();
  }

  async refreshToken(refreshToken: string): Promise<{ accessToken: string; refreshToken: string; expiresIn: number }> {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 500));

    if (refreshToken === 'mock-refresh-token') {
      return {
        accessToken: 'new-mock-access-token',
        refreshToken: 'new-mock-refresh-token',
        expiresIn: 3600,
      };
    } else {
      throw new Error('Invalid refresh token');
    }
  }

  async getProfile(): Promise<User> {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 500));

    if (!this.isLoggedIn || !this.currentUser) {
      throw new Error('Not authenticated');
    }

    return this.currentUser;
  }

  async updateProfile(data: UserUpdateData): Promise<User> {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1000));

    if (!this.isLoggedIn || !this.currentUser) {
      throw new Error('Not authenticated');
    }

    const updatedUser: User = {
      ...this.currentUser,
      ...data,
      updatedAt: new Date(),
    };

    this.currentUser = updatedUser;
    return updatedUser;
  }

  async changePassword(data: PasswordChangeData): Promise<void> {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1000));

    if (!this.isLoggedIn) {
      throw new Error('Not authenticated');
    }

    // Mock password validation
    if (data.currentPassword !== 'password') {
      throw new Error('Current password is incorrect');
    }

    if (data.newPassword !== data.confirmPassword) {
      throw new Error('New passwords do not match');
    }

    if (data.newPassword.length < 8) {
      throw new Error('Password must be at least 8 characters long');
    }
  }

  // Utility Methods
  isAuthenticated(): boolean {
    return this.isLoggedIn;
  }

  getTokenExpiration(): Date | null {
    if (!this.isLoggedIn) return null;
    return new Date(Date.now() + 3600 * 1000); // 1 hour from now
  }

  isTokenExpired(): boolean {
    const expiration = this.getTokenExpiration();
    if (!expiration) return true;
    return expiration < new Date();
  }

  getTokenPayload(): any {
    if (!this.isLoggedIn) return null;
    return {
      sub: this.currentUser?.id,
      email: this.currentUser?.email,
      role: this.currentUser?.role.name,
      exp: Math.floor(Date.now() / 1000) + 3600,
    };
  }
}

// Singleton instance
export const mockAuthService = new MockAuthService();
export default mockAuthService; 