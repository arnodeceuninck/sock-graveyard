import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  ActivityIndicator,
  TouchableOpacity,
  Image,
  Platform,
} from 'react-native';
import { matchesAPI, socksAPI, getToken, getTokenSync } from '../services/api';
import { Match } from '../types';
import { theme, GHOST_EMOJIS, SOCK_EMOJIS } from '../theme';
import { Alert } from '../utils/alert';

export default function MatchesScreen({ navigation }: any) {
  const [matches, setMatches] = useState<Match[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [authToken, setAuthToken] = useState<string>('');

  useEffect(() => {
    const unsubscribe = navigation.addListener('focus', () => {
      loadMatches();
    });

    return unsubscribe;
  }, [navigation]);

  const loadMatches = async () => {
    setIsLoading(true);
    try {
      // Get auth token for image URLs
      if (Platform.OS === 'web') {
        try {
          const token = getTokenSync();
          setAuthToken(token);
        } catch (e) {
          console.warn('[MatchesScreen] Could not get token on web');
        }
      } else {
        const token = await getToken();
        setAuthToken(token || '');
      }
      
      const data = await matchesAPI.list();
      setMatches(data);
    } catch (error: any) {
      Alert.alert('Error', 'Failed to load matches');
    } finally {
      setIsLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  const renderMatchItem = ({ item }: { item: Match }) => (
    <TouchableOpacity
      style={styles.matchCard}
      onPress={() => navigation.navigate('MatchDetail', { matchId: item.id })}
    >
      <View style={styles.matchImages}>
        <Image
          source={{ uri: socksAPI.getImageUrl(item.sock1_id, authToken) }}
          style={styles.sockImage}
        />
        <View style={styles.heartContainer}>
          <Image
            source={require('../../assets/matches.png')}
            style={styles.matchIconImage}
          />
        </View>
        <Image
          source={{ uri: socksAPI.getImageUrl(item.sock2_id, authToken) }}
          style={styles.sockImage}
        />
      </View>
      <View style={styles.matchInfo}>
        <Text style={styles.matchTitle}>Soul Mates #{item.id}</Text>
        <Text style={styles.matchDate}>United {formatDate(item.matched_at)}</Text>
      </View>
    </TouchableOpacity>
  );

  if (isLoading) {
    return (
      <View style={styles.centerContainer}>
        <Image
          source={require('../../assets/matches.png')}
          style={styles.loadingIcon}
        />
        <ActivityIndicator size="large" color={theme.colors.ghostWhite} />
        <Text style={styles.loadingText}>Seeking soul mates...</Text>
      </View>
    );
  }

  if (matches.length === 0) {
    return (
      <View style={styles.centerContainer}>
        <Image
          source={require('../../assets/sad.png')}
          style={styles.emptyImage}
        />
        <Text style={styles.emptyTitle}>No Reunions Yet</Text>
        <Text style={styles.emptyText}>
          When lost souls find their match, they'll rest here in eternal peace.
        </Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <FlatList
        data={matches}
        renderItem={renderMatchItem}
        keyExtractor={(item) => item.id.toString()}
        contentContainerStyle={styles.listContent}
      />
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
    padding: theme.spacing.lg,
  },
  loadingIcon: {
    width: 72,
    height: 72,
    marginBottom: theme.spacing.md,
  },
  loadingText: {
    marginTop: theme.spacing.md,
    color: theme.colors.textSecondary,
    fontSize: 16,
  },
  emptyIcon: {
    fontSize: 96,
    marginBottom: theme.spacing.lg,
  },
  emptyImage: {
    width: 150,
    height: 150,
    marginBottom: theme.spacing.lg,
  },
  emptyTitle: {
    ...theme.typography.h2,
    color: theme.colors.text,
    marginBottom: theme.spacing.sm,
    textAlign: 'center',
  },
  emptyText: {
    fontSize: 16,
    color: theme.colors.textSecondary,
    textAlign: 'center',
    lineHeight: 22,
    fontStyle: 'italic',
  },
  listContent: {
    padding: theme.spacing.md,
  },
  matchCard: {
    backgroundColor: theme.colors.surface,
    borderRadius: theme.borderRadius.lg,
    padding: theme.spacing.lg,
    marginBottom: theme.spacing.md,
    borderWidth: 1,
    borderColor: theme.colors.ghostWhite,
    ...theme.shadows.large,
    shadowColor: theme.colors.ghostWhite,
  },
  matchImages: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: theme.spacing.md,
  },
  sockImage: {
    width: 120,
    height: 120,
    borderRadius: theme.borderRadius.md,
    backgroundColor: theme.colors.surfaceLight,
    borderWidth: 2,
    borderColor: theme.colors.tombstone,
  },
  heartContainer: {
    marginHorizontal: theme.spacing.md,
    alignItems: 'center',
    justifyContent: 'center',
  },
  matchIconImage: {
    width: 40,
    height: 40,
  },
  matchInfo: {
    alignItems: 'center',
  },
  matchTitle: {
    ...theme.typography.h3,
    color: theme.colors.ghostWhite,
    marginBottom: theme.spacing.xs,
    textShadowColor: 'rgba(240, 240, 255, 0.3)',
    textShadowOffset: { width: 0, height: 0 },
    textShadowRadius: 10,
  },
  matchDate: {
    fontSize: 14,
    color: theme.colors.textSecondary,
    fontStyle: 'italic',
  },
});
