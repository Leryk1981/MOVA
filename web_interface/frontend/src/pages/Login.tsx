import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import LoginForm from '../components/auth/LoginForm';
import { useAuth } from '../contexts/AuthContext';

const Login: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { isAuthenticated } = useAuth();

  // Redirect if already authenticated
  React.useEffect(() => {
    if (isAuthenticated) {
      const from = (location.state as any)?.from?.pathname || '/';
      navigate(from, { replace: true });
    }
  }, [isAuthenticated, navigate, location]);

  const handleLoginSuccess = () => {
    const from = (location.state as any)?.from?.pathname || '/';
    navigate(from, { replace: true });
  };

  const handleLoginError = (error: string) => {
    console.error('Login error:', error);
  };

  if (isAuthenticated) {
    return null; // Will redirect in useEffect
  }

  return (
    <LoginForm
      onSuccess={handleLoginSuccess}
      onError={handleLoginError}
    />
  );
};

export default Login; 