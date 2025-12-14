import axios, { AxiosInstance, AxiosError } from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { API_BASE_URL } from '../constants/theme';

// API Client
class ApiService {
  private client: AxiosInstance;
  private token: string | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      async (config) => {
        if (!this.token) {
          this.token = await AsyncStorage.getItem('auth_token');
        }
        if (this.token) {
          config.headers.Authorization = `Bearer ${this.token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Token expired or invalid
          await this.logout();
        }
        return Promise.reject(error);
      }
    );
  }

  // Auth methods
  async register(email: string, username: string, password: string) {
    const response = await this.client.post('/auth/register', {
      email,
      username,
      password,
    });
    return response.data;
  }

  async login(username: string, password: string) {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);

    const response = await this.client.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    const { access_token } = response.data;
    this.token = access_token;
    await AsyncStorage.setItem('auth_token', access_token);

    return response.data;
  }

  async logout() {
    this.token = null;
    await AsyncStorage.removeItem('auth_token');
  }

  async getCurrentUser() {
    const response = await this.client.get('/users/me');
    return response.data;
  }

  // Sock methods
  async uploadSock(imageUri: string, description?: string) {
    const formData = new FormData();
    
    // Handle file upload differently for web vs native
    if (imageUri.startsWith('http://') || imageUri.startsWith('https://')) {
      // Web: fetch the blob first
      const response = await fetch(imageUri);
      const blob = await response.blob();
      // @ts-ignore - File constructor works in web environment
      const file = new File([blob], 'sock.jpg', { type: blob.type || 'image/jpeg' });
      formData.append('file', file);
    } else if (imageUri.startsWith('file://')) {
      // Mobile: Use the file URI directly
      // @ts-ignore - React Native handles file upload differently
      formData.append('file', {
        uri: imageUri,
        type: 'image/jpeg',
        name: 'sock.jpg',
      } as any);
    } else {
      // Web (blob URI): Try to fetch as blob
      try {
        const response = await fetch(imageUri);
        const blob = await response.blob();
        // @ts-ignore - File constructor works in web environment
        const file = new File([blob], 'sock.jpg', { type: blob.type || 'image/jpeg' });
        formData.append('file', file);
      } catch (error) {
        // Fallback for React Native
        // @ts-ignore
        formData.append('file', {
          uri: imageUri,
          type: 'image/jpeg',
          name: 'sock.jpg',
        } as any);
      }
    }

    if (description) {
      formData.append('description', description);
    }

    const response = await this.client.post('/socks/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  }

  async getSocks(unmatchedOnly: boolean = false) {
    const response = await this.client.get('/socks/', {
      params: { unmatched_only: unmatchedOnly },
    });
    return response.data;
  }

  async getSock(sockId: number) {
    const response = await this.client.get(`/socks/${sockId}`);
    return response.data;
  }

  async getSockImage(sockId: number, processed: boolean = false) {
    const response = await this.client.get(`/socks/${sockId}/image`, {
      params: { processed },
      responseType: 'blob',
    });
    return response.data;
  }

  async searchSimilarSocks(sockId: number, threshold: number = 0.85, limit: number = 10) {
    const response = await this.client.post('/socks/search', null, {
      params: { sock_id: sockId, threshold, limit },
    });
    return response.data;
  }

  async confirmMatch(sockId1: number, sockId2: number) {
    const response = await this.client.post('/socks/match', {
      sock_id_1: sockId1,
      sock_id_2: sockId2,
    });
    return response.data;
  }

  async deleteSock(sockId: number) {
    const response = await this.client.delete(`/socks/${sockId}`);
    return response.data;
  }

  // Helper to check if user is authenticated
  async isAuthenticated(): Promise<boolean> {
    const token = await AsyncStorage.getItem('auth_token');
    return !!token;
  }
}

export default new ApiService();
