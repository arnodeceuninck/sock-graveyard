import { Platform } from 'react-native';
import Constants from 'expo-constants';

// Get the development machine's IP from Expo
const getDevApiUrl = () => {
  // For Expo Go on mobile, we need the actual IP address and port
  if (Platform.OS !== 'web') {
    const debuggerHost = Constants.expoConfig?.hostUri?.split(':').shift();
    const apiUrl = debuggerHost 
      ? `http://${debuggerHost}:8000`
      : 'http://192.168.0.148:8000'; // Fallback to your local IP
    
    return apiUrl;
  }
  
  // For web, check if we're in development or production
  // In development: frontend is on port 8081, backend is on port 8000
  // In production: nginx routes /api to backend
  if (typeof window !== 'undefined') {
    // Development: frontend runs on port 8081, need to hit backend directly on 8000
    if (window.location.port === '8081' || process.env.NODE_ENV === 'development') {
      return 'http://localhost:8000';
    }
  }
  
  // Production web: use relative path through nginx (strips /api prefix)
  return '/api';
};

// API is accessed via /api path on web (nginx routes this to backend)
// On mobile (Expo Go), use the development machine's IP and port
export const API_BASE_URL = process.env.API_BASE_URL || getDevApiUrl();
