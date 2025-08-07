import React from 'react';
import { useNavigate } from 'react-router-dom';
import RegisterForm from '../components/auth/RegisterForm';
import { useAuth } from '../contexts/AuthContext';

const Register: React.FC = () => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  // Redirect if already authenticated
  React.useEffect(() => {
    if (isAuthenticated) {
      navigate('/', { replace: true });
    }
  }, [isAuthenticated, navigate]);

  const handleRegisterSuccess = () => {
    // Registration successful, user will be redirected to login or dashboard
    console.log('Registration successful');
  };

  const handleRegisterError = (error: string) => {
    console.error('Registration error:', error);
  };

  if (isAuthenticated) {
    return null; // Will redirect in useEffect
  }

  return (
    <RegisterForm
      onSuccess={handleRegisterSuccess}
      onError={handleRegisterError}
      requireEmailVerification={true}
    />
  );
};

export default Register; 