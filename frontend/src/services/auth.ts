import api from './api';
import type { UserRegister, UserLogin, Token, User } from '../types';

export const authService = {
  async register(data: UserRegister): Promise<User> {
    const response = await api.post('/auth/register', data);
    return response.data;
  },

  async login(data: UserLogin): Promise<Token> {
    const response = await api.post('/auth/login', data);
    const token: Token = response.data;
    
    localStorage.setItem('access_token', token.access_token);
    localStorage.setItem('refresh_token', token.refresh_token);
    
    return token;
  },

  async logout(): Promise<void> {
    try {
      await api.post('/auth/logout');
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    }
  },

  async getCurrentUser(): Promise<User> {
    const response = await api.get('/auth/me');
    return response.data;
  },

  isAuthenticated(): boolean {
    return !!localStorage.getItem('access_token');
  },

  async changePassword(oldPassword: string, newPassword: string): Promise<void> {
    const response = await api.put('/settings/password', {
      old_password: oldPassword,
      new_password: newPassword,
    });
    return response.data;
  },

  async deleteAccount(): Promise<void> {
    const response = await api.delete('/settings/account');
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('session_id');
    return response.data;
  },
};