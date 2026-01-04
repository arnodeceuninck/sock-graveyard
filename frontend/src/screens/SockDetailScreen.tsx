import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  Image,
  StyleSheet,
  ScrollView,
  ActivityIndicator,
  TouchableOpacity,
  Alert,
  Platform,
} from 'react-native';
import { socksAPI, getToken, getTokenSync } from '../services/api';
import { Sock, SockMatch } from '../types';
import SimilarSocksList from '../components/SimilarSocksList';

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
              Alert.alert('Success', 'Sock deleted successfully');
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
        <ActivityIndicator size="large" color="#007AFF" />
        <Text style={styles.loadingText}>Loading sock details...</Text>
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
      />

      <View style={styles.content}>
        <View style={styles.header}>
          <Text style={styles.title}>Sock #{sock.id}</Text>
          <View style={[styles.badge, sock.is_matched ? styles.matchedBadge : styles.unmatchedBadge]}>
            <Text style={styles.badgeText}>
              {sock.is_matched ? '✓ Matched' : '⏳ Unmatched'}
            </Text>
          </View>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Details</Text>
          
          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>Date Added:</Text>
            <Text style={styles.detailValue}>{formatDate(sock.created_at)}</Text>
          </View>

          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>Time Added:</Text>
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
              <Text style={styles.actionButtonText}>
                {isSearching ? 'Searching...' : 'Find Similar Socks'}
              </Text>
            </TouchableOpacity>

            {!sock.is_matched && (
              <TouchableOpacity
                style={[styles.deleteButton, isSearching && styles.buttonDisabled]}
                onPress={handleDelete}
                disabled={isSearching}
              >
                <Text style={styles.deleteButtonText}>
                  Delete Sock
                </Text>
              </TouchableOpacity>
            )}
          </View>
        )}

        {isSearching && (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color="#007AFF" />
            <Text style={styles.searchingText}>Searching for matches...</Text>
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
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
  },
  loadingText: {
    marginTop: 10,
    color: '#666',
  },
  errorText: {
    fontSize: 16,
    color: '#666',
  },
  image: {
    width: '100%',
    maxWidth: 500,
    aspectRatio: 1,
    backgroundColor: '#f0f0f0',
    alignSelf: 'center',
  },
  content: {
    padding: 20,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#333',
  },
  badge: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
  },
  matchedBadge: {
    backgroundColor: '#34C759',
  },
  unmatchedBadge: {
    backgroundColor: '#FF9500',
  },
  badgeText: {
    color: 'white',
    fontSize: 12,
    fontWeight: '600',
  },
  section: {
    backgroundColor: 'white',
    borderRadius: 8,
    padding: 15,
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
  },
  detailRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  detailLabel: {
    fontSize: 14,
    color: '#666',
  },
  detailValue: {
    fontSize: 14,
    color: '#333',
    fontWeight: '500',
    textAlign: 'right',
    flex: 1,
    marginLeft: 10,
  },
  actions: {
    marginTop: 10,
  },
  actionButton: {
    backgroundColor: '#007AFF',
    borderRadius: 8,
    padding: 15,
    alignItems: 'center',
    marginBottom: 10,
  },
  deleteButton: {
    backgroundColor: '#FF3B30',
    borderRadius: 8,
    padding: 15,
    alignItems: 'center',
  },
  buttonDisabled: {
    opacity: 0.6,
  },
  actionButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
  deleteButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
  loadingContainer: {
    alignItems: 'center',
    marginTop: 20,
  },
  searchingText: {
    marginTop: 10,
    color: '#666',
  },
});
