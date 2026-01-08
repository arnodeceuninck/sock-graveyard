import 'react-native-gesture-handler';
import React, { useEffect } from 'react';
import { StatusBar } from 'expo-status-bar';
import { AuthProvider } from './src/contexts/AuthContext';
import AppNavigator from './src/navigation/AppNavigator';
import ErrorBoundary from './src/components/ErrorBoundary';
import { setupGlobalErrorHandlers } from './src/utils/errorReporting';

export default function App() {
  useEffect(() => {
    // Setup global error handlers for uncaught errors
    setupGlobalErrorHandlers();
  }, []);

  return (
    <ErrorBoundary>
      <AuthProvider>
        <AppNavigator />
        <StatusBar style="dark" />
      </AuthProvider>
    </ErrorBoundary>
  );
}
