import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  Alert,
} from 'react-native';
import { useAuth } from '../contexts/AuthContext';
import { useTheme } from '../contexts/ThemeContext';
import { Button } from '../components/Button';
import { Spacing, Typography, BorderRadius } from '../constants/theme';

export default function LoginScreen({ navigation }: any) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  
  const { login } = useAuth();
  const { colors } = useTheme();

  const handleLogin = async () => {
    if (!username || !password) {
      Alert.alert('Error', 'Please fill in all fields');
      return;
    }

    setLoading(true);
    try {
      await login(username, password);
    } catch (error: any) {
      Alert.alert('Login Failed', error.response?.data?.detail || 'Invalid credentials');
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      style={[styles.container, { backgroundColor: colors.background }]}
    >
      <ScrollView contentContainerStyle={styles.scrollContent}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={[styles.wanted, { color: colors.wanted }]}>WANTED</Text>
          <Text style={[styles.title, { color: colors.text }]}>
            SOCK GRAVEYARD
          </Text>
          <Text style={[styles.subtitle, { color: colors.textSecondary }]}>
            Find Your Missing Socks
          </Text>
        </View>

        {/* Form */}
        <View style={[styles.form, { backgroundColor: colors.surface }]}>
          <Text style={[styles.label, { color: colors.text }]}>Username</Text>
          <TextInput
            style={[
              styles.input,
              {
                backgroundColor: colors.background,
                color: colors.text,
                borderColor: colors.border,
              },
            ]}
            value={username}
            onChangeText={setUsername}
            autoCapitalize="none"
            placeholder="Enter username"
            placeholderTextColor={colors.textSecondary}
          />

          <Text style={[styles.label, { color: colors.text }]}>Password</Text>
          <TextInput
            style={[
              styles.input,
              {
                backgroundColor: colors.background,
                color: colors.text,
                borderColor: colors.border,
              },
            ]}
            value={password}
            onChangeText={setPassword}
            secureTextEntry
            placeholder="Enter password"
            placeholderTextColor={colors.textSecondary}
          />

          <Button
            title="Login"
            onPress={handleLogin}
            loading={loading}
            style={styles.button}
          />

          <Button
            title="Create Account"
            onPress={() => navigation.navigate('Register')}
            variant="outline"
            style={styles.button}
          />
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    justifyContent: 'center',
    padding: Spacing.lg,
  },
  header: {
    alignItems: 'center',
    marginBottom: Spacing.xl,
  },
  wanted: {
    fontSize: Typography.fontSize.poster,
    fontWeight: 'bold',
    letterSpacing: 8,
  },
  title: {
    fontSize: Typography.fontSize.xxl,
    fontWeight: 'bold',
    marginTop: Spacing.sm,
  },
  subtitle: {
    fontSize: Typography.fontSize.md,
    marginTop: Spacing.xs,
  },
  form: {
    padding: Spacing.lg,
    borderRadius: BorderRadius.lg,
    borderWidth: 3,
  },
  label: {
    fontSize: Typography.fontSize.md,
    fontWeight: '600',
    marginBottom: Spacing.xs,
    marginTop: Spacing.md,
  },
  input: {
    borderWidth: 2,
    borderRadius: BorderRadius.md,
    padding: Spacing.md,
    fontSize: Typography.fontSize.md,
  },
  button: {
    marginTop: Spacing.lg,
  },
});
