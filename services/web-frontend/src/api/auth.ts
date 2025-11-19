// FILE: services/web-frontend/src/api/auth.ts

import { apiClient } from './client';
import { User, AuthTokens } from '../types';

export const authApi = {
  async login(googleToken: string): Promise<AuthTokens> {
    return apiClient.post<AuthTokens>('/api/auth/google/token', {
      token: googleToken,
    });
  },

  async refreshToken(refreshToken: string): Promise<AuthTokens> {
    return apiClient.post<AuthTokens>('/api/auth/refresh', {
      refresh_token: refreshToken,
    });
  },

  async getCurrentUser(): Promise<User> {
    return apiClient.get<User>('/api/auth/me');
  },

  async logout(): Promise<void> {
    await apiClient.post('/api/auth/logout');
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  },
};
