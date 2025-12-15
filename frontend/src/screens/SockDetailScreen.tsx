import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, Image, ActivityIndicator, Alert, TouchableOpacity } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useTheme } from '../contexts/ThemeContext';
import { useAuth } from '../contexts/AuthContext';
import ApiService from '../services/api';
import { API_BASE_URL } from '../constants/theme';
import { Button } from '../components/Button';
import { Spacing, Typography } from '../constants/theme';

export default function SockDetailScreen({ route, navigation }: any) {
  const { sockId } = route.params;
  const [sock, setSock] = useState<any>(null);
  const [matches, setMatches] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [authToken, setAuthToken] = useState<string | null>(null);
  const [searching, setSearching] = useState(true);
  
  const { colors } = useTheme();
  const { user } = useAuth();

  useEffect(() => {
    loadSockDetails();
    loadAuthToken();
  }, [sockId]);

  const loadAuthToken = async () => {
    const token = await AsyncStorage.getItem('auth_token');
    setAuthToken(token);
  };

  const loadSockDetails = async () => {
    setLoading(true);
    setSearching(true);
    try {
      // Get sock details
      const sockData = await ApiService.getSock(sockId);
      setSock(sockData);
      
      // Search for matches
      const matchData = await ApiService.searchSimilarSocks(sockId, 0.7, 10);
      setMatches(matchData.matches || []);
    } catch (error) {
      console.error('Failed to load sock details:', error);
      Alert.alert('Error', 'Failed to load sock details');
    } finally {
      setLoading(false);
      setSearching(false);
    }
  };

  const getImageUrl = (sockId: number) => {
    const baseUrl = `${API_BASE_URL}/socks/${sockId}/image?processed=true`;
    return authToken ? `${baseUrl}&token=${authToken}` : baseUrl;
  };

  const handleConfirmMatch = async (matchId: number) => {
    Alert.alert(
      'Confirm Match',
      'Are you sure these socks match?',
      [
        {
          text: 'Cancel',
          style: 'cancel'
        },
        {
          text: 'Confirm',
          onPress: async () => {
            try {
              await ApiService.confirmMatch(sockId, matchId);
              Alert.alert('Success!', 'Match confirmed! Both socks are now reunited.', [
                {
                  text: 'OK',
                  onPress: () => {
                    // Navigate back to Home tab
                    navigation.getParent()?.navigate('Home');
                  }
                }
              ]);
            } catch (error) {
              console.error('Failed to confirm match:', error);
              Alert.alert('Error', 'Failed to confirm match');
            }
          }
        }
      ]
    );
  };

  const getSimilarityPercentage = (score: number) => {
    return Math.round(score * 100);
  };

  const getSimilarityColor = (score: number) => {
    if (score >= 0.9) return '#22C55E'; // Green - Excellent match
    if (score >= 0.8) return '#EAB308'; // Yellow - Good match
    if (score >= 0.7) return '#F97316'; // Orange - Possible match
    return '#EF4444'; // Red - Poor match
  };

  if (loading) {
    return (
      <View style={[styles.container, { backgroundColor: colors.background }]}>
        <ActivityIndicator size="large" color={colors.wanted} />
        <Text style={[styles.loadingText, { color: colors.text }]}>
          Loading sock details...
        </Text>
      </View>
    );
  }

  if (!sock) {
    return (
      <View style={[styles.container, { backgroundColor: colors.background }]}>
        <Text style={[styles.errorText, { color: colors.text }]}>
          Sock not found
        </Text>
        <Button
          title="Go Back"
          onPress={() => navigation.goBack()}
        />
      </View>
    );
  }

  const hasMatch = sock.is_matched;
  const hasPotentialMatches = matches.length > 0;

  return (
    <ScrollView style={[styles.container, { backgroundColor: colors.background }]}>
      {/* Header */}
      <View style={[styles.header, { backgroundColor: colors.surface }]}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backButton}>
          <Text style={[styles.backButtonText, { color: colors.wanted }]}>← Back</Text>
        </TouchableOpacity>
        <Text style={[styles.title, { color: colors.wanted }]}>SOCK DETAILS</Text>
        <Text style={[styles.subtitle, { color: colors.text }]}>
          Sock #{sockId}
        </Text>
      </View>

      {/* Match Status Badge */}
      <View style={styles.statusContainer}>
        <View style={[
          styles.statusBadge,
          { backgroundColor: hasMatch ? '#22C55E' : '#F97316' }
        ]}>
          <Text style={styles.statusText}>
            {hasMatch ? '✓ MATCHED' : hasPotentialMatches ? '🔍 SEARCHING' : '❌ NO MATCHES YET'}
          </Text>
        </View>
      </View>

      {/* Sock Image */}
      <View style={[styles.posterFrame, { borderColor: colors.wanted }]}>
        <Image
          source={{ uri: getImageUrl(sockId) }}
          style={styles.sockImage}
          resizeMode="contain"
        />
      </View>

      {/* Description */}
      {sock.description && (
        <View style={[styles.descriptionContainer, { backgroundColor: colors.surface }]}>
          <Text style={[styles.descriptionLabel, { color: colors.textSecondary }]}>
            Description:
          </Text>
          <Text style={[styles.descriptionText, { color: colors.text }]}>
            {sock.description}
          </Text>
        </View>
      )}

      {/* Features */}
      <View style={[styles.featuresContainer, { backgroundColor: colors.surface }]}>
        <Text style={[styles.featuresTitle, { color: colors.wanted }]}>
          SOCK FEATURES
        </Text>
        {sock.dominant_color && (
          <View style={styles.featureRow}>
            <View style={[styles.colorSwatch, { backgroundColor: sock.dominant_color }]} />
            <Text style={[styles.featureText, { color: colors.text }]}>
              Color: {sock.dominant_color}
            </Text>
          </View>
        )}
        {sock.pattern_type && (
          <Text style={[styles.featureText, { color: colors.text }]}>
            Pattern: {sock.pattern_type}
          </Text>
        )}
      </View>

      {/* Matches Section */}
      <View style={styles.matchesSection}>
        <Text style={[styles.matchesTitle, { color: colors.wanted }]}>
          {searching ? 'SEARCHING FOR MATCHES...' : 
           hasMatch ? 'YOUR MATCH' :
           hasPotentialMatches ? 'POSSIBLE MATCHES' : 'NO MATCHES FOUND'}
        </Text>

        {searching && (
          <View style={styles.searchingContainer}>
            <ActivityIndicator size="large" color={colors.wanted} />
            <Text style={[styles.searchingText, { color: colors.text }]}>
              Analyzing your sock and searching the graveyard...
            </Text>
          </View>
        )}

        {!searching && !hasPotentialMatches && !hasMatch && (
          <View style={[styles.noMatchesContainer, { backgroundColor: colors.surface }]}>
            <Text style={[styles.noMatchesText, { color: colors.text }]}>
              No matching socks found yet.
            </Text>
            <Text style={[styles.noMatchesSubtext, { color: colors.textSecondary }]}>
              Upload more socks to increase your chances of finding a match!
            </Text>
          </View>
        )}

        {!searching && hasPotentialMatches && matches.map((match, index) => (
          <View key={match.sock?.id || index} style={[styles.matchCard, { backgroundColor: colors.surface }]}>
            <View style={styles.matchHeader}>
              <Text style={[styles.matchTitle, { color: colors.text }]}>
                Sock #{match.sock?.id}
              </Text>
              <View style={[
                styles.similarityBadge,
                { backgroundColor: getSimilarityColor(match.similarity) }
              ]}>
                <Text style={styles.similarityText}>
                  {getSimilarityPercentage(match.similarity)}% match
                </Text>
              </View>
            </View>

            <View style={styles.matchContent}>
              <Image
                source={{ uri: getImageUrl(match.sock?.id) }}
                style={styles.matchImage}
                resizeMode="contain"
              />
              
              <View style={styles.matchInfo}>
                {match.sock?.description && (
                  <Text style={[styles.matchDescription, { color: colors.text }]}>
                    {match.sock.description}
                  </Text>
                )}
                {match.sock?.dominant_color && (
                  <View style={styles.matchFeatureRow}>
                    <View style={[styles.colorSwatch, { backgroundColor: match.sock.dominant_color }]} />
                    <Text style={[styles.matchFeature, { color: colors.textSecondary }]}>
                      Color: {match.sock.dominant_color}
                    </Text>
                  </View>
                )}
                {match.sock?.pattern_type && (
                  <Text style={[styles.matchFeature, { color: colors.textSecondary }]}>
                    Pattern: {match.sock.pattern_type}
                  </Text>
                )}
              </View>
            </View>

            {!hasMatch && (
              <Button
                title="✓ Confirm This Match"
                onPress={() => handleConfirmMatch(match.sock?.id)}
                style={styles.confirmButton}
              />
            )}
          </View>
        ))}
      </View>

      {/* Action Buttons */}
      <View style={styles.actionButtons}>
        <Button
          title="← Back to Home"
          onPress={() => {
            // Navigate to the Home tab
            navigation.getParent()?.navigate('Home');
          }}
          style={styles.homeButton}
        />
        <Button
          title="+ Add Another Sock"
          onPress={() => {
            // Navigate to the Camera tab
            navigation.getParent()?.navigate('Camera');
          }}
          variant="secondary"
          style={styles.addButton}
        />
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  header: {
    padding: Spacing.lg,
    paddingTop: Spacing.xl + 20,
    borderBottomWidth: 3,
    borderBottomColor: '#8B4513',
  },
  backButton: {
    marginBottom: Spacing.sm,
  },
  backButtonText: {
    fontSize: Typography.fontSize.md,
    fontWeight: '600',
  },
  title: {
    fontSize: Typography.fontSize.xxl,
    fontWeight: 'bold',
    textAlign: 'center',
    fontFamily: Typography.fontFamily.poster,
    letterSpacing: 2,
  },
  subtitle: {
    fontSize: Typography.fontSize.md,
    textAlign: 'center',
    marginTop: Spacing.xs,
  },
  statusContainer: {
    padding: Spacing.lg,
    alignItems: 'center',
  },
  statusBadge: {
    paddingHorizontal: Spacing.lg,
    paddingVertical: Spacing.sm,
    borderRadius: 20,
  },
  statusText: {
    color: '#FFFFFF',
    fontSize: Typography.fontSize.md,
    fontWeight: 'bold',
    letterSpacing: 1,
  },
  posterFrame: {
    margin: Spacing.lg,
    borderWidth: 4,
    borderStyle: 'solid',
    padding: Spacing.md,
    backgroundColor: '#FFFFFF',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  sockImage: {
    width: '100%',
    height: 300,
  },
  descriptionContainer: {
    margin: Spacing.lg,
    marginTop: 0,
    padding: Spacing.md,
    borderRadius: 8,
    borderWidth: 2,
    borderColor: '#8B4513',
  },
  descriptionLabel: {
    fontSize: Typography.fontSize.sm,
    fontWeight: 'bold',
    marginBottom: Spacing.xs,
  },
  descriptionText: {
    fontSize: Typography.fontSize.md,
  },
  featuresContainer: {
    margin: Spacing.lg,
    marginTop: 0,
    padding: Spacing.md,
    borderRadius: 8,
    borderWidth: 2,
    borderColor: '#8B4513',
  },
  featuresTitle: {
    fontSize: Typography.fontSize.lg,
    fontWeight: 'bold',
    marginBottom: Spacing.sm,
    letterSpacing: 1,
  },
  featureRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: Spacing.xs,
  },
  colorSwatch: {
    width: 24,
    height: 24,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: '#8B4513',
    marginRight: Spacing.sm,
  },
  featureText: {
    fontSize: Typography.fontSize.md,
    marginBottom: Spacing.xs,
  },
  matchesSection: {
    padding: Spacing.lg,
  },
  matchesTitle: {
    fontSize: Typography.fontSize.xl,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: Spacing.lg,
    letterSpacing: 1,
  },
  searchingContainer: {
    alignItems: 'center',
    padding: Spacing.xl,
  },
  searchingText: {
    fontSize: Typography.fontSize.md,
    textAlign: 'center',
    marginTop: Spacing.md,
  },
  noMatchesContainer: {
    padding: Spacing.lg,
    borderRadius: 8,
    borderWidth: 2,
    borderColor: '#8B4513',
  },
  noMatchesText: {
    fontSize: Typography.fontSize.lg,
    textAlign: 'center',
    marginBottom: Spacing.sm,
  },
  noMatchesSubtext: {
    fontSize: Typography.fontSize.md,
    textAlign: 'center',
  },
  matchCard: {
    marginBottom: Spacing.lg,
    padding: Spacing.md,
    borderRadius: 8,
    borderWidth: 3,
    borderColor: '#8B4513',
  },
  matchHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: Spacing.md,
  },
  matchTitle: {
    fontSize: Typography.fontSize.lg,
    fontWeight: 'bold',
  },
  similarityBadge: {
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.xs,
    borderRadius: 12,
  },
  similarityText: {
    color: '#FFFFFF',
    fontSize: Typography.fontSize.sm,
    fontWeight: 'bold',
  },
  matchContent: {
    flexDirection: 'row',
    marginBottom: Spacing.md,
  },
  matchImage: {
    width: 120,
    height: 120,
    borderWidth: 2,
    borderColor: '#8B4513',
    backgroundColor: '#FFFFFF',
  },
  matchInfo: {
    flex: 1,
    marginLeft: Spacing.md,
    justifyContent: 'center',
  },
  matchDescription: {
    fontSize: Typography.fontSize.md,
    marginBottom: Spacing.xs,
  },
  matchFeatureRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: Spacing.xs,
  },
  matchFeature: {
    fontSize: Typography.fontSize.sm,
    marginBottom: Spacing.xs,
  },
  confirmButton: {
    marginTop: Spacing.sm,
  },
  actionButtons: {
    padding: Spacing.lg,
    gap: Spacing.md,
  },
  homeButton: {
    marginBottom: Spacing.sm,
  },
  addButton: {
    marginBottom: Spacing.lg,
  },
  loadingText: {
    fontSize: Typography.fontSize.lg,
    textAlign: 'center',
    marginTop: Spacing.md,
  },
  errorText: {
    fontSize: Typography.fontSize.lg,
    textAlign: 'center',
    marginBottom: Spacing.lg,
  },
});
