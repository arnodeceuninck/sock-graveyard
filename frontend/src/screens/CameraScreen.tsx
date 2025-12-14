import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { useTheme } from '../contexts/ThemeContext';
import { Button } from '../components/Button';
import { Spacing, Typography } from '../constants/theme';

export default function CameraScreen({ navigation }: any) {
  const { colors } = useTheme();

  return (
    <View style={[styles.container, { backgroundColor: colors.background }]}>
      <Text style={[styles.title, { color: colors.text }]}>Camera Screen</Text>
      <Text style={[styles.subtitle, { color: colors.textSecondary }]}>
        Take a photo of your lost sock
      </Text>
      <Button
        title="Placeholder - Camera Integration Coming"
        onPress={() => {}}
        style={styles.button}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: Spacing.lg,
  },
  title: {
    fontSize: Typography.fontSize.xxl,
    fontWeight: 'bold',
    marginBottom: Spacing.sm,
  },
  subtitle: {
    fontSize: Typography.fontSize.md,
    marginBottom: Spacing.xl,
    textAlign: 'center',
  },
  button: {
    minWidth: 200,
  },
});
