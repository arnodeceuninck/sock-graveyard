import React, { useState, useRef } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Alert, Platform } from 'react-native';
import { CameraView, useCameraPermissions, Camera } from 'expo-camera';
import * as ImagePicker from 'expo-image-picker';
import { useTheme } from '../contexts/ThemeContext';
import { Button } from '../components/Button';
import { Spacing, Typography } from '../constants/theme';

export default function CameraScreen({ navigation }: any) {
  const { colors } = useTheme();
  const [facing, setFacing] = useState<'back' | 'front'>('back');
  const [permission, requestPermission] = useCameraPermissions();
  const [showCamera, setShowCamera] = useState(false);
  const cameraRef = useRef<CameraView>(null);

  // Request permissions on mount
  React.useEffect(() => {
    (async () => {
      if (Platform.OS !== 'web') {
        await ImagePicker.requestMediaLibraryPermissionsAsync();
        await Camera.requestCameraPermissionsAsync();
      }
    })();
  }, []);

  const handleTakePicture = async () => {
    if (!permission) {
      const { status } = await requestPermission();
      if (status !== 'granted') {
        Alert.alert('Permission Required', 'Camera permission is required to take photos');
        return;
      }
    }

    if (!permission?.granted) {
      Alert.alert('Permission Required', 'Camera permission is required to take photos');
      return;
    }

    setShowCamera(true);
  };

  const handleCapture = async () => {
    if (cameraRef.current) {
      try {
        const photo = await cameraRef.current.takePictureAsync();
        setShowCamera(false);
        if (photo?.uri) {
          navigation.navigate('ImageUpload', { imageUri: photo.uri });
        }
      } catch (error) {
        console.error('Error taking picture:', error);
        Alert.alert('Error', 'Failed to take picture');
      }
    }
  };

  const handlePickImage = async () => {
    try {
      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: true,
        aspect: [4, 3],
        quality: 1,
      });

      if (!result.canceled && result.assets && result.assets.length > 0) {
        navigation.navigate('ImageUpload', { imageUri: result.assets[0].uri });
      }
    } catch (error) {
      console.error('Error picking image:', error);
      Alert.alert('Error', 'Failed to pick image');
    }
  };

  const toggleCameraFacing = () => {
    setFacing(current => (current === 'back' ? 'front' : 'back'));
  };

  if (showCamera) {
    return (
      <View style={styles.cameraContainer}>
        <CameraView 
          style={styles.camera} 
          facing={facing}
          ref={cameraRef}
        >
          <View style={styles.cameraControls}>
            <TouchableOpacity
              style={[styles.controlButton, { backgroundColor: colors.surface }]}
              onPress={() => setShowCamera(false)}
            >
              <Text style={[styles.controlButtonText, { color: colors.text }]}>✕</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={[styles.captureButton, { backgroundColor: colors.wanted }]}
              onPress={handleCapture}
            >
              <View style={[styles.captureButtonInner, { backgroundColor: colors.background }]} />
            </TouchableOpacity>

            <TouchableOpacity
              style={[styles.controlButton, { backgroundColor: colors.surface }]}
              onPress={toggleCameraFacing}
            >
              <Text style={[styles.controlButtonText, { color: colors.text }]}>🔄</Text>
            </TouchableOpacity>
          </View>
        </CameraView>
      </View>
    );
  }

  return (
    <View style={[styles.container, { backgroundColor: colors.background }]}>
      <View style={[styles.header, { backgroundColor: colors.surface }]}>
        <Text style={[styles.title, { color: colors.wanted }]}>CAPTURE SOCK</Text>
        <Text style={[styles.subtitle, { color: colors.text }]}>
          Take a clear photo of your lonely sock
        </Text>
      </View>

      <View style={styles.content}>
        <View style={[styles.instructionsBox, { backgroundColor: colors.surface }]}>
          <Text style={[styles.instructionsTitle, { color: colors.wanted }]}>
            📸 Photography Tips
          </Text>
          <Text style={[styles.instructionsText, { color: colors.text }]}>
            • Use good lighting{'\n'}
            • Lay sock flat on solid background{'\n'}
            • Show full sock including heel{'\n'}
            • Avoid shadows and glare
          </Text>
        </View>

        <View style={styles.buttonContainer}>
          <Button
            title="📷 Take Photo"
            onPress={handleTakePicture}
            style={styles.primaryButton}
          />
          
          <Button
            title="🖼️ Choose from Gallery"
            onPress={handlePickImage}
            style={styles.secondaryButton}
            variant="secondary"
          />
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
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
  content: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: Spacing.lg,
  },
  instructionsBox: {
    padding: Spacing.lg,
    borderRadius: 8,
    borderWidth: 2,
    borderColor: '#8B4513',
    marginBottom: Spacing.xl,
    width: '100%',
  },
  instructionsTitle: {
    fontSize: Typography.fontSize.lg,
    fontWeight: 'bold',
    marginBottom: Spacing.sm,
  },
  instructionsText: {
    fontSize: Typography.fontSize.md,
    lineHeight: 24,
  },
  buttonContainer: {
    width: '100%',
    gap: Spacing.md,
  },
  primaryButton: {
    width: '100%',
  },
  secondaryButton: {
    width: '100%',
  },
  cameraContainer: {
    flex: 1,
  },
  camera: {
    flex: 1,
  },
  cameraControls: {
    flex: 1,
    backgroundColor: 'transparent',
    flexDirection: 'row',
    justifyContent: 'space-around',
    alignItems: 'flex-end',
    paddingBottom: 40,
  },
  controlButton: {
    width: 60,
    height: 60,
    borderRadius: 30,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 2,
    borderColor: '#8B4513',
  },
  controlButtonText: {
    fontSize: 24,
  },
  captureButton: {
    width: 80,
    height: 80,
    borderRadius: 40,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 4,
    borderColor: '#fff',
  },
  captureButtonInner: {
    width: 64,
    height: 64,
    borderRadius: 32,
  },
});
