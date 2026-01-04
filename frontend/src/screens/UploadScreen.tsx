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
} from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { socksAPI, getTokenSync } from '../services/api';
import { SockMatch } from '../types';
import SimilarSocksList from '../components/SimilarSocksList';

export default function UploadScreen({ navigation }: any) {
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const [similarSocks, setSimilarSocks] = useState<SockMatch[]>([]);
  const [uploadedSockId, setUploadedSockId] = useState<number | null>(null);
  const [showResults, setShowResults] = useState(false);

  const pickImage = async () => {
    const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
    
    if (status !== 'granted') {
      Alert.alert('Permission needed', 'We need camera roll permissions to upload sock images');
      return;
    }

    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      aspect: [4, 3],
      quality: 0.8,
    });

    if (!result.canceled && result.assets[0]) {
      setSelectedImage(result.assets[0].uri);
      setSimilarSocks([]);
      setShowResults(false);
      setUploadedSockId(null);
    }
  };

  const takePhoto = async () => {
    const { status } = await ImagePicker.requestCameraPermissionsAsync();
    
    if (status !== 'granted') {
      Alert.alert('Permission needed', 'We need camera permissions to take sock photos');
      return;
    }

    const result = await ImagePicker.launchCameraAsync({
      allowsEditing: true,
      aspect: [4, 3],
      quality: 0.8,
    });

    if (!result.canceled && result.assets[0]) {
      setSelectedImage(result.assets[0].uri);
      setSimilarSocks([]);
      setShowResults(false);
      setUploadedSockId(null);
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

  const handleUpload = async () => {
    if (!selectedImage) return;

    setIsUploading(true);
    try {
      const sock = await socksAPI.upload(selectedImage);
      setUploadedSockId(sock.id);
      
      // Automatically search for similar socks after upload
      const matches = await socksAPI.search(selectedImage);
      setSimilarSocks(matches);
      setShowResults(true);
      
      Alert.alert('Success', 'Sock uploaded! Check below for similar matches.');
    } catch (error: any) {
      Alert.alert('Upload Failed', error.response?.data?.detail || 'Failed to upload sock');
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
            
            {!uploadedSockId ? (
              <TouchableOpacity
                style={[styles.uploadButton, isUploading && styles.buttonDisabled]}
                onPress={handleUpload}
                disabled={isUploading}
              >
                <Text style={styles.uploadButtonText}>
                  {isUploading ? 'Uploading...' : 'Upload & Find Matches'}
                </Text>
              </TouchableOpacity>
            ) : (
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
  },
  image: {
    width: '100%',
    height: 300,
    borderRadius: 8,
    marginBottom: 15,
  },
  uploadButton: {
    backgroundColor: '#007AFF',
    borderRadius: 8,
    padding: 15,
    alignItems: 'center',
  },
  buttonDisabled: {
    opacity: 0.6,
  },
  uploadButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
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