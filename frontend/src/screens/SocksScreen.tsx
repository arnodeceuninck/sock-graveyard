import React, { useState, useCallback } from 'react';
import {
  View,
  Text,
  FlatList,
  Image,
  TouchableOpacity,
  StyleSheet,
  RefreshControl,
  ActivityIndicator,
  useWindowDimensions,
  Platform,
} from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import { socksAPI, getToken, getTokenSync } from '../services/api';
import { Sock } from '../types';
import { theme, GHOST_EMOJIS, SOCK_EMOJIS } from '../theme';

export default function SocksScreen({ navigation }: any) {
  const [socks, setSocks] = useState<Sock[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [authToken, setAuthToken] = useState<string>('');
  const { width } = useWindowDimensions();
  
  // Calculate number of columns based on screen width
  // Each card should be around 300-350px
  const numColumns = Math.max(2, Math.min(6, Math.floor(width / 320)));

  const loadSocks = async () => {
    try {
      // Get auth token for image URLs
      if (Platform.OS === 'web') {
        try {
          const token = getTokenSync();
          setAuthToken(token);
        } catch (e) {
          console.warn('[SocksScreen] Could not get token on web');
        }
      } else {
        const token = await getToken();
        setAuthToken(token || '');
      }
      
      const data = await socksAPI.list();
      setSocks(data);
    } catch (error) {
      console.error('Failed to load socks:', error);
    } finally {
      setIsLoading(false);
      setRefreshing(false);
    }
  };

  useFocusEffect(
    useCallback(() => {
      loadSocks();
    }, [])
  );

  const onRefresh = () => {
    setRefreshing(true);
    loadSocks();
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const renderSockItem = ({ item }: { item: Sock }) => {
    // Calculate card width to fit columns with proper spacing
    const cardWidth = (width - 40) / numColumns - 20; // Subtract padding and margins
    
    return (
      <TouchableOpacity
        style={[styles.sockCard, { width: cardWidth }]}
        onPress={() => navigation.navigate('SockDetail', { sockId: item.id })}
      >
        <Image
          source={{
            uri: socksAPI.getImageUrl(item.id, authToken),
          }}
          style={styles.sockImage}
        />
        <View style={styles.sockInfo}>
          <Text style={styles.sockId}>Sock #{item.id}</Text>
          <Text style={styles.sockDate}>Added {formatDate(item.created_at)}</Text>
        </View>
      </TouchableOpacity>
    );
  };

  if (isLoading) {
    return (
      <View style={styles.centerContainer}>
        <Image
          source={require('../../assets/singles.png')}
          style={styles.loadingImage}
        />
        <ActivityIndicator size="large" color={theme.colors.primary} />
        <Text style={styles.loadingText}>Searching the graveyard...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <View style={styles.headerTop}>
          <Image
            source={require('../../assets/single.png')}
            style={styles.headerIcon}
          />
          <Text style={styles.title}>Singles</Text>
        </View>
        <Text style={styles.count}>
          {socks.length} lonely sock{socks.length !== 1 ? 's' : ''} seeking their soul mate
        </Text>
      </View>

      {socks.length === 0 ? (
        <View style={styles.emptyContainer}>
          <Text style={styles.emptyEmoji}>{SOCK_EMOJIS.ghost}</Text>
          <Text style={styles.emptyTitle}>The graveyard is empty...</Text>
          <Text style={styles.emptySubtitle}>
            No lost souls yet. Lay your first sock to rest.
          </Text>
          <TouchableOpacity
            style={styles.uploadButton}
            onPress={() => navigation.navigate('Upload')}
          >
            <Text style={styles.uploadButtonEmoji}>{SOCK_EMOJIS.rip}</Text>
            <Text style={styles.uploadButtonText}>Bury a Sock</Text>
          </TouchableOpacity>
        </View>
      ) : (
        <FlatList
          data={socks}
          renderItem={renderSockItem}
          keyExtractor={(item) => item.id.toString()}
          key={numColumns}
          numColumns={numColumns}
          contentContainerStyle={styles.list}
          columnWrapperStyle={styles.columnWrapper}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
          }
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: theme.colors.background,
  },
  loadingEmoji: {
    fontSize: 72,
    marginBottom: theme.spacing.md,
  },
  loadingImage: {
    width: 120,
    height: 120,
    marginBottom: theme.spacing.md,
  },
  loadingText: {
    marginTop: theme.spacing.md,
    color: theme.colors.textSecondary,
    fontSize: 16,
  },
  header: {
    padding: theme.spacing.lg,
    backgroundColor: theme.colors.surface,
    borderBottomWidth: 2,
    borderBottomColor: theme.colors.tombstone,
  },
  headerTop: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: theme.spacing.sm,
  },
  headerIcon: {
    width: 32,
    height: 32,
  },
  title: {
    ...theme.typography.h2,
    color: theme.colors.primary,
    textShadowColor: theme.colors.ghostGlow,
    textShadowOffset: { width: 0, height: 0 },
    textShadowRadius: 10,
  },
  count: {
    fontSize: 14,
    color: theme.colors.textSecondary,
    marginTop: theme.spacing.xs,
    fontStyle: 'italic',
  },
  list: {
    padding: theme.spacing.sm,
  },
  columnWrapper: {
    justifyContent: 'space-evenly',
  },
  sockCard: {
    margin: theme.spacing.sm,
    backgroundColor: theme.colors.surface,
    borderRadius: theme.borderRadius.md,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: theme.colors.tombstone,
    ...theme.shadows.medium,
  },
  sockImage: {
    width: '100%',
    aspectRatio: 1,
    backgroundColor: theme.colors.surfaceLight,
  },
  sockInfo: {
    padding: theme.spacing.md,
    backgroundColor: theme.colors.surface,
  },
  sockId: {
    fontSize: 14,
    fontWeight: '600',
    color: theme.colors.accent,
  },
  sockDate: {
    fontSize: 12,
    color: theme.colors.textMuted,
    marginTop: 2,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: theme.spacing.xxl,
  },
  emptyEmoji: {
    fontSize: 96,
    marginBottom: theme.spacing.lg,
  },
  emptyTitle: {
    ...theme.typography.h2,
    color: theme.colors.text,
    marginBottom: theme.spacing.sm,
    textAlign: 'center',
  },
  emptySubtitle: {
    fontSize: 14,
    color: theme.colors.textSecondary,
    textAlign: 'center',
    marginBottom: theme.spacing.xl,
    fontStyle: 'italic',
  },
  uploadButton: {
    backgroundColor: theme.colors.primary,
    borderRadius: theme.borderRadius.md,
    paddingVertical: theme.spacing.md,
    paddingHorizontal: theme.spacing.xl,
    flexDirection: 'row',
    alignItems: 'center',
    gap: theme.spacing.sm,
    ...theme.shadows.large,
  },
  uploadButtonEmoji: {
    fontSize: 24,
  },
  uploadButtonText: {
    ...theme.typography.button,
    color: theme.colors.textInverse,
  },
});
