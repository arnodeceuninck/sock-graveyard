import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, FlatList, RefreshControl } from 'react-native';
import { useTheme } from '../contexts/ThemeContext';
import { useAuth } from '../contexts/AuthContext';
import ApiService from '../services/api';
import { WantedPosterCard } from '../components/WantedPosterCard';
import { Button } from '../components/Button';
import { Spacing, Typography } from '../constants/theme';

export default function HomeScreen({ navigation }: any) {
  const [socks, setSocks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  
  const { colors } = useTheme();
  const { user } = useAuth();

  useEffect(() => {
    loadSocks();
  }, []);

  const loadSocks = async () => {
    setLoading(true);
    try {
      const data = await ApiService.getSocks(true); // unmatched only
      setSocks(data);
    } catch (error) {
      console.error('Failed to load socks:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleRefresh = () => {
    setRefreshing(true);
    loadSocks();
  };

  return (
    <View style={[styles.container, { backgroundColor: colors.background }]}>
      {/* Header */}
      <View style={[styles.header, { backgroundColor: colors.surface }]}>
        <Text style={[styles.title, { color: colors.wanted }]}>SOCK GRAVEYARD</Text>
        <Text style={[styles.subtitle, { color: colors.text }]}>
          Welcome, {user?.username}!
        </Text>
      </View>

      {/* Content */}
      {socks.length === 0 ? (
        <View style={styles.emptyState}>
          <Text style={[styles.emptyText, { color: colors.textSecondary }]}>
            No lonely socks yet
          </Text>
          <Text style={[styles.emptySubtext, { color: colors.textSecondary }]}>
            Take a photo to start finding matches
          </Text>
          <Button
            title="Add Your First Sock"
            onPress={() => navigation.navigate('Camera')}
            style={styles.emptyButton}
          />
        </View>
      ) : (
        <FlatList
          data={socks}
          keyExtractor={(item: any) => item.id.toString()}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={handleRefresh} />
          }
          renderItem={({ item }: any) => (
            <WantedPosterCard
              title={`Sock #${item.id}`}
              subtitle={item.description || 'No description'}
              reward="FIND YOUR MATCH"
              onPress={() => {
                // Navigate to search results
              }}
            >
              <View style={styles.sockInfo}>
                <Text style={[styles.infoText, { color: colors.text }]}>
                  Color: {item.dominant_color || 'Unknown'}
                </Text>
                <Text style={[styles.infoText, { color: colors.text }]}>
                  Pattern: {item.pattern_type || 'Unknown'}
                </Text>
                <Text style={[styles.infoText, { color: colors.textSecondary }]}>
                  Added: {new Date(item.created_at).toLocaleDateString()}
                </Text>
              </View>
            </WantedPosterCard>
          )}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  header: {
    padding: Spacing.lg,
    paddingTop: Spacing.xxl,
    alignItems: 'center',
    borderBottomWidth: 3,
  },
  title: {
    fontSize: Typography.fontSize.xxl,
    fontWeight: 'bold',
    letterSpacing: 4,
  },
  subtitle: {
    fontSize: Typography.fontSize.md,
    marginTop: Spacing.xs,
  },
  emptyState: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: Spacing.xl,
  },
  emptyText: {
    fontSize: Typography.fontSize.xl,
    fontWeight: 'bold',
    marginBottom: Spacing.sm,
  },
  emptySubtext: {
    fontSize: Typography.fontSize.md,
    marginBottom: Spacing.xl,
    textAlign: 'center',
  },
  emptyButton: {
    minWidth: 200,
  },
  sockInfo: {
    gap: Spacing.xs,
  },
  infoText: {
    fontSize: Typography.fontSize.md,
  },
});
