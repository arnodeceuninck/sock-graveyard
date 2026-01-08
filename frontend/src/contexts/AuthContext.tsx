import React, { createContext, useState, useContext, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { authAPI, saveToken, getToken, removeToken } from '../services/api';
import { User, LoginRequest, RegisterRequest } from '../types';

const TUTORIAL_COMPLETED_KEY = '@sock_graveyard_tutorial_completed';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  tutorialCompleted: boolean;
  login: (data: LoginRequest) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => Promise<void>;
  completeTutorial: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [tutorialCompleted, setTutorialCompleted] = useState(false);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const token = await getToken();
      if (token) {
        const userData = await authAPI.me();
        setUser(userData);
      }
      
      // Check if tutorial has been completed
      const tutorialStatus = await AsyncStorage.getItem(TUTORIAL_COMPLETED_KEY);
      setTutorialCompleted(tutorialStatus === 'true');
    } catch (error) {
      console.error('Auth check failed:', error);
      await removeToken();
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (data: LoginRequest) => {
    const response = await authAPI.login(data);
    await saveToken(response.access_token);
    const userData = await authAPI.me();
    setUser(userData);
  };

  const register = async (data: RegisterRequest) => {
    await authAPI.register(data);
    await login(data);
  };

  const logout = async () => {
    await removeToken();
    setUser(null);
  };

  const completeTutorial = async () => {
    await AsyncStorage.setItem(TUTORIAL_COMPLETED_KEY, 'true');
    setTutorialCompleted(true);
  };

  return (
    <AuthContext.Provider value={{ user, isLoading, tutorialCompleted, login, register, logout, completeTutorial }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
