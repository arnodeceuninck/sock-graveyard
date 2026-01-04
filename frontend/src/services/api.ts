import axios from 'axios';
import * as SecureStore from 'expo-secure-store';
import { Platform } from 'react-native';
import { API_BASE_URL } from '../config';
import { User, Sock, SockMatch, LoginRequest, RegisterRequest, AuthResponse, MatchCreate, Match } from '../types';

const api = axios.create({
  baseURL: API_BASE_URL,
});

// Token management
const TOKEN_KEY = 'auth_token';

// Check if we're on web or native
const isWeb = Platform.OS === 'web';

export const saveToken = async (token: string) => {
  if (isWeb) {
    localStorage.setItem(TOKEN_KEY, token);
  } else {
    await SecureStore.setItemAsync(TOKEN_KEY, token);
  }
};

export const getToken = async () => {
  if (isWeb) {
    return localStorage.getItem(TOKEN_KEY);
  } else {
    return await SecureStore.getItemAsync(TOKEN_KEY);
  }
};

// Synchronous version for web (used in image headers)
export const getTokenSync = () => {
  if (isWeb) {
    return localStorage.getItem(TOKEN_KEY);
  }
  // For native, this won't work synchronously, should use async version
  throw new Error('getTokenSync is only available on web');
};

export const removeToken = async () => {
  if (isWeb) {
    localStorage.removeItem(TOKEN_KEY);
  } else {
    await SecureStore.deleteItemAsync(TOKEN_KEY);
  }
};

// Add token to requests
api.interceptors.request.use(async (config) => {
  const token = await getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth API
export const authAPI = {
  register: async (data: RegisterRequest): Promise<User> => {
    const response = await api.post<User>('/auth/register', data);
    return response.data;
  },

  login: async (data: LoginRequest): Promise<AuthResponse> => {
    const formData = new FormData();
    formData.append('username', data.username);
    formData.append('password', data.password);
    
    const response = await api.post<AuthResponse>('/auth/login', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  me: async (): Promise<User> => {
    const response = await api.get<User>('/auth/me');
    return response.data;
  },
};

// Socks API
export const socksAPI = {
  upload: async (uri: string): Promise<Sock> => {
    const formData = new FormData();
    
    if (isWeb) {
      // For web, fetch the blob from the URI and create a File object
      const response = await fetch(uri);
      const blob = await response.blob();
      formData.append('file', blob, 'sock.jpg');
    } else {
      // For React Native
      formData.append('file', {
        uri,
        type: 'image/jpeg',
        name: 'sock.jpg',
      } as any);
    }

    const response = await api.post<Sock>('/socks/upload', formData);
    return response.data;
  },

  list: async (): Promise<Sock[]> => {
    const response = await api.get<Sock[]>('/socks/list');
    return response.data;
  },

  get: async (sockId: number): Promise<Sock> => {
    const response = await api.get<Sock>(`/socks/${sockId}`);
    return response.data;
  },

  getImageUrl: (sockId: number): string => {
    const token = getTokenSync();
    return `${API_BASE_URL}/socks/${sockId}/image?token=${encodeURIComponent(token || '')}`;
  },

  search: async (uri: string, excludeSockId?: number): Promise<SockMatch[]> => {
    const formData = new FormData();
    
    if (isWeb) {
      // For web, fetch the blob from the URI and create a File object
      const response = await fetch(uri);
      const blob = await response.blob();
      formData.append('file', blob, 'sock.jpg');
    } else {
      // For React Native
      formData.append('file', {
        uri,
        type: 'image/jpeg',
        name: 'sock.jpg',
      } as any);
    }

    const url = excludeSockId 
      ? `/socks/search?exclude_sock_id=${excludeSockId}`
      : '/socks/search';
    
    const response = await api.post<SockMatch[]>(url, formData);
    return response.data;
  },
};

// Matches API
export const matchesAPI = {
  create: async (data: MatchCreate): Promise<Match> => {
    const response = await api.post<Match>('/socks/match', data);
    return response.data;
  },

  list: async (): Promise<Match[]> => {
    const response = await api.get<Match[]>('/socks/matches');
    return response.data;
  },

  get: async (matchId: number): Promise<Match> => {
    const response = await api.get<Match>(`/socks/matches/${matchId}`);
    return response.data;
  },
};

export default api;
