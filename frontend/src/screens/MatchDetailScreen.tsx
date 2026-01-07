import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  ActivityIndicator,
  Platform,
  TouchableOpacity,
} from 'react-native';
import { Image } from 'expo-image';
import { matchesAPI, socksAPI, getToken, getTokenSync } from '../services/api';
import { Match } from '../types';
import { theme, GHOST_EMOJIS, SOCK_EMOJIS } from '../theme';
import { Alert } from '../utils/alert';

export default function MatchDetailScreen({ route, navigation }: any) {
  const { matchId } = route.params;
  const [match, setMatch] = useState<Match | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [authToken, setAuthToken] = useState<string>('');

  useEffect(() => {
    loadMatch();
  }, [matchId]);

  const loadMatch = async () => {
    try {
      // Get auth token for image URLs
      if (Platform.OS === 'web') {
        try {
          const token = getTokenSync();
          setAuthToken(token ?? '');
        } catch (e) {
          // Token retrieval failed
        }
      } else {
        const token = await getToken();
        setAuthToken(token ?? '');
      }
      
      const data = await matchesAPI.get(matchId);
      setMatch(data);
    } catch (error: any) {
      Alert.alert('Error', 'Failed to load match details');
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

  const handleDelete = (decouple: boolean) => {
    if (!match) return;

    const title = decouple ? 'Decouple Match' : 'Delete Match';
    const message = decouple
      ? 'This will break the match and move both socks back to singles. The socks will not be deleted.'
      : 'This will permanently delete both socks and the match. This action cannot be undone.';

    Alert.alert(title, message, [
      {
        text: 'Cancel',
        style: 'cancel',
      },
      {
        text: decouple ? 'Decouple' : 'Delete',
        style: 'destructive',
        onPress: async () => {
          try {
            await matchesAPI.delete(match.id, decouple);
            navigation.goBack();
          } catch (error: any) {
            Alert.alert('Error', error.message || 'Failed to delete match');
          }
        },
      },
    ]);
  };

  if (isLoading) {
    return (
      <View style={styles.centerContainer}>
        <Image
          source={require('../../assets/matches.png')}
          style={styles.loadingIcon}
          cachePolicy="memory-disk"
          contentFit="contain"
        />
        <ActivityIndicator size="large" color={theme.colors.ghostWhite} />
        <Text style={styles.loadingText}>Summoning soul mates...</Text>
      </View>
    );
  }

  if (!match) {
    return (
      <View style={styles.centerContainer}>
        <Text style={styles.errorText}>Match not found</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Image
          source={require('../../assets/matches.png')}
          style={styles.headerIcon}
          cachePolicy="memory-disk"
          contentFit="contain"
        />
        <Text style={styles.title}>Soul Mates #{match.id}</Text>
        <Text style={styles.subtitle}>Forever United</Text>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>{SOCK_EMOJIS.pair} Reunited Souls</Text>
        
        <View style={styles.socksContainer}>
          <View style={styles.sockContainer}>
            <Image
              source={{ uri: socksAPI.getImageUrl(match.sock1.id, authToken) }}
              style={styles.sockImage}
              cachePolicy="memory-disk"
              contentFit="cover"
              transition={200}
              priority="high"
            />
            <Text style={styles.sockLabel}>Soul #{match.sock1.id}</Text>
            <Text style={styles.sockDate}>
              Entered {formatDate(match.sock1.created_at)}
            </Text>
          </View>

          <View style={styles.sockContainer}>
            <Image
              source={{ uri: socksAPI.getImageUrl(match.sock2.id, authToken) }}
              style={styles.sockImage}
              cachePolicy="memory-disk"
              contentFit="cover"
              transition={200}
              priority="high"
            />
            <Text style={styles.sockLabel}>Soul #{match.sock2.id}</Text>
            <Text style={styles.sockDate}>
              Entered {formatDate(match.sock2.created_at)}
            </Text>
          </View>
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>{SOCK_EMOJIS.sparkle} Reunion Record</Text>
        
        <View style={styles.detailRow}>
          <Text style={styles.detailLabel}>United:</Text>
          <Text style={styles.detailValue}>{formatDate(match.matched_at)}</Text>
        </View>

        <View style={styles.detailRow}>
          <Text style={styles.detailLabel}>Time of Reunion:</Text>
          <Text style={styles.detailValue}>{formatTime(match.matched_at)}</Text>
        </View>
      </View>

      <View style={styles.actionsSection}>
        <Text style={styles.sectionTitle}>⚠️ Actions</Text>
        
        <TouchableOpacity
          style={styles.decoupleButton}
          onPress={() => handleDelete(true)}
        >
          <Text style={styles.decoupleButtonText}>
            🔗 Separate Souls
          </Text>
          <Text style={styles.buttonSubtext}>
            Return both to wandering
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.deleteButton}
          onPress={() => handleDelete(false)}
        >
          <Text style={styles.deleteButtonText}>
            ☠️ Release Forever
          </Text>
          <Text style={styles.buttonSubtext}>
            Permanently remove both souls
          </Text>
        </TouchableOpacity>
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
  errorText: {
    fontSize: 16,
    color: theme.colors.textMuted,
  },
  header: {
    alignItems: 'center',
    padding: theme.spacing.xl,
    backgroundColor: theme.colors.surface,
    borderBottomWidth: 2,
    borderBottomColor: theme.colors.ghostWhite,
  },
  headerIcon: {
    width: 80,
    height: 80,
    marginBottom: theme.spacing.md,
  },
  title: {
    ...theme.typography.h1,
    color: theme.colors.ghostWhite,
    marginBottom: theme.spacing.xs,
    textShadowColor: 'rgba(240, 240, 255, 0.3)',
    textShadowOffset: { width: 0, height: 0 },
    textShadowRadius: 15,
  },
  subtitle: {
    fontSize: 16,
    color: theme.colors.textSecondary,
    fontStyle: 'italic',
  },
  section: {
    backgroundColor: theme.colors.surface,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.lg,
    margin: theme.spacing.md,
    borderWidth: 1,
    borderColor: theme.colors.tombstone,
  },
  sectionTitle: {
    ...theme.typography.h3,
    color: theme.colors.ghostWhite,
    marginBottom: theme.spacing.md,
  },
  socksContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  sockContainer: {
    alignItems: 'center',
    flex: 1,
    margin: theme.spacing.xs,
  },
  sockImage: {
    width: 150,
    height: 150,
    borderRadius: theme.borderRadius.md,
    backgroundColor: theme.colors.surfaceLight,
    marginBottom: theme.spacing.sm,
    borderWidth: 2,
    borderColor: theme.colors.tombstone,
  },
  sockLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: theme.colors.primary,
    marginBottom: theme.spacing.xs,
  },
  sockDate: {
    fontSize: 12,
    color: theme.colors.textMuted,
    textAlign: 'center',
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
  actionsSection: {
    backgroundColor: theme.colors.surface,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.lg,
    margin: theme.spacing.md,
    borderWidth: 1,
    borderColor: theme.colors.tombstone,
  },
  decoupleButton: {
    backgroundColor: theme.colors.warning,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.md,
    alignItems: 'center',
    marginBottom: theme.spacing.sm,
    ...theme.shadows.medium,
  },
  deleteButton: {
    backgroundColor: theme.colors.danger,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.md,
    alignItems: 'center',
    ...theme.shadows.medium,
  },
  decoupleButtonText: {
    color: theme.colors.textInverse,
    fontSize: 16,
    fontWeight: '600',
    marginBottom: theme.spacing.xs,
  },
  deleteButtonText: {
    color: theme.colors.ghostWhite,
    fontSize: 16,
    fontWeight: '600',
    marginBottom: theme.spacing.xs,
  },
  buttonSubtext: {
    color: 'rgba(255, 255, 255, 0.9)',
    fontSize: 12,
  },
});
