"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { auth, User, LoginCredentials, RegisterData } from '../lib/api';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (credentials: LoginCredentials) => Promise<{ success: boolean; error?: string }>;
  register: (userData: RegisterData) => Promise<{ success: boolean; error?: string }>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Check authentication status on mount
  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    setLoading(true);
    
    if (auth.isAuthenticated()) {
      try {
        const response = await auth.getCurrentUser();
        if (response.success && response.data) {
          setUser(response.data);
          setIsAuthenticated(true);
        } else {
          // Token might be invalid, clear it
          await logout();
        }
      } catch (error) {
        // Auth check failed - clear authentication state
        await logout();
      }
    }
    
    setLoading(false);
  };

  const login = async (credentials: LoginCredentials) => {
    setLoading(true);
    
    try {
      const response = await auth.login(credentials);
      
      if (response.success) {
        // Get user data after successful login
        const userResponse = await auth.getCurrentUser();
        if (userResponse.success && userResponse.data) {
          setUser(userResponse.data);
          setIsAuthenticated(true);
        }
        setLoading(false);
        return { success: true };
      } else {
        setLoading(false);
        return { 
          success: false, 
          error: response.error || 'Login failed' 
        };
      }
    } catch (error) {
      setLoading(false);
      return { 
        success: false, 
        error: error instanceof Error ? error.message : 'Login failed' 
      };
    }
  };

  const register = async (userData: RegisterData) => {
    setLoading(true);
    
    try {
      const response = await auth.register(userData);
      
      if (response.success) {
        // Get user data after successful registration
        const userResponse = await auth.getCurrentUser();
        if (userResponse.success && userResponse.data) {
          setUser(userResponse.data);
          setIsAuthenticated(true);
        }
        setLoading(false);
        return { success: true };
      } else {
        setLoading(false);
        return { 
          success: false, 
          error: response.error || 'Registration failed' 
        };
      }
    } catch (error) {
      setLoading(false);
      return { 
        success: false, 
        error: error instanceof Error ? error.message : 'Registration failed' 
      };
    }
  };

  const logout = async () => {
    try {
      await auth.logout();
    } catch (error) {
      // Logout error handled gracefully
    } finally {
      setUser(null);
      setIsAuthenticated(false);
    }
  };

  const refreshUser = async () => {
    if (auth.isAuthenticated()) {
      try {
        const response = await auth.getCurrentUser();
        if (response.success && response.data) {
          setUser(response.data);
          setIsAuthenticated(true);
        }
      } catch (error) {
        // User refresh failed - handled silently
      }
    }
  };

  const value: AuthContextType = {
    user,
    loading,
    login,
    register,
    logout,
    refreshUser,
    isAuthenticated,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext;