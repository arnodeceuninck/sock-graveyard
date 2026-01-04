import React from 'react';
import {
  View,
  Text,
  Image,
  TouchableOpacity,
  StyleSheet,
  FlatList,
  useWindowDimensions,
} from 'react-native';
import { socksAPI } from '../services/api';
import { SockMatch } from '../types';

interface SimilarSocksListProps {
  matches: SockMatch[];
  onSockPress: (sockId: number) => void;
  showNoMatchMessage?: boolean;
}

export default function SimilarSocksList({ 
  matches, 
  onSockPress,
  showNoMatchMessage = true 
}: SimilarSocksListProps) {
  const { width } = useWindowDimensions();
  
  // Calculate number of columns based on screen width
  const numColumns = Math.max(2, Math.min(6, Math.floor(width / 320)));
  
  if (matches.length === 0 && !showNoMatchMessage) {
    return null;
  }

  const renderMatchItem = ({ item }: { item: SockMatch }) => (
    <TouchableOpacity
      style={styles.matchCard}
      onPress={() => onSockPress(item.sock_id)}
    >
      <Image
        source={{
          uri: socksAPI.getImageUrl(item.sock_id),
        }}
        style={styles.matchImage}
      />
      <Text style={styles.matchSimilarity}>
        {(item.similarity * 100).toFixed(0)}% match
      </Text>
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      <Text style={styles.title}>
        {matches.length > 0 ? 'Similar Socks Found' : 'No Similar Socks Found'}
      </Text>

      {matches.length > 0 ? (
        <FlatList
          data={matches}
          renderItem={renderMatchItem}
          keyExtractor={(item) => item.sock_id.toString()}
          key={numColumns}
          numColumns={numColumns}
          contentContainerStyle={styles.matchList}
          columnWrapperStyle={styles.columnWrapper}
          scrollEnabled={false}
        />
      ) : (
        showNoMatchMessage && (
          <Text style={styles.noMatchText}>
            This sock doesn't match any in your collection.
          </Text>
        )
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    marginTop: 20,
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 15,
    color: '#333',
  },
  matchList: {
    padding: 10,
  },
  columnWrapper: {
    justifyContent: 'space-evenly',
  },
  matchCard: {
    margin: 10,
    width: 280,
    alignItems: 'center',
    backgroundColor: 'white',
    borderRadius: 8,
    padding: 10,
    borderWidth: 1,
    borderColor: '#ddd',
  },
  matchImage: {
    width: '100%',
    aspectRatio: 1,
    borderRadius: 8,
    marginBottom: 8,
    backgroundColor: '#f0f0f0',
  },
  matchSimilarity: {
    fontSize: 12,
    color: '#007AFF',
    fontWeight: '600',
  },
  noMatchText: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
    marginBottom: 15,
  },
});
