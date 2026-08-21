import React, { createContext, useState, useEffect } from 'react';
import { authApi } from '../api/authApi';
import axiosClient from '../api/axiosClient';

export const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // Initialize auth state on app load
  useEffect(() => {
    const initializeAuth = async () => {
      const token = localStorage.getItem('access_token');
      if (token) {
        setIsAuthenticated(true);
        setIsLoading(false);
        return;
      }

      // Only attempt silent refresh if the user has previously logged in.
      // This prevents unnecessary /auth/refresh calls on the public landing page.
      const hasSession = localStorage.getItem('has_session');
      if (!hasSession) {
        setIsLoading(false);
        return;
      }

      // If no access token but a past session exists, try silent refresh with the http-only cookie
      try {
        const { access_token } = await authApi.silentRefresh();
        localStorage.setItem('access_token', access_token);
        setIsAuthenticated(true);
      } catch (err) {
        // Refresh token is expired or invalid — clear everything
        localStorage.removeItem('access_token');
        localStorage.removeItem('has_session');
        setIsAuthenticated(false);
      } finally {
        setIsLoading(false);
      }
    };

    initializeAuth();
  }, []);

  const login = async (email, password) => {
    const { access_token } = await authApi.login({ email, password });
    localStorage.setItem('access_token', access_token);
    localStorage.setItem('has_session', '1'); // Mark that a session exists for future refreshes
    setIsAuthenticated(true);
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('has_session'); // Clear session flag so refresh isn't attempted again
    setIsAuthenticated(false);
  };

  if (isLoading) {
    // Return a full screen loader matching the theme while checking auth
    return (
      <div style={{ height: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: '#0a0a0a' }}>
        <span style={{ color: '#e8651a', fontFamily: 'JetBrains Mono, monospace' }}>[ Checking Session... ]</span>
      </div>
    );
  }

  return (
    <AuthContext.Provider value={{ isAuthenticated, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}
