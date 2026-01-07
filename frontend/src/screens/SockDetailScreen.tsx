import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  ActivityIndicator,
  TouchableOpacity,
  Platform,
} from 'react-native';
import { Image } from 'expo-image';
import { socksAPI, getToken, getTokenSync } from '../services/api';
import { Sock, SockMatch } from '../types';
import SimilarSocksList from '../components/SimilarSocksList';
import GravestoneWithSock from '../components/GravestoneWithSock';
import { theme, GHOST_EMOJIS, SOCK_EMOJIS } from '../theme';
import { Alert } from '../utils/alert';

export default function SockDetailScreen({ route, navigation }: any) {
  const { sockId } = route.params;
  const [sock, setSock] = useState<Sock | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSearching, setIsSearching] = useState(false);
  const [similarSocks, setSimilarSocks] = useState<SockMatch[]>([]);
  const [showResults, setShowResults] = useState(false);
  const [authToken, setAuthToken] = useState<string>('');

  useEffect(() => {
    loadSock();
  }, [sockId]);

  useEffect(() => {
    // Automatically search for similar socks once sock is loaded
    if (sock && !isSearching && !showResults) {
      findSimilarSocks();
    }
  }, [sock]);

  const loadSock = async () => {
    try {
      // Get auth token for image URLs
      if (Platform.OS === 'web') {
        try {
          const token = getTokenSync();
          setAuthToken(token ?? '');
        } catch (e) {
          console.warn('[SockDetailScreen] Could not get token on web');
        }
      } else {
        const token = await getToken();
        setAuthToken(token ?? '');
      }
      
      const data = await socksAPI.get(sockId);
      setSock(data);
    } catch (error: any) {
      Alert.alert('Error', 'Failed to load sock details');
      navigation.goBack();
    } finally {
      setIsLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const findSimilarSocks = async () => {
    if (!sock) return;

    setIsSearching(true);
    try {
      // Use the sock ID search endpoint (uses stored embedding)
      const matches = await socksAPI.searchBySockId(sock.id);
      setSimilarSocks(matches);
      setShowResults(true);
    } catch (error: any) {
      Alert.alert('Search Failed', error.message || 'Failed to search for similar socks');
    } finally {
      setIsSearching(false);
    }
  };

  const handleDelete = () => {
    if (!sock) return;

    Alert.alert(
      'Delete Sock',
      'Are you sure you want to delete this sock? This action cannot be undone.',
      [
        {
          text: 'Cancel',
          style: 'cancel',
        },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: async () => {
            try {
              await socksAPI.delete(sock.id);
              navigation.goBack();
            } catch (error: any) {
              Alert.alert('Error', error.message || 'Failed to delete sock');
            }
          },
        },
      ]
    );
  };

  const viewSockDetail = (sockId: number) => {
    // Reset the search results when navigating
    setSimilarSocks([]);
    setShowResults(false);
    navigation.push('SockDetail', { sockId });
  };

  if (isLoading) {
    return (
      <View style={styles.centerContainer}>
        <Text style={styles.loadingEmoji}>{GHOST_EMOJIS.search}</Text>
        <ActivityIndicator size="large" color={theme.colors.primary} />
        <Text style={styles.loadingText}>Summoning from the graveyard...</Text>
      </View>
    );
  }

  if (!sock) {
    return (
      <View style={styles.centerContainer}>
        <Text style={styles.errorText}>Sock not found</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <Image
        source={{
          uri: socksAPI.getImageUrl(sock.id, authToken),
        }}
        style={styles.image}
        cachePolicy="memory-disk"
        contentFit="cover"
        transition={300}
        priority="high"
      />

      <View style={styles.content}>
        <View style={styles.header}>
          <View style={styles.titleContainer}>
            <Text style={styles.titleEmoji}>{SOCK_EMOJIS.ghost}</Text>
            <Text style={styles.title}>Soul #{sock.id}</Text>
          </View>
          <View style={[styles.badge, sock.is_matched ? styles.matchedBadge : styles.unmatchedBadge]}>
            <Text style={styles.badgeText}>
              {sock.is_matched ? '✓ Reunited' : '⏳ Wandering'}
            </Text>
          </View>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Eternal Record</Text>

          <GravestoneWithSock
            sockImageUri={socksAPI.getImageNoBgUrl(sock.id, authToken)}
            style={styles.gravestoneWrapper}
            gravestoneStyle={styles.gravestoneImage}
            sockStyle={styles.sockOnGravestone}
          />
          
          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>Entered Graveyard:</Text>
            <Text style={styles.detailValue}>{formatDate(sock.created_at)}</Text>
          </View>

          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>Time of Arrival:</Text>
            <Text style={styles.detailValue}>{formatTime(sock.created_at)}</Text>
          </View>

          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>Status:</Text>
            <Text style={styles.detailValue}>
              {sock.is_matched ? 'Matched' : 'Unmatched'}
            </Text>
          </View>

          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>Owner ID:</Text>
            <Text style={styles.detailValue}>{sock.owner_id}</Text>
          </View>
        </View>

        {!showResults && (
          <View style={styles.actions}>
            <TouchableOpacity
              style={[styles.actionButton, isSearching && styles.buttonDisabled]}
              onPress={findSimilarSocks}
              disabled={isSearching}
            >
              <Text style={styles.actionButtonEmoji}>{GHOST_EMOJIS.search}</Text>
              <Text style={styles.actionButtonText}>
                {isSearching ? 'Searching...' : 'Seek Reunion'}
              </Text>
            </TouchableOpacity>
          </View>
        )}

        {isSearching && (
          <View style={styles.loadingContainer}>
            <Text style={styles.searchingEmoji}>{GHOST_EMOJIS.search}</Text>
            <ActivityIndicator size="large" color={theme.colors.primary} />
            <Text style={styles.searchingText}>Seeking lost souls...</Text>
          </View>
        )}

        {showResults && !isSearching && (
          <SimilarSocksList
            matches={similarSocks}
            onSockPress={viewSockDetail}
            showNoMatchMessage={false}
            sourceSockId={sock.id}
            authToken={authToken}
            onMatchCreated={(matchId) => {
              // Replace current screen with match detail so back goes to socks list
              navigation.replace('MatchDetail', { matchId });
            }}
          />
        )}

        {!sock.is_matched && (
          <View style={styles.deleteSection}>
            <TouchableOpacity
              style={[styles.deleteButton, isSearching && styles.buttonDisabled]}
              onPress={handleDelete}
              disabled={isSearching}
            >
              <Text style={styles.deleteButtonEmoji}>☠️</Text>
              <Text style={styles.deleteButtonText}>
                Release from Graveyard
              </Text>
            </TouchableOpacity>
          </View>
        )}
      </View>
    </ScrollView>
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
  loadingText: {
    marginTop: theme.spacing.md,
    color: theme.colors.textSecondary,
    fontSize: 16,
  },
  errorText: {
    fontSize: 16,
    color: theme.colors.textMuted,
  },
  image: {
    width: '100%',
    maxWidth: 500,
    aspectRatio: 1,
    backgroundColor: theme.colors.surfaceLight,
    alignSelf: 'center',
    borderBottomWidth: 2,
    borderBottomColor: theme.colors.tombstone,
  },
  content: {
    padding: theme.spacing.lg,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: theme.spacing.lg,
  },
  titleContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: theme.spacing.sm,
  },
  titleEmoji: {
    fontSize: 32,
  },
  title: {
    ...theme.typography.h2,
    color: theme.colors.primary,
    textShadowColor: theme.colors.ghostGlow,
    textShadowOffset: { width: 0, height: 0 },
    textShadowRadius: 10,
  },
  badge: {
    paddingHorizontal: theme.spacing.md,
    paddingVertical: theme.spacing.xs,
    borderRadius: theme.borderRadius.round,
  },
  matchedBadge: {
    backgroundColor: theme.colors.success,
  },
  unmatchedBadge: {
    backgroundColor: theme.colors.warning,
  },
  badgeText: {
    color: theme.colors.textInverse,
    fontSize: 12,
    fontWeight: '600',
  },
  section: {
    backgroundColor: theme.colors.surface,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.lg,
    marginBottom: theme.spacing.lg,
    borderWidth: 1,
    borderColor: theme.colors.tombstone,
  },
  sectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: theme.spacing.sm,
    marginBottom: theme.spacing.md,
  },
  tombstoneIcon: {
    width: 32,
    height: 32,
  },
  sectionTitle: {
    ...theme.typography.h3,
    color: theme.colors.accent,
    marginBottom: theme.spacing.sm,
  },
  gravestoneWrapper: {
    width: '50%',
    maxWidth: 250,
    marginBottom: theme.spacing.sm,
    marginTop: -theme.spacing.sm,
  },
  gravestoneImage: {
    // Applied to gravestone image in component
  },
  sockOnGravestone: {
    // Applied to sock image in component
  },
  detailRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: theme.spacing.sm,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.tombstone,
  },
  detailLabel: {
    fontSize: 14,
    color: theme.colors.textMuted,
  },
  detailValue: {
    fontSize: 14,
    color: theme.colors.text,
    fontWeight: '500',
    textAlign: 'right',
    flex: 1,
    marginLeft: theme.spacing.sm,
  },
  actions: {
    marginTop: theme.spacing.sm,
  },
  deleteSection: {
    marginTop: theme.spacing.lg,
  },
  actionButton: {
    backgroundColor: theme.colors.primary,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.md,
    alignItems: 'center',
    marginBottom: theme.spacing.sm,
    flexDirection: 'row',
    justifyContent: 'center',
    gap: theme.spacing.sm,
    ...theme.shadows.medium,
  },
  actionButtonEmoji: {
    fontSize: 24,
  },
  deleteButton: {
    backgroundColor: theme.colors.danger,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.md,
    alignItems: 'center',
    flexDirection: 'row',
    justifyContent: 'center',
    gap: theme.spacing.sm,
    ...theme.shadows.medium,
  },
  deleteButtonEmoji: {
    fontSize: 24,
  },
  buttonDisabled: {
    opacity: 0.6,
  },
  actionButtonText: {
    color: theme.colors.textInverse,
    fontSize: 16,
    fontWeight: '600',
  },
  deleteButtonText: {
    color: theme.colors.ghostWhite,
    fontSize: 16,
    fontWeight: '600',
  },
  loadingContainer: {
    alignItems: 'center',
    marginTop: theme.spacing.lg,
  },
  searchingEmoji: {
    fontSize: 56,
    marginBottom: theme.spacing.md,
  },
  searchingText: {
    marginTop: theme.spacing.sm,
    color: theme.colors.textSecondary,
    fontSize: 16,
  },
});
