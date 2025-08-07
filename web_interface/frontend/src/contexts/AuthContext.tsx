import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { authService } from '../services/auth';
import {
  AuthContextType,
  User,
  LoginCredentials,
  RegisterData,
  UserUpdateData,
  PasswordChangeData,
} from '../types/auth';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isInitialized, setIsInitialized] = useState(false);

  // Initialize auth state
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        if (authService.isAuthenticated() && !authService.isTokenExpired()) {
          const userProfile = await authService.getProfile();
          setUser(userProfile);
        }
      } catch (error) {
        console.error('Failed to initialize auth:', error);
        authService.clearTokens();
      } finally {
        setIsLoading(false);
        setIsInitialized(true);
      }
    };

    initializeAuth();
  }, []);

  // Auto-refresh token
  useEffect(() => {
    if (!user) return;

    const checkTokenExpiration = () => {
      if (authService.isTokenExpired()) {
        const refreshToken = authService.getRefreshToken();
        if (refreshToken) {
          authService.refreshToken(refreshToken)
            .then(({ accessToken, refreshToken }) => {
              authService.setTokens(accessToken, refreshToken);
            })
            .catch(() => {
              logout();
            });
        }
      }
    };

    const interval = setInterval(checkTokenExpiration, 60000); // Check every minute
    return () => clearInterval(interval);
  }, [user]);

  const login = async (credentials: LoginCredentials): Promise<void> => {
    try {
      setIsLoading(true);
      const response = await authService.login(credentials);
      setUser(response.user);
    } catch (error) {
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async (): Promise<void> => {
    try {
      await authService.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setUser(null);
      authService.clearTokens();
    }
  };

  const register = async (data: RegisterData): Promise<void> => {
    try {
      setIsLoading(true);
      const response = await authService.register(data);
      setUser(response.user);
      // Встановлюємо токени після успішної реєстрації
      authService.setTokens(response.accessToken, response.refreshToken);
    } catch (error) {
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const updateProfile = async (data: UserUpdateData): Promise<void> => {
    try {
      setIsLoading(true);
      const updatedUser = await authService.updateProfile(data);
      setUser(updatedUser);
    } catch (error) {
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const changePassword = async (data: PasswordChangeData): Promise<void> => {
    try {
      setIsLoading(true);
      await authService.changePassword(data);
    } catch (error) {
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const refreshToken = async (): Promise<void> => {
    try {
      const refreshToken = authService.getRefreshToken();
      if (refreshToken) {
        const response = await authService.refreshToken(refreshToken);
        authService.setTokens(response.accessToken, response.refreshToken);
      }
    } catch (error) {
      logout();
      throw error;
    }
  };

  const hasRole = (role: string): boolean => {
    if (!user) return false;
    return user.role.name === role;
  };

  const hasPermission = (permission: string): boolean => {
    if (!user) return false;
    return user.permissions.some(p => p.name === permission);
  };

  const hasAnyRole = (roles: string[]): boolean => {
    if (!user) return false;
    return roles.includes(user.role.name);
  };

  const hasAnyPermission = (permissions: string[]): boolean => {
    if (!user) return false;
    return user.permissions.some(p => permissions.includes(p.name));
  };

  const clearAuth = (): void => {
    setUser(null);
    authService.clearTokens();
  };

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    isInitialized,
    login,
    logout,
    register,
    updateProfile,
    changePassword,
    refreshToken,
    hasRole,
    hasPermission,
    hasAnyRole,
    hasAnyPermission,
    clearAuth,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext; 