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
      // For React Native - use the URI exactly as provided by ImagePicker
      const fileName = uri.split('/').pop() || 'sock.jpg';
      formData.append('file', {
        uri: uri,
        type: 'image/jpeg',
        name: fileName,
      } as any);
    }

    if (!isWeb) {
      // On mobile, use fetch API directly as axios has issues with FormData
      const token = await getToken();
      const response = await fetch(`${API_BASE_URL}/singles/upload`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          // Don't set Content-Type - let fetch set it with boundary
        },
        body: formData,
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Upload failed: ${response.status} ${errorText}`);
      }
      
      const data = await response.json();
      return data;
    } else {
      // On web, use axios as usual
      const response = await api.post<Sock>('/singles/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    }
  },

  list: async (): Promise<Sock[]> => {
    const response = await api.get<Sock[]>('/singles/list');
    return response.data;
  },

  get: async (sockId: number): Promise<Sock> => {
    const response = await api.get<Sock>(`/singles/${sockId}`);
    return response.data;
  },

  // Search for similar socks using an existing sock's ID (uses stored embedding)
  searchBySockId: async (sockId: number, limit: number = 10): Promise<SockMatch[]> => {
    const response = await api.get<SockMatch[]>(`/singles/${sockId}/search`, {
      params: { limit },
    });
    return response.data;
  },

  // Get image URL with authentication token
  // Pass token explicitly (from AsyncStorage on mobile, from localStorage on web)
  getImageUrl: (sockId: number, token?: string): string => {
    // Both web and mobile need token in URL because:
    // - Web: <img> tags can't send custom headers
    // - Mobile: React Native Image component doesn't send custom headers
    
    if (!token && isWeb) {
      try {
        token = getTokenSync();
      } catch (e) {
        console.warn('[API] Could not get token synchronously');
      }
    }
    
    if (token) {
      return `${API_BASE_URL}/singles/${sockId}/image?token=${encodeURIComponent(token)}`;
    }
    
    // Fallback without token (will fail auth but better than crashing)
    return `${API_BASE_URL}/singles/${sockId}/image`;
  },


};

// Matches API
export const matchesAPI = {
  create: async (data: MatchCreate): Promise<Match> => {
    const response = await api.post<Match>('/matches', data);
    return response.data;
  },

  list: async (): Promise<Match[]> => {
    const response = await api.get<Match[]>('/matches');
    return response.data;
  },

  get: async (matchId: number): Promise<Match> => {
    const response = await api.get<Match>(`/matches/${matchId}`);
    return response.data;
  },
};

export default api;
