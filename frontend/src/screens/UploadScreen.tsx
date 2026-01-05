import React, { useState } from 'react';
import {
  View,
  Text,
  Image,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  ActivityIndicator,
  Platform,
} from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { socksAPI, getToken, getTokenSync } from '../services/api';
import { SockMatch } from '../types';
import SimilarSocksList from '../components/SimilarSocksList';
import { theme, GHOST_EMOJIS, SOCK_EMOJIS } from '../theme';
import { Alert } from '../utils/alert';

export default function UploadScreen({ navigation }: any) {
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const [similarSocks, setSimilarSocks] = useState<SockMatch[]>([]);
  const [uploadedSockId, setUploadedSockId] = useState<number | null>(null);
  const [showResults, setShowResults] = useState(false);
  const [authToken, setAuthToken] = useState<string>('');

  const pickImage = async () => {
    const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
    
    if (status !== 'granted') {
      Alert.alert('Permission needed', 'We need camera roll permissions to upload sock images');
      return;
    }

    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: false,
      quality: 0.8,
    });

    if (!result.canceled && result.assets[0]) {
      const imageUri = result.assets[0].uri;
      setSelectedImage(imageUri);
      setSimilarSocks([]);
      setShowResults(false);
      setUploadedSockId(null);
      setAuthToken('');
      setIsUploading(false);
      setIsSearching(false);
      
      // Automatically upload the image
      await handleUpload(imageUri);
    }
  };

  const takePhoto = async () => {
    const { status } = await ImagePicker.requestCameraPermissionsAsync();
    
    if (status !== 'granted') {
      Alert.alert('Permission needed', 'We need camera permissions to take sock photos');
      return;
    }

    const result = await ImagePicker.launchCameraAsync({
      allowsEditing: false,
      quality: 0.8,
    });

    if (!result.canceled && result.assets[0]) {
      const imageUri = result.assets[0].uri;
      setSelectedImage(imageUri);
      setSimilarSocks([]);
      setShowResults(false);
      setUploadedSockId(null);
      setAuthToken('');
      setIsUploading(false);
      setIsSearching(false);
      
      // Automatically upload the image
      await handleUpload(imageUri);
    }
  };

  const searchSimilar = async () => {
    if (!selectedImage) return;

    setIsSearching(true);
    try {
      const matches = await socksAPI.search(selectedImage);
      setSimilarSocks(matches);
      setShowResults(true);
    } catch (error: any) {
      Alert.alert('Search Failed', error.response?.data?.detail || 'Failed to search for similar socks');
    } finally {
      setIsSearching(false);
    }
  };

  const handleUpload = async (imageUri: string) => {
    if (!imageUri) return;

    setIsUploading(true);
    try {
      // Get auth token for image URLs
      if (Platform.OS === 'web') {
        try {
          const token = getTokenSync();
          setAuthToken(token);
        } catch (e) {
          // Token retrieval failed
        }
      } else {
        const token = await getToken();
        setAuthToken(token || '');
      }
      
      const sock = await socksAPI.upload(imageUri);
      setUploadedSockId(sock.id);
      
      // Automatically search for similar socks using the stored embedding
      try {
        const matches = await socksAPI.searchBySockId(sock.id);
        setSimilarSocks(matches);
        setShowResults(true);
      } catch (searchError: any) {
        // Search failure is non-critical
        setShowResults(false);
      }
    } catch (error: any) {
      Alert.alert('Upload Failed', error.response?.data?.detail || error.message || 'Failed to upload sock');
    } finally {
      setIsUploading(false);
    }
  };

  const addToCollection = () => {
    Alert.alert(
      'Added to Collection',
      'Your sock has been added to your collection',
      [
        {
          text: 'View Collection',
          onPress: () => {
            setSelectedImage(null);
            setSimilarSocks([]);
            setShowResults(false);
            navigation.navigate('Socks');
          },
        },
        {
          text: 'Upload Another',
          onPress: () => {
            setSelectedImage(null);
            setSimilarSocks([]);
            setShowResults(false);
            setUploadedSockId(null);
          },
        },
      ]
    );
  };

  const viewSockDetail = (sockId: number) => {
    navigation.navigate('SockDetail', { sockId });
  };

  const handleMatchCreated = (matchId: number) => {
    // Clear the upload state so when user comes back, they see an empty upload page
    setSelectedImage(null);
    setSimilarSocks([]);
    setShowResults(false);
    setUploadedSockId(null);
    
    // Navigate to the match detail page
    navigation.navigate('MatchDetail', { matchId });
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.content}>
        <View style={styles.titleContainer}>
          <Image
            source={require('../../assets/upload.png')}
            style={styles.titleIcon}
          />
          <Text style={styles.title}>Upload Socks</Text>
        </View>
        <Text style={styles.subtitle}>Photograph the departed and give them peace</Text>

        <View style={styles.buttonGroup}>
          <TouchableOpacity style={styles.actionButton} onPress={takePhoto}>
            <Image
              source={require('../../assets/upload-from-camera.png')}
              style={styles.actionButtonIcon}
            />
            <Text style={styles.actionButtonText}>Take Photo</Text>
          </TouchableOpacity>

          <TouchableOpacity style={styles.actionButton} onPress={pickImage}>
            <Image
              source={require('../../assets/upload-from-gallery.png')}
              style={styles.actionButtonIcon}
            />
            <Text style={styles.actionButtonText}>From Gallery</Text>
          </TouchableOpacity>
        </View>

        {selectedImage && (
          <View style={styles.imageContainer}>
            <Image source={{ uri: selectedImage }} style={styles.image} />
            
            {isUploading && (
              <View style={styles.uploadingOverlay}>
                <Image
                  source={require('../../assets/upload.png')}
                  style={styles.uploadingIcon}
                />
                <ActivityIndicator size="large" color={theme.colors.primary} />
                <Text style={styles.uploadingText}>Entering the graveyard...</Text>
              </View>
            )}
            
            {uploadedSockId && !isUploading && (
              <View style={styles.uploadedBadge}>
                <Text style={styles.uploadedText}>✓ Laid to Rest</Text>
              </View>
            )}
          </View>
        )}

        {showResults && (
          <View style={styles.resultsContainer}>
            <SimilarSocksList
              matches={similarSocks}
              onSockPress={viewSockDetail}
              showNoMatchMessage={true}
              sourceSockId={uploadedSockId || undefined}
              onMatchCreated={handleMatchCreated}
              authToken={authToken}
            />
          </View>
        )}

        {isSearching && (
          <View style={styles.loadingContainer}>
            <Image
              source={require('../../assets/single.png')}
              style={styles.loadingIcon}
            />
            <ActivityIndicator size="large" color={theme.colors.primary} />
            <Text style={styles.loadingText}>Seeking reunions...</Text>
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
  content: {
    padding: theme.spacing.lg,
  },
  titleContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: theme.spacing.sm,
    gap: theme.spacing.sm,
  },
  titleIcon: {
    width: 36,
    height: 36,
  },
  title: {
    ...theme.typography.h1,
    color: theme.colors.primary,
    textShadowColor: theme.colors.ghostGlow,
    textShadowOffset: { width: 0, height: 0 },
    textShadowRadius: 15,
  },
  subtitle: {
    fontSize: 14,
    color: theme.colors.textSecondary,
    marginBottom: theme.spacing.lg,
    textAlign: 'center',
    fontStyle: 'italic',
  },
  buttonGroup: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: theme.spacing.lg,
    gap: theme.spacing.md,
  },
  actionButton: {
    backgroundColor: theme.colors.surface,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.lg,
    flex: 1,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: theme.colors.tombstone,
    ...theme.shadows.medium,
  },
  actionButtonIcon: {
    width: 48,
    height: 48,
    marginBottom: theme.spacing.sm,
  },
  actionButtonText: {
    fontSize: 14,
    color: theme.colors.text,
    fontWeight: '600',
  },
  imageContainer: {
    marginBottom: theme.spacing.lg,
    position: 'relative',
  },
  image: {
    width: '100%',
    maxWidth: 400,
    aspectRatio: 1,
    borderRadius: theme.borderRadius.md,
    marginBottom: theme.spacing.md,
    alignSelf: 'center',
    borderWidth: 2,
    borderColor: theme.colors.tombstone,
  },
  uploadingOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: theme.spacing.md,
    backgroundColor: theme.colors.overlay,
    borderRadius: theme.borderRadius.md,
    justifyContent: 'center',
    alignItems: 'center',
  },
  uploadingIcon: {
    width: 48,
    height: 48,
    marginBottom: theme.spacing.sm,
  },
  uploadingText: {
    color: theme.colors.text,
    fontSize: 16,
    fontWeight: '600',
    marginTop: theme.spacing.sm,
  },
  uploadedBadge: {
    backgroundColor: theme.colors.success,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.md,
    alignItems: 'center',
    ...theme.shadows.glow,
  },
  uploadedText: {
    color: theme.colors.textInverse,
    fontSize: 16,
    fontWeight: '600',
  },
  resultsContainer: {
    marginTop: theme.spacing.lg,
  },
  addButton: {
    backgroundColor: theme.colors.success,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.md,
    alignItems: 'center',
    marginTop: theme.spacing.sm,
    ...theme.shadows.glow,
  },
  addButtonText: {
    color: theme.colors.textInverse,
    fontSize: 16,
    fontWeight: '600',
  },
  loadingContainer: {
    alignItems: 'center',
    marginTop: theme.spacing.lg,
  },
  loadingIcon: {
    width: 56,
    height: 56,
    marginBottom: theme.spacing.md,
  },
  loadingText: {
    marginTop: theme.spacing.sm,
    color: theme.colors.textSecondary,
    fontSize: 16,
  },
});