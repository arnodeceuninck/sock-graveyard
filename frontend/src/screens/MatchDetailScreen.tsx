import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  Image,
  StyleSheet,
  ScrollView,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { matchesAPI, socksAPI } from '../services/api';
import { Match } from '../types';

export default function MatchDetailScreen({ route, navigation }: any) {
  const { matchId } = route.params;
  const [match, setMatch] = useState<Match | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadMatch();
  }, [matchId]);

  const loadMatch = async () => {
    try {
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

  if (isLoading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#007AFF" />
        <Text style={styles.loadingText}>Loading match details...</Text>
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
        <Text style={styles.title}>Match #{match.id}</Text>
        <Text style={styles.matchIcon}>💕</Text>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Matched Socks</Text>
        
        <View style={styles.socksContainer}>
          <View style={styles.sockContainer}>
            <Image
              source={{ uri: socksAPI.getImageUrl(match.sock1.id) }}
              style={styles.sockImage}
            />
            <Text style={styles.sockLabel}>Sock #{match.sock1.id}</Text>
            <Text style={styles.sockDate}>
              Added {formatDate(match.sock1.created_at)}
            </Text>
          </View>

          <View style={styles.sockContainer}>
            <Image
              source={{ uri: socksAPI.getImageUrl(match.sock2.id) }}
              style={styles.sockImage}
            />
            <Text style={styles.sockLabel}>Sock #{match.sock2.id}</Text>
            <Text style={styles.sockDate}>
              Added {formatDate(match.sock2.created_at)}
            </Text>
          </View>
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Match Details</Text>
        
        <View style={styles.detailRow}>
          <Text style={styles.detailLabel}>Match Date:</Text>
          <Text style={styles.detailValue}>{formatDate(match.matched_at)}</Text>
        </View>

        <View style={styles.detailRow}>
          <Text style={styles.detailLabel}>Match Time:</Text>
          <Text style={styles.detailValue}>{formatTime(match.matched_at)}</Text>
        </View>
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
  header: {
    alignItems: 'center',
    padding: 20,
    backgroundColor: 'white',
    borderBottomWidth: 1,
    borderBottomColor: '#ddd',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 10,
  },
  matchIcon: {
    fontSize: 48,
  },
  section: {
    backgroundColor: 'white',
    borderRadius: 8,
    padding: 15,
    margin: 15,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
  },
  socksContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  sockContainer: {
    alignItems: 'center',
    flex: 1,
    margin: 5,
  },
  sockImage: {
    width: 150,
    height: 150,
    borderRadius: 8,
    backgroundColor: '#f0f0f0',
    marginBottom: 10,
  },
  sockLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 5,
  },
  sockDate: {
    fontSize: 12,
    color: '#666',
    textAlign: 'center',
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
});
