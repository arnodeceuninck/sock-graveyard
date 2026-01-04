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
} from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import { socksAPI, getTokenSync } from '../services/api';
import { Sock } from '../types';

export default function SocksScreen({ navigation }: any) {
  const [socks, setSocks] = useState<Sock[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const loadSocks = async () => {
    try {
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

  const renderSockItem = ({ item }: { item: Sock }) => (
    <TouchableOpacity
      style={styles.sockCard}
      onPress={() => navigation.navigate('SockDetail', { sockId: item.id })}
    >
      <Image
        source={{
          uri: socksAPI.getImageUrl(item.id),
        }}
        style={styles.sockImage}
      />
      <View style={styles.sockInfo}>
        <Text style={styles.sockId}>Sock #{item.id}</Text>
        <Text style={styles.sockDate}>Added {formatDate(item.created_at)}</Text>
      </View>
    </TouchableOpacity>
  );

  if (isLoading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#007AFF" />
        <Text style={styles.loadingText}>Loading your socks...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>My Unmatched Socks</Text>
        <Text style={styles.count}>{socks.length} sock{socks.length !== 1 ? 's' : ''}</Text>
      </View>

      {socks.length === 0 ? (
        <View style={styles.emptyContainer}>
          <Text style={styles.emptyText}>🧦</Text>
          <Text style={styles.emptyTitle}>No unmatched socks yet</Text>
          <Text style={styles.emptySubtitle}>
            Upload your first sock to get started!
          </Text>
          <TouchableOpacity
            style={styles.uploadButton}
            onPress={() => navigation.navigate('Upload')}
          >
            <Text style={styles.uploadButtonText}>Upload Sock</Text>
          </TouchableOpacity>
        </View>
      ) : (
        <FlatList
          data={socks}
          renderItem={renderSockItem}
          keyExtractor={(item) => item.id.toString()}
          numColumns={2}
          contentContainerStyle={styles.list}
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
  header: {
    padding: 20,
    backgroundColor: 'white',
    borderBottomWidth: 1,
    borderBottomColor: '#ddd',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
  },
  count: {
    fontSize: 14,
    color: '#666',
    marginTop: 5,
  },
  list: {
    padding: 10,
  },
  sockCard: {
    flex: 1,
    margin: 5,
    backgroundColor: 'white',
    borderRadius: 8,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: '#ddd',
  },
  sockImage: {
    width: '100%',
    height: 150,
    backgroundColor: '#f0f0f0',
  },
  sockInfo: {
    padding: 10,
  },
  sockId: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },
  sockDate: {
    fontSize: 12,
    color: '#666',
    marginTop: 2,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 40,
  },
  emptyText: {
    fontSize: 64,
    marginBottom: 20,
  },
  emptyTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 10,
  },
  emptySubtitle: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
    marginBottom: 30,
  },
  uploadButton: {
    backgroundColor: '#007AFF',
    borderRadius: 8,
    paddingVertical: 12,
    paddingHorizontal: 30,
  },
  uploadButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
});
