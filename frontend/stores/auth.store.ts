import { create } from 'zustand';
import { User } from '@/types/api.types';
import { api } from '@/lib/api';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  checkAuth: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  isLoading: true,
  
  login: async (username: string, password: string) => {
    try {
      const response = await api.login({ username, password });
      console.log('Login successful, token received');
      
      // Small delay to ensure token is saved
      await new Promise(resolve => setTimeout(resolve, 100));
      
      const user = await api.getCurrentUser();
      console.log('User fetched:', user);
      set({ user, isAuthenticated: true });
    } catch (error) {
      console.error('Login failed:', error);
      set({ user: null, isAuthenticated: false });
      throw error;
    }
  },
  
  register: async (username: string, email: string, password: string) => {
    try {
      await api.register({ username, email, password });
      // Auto-login after registration
      await api.login({ username, password });
      const user = await api.getCurrentUser();
      set({ user, isAuthenticated: true });
    } catch (error) {
      set({ user: null, isAuthenticated: false });
      throw error;
    }
  },
  
  logout: () => {
    api.clearToken();
    set({ user: null, isAuthenticated: false });
  },
  
  checkAuth: async () => {
    set({ isLoading: true });
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        set({ user: null, isAuthenticated: false, isLoading: false });
        return;
      }
      const user = await api.getCurrentUser();
      set({ user, isAuthenticated: true, isLoading: false });
    } catch (error) {
      console.error('Auth check failed:', error);
      set({ user: null, isAuthenticated: false, isLoading: false });
    }
  },
}));