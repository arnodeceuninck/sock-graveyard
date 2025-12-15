import React, { useState } from 'react';
import { 
  View, 
  Text, 
  StyleSheet, 
  Image, 
  TextInput, 
  ScrollView,
  ActivityIndicator,
  Alert 
} from 'react-native';
import { useTheme } from '../contexts/ThemeContext';
import { Button } from '../components/Button';
import ApiService from '../services/api';
import { Spacing, Typography } from '../constants/theme';

export default function ImageUploadScreen({ route, navigation }: any) {
  const { imageUri } = route.params;
  const { colors } = useTheme();
  const [description, setDescription] = useState('');
  const [uploading, setUploading] = useState(false);

  const handleUpload = async () => {
    try {
      setUploading(true);
      
      // Upload the image
      const result = await ApiService.uploadSock(imageUri, description || undefined);
      
      // Navigate directly to the sock detail screen
      navigation.navigate('SockDetail', { sockId: result.id });
      
    } catch (error: any) {
      console.error('Upload failed:', error);
      Alert.alert(
        'Upload Failed',
        error.response?.data?.detail || 'Failed to upload sock. Please try again.',
        [
          {
            text: 'Try Again',
            style: 'default'
          },
          {
            text: 'Cancel',
            style: 'cancel',
            onPress: () => navigation.goBack()
          }
        ]
      );
    } finally {
      setUploading(false);
    }
  };

  const handleCancel = () => {
    Alert.alert(
      'Discard Photo?',
      'Are you sure you want to discard this photo?',
      [
        {
          text: 'Keep Editing',
          style: 'cancel'
        },
        {
          text: 'Discard',
          style: 'destructive',
          onPress: () => navigation.goBack()
        }
      ]
    );
  };

  return (
    <ScrollView 
      style={[styles.container, { backgroundColor: colors.background }]}
      contentContainerStyle={styles.contentContainer}
    >
      <View style={[styles.header, { backgroundColor: colors.surface }]}>
        <Text style={[styles.title, { color: colors.wanted }]}>REVIEW & UPLOAD</Text>
        <Text style={[styles.subtitle, { color: colors.text }]}>
          Check your photo and add details
        </Text>
      </View>

      <View style={styles.imageContainer}>
        <View style={[styles.posterFrame, { borderColor: colors.wanted }]}>
          <Image 
            source={{ uri: imageUri }} 
            style={styles.image}
            resizeMode="contain"
          />
        </View>
      </View>

      <View style={[styles.formContainer, { backgroundColor: colors.surface }]}>
        <Text style={[styles.label, { color: colors.text }]}>
          Description (Optional)
        </Text>
        <TextInput
          style={[
            styles.input,
            { 
              backgroundColor: colors.background,
              color: colors.text,
              borderColor: '#8B4513'
            }
          ]}
          value={description}
          onChangeText={setDescription}
          placeholder="e.g., Blue striped athletic sock, wool winter sock..."
          placeholderTextColor={colors.textSecondary}
          multiline
          numberOfLines={3}
          maxLength={200}
        />
        <Text style={[styles.charCount, { color: colors.textSecondary }]}>
          {description.length}/200
        </Text>
      </View>

      <View style={styles.buttonContainer}>
        {uploading ? (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color={colors.wanted} />
            <Text style={[styles.loadingText, { color: colors.text }]}>
              Processing image and searching for matches...
            </Text>
          </View>
        ) : (
          <>
            <Button
              title="🔍 Upload & Find Matches"
              onPress={handleUpload}
              style={styles.uploadButton}
            />
            
            <Button
              title="Cancel"
              onPress={handleCancel}
              style={styles.cancelButton}
              variant="secondary"
            />
          </>
        )}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  contentContainer: {
    paddingBottom: Spacing.xl,
  },
  header: {
    padding: Spacing.lg,
    borderBottomWidth: 3,
    borderBottomColor: '#8B4513',
  },
  title: {
    fontSize: Typography.fontSize.xxl,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: Spacing.xs,
  },
  subtitle: {
    fontSize: Typography.fontSize.md,
    textAlign: 'center',
  },
  imageContainer: {
    padding: Spacing.lg,
    alignItems: 'center',
  },
  posterFrame: {
    borderWidth: 4,
    borderRadius: 8,
    padding: Spacing.sm,
    width: '100%',
    maxWidth: 400,
    aspectRatio: 4 / 3,
  },
  image: {
    width: '100%',
    height: '100%',
    borderRadius: 4,
  },
  formContainer: {
    margin: Spacing.lg,
    padding: Spacing.lg,
    borderRadius: 8,
    borderWidth: 2,
    borderColor: '#8B4513',
  },
  label: {
    fontSize: Typography.fontSize.md,
    fontWeight: 'bold',
    marginBottom: Spacing.sm,
  },
  input: {
    borderWidth: 2,
    borderRadius: 4,
    padding: Spacing.md,
    fontSize: Typography.fontSize.md,
    textAlignVertical: 'top',
  },
  charCount: {
    fontSize: Typography.fontSize.sm,
    textAlign: 'right',
    marginTop: Spacing.xs,
  },
  buttonContainer: {
    padding: Spacing.lg,
    gap: Spacing.md,
  },
  uploadButton: {
    width: '100%',
  },
  cancelButton: {
    width: '100%',
  },
  loadingContainer: {
    alignItems: 'center',
    padding: Spacing.xl,
  },
  loadingText: {
    marginTop: Spacing.md,
    fontSize: Typography.fontSize.md,
    textAlign: 'center',
  },
});
