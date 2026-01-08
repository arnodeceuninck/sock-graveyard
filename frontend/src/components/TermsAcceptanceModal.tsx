import React, { useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Modal,
  ScrollView,
} from 'react-native';
import { theme } from '../theme';
import { Alert } from '../utils/alert';
import { authAPI } from '../services/api';

interface TermsAcceptanceModalProps {
  visible: boolean;
  onAccepted: () => void;
  onLogout: () => void;
  userEmail?: string;
}

export default function TermsAcceptanceModal({
  visible,
  onAccepted,
  onLogout,
  userEmail,
}: TermsAcceptanceModalProps) {
  const [agreedToTerms, setAgreedToTerms] = useState(false);
  const [agreedToPrivacy, setAgreedToPrivacy] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleAccept = async () => {
    if (!agreedToTerms || !agreedToPrivacy) {
      Alert.alert('Error', 'Please agree to both the Terms of Service and Privacy Policy to continue');
      return;
    }

    setIsLoading(true);
    try {
      // Call backend to record acceptance
      await authAPI.acceptTermsForCurrentUser();
      
      // Reset checkboxes
      setAgreedToTerms(false);
      setAgreedToPrivacy(false);
      
      // Notify parent that terms were accepted
      onAccepted();
    } catch (error: any) {
      Alert.alert('Error', error.response?.data?.detail || 'Failed to save acceptance');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Modal
      visible={visible}
      transparent
      animationType="slide"
      onRequestClose={() => {}} // Prevent closing - force user to decide
    >
      <View style={styles.modalOverlay}>
        <View style={styles.modalContent}>
          <Text style={styles.modalTitle}>Welcome to Sock Graveyard!</Text>
          <Text style={styles.modalSubtitle}>
            Before you continue, please accept our legal terms:
          </Text>

          <ScrollView style={styles.checkboxContainer}>
            <TouchableOpacity
              style={styles.checkboxRow}
              onPress={() => setAgreedToTerms(!agreedToTerms)}
            >
              <View style={[styles.checkboxBox, agreedToTerms && styles.checkboxChecked]}>
                {agreedToTerms && <Text style={styles.checkboxMark}>✓</Text>}
              </View>
              <Text style={styles.checkboxText}>
                I agree to the{' '}
                <Text style={styles.linkTextInline}>
                  Terms of Service
                </Text>
              </Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.checkboxRow}
              onPress={() => setAgreedToPrivacy(!agreedToPrivacy)}
            >
              <View style={[styles.checkboxBox, agreedToPrivacy && styles.checkboxChecked]}>
                {agreedToPrivacy && <Text style={styles.checkboxMark}>✓</Text>}
              </View>
              <Text style={styles.checkboxText}>
                I agree to the{' '}
                <Text style={styles.linkTextInline}>
                  Privacy Policy
                </Text>
              </Text>
            </TouchableOpacity>
          </ScrollView>

          <TouchableOpacity
            style={[
              styles.button,
              (!agreedToTerms || !agreedToPrivacy || isLoading) && styles.buttonDisabled
            ]}
            onPress={handleAccept}
            disabled={!agreedToTerms || !agreedToPrivacy || isLoading}
          >
            <Text style={styles.buttonText}>
              {isLoading ? 'Saving...' : 'Accept & Continue'}
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.logoutButton}
            onPress={onLogout}
            disabled={isLoading}
          >
            <Text style={styles.logoutButtonText}>Log Out</Text>
          </TouchableOpacity>
        </View>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.8)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  modalContent: {
    backgroundColor: theme.colors.background,
    borderRadius: 16,
    padding: 24,
    width: '100%',
    maxWidth: 400,
    maxHeight: '80%',
    borderWidth: 2,
    borderColor: theme.colors.primary,
  },
  modalTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: theme.colors.text,
    marginBottom: 8,
    textAlign: 'center',
  },
  modalSubtitle: {
    fontSize: 16,
    color: theme.colors.textSecondary,
    marginBottom: 20,
    textAlign: 'center',
  },
  checkboxContainer: {
    marginBottom: 20,
  },
  checkboxRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  checkboxBox: {
    width: 24,
    height: 24,
    borderWidth: 2,
    borderColor: theme.colors.textSecondary,
    borderRadius: 4,
    marginRight: 12,
    justifyContent: 'center',
    alignItems: 'center',
  },
  checkboxChecked: {
    backgroundColor: theme.colors.primary,
    borderColor: theme.colors.primary,
  },
  checkboxMark: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  checkboxText: {
    flex: 1,
    fontSize: 14,
    color: theme.colors.text,
  },
  linkTextInline: {
    color: theme.colors.primary,
    textDecorationLine: 'underline',
  },
  button: {
    backgroundColor: theme.colors.primary,
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 12,
  },
  buttonDisabled: {
    backgroundColor: theme.colors.textSecondary,
    opacity: 0.5,
  },
  buttonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  logoutButton: {
    padding: 12,
    alignItems: 'center',
  },
  logoutButtonText: {
    color: theme.colors.textSecondary,
    fontSize: 14,
  },
});
