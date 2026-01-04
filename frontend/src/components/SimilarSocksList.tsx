import React from 'react';
import {
  View,
  Text,
  Image,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
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
  if (matches.length === 0 && !showNoMatchMessage) {
    return null;
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>
        {matches.length > 0 ? 'Similar Socks Found' : 'No Similar Socks Found'}
      </Text>

      {matches.length > 0 ? (
        <>
          <ScrollView 
            horizontal 
            showsHorizontalScrollIndicator={false} 
            style={styles.matchList}
          >
            {matches.map((match) => (
              <TouchableOpacity
                key={match.sock_id}
                style={styles.matchCard}
                onPress={() => onSockPress(match.sock_id)}
              >
                <Image
                  source={{
                    uri: socksAPI.getImageUrl(match.sock_id),
                  }}
                  style={styles.matchImage}
                />
                <Text style={styles.matchSimilarity}>
                  {(match.similarity * 100).toFixed(0)}% match
                </Text>
              </TouchableOpacity>
            ))}
          </ScrollView>

          {showNoMatchMessage && (
            <Text style={styles.noMatchText}>
              Don't see a match? Add this sock to your collection.
            </Text>
          )}
        </>
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
    marginBottom: 20,
  },
  matchCard: {
    marginRight: 15,
    alignItems: 'center',
    backgroundColor: 'white',
    borderRadius: 8,
    padding: 10,
    borderWidth: 1,
    borderColor: '#ddd',
  },
  matchImage: {
    width: 120,
    height: 120,
    borderRadius: 8,
    marginBottom: 8,
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
