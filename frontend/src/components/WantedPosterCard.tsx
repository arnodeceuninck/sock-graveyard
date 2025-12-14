import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ViewStyle, TextStyle } from 'react-native';
import { useTheme } from '../contexts/ThemeContext';
import { BorderRadius, Shadow, Spacing, Typography } from '../constants/theme';

interface WantedPosterCardProps {
  title: string;
  subtitle?: string;
  reward?: string;
  children: React.ReactNode;
  onPress?: () => void;
  style?: ViewStyle;
}

export const WantedPosterCard: React.FC<WantedPosterCardProps> = ({
  title,
  subtitle,
  reward,
  children,
  onPress,
  style,
}) => {
  const { colors } = useTheme();

  const Container = onPress ? TouchableOpacity : View;

  return (
    <Container
      onPress={onPress}
      style={[
        styles.container,
        {
          backgroundColor: colors.surface,
          borderColor: colors.border,
        },
        Shadow.large,
        style,
      ]}
      activeOpacity={onPress ? 0.7 : 1}
    >
      {/* Decorative corners */}
      <View style={[styles.cornerTL, { borderColor: colors.wanted }]} />
      <View style={[styles.cornerTR, { borderColor: colors.wanted }]} />
      <View style={[styles.cornerBL, { borderColor: colors.wanted }]} />
      <View style={[styles.cornerBR, { borderColor: colors.wanted }]} />

      {/* Header */}
      <View style={styles.header}>
        <Text style={[styles.wanted, { color: colors.wanted }]}>WANTED</Text>
        <Text style={[styles.title, { color: colors.text }]}>{title}</Text>
        {subtitle && (
          <Text style={[styles.subtitle, { color: colors.textSecondary }]}>
            {subtitle}
          </Text>
        )}
      </View>

      {/* Content */}
      <View style={styles.content}>{children}</View>

      {/* Reward banner */}
      {reward && (
        <View style={[styles.rewardBanner, { backgroundColor: colors.stamp }]}>
          <Text style={[styles.rewardText, { color: colors.surface }]}>
            REWARD: {reward}
          </Text>
        </View>
      )}
    </Container>
  );
};

const styles = StyleSheet.create({
  container: {
    borderWidth: 3,
    borderRadius: BorderRadius.lg,
    padding: Spacing.lg,
    margin: Spacing.md,
    position: 'relative',
  },
  cornerTL: {
    position: 'absolute',
    top: -2,
    left: -2,
    width: 20,
    height: 20,
    borderTopWidth: 4,
    borderLeftWidth: 4,
  },
  cornerTR: {
    position: 'absolute',
    top: -2,
    right: -2,
    width: 20,
    height: 20,
    borderTopWidth: 4,
    borderRightWidth: 4,
  },
  cornerBL: {
    position: 'absolute',
    bottom: -2,
    left: -2,
    width: 20,
    height: 20,
    borderBottomWidth: 4,
    borderLeftWidth: 4,
  },
  cornerBR: {
    position: 'absolute',
    bottom: -2,
    right: -2,
    width: 20,
    height: 20,
    borderBottomWidth: 4,
    borderRightWidth: 4,
  },
  header: {
    alignItems: 'center',
    marginBottom: Spacing.md,
    borderBottomWidth: 2,
    borderBottomColor: '#00000020',
    paddingBottom: Spacing.md,
  },
  wanted: {
    fontSize: Typography.fontSize.xxl,
    fontWeight: 'bold',
    letterSpacing: 4,
    textTransform: 'uppercase',
  },
  title: {
    fontSize: Typography.fontSize.xl,
    fontWeight: '600',
    marginTop: Spacing.xs,
    textAlign: 'center',
  },
  subtitle: {
    fontSize: Typography.fontSize.sm,
    marginTop: Spacing.xs,
    textAlign: 'center',
  },
  content: {
    marginVertical: Spacing.md,
  },
  rewardBanner: {
    position: 'absolute',
    bottom: -10,
    right: 20,
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.xs,
    borderRadius: BorderRadius.sm,
    transform: [{ rotate: '5deg' }],
  },
  rewardText: {
    fontSize: Typography.fontSize.sm,
    fontWeight: 'bold',
    letterSpacing: 1,
  },
});
