import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requireAuth?: boolean;
  requiredRoles?: string[];
  requiredPermissions?: string[];
  fallback?: React.ReactNode;
  redirectTo?: string;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requireAuth = true,
  requiredRoles = [],
  requiredPermissions = [],
  fallback,
  redirectTo = '/login',
}) => {
  const { user, isAuthenticated, isLoading, isInitialized } = useAuth();
  const location = useLocation();

  // Show loading spinner while auth is initializing
  if (!isInitialized || isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  // Check if authentication is required
  if (requireAuth && !isAuthenticated) {
    return <Navigate to={redirectTo} state={{ from: location }} replace />;
  }

  // Check if specific roles are required
  if (requiredRoles.length > 0 && user) {
    const hasRequiredRole = requiredRoles.some(role => user.role.name === role);
    if (!hasRequiredRole) {
      if (fallback) {
        return <>{fallback}</>;
      }
      return <Navigate to="/unauthorized" replace />;
    }
  }

  // Check if specific permissions are required
  if (requiredPermissions.length > 0 && user) {
    const hasRequiredPermission = requiredPermissions.some(permission =>
      user.permissions.some(p => p.name === permission)
    );
    if (!hasRequiredPermission) {
      if (fallback) {
        return <>{fallback}</>;
      }
      return <Navigate to="/unauthorized" replace />;
    }
  }

  return <>{children}</>;
};

export default ProtectedRoute; 