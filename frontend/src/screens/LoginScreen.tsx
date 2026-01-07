import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  Image,
} from 'react-native';
import { useAuth } from '../contexts/AuthContext';
import { theme, SOCK_EMOJIS } from '../theme';
import { Alert } from '../utils/alert';

export default function LoginScreen({ navigation }: any) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();

  const handleLogin = async () => {
    if (!username.trim() || !password) {
      Alert.alert('Error', 'Please enter username and password');
      return;
    }

    setIsLoading(true);
    try {
      await login({ username: username.trim(), password });
    } catch (error: any) {
      Alert.alert('Login Failed', error.response?.data?.detail || 'Invalid credentials');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      style={styles.container}
    >
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.content}>
          <Image
            source={require('../../assets/banner.png')}
            style={styles.banner}
            resizeMode="contain"
          />
          <Text style={styles.title}>Sock Graveyard</Text>
          <Text style={styles.subtitle}>Login to prevent your lost socks from dying alone</Text>

          <View style={styles.form}>
            <TextInput
              style={styles.input}
              placeholder="Username"
              placeholderTextColor={theme.colors.textMuted}
              value={username}
              onChangeText={setUsername}
              autoCapitalize="none"
              autoCorrect={false}
            />

            <TextInput
              style={styles.input}
              placeholder="Password"
              placeholderTextColor={theme.colors.textMuted}
              value={password}
              onChangeText={setPassword}
              secureTextEntry
              autoCapitalize="none"
            />

            <TouchableOpacity
              style={[styles.button, isLoading && styles.buttonDisabled]}
              onPress={handleLogin}
              disabled={isLoading}
            >
              <Text style={styles.buttonText}>
                {isLoading ? 'Logging in...' : 'Login'}
              </Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.linkButton}
              onPress={() => navigation.navigate('Register')}
            >
              <Text style={styles.linkText}>Don't have an account? Register</Text>
            </TouchableOpacity>
          </View>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  scrollContent: {
    flexGrow: 1,
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    padding: theme.spacing.lg,
  },
  banner: {
    width: '100%',
    height: 120,
    marginBottom: theme.spacing.lg,
    alignSelf: 'center',
  },
  title: {
    ...theme.typography.h1,
    textAlign: 'center',
    marginBottom: theme.spacing.sm,
    color: theme.colors.primary,
    textShadowColor: theme.colors.ghostGlow,
    textShadowOffset: { width: 0, height: 0 },
    textShadowRadius: 20,
  },
  subtitle: {
    fontSize: 16,
    textAlign: 'center',
    marginBottom: theme.spacing.xxl,
    color: theme.colors.textSecondary,
    fontStyle: 'italic',
  },
  form: {
    width: '100%',
  },
  input: {
    backgroundColor: theme.colors.surface,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.md,
    marginBottom: theme.spacing.md,
    fontSize: 16,
    borderWidth: 1,
    borderColor: theme.colors.tombstone,
    color: theme.colors.text,
  },
  button: {
    backgroundColor: theme.colors.primary,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.md,
    alignItems: 'center',
    marginTop: theme.spacing.sm,
    ...theme.shadows.medium,
  },
  buttonDisabled: {
    opacity: 0.6,
  },
  buttonText: {
    ...theme.typography.button,
    color: theme.colors.textInverse,
  },
  linkButton: {
    marginTop: theme.spacing.lg,
    alignItems: 'center',
  },
  linkText: {
    color: theme.colors.accent,
    fontSize: 14,
  },
});
