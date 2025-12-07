import { createContext, useContext, useState, useEffect } from 'react';
import api from '../utils/axios';

const AuthContext = createContext();

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is already logged in
    const storedUser = localStorage.getItem('user');
    const accessToken = localStorage.getItem('access_token');

    if (storedUser && accessToken) {
      setUser(JSON.parse(storedUser));
    }
    setLoading(false);
  }, []);

  const signin = async (email, password) => {
    const response = await api.post('/api/sign-in/', { email, password });
    const { user: userData, access, refresh } = response.data;

    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
    localStorage.setItem('user', JSON.stringify(userData));
    setUser(userData);

    return response.data;
  };

  const signup = async (full_name, email, password) => {
    const response = await api.post('/api/users/', {
      full_name,
      email,
      password,
    });
    return response.data;
  };

  const verifyOTP = async (email, otp) => {
    const response = await api.post('/api/verify-otp/', { email, otp });
    const { user: userData, access, refresh } = response.data;

    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
    localStorage.setItem('user', JSON.stringify(userData));
    setUser(userData);

    return response.data;
  };

  const googleSignIn = async (code) => {
    const response = await api.post('/api/sign-in/google/', { code });
    const { user: userData, access, refresh } = response.data;

    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
    localStorage.setItem('user', JSON.stringify(userData));
    setUser(userData);

    return response.data;
  };

  const forgotPassword = async (email) => {
    const response = await api.post('/api/forgot-password/', { email });
    return response.data;
  };

  const resetPassword = async (email, otp, new_password) => {
    const response = await api.post('/api/reset-password/', {
      email,
      otp,
      new_password,
    });
    return response.data;
  };

  const signout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    setUser(null);
  };

  const value = {
    user,
    loading,
    signin,
    signup,
    verifyOTP,
    googleSignIn,
    forgotPassword,
    resetPassword,
    signout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
