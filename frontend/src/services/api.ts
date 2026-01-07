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
const REFRESH_TOKEN_KEY = 'refresh_token';

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

export const saveRefreshToken = async (token: string) => {
  if (isWeb) {
    localStorage.setItem(REFRESH_TOKEN_KEY, token);
  } else {
    await SecureStore.setItemAsync(REFRESH_TOKEN_KEY, token);
  }
};

export const getRefreshToken = async () => {
  if (isWeb) {
    return localStorage.getItem(REFRESH_TOKEN_KEY);
  } else {
    return await SecureStore.getItemAsync(REFRESH_TOKEN_KEY);
  }
};

export const saveTokens = async (accessToken: string, refreshToken: string) => {
  await saveToken(accessToken);
  await saveRefreshToken(refreshToken);
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
    localStorage.removeItem(REFRESH_TOKEN_KEY);
  } else {
    await SecureStore.deleteItemAsync(TOKEN_KEY);
    await SecureStore.deleteItemAsync(REFRESH_TOKEN_KEY);
  }
};

// Flag to prevent multiple simultaneous refresh attempts
let isRefreshing = false;
let refreshPromise: Promise<string | null> | null = null;

// Refresh the access token using the refresh token
const refreshAccessToken = async (): Promise<string | null> => {
  // If already refreshing, return the existing promise
  if (isRefreshing && refreshPromise) {
    return refreshPromise;
  }

  isRefreshing = true;
  refreshPromise = (async () => {
    try {
      const refreshToken = await getRefreshToken();
      if (!refreshToken) {
        return null;
      }

      const response = await axios.post<AuthResponse>(`${API_BASE_URL}/auth/refresh`, {
        refresh_token: refreshToken,
      });

      const { access_token, refresh_token: newRefreshToken } = response.data;
      await saveTokens(access_token, newRefreshToken);
      return access_token;
    } catch (error) {
      // Refresh failed - clear tokens
      await removeToken();
      return null;
    } finally {
      isRefreshing = false;
      refreshPromise = null;
    }
  })();

  return refreshPromise;
};

// Add token to requests
api.interceptors.request.use(async (config) => {
  const token = await getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 errors by refreshing the token
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If error is 401 and we haven't tried refreshing yet
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      const newToken = await refreshAccessToken();
      if (newToken) {
        // Retry the original request with the new token
        originalRequest.headers.Authorization = `Bearer ${newToken}`;
        return api(originalRequest);
      } else {
        // Refresh failed, redirect to login will be handled by AuthContext
        return Promise.reject(error);
      }
    }

    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  register: async (data: RegisterRequest): Promise<User> => {
    const response = await api.post<User>('/auth/register', data);
    return response.data;
  },

  login: async (data: LoginRequest): Promise<AuthResponse> => {
    const formData = new FormData();
    formData.append('username', data.email);
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
    const maxRetries = 3;
    let lastError: any;
    
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
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
      } catch (error: any) {
        lastError = error;
        
        // If this was the last attempt, throw the error
        if (attempt === maxRetries) {
          throw error;
        }
        
        // Wait before retrying (exponential backoff: 1s, 2s)
        const delayMs = attempt * 1000;
        await new Promise(resolve => setTimeout(resolve, delayMs));
      }
    }
    
    // Should never reach here, but just in case
    throw lastError;
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
  // useThumbnail: if true, requests a smaller, optimized version for list views
  getImageUrl: (sockId: number, token?: string, useThumbnail: boolean = false): string => {
    // Both web and mobile need token in URL because:
    // - Web: <img> tags can't send custom headers
    // - Mobile: React Native Image component doesn't send custom headers
    
    if (!token && isWeb) {
      try {
        token = getTokenSync() ?? undefined;
      } catch (e) {
        console.warn('[API] Could not get token synchronously');
      }
    }
    
    const params = new URLSearchParams();
    if (token) {
      params.append('token', token);
    }
    if (useThumbnail) {
      params.append('thumbnail', 'true');
      params.append('quality', '85');
    }
    
    return `${API_BASE_URL}/singles/${sockId}/image?${params.toString()}`;
  },

  // Get background-removed image URL with authentication token
  getImageNoBgUrl: (sockId: number, token?: string): string => {
    if (!token && isWeb) {
      try {
        token = getTokenSync() ?? undefined;
      } catch (e) {
        console.warn('[API] Could not get token synchronously');
      }
    }
    
    if (token) {
      return `${API_BASE_URL}/singles/${sockId}/image-no-bg?token=${encodeURIComponent(token)}`;
    }
    
    // Fallback without token (will fail auth but better than crashing)
    return `${API_BASE_URL}/singles/${sockId}/image-no-bg`;
  },

  delete: async (sockId: number): Promise<void> => {
    await api.delete(`/singles/${sockId}`);
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

  delete: async (matchId: number, decouple: boolean = false): Promise<void> => {
    await api.delete(`/matches/${matchId}`, {
      params: { decouple },
    });
  },
};

export default api;
