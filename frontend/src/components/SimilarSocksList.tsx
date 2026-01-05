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
} from 'react-native';
import { socksAPI, matchesAPI } from '../services/api';
import { SockMatch } from '../types';
import { theme, SOCK_EMOJIS, GHOST_EMOJIS } from '../theme';
import { Alert } from '../utils/alert';

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
        {matches.length > 0 ? 'Soul Mates Found' : 'No Soul Mates Found'}
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
                  {isCreatingMatch ? 'Uniting...' : 'Reunite'}
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
    marginTop: theme.spacing.lg,
  },
  titleContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: theme.spacing.md,
    gap: theme.spacing.sm,
  },
  titleEmoji: {
    fontSize: 28,
  },
  title: {
    ...theme.typography.h3,
    color: theme.colors.accent,
  },
  matchList: {
    padding: theme.spacing.sm,
  },
  columnWrapper: {
    justifyContent: 'space-evenly',
  },
  matchCard: {
    margin: theme.spacing.sm,
    alignItems: 'center',
    backgroundColor: theme.colors.surface,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.sm,
    borderWidth: 1,
    borderColor: theme.colors.tombstone,
    ...theme.shadows.medium,
  },
  matchImage: {
    width: '100%',
    aspectRatio: 1,
    borderRadius: theme.borderRadius.sm,
    marginBottom: theme.spacing.sm,
    backgroundColor: theme.colors.surfaceLight,
  },
  matchSimilarity: {
    fontSize: 12,
    color: theme.colors.accent,
    fontWeight: '600',
  },
  noMatchText: {
    fontSize: 14,
    color: theme.colors.textSecondary,
    textAlign: 'center',
    marginBottom: theme.spacing.md,
    fontStyle: 'italic',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.85)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContent: {
    backgroundColor: theme.colors.surface,
    borderRadius: theme.borderRadius.lg,
    padding: theme.spacing.xl,
    width: '80%',
    maxWidth: 400,
    borderWidth: 2,
    borderColor: theme.colors.primary,
    ...theme.shadows.large,
  },
  modalTitle: {
    ...theme.typography.h2,
    marginBottom: theme.spacing.sm,
    color: theme.colors.primary,
    textAlign: 'center',
  },
  modalMessage: {
    fontSize: 16,
    color: theme.colors.textSecondary,
    marginBottom: theme.spacing.lg,
    lineHeight: 22,
    textAlign: 'center',
    fontStyle: 'italic',
  },
  modalButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    gap: theme.spacing.sm,
  },
  modalButton: {
    flex: 1,
    paddingVertical: theme.spacing.md,
    paddingHorizontal: theme.spacing.lg,
    borderRadius: theme.borderRadius.md,
    alignItems: 'center',
  },
  cancelButton: {
    backgroundColor: theme.colors.tombstone,
  },
  cancelButtonText: {
    color: theme.colors.text,
    fontSize: 16,
    fontWeight: '600',
  },
  confirmButton: {
    backgroundColor: theme.colors.primary,
    ...theme.shadows.medium,
  },
  confirmButtonText: {
    color: theme.colors.textInverse,
    fontSize: 16,
    fontWeight: '600',
  },
});
