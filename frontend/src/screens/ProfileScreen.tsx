import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { useTheme } from '../contexts/ThemeContext';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '../components/Button';
import { Spacing, Typography } from '../constants/theme';

export default function ProfileScreen() {
  const { colors, toggleTheme, isDark } = useTheme();
  const { user, logout } = useAuth();

  return (
    <ScrollView style={[styles.container, { backgroundColor: colors.background }]}>
      <View style={styles.content}>
        <Text style={[styles.title, { color: colors.text }]}>Profile</Text>
        
        <View style={[styles.card, { backgroundColor: colors.surface }]}>
          <Text style={[styles.label, { color: colors.textSecondary }]}>
            Username
          </Text>
          <Text style={[styles.value, { color: colors.text }]}>
            {user?.username}
          </Text>
          
          <Text style={[styles.label, { color: colors.textSecondary }]}>
            Email
          </Text>
          <Text style={[styles.value, { color: colors.text }]}>
            {user?.email}
          </Text>
        </View>

        <Button
          title={`Theme: ${isDark ? 'Dark' : 'Light'}`}
          onPress={toggleTheme}
          variant="secondary"
          style={styles.button}
        />

        <Button
          title="Logout"
          onPress={logout}
          variant="danger"
          style={styles.button}
        />
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  content: {
    padding: Spacing.lg,
    paddingTop: Spacing.xxl,
  },
  title: {
    fontSize: Typography.fontSize.xxl,
    fontWeight: 'bold',
    marginBottom: Spacing.lg,
  },
  card: {
    padding: Spacing.lg,
    borderRadius: 8,
    marginBottom: Spacing.lg,
  },
  label: {
    fontSize: Typography.fontSize.sm,
    marginTop: Spacing.md,
    marginBottom: Spacing.xs,
  },
  value: {
    fontSize: Typography.fontSize.lg,
    fontWeight: '600',
  },
  button: {
    marginBottom: Spacing.md,
  },
});
