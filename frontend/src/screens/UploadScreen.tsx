import React, { useState } from 'react';
import {
  View,
  Text,
  Image,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ScrollView,
  ActivityIndicator,
  Platform,
} from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { socksAPI, getToken, getTokenSync } from '../services/api';
import { SockMatch } from '../types';
import SimilarSocksList from '../components/SimilarSocksList';

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
      
      Alert.alert('Success', 'Sock uploaded successfully!');
      
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
        <Text style={styles.title}>Upload Sock</Text>
        <Text style={styles.subtitle}>Take a photo or select from gallery</Text>

        <View style={styles.buttonGroup}>
          <TouchableOpacity style={styles.actionButton} onPress={takePhoto}>
            <Text style={styles.actionButtonText}>📷 Take Photo</Text>
          </TouchableOpacity>

          <TouchableOpacity style={styles.actionButton} onPress={pickImage}>
            <Text style={styles.actionButtonText}>🖼️ Choose from Gallery</Text>
          </TouchableOpacity>
        </View>

        {selectedImage && (
          <View style={styles.imageContainer}>
            <Image source={{ uri: selectedImage }} style={styles.image} />
            
            {isUploading && (
              <View style={styles.uploadingOverlay}>
                <ActivityIndicator size="large" color="#007AFF" />
                <Text style={styles.uploadingText}>Uploading...</Text>
              </View>
            )}
            
            {uploadedSockId && !isUploading && (
              <View style={styles.uploadedBadge}>
                <Text style={styles.uploadedText}>✓ Uploaded</Text>
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
            <ActivityIndicator size="large" color="#007AFF" />
            <Text style={styles.loadingText}>Searching for matches...</Text>
          </View>
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
  content: {
    padding: 20,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    marginBottom: 5,
    color: '#333',
  },
  subtitle: {
    fontSize: 14,
    color: '#666',
    marginBottom: 20,
  },
  buttonGroup: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 20,
  },
  actionButton: {
    backgroundColor: 'white',
    borderRadius: 8,
    padding: 15,
    flex: 0.48,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#ddd',
  },
  actionButtonText: {
    fontSize: 14,
    color: '#333',
  },
  imageContainer: {
    marginBottom: 20,
    position: 'relative',
  },
  image: {
    width: '100%',
    maxWidth: 400,
    aspectRatio: 1,
    borderRadius: 8,
    marginBottom: 15,
    alignSelf: 'center',
  },
  uploadingOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 15,
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center',
  },
  uploadingText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
    marginTop: 10,
  },
  uploadedBadge: {
    backgroundColor: '#34C759',
    borderRadius: 8,
    padding: 15,
    alignItems: 'center',
  },
  uploadedText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
  resultsContainer: {
    marginTop: 20,
  },
  addButton: {
    backgroundColor: '#34C759',
    borderRadius: 8,
    padding: 15,
    alignItems: 'center',
    marginTop: 10,
  },
  addButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
  loadingContainer: {
    alignItems: 'center',
    marginTop: 20,
  },
  loadingText: {
    marginTop: 10,
    color: '#666',
  },
});