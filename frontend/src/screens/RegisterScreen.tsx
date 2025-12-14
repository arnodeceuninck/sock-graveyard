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

export default function RegisterScreen({ navigation }: any) {
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  
  const { register } = useAuth();
  const { colors } = useTheme();

  const handleRegister = async () => {
    if (!email || !username || !password || !confirmPassword) {
      Alert.alert('Error', 'Please fill in all fields');
      return;
    }

    if (password !== confirmPassword) {
      Alert.alert('Error', 'Passwords do not match');
      return;
    }

    if (password.length < 8) {
      Alert.alert('Error', 'Password must be at least 8 characters');
      return;
    }

    setLoading(true);
    try {
      await register(email, username, password);
    } catch (error: any) {
      Alert.alert(
        'Registration Failed',
        error.response?.data?.detail || 'Could not create account'
      );
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
          <Text style={[styles.wanted, { color: colors.wanted }]}>JOIN THE HUNT</Text>
          <Text style={[styles.subtitle, { color: colors.textSecondary }]}>
            Create Your Account
          </Text>
        </View>

        {/* Form */}
        <View style={[styles.form, { backgroundColor: colors.surface }]}>
          <Text style={[styles.label, { color: colors.text }]}>Email</Text>
          <TextInput
            style={[
              styles.input,
              {
                backgroundColor: colors.background,
                color: colors.text,
                borderColor: colors.border,
              },
            ]}
            value={email}
            onChangeText={setEmail}
            autoCapitalize="none"
            keyboardType="email-address"
            placeholder="your@email.com"
            placeholderTextColor={colors.textSecondary}
          />

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
            placeholder="Choose a username"
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
            placeholder="At least 8 characters"
            placeholderTextColor={colors.textSecondary}
          />

          <Text style={[styles.label, { color: colors.text }]}>
            Confirm Password
          </Text>
          <TextInput
            style={[
              styles.input,
              {
                backgroundColor: colors.background,
                color: colors.text,
                borderColor: colors.border,
              },
            ]}
            value={confirmPassword}
            onChangeText={setConfirmPassword}
            secureTextEntry
            placeholder="Re-enter password"
            placeholderTextColor={colors.textSecondary}
          />

          <Button
            title="Create Account"
            onPress={handleRegister}
            loading={loading}
            style={styles.button}
          />

          <Button
            title="Back to Login"
            onPress={() => navigation.goBack()}
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
    letterSpacing: 6,
  },
  subtitle: {
    fontSize: Typography.fontSize.md,
    marginTop: Spacing.sm,
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
