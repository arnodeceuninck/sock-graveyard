import React, { useState } from 'react';
import {
  View,
  Text,
  Image,
  TouchableOpacity,
  StyleSheet,
  FlatList,
  useWindowDimensions,
  Modal,
  Alert,
} from 'react-native';
import { socksAPI, matchesAPI } from '../services/api';
import { SockMatch } from '../types';

interface SimilarSocksListProps {
  matches: SockMatch[];
  onSockPress: (sockId: number) => void;
  showNoMatchMessage?: boolean;
  sourceSockId?: number; // The original sock we're finding matches for
  onMatchCreated?: (matchId: number) => void; // Callback when a match is created
  authToken?: string; // Auth token for image URLs
}

export default function SimilarSocksList({ 
  matches, 
  onSockPress,
  showNoMatchMessage = true,
  sourceSockId,
  onMatchCreated,
  authToken = '',
}: SimilarSocksListProps) {
  const { width } = useWindowDimensions();
  const [showMatchModal, setShowMatchModal] = useState(false);
  const [selectedSockId, setSelectedSockId] = useState<number | null>(null);
  const [isCreatingMatch, setIsCreatingMatch] = useState(false);
  
  // Calculate number of columns based on screen width
  const numColumns = Math.max(2, Math.min(6, Math.floor(width / 320)));
  
  if (matches.length === 0 && !showNoMatchMessage) {
    return null;
  }

  const handleSockPress = (sockId: number) => {
    if (sourceSockId) {
      // Show match confirmation modal
      setSelectedSockId(sockId);
      setShowMatchModal(true);
    } else {
      // Just navigate to sock detail
      onSockPress(sockId);
    }
  };

  const handleConfirmMatch = async () => {
    if (!sourceSockId || !selectedSockId) return;

    setIsCreatingMatch(true);
    try {
      const match = await matchesAPI.create({
        sock1_id: sourceSockId,
        sock2_id: selectedSockId,
      });
      
      setShowMatchModal(false);
      
      // Show simple toast-style message
      Alert.alert('Socks matched successfully!');
      
      if (onMatchCreated) {
        onMatchCreated(match.id);
      }
    } catch (error: any) {
      Alert.alert('Error', error.response?.data?.detail || 'Failed to create match');
    } finally {
      setIsCreatingMatch(false);
    }
  };

  const renderMatchItem = ({ item }: { item: SockMatch }) => {
    // Calculate card width to fit columns with proper spacing
    const cardWidth = (width - 40) / numColumns - 20; // Subtract padding and margins
    
    return (
      <TouchableOpacity
        style={[styles.matchCard, { width: cardWidth }]}
        onPress={() => handleSockPress(item.sock_id)}
      >
        <Image
          source={{
            uri: socksAPI.getImageUrl(item.sock_id, authToken),
          }}
          style={styles.matchImage}
        />
        <Text style={styles.matchSimilarity}>
          {(item.similarity * 100).toFixed(0)}% match
        </Text>
      </TouchableOpacity>
    );
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>
        {matches.length > 0 ? 'Similar Socks Found' : 'No Similar Socks Found'}
      </Text>

      {matches.length > 0 ? (
        <FlatList
          data={matches}
          renderItem={renderMatchItem}
          keyExtractor={(item, index) => item?.sock_id?.toString() || index.toString()}
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

      {/* Match Confirmation Modal */}
      <Modal
        visible={showMatchModal}
        transparent={true}
        animationType="fade"
        onRequestClose={() => setShowMatchModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Match Socks?</Text>
            <Text style={styles.modalMessage}>
              Are you sure you want to mark these socks as a match?
            </Text>
            
            <View style={styles.modalButtons}>
              <TouchableOpacity
                style={[styles.modalButton, styles.cancelButton]}
                onPress={() => setShowMatchModal(false)}
                disabled={isCreatingMatch}
              >
                <Text style={styles.cancelButtonText}>Cancel</Text>
              </TouchableOpacity>
              
              <TouchableOpacity
                style={[styles.modalButton, styles.confirmButton]}
                onPress={handleConfirmMatch}
                disabled={isCreatingMatch}
              >
                <Text style={styles.confirmButtonText}>
                  {isCreatingMatch ? 'Matching...' : 'Confirm'}
                </Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>
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
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContent: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 20,
    width: '80%',
    maxWidth: 400,
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 10,
    color: '#333',
  },
  modalMessage: {
    fontSize: 16,
    color: '#666',
    marginBottom: 20,
    lineHeight: 22,
  },
  modalButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  modalButton: {
    flex: 1,
    paddingVertical: 12,
    paddingHorizontal: 20,
    borderRadius: 8,
    alignItems: 'center',
    marginHorizontal: 5,
  },
  cancelButton: {
    backgroundColor: '#f0f0f0',
  },
  cancelButtonText: {
    color: '#333',
    fontSize: 16,
    fontWeight: '600',
  },
  confirmButton: {
    backgroundColor: '#007AFF',
  },
  confirmButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
});
