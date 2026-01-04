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
  // For web (development and production), use relative path through nginx
  return '/api';
};

// API is accessed via /api path on web (nginx routes this to backend)
// On mobile (Expo Go), use the development machine's IP and port
export const API_BASE_URL = process.env.API_BASE_URL || getDevApiUrl();
