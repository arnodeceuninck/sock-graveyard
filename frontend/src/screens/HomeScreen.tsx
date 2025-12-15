import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, FlatList, RefreshControl, Image } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useTheme } from '../contexts/ThemeContext';
import { useAuth } from '../contexts/AuthContext';
import ApiService from '../services/api';
import { API_BASE_URL } from '../constants/theme';
import { WantedPosterCard } from '../components/WantedPosterCard';
import { Button } from '../components/Button';
import { Spacing, Typography } from '../constants/theme';

export default function HomeScreen({ navigation }: any) {
  const [socks, setSocks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [authToken, setAuthToken] = useState<string | null>(null);
  
  const { colors } = useTheme();
  const { user } = useAuth();

  useEffect(() => {
    loadSocks();
    loadAuthToken();
  }, []);

  const loadAuthToken = async () => {
    const token = await AsyncStorage.getItem('auth_token');
    setAuthToken(token);
  };

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

  const getImageUrl = (sockId: number) => {
    // Get processed image (without background) with token in query string
    // This is needed because React Native Image component on web doesn't support headers
    const baseUrl = `${API_BASE_URL}/socks/${sockId}/image?processed=true`;
    return authToken ? `${baseUrl}&token=${authToken}` : baseUrl;
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
                // Navigate to sock detail screen
                navigation.navigate('SockDetail', { sockId: item.id });
              }}
            >
              <View style={styles.sockContent}>
                {/* Sock Image */}
                <View style={[styles.imageContainer, { borderColor: colors.border }]}>
                  <Image
                    source={{ uri: getImageUrl(item.id) }}
                    style={styles.sockImage}
                    resizeMode="contain"
                  />
                </View>

                {/* Sock Info */}
                <View style={styles.sockInfo}>
                  <View style={[styles.colorSwatch, { backgroundColor: item.dominant_color }]} />
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
  sockContent: {
    flexDirection: 'row',
    gap: Spacing.md,
    alignItems: 'center',
  },
  imageContainer: {
    width: 120,
    height: 120,
    borderWidth: 2,
    borderRadius: 8,
    padding: Spacing.xs,
    backgroundColor: '#fff',
    justifyContent: 'center',
    alignItems: 'center',
  },
  sockImage: {
    width: '100%',
    height: '100%',
  },
  sockInfo: {
    flex: 1,
    gap: Spacing.xs,
  },
  colorSwatch: {
    width: 24,
    height: 24,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: '#8B4513',
    marginBottom: Spacing.xs,
  },
  infoText: {
    fontSize: Typography.fontSize.md,
  },
});
