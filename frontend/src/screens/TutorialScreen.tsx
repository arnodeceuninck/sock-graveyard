import React, { useState, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Dimensions,
  TouchableOpacity,
  ScrollView,
  Image,
} from 'react-native';
import { theme } from '../theme';

const { width: SCREEN_WIDTH, height: SCREEN_HEIGHT } = Dimensions.get('window');

interface TutorialScreenProps {
  onComplete: () => void;
}

const tutorialSlides = [
  {
    title: 'After Doing Laundry',
    description: 'Scan your single socks one by one to build your sock graveyard collection',
    image: require('../../assets/upload-from-camera.png'),
    gradient: ['#8b7aff', '#6b5acc'],
  },
  {
    title: 'Find Possible Matches',
    description: 'Our AI analyzes your stack of single socks to find potential soulmates',
    emoji: '🤖',
    gradient: ['#4dffaa', '#2dd88a'],
  },
  {
    title: 'Found a Match?',
    description: 'Great! Both socks will be reunited and removed from the search space',
    image: require('../../assets/matches.png'),
    gradient: ['#4dffaa', '#2dd88a'],
  },
  {
    title: 'No Match Yet?',
    description: "No worries! Your sock joins the graveyard, waiting patiently for its soulmate",
    image: require('../../assets/singles.png'),
    gradient: ['#8b7aff', '#6b5acc'],
  },
];

export default function TutorialScreen({ onComplete }: TutorialScreenProps) {
  const [currentSlide, setCurrentSlide] = useState(0);
  const scrollViewRef = useRef<ScrollView>(null);

  const handleNext = () => {
    if (currentSlide < tutorialSlides.length - 1) {
      const nextSlide = currentSlide + 1;
      setCurrentSlide(nextSlide);
      scrollViewRef.current?.scrollTo({
        x: nextSlide * SCREEN_WIDTH,
        animated: true,
      });
    } else {
      onComplete();
    }
  };

  const handleSkip = () => {
    onComplete();
  };

  const handleScroll = (event: any) => {
    const slideIndex = Math.round(event.nativeEvent.contentOffset.x / SCREEN_WIDTH);
    setCurrentSlide(slideIndex);
  };

  return (
    <View style={styles.container}>
      <ScrollView
        ref={scrollViewRef}
        horizontal
        pagingEnabled
        showsHorizontalScrollIndicator={false}
        onMomentumScrollEnd={handleScroll}
        scrollEventThrottle={16}
      >
        {tutorialSlides.map((slide, index) => (
          <View key={index} style={styles.slide}>
            <View style={styles.content}>
              {slide.image ? (
                <Image source={slide.image} style={styles.image} />
              ) : (
                <Text style={styles.emoji}>{slide.emoji}</Text>
              )}
              <Text style={styles.title}>{slide.title}</Text>
              <Text style={styles.description}>{slide.description}</Text>
            </View>
          </View>
        ))}
      </ScrollView>

      {/* Pagination Dots */}
      <View style={styles.pagination}>
        {tutorialSlides.map((_, index) => (
          <View
            key={index}
            style={[
              styles.dot,
              currentSlide === index && styles.dotActive,
            ]}
          />
        ))}
      </View>

      {/* Navigation Buttons */}
      <View style={styles.footer}>
        {currentSlide < tutorialSlides.length - 1 && (
          <TouchableOpacity
            style={styles.skipButton}
            onPress={handleSkip}
          >
            <Text style={styles.skipText}>Skip</Text>
          </TouchableOpacity>
        )}
        <TouchableOpacity
          style={[
            styles.nextButton,
            currentSlide === tutorialSlides.length - 1 && styles.getStartedButton,
          ]}
          onPress={handleNext}
        >
          <Text style={styles.nextText}>
            {currentSlide === tutorialSlides.length - 1 ? 'Get Started' : 'Next'}
          </Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  slide: {
    width: SCREEN_WIDTH,
    height: SCREEN_HEIGHT,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: theme.spacing.xl,
  },
  content: {
    alignItems: 'center',
    maxWidth: 400,
  },
  image: {
    width: 120,
    height: 120,
    marginBottom: theme.spacing.xl,
    resizeMode: 'contain',
  },
  emoji: {
    fontSize: 100,
    marginBottom: theme.spacing.xl,
  },
  title: {
    ...theme.typography.h1,
    color: theme.colors.text,
    textAlign: 'center',
    marginBottom: theme.spacing.lg,
  },
  description: {
    ...theme.typography.body,
    color: theme.colors.textSecondary,
    textAlign: 'center',
    lineHeight: 24,
  },
  pagination: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    position: 'absolute',
    bottom: 120,
    left: 0,
    right: 0,
  },
  dot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: theme.colors.tombstone,
    marginHorizontal: theme.spacing.xs,
  },
  dotActive: {
    backgroundColor: theme.colors.accent,
    width: 24,
  },
  footer: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    paddingHorizontal: theme.spacing.xl,
    paddingBottom: theme.spacing.xl + 20,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  skipButton: {
    paddingVertical: theme.spacing.md,
    paddingHorizontal: theme.spacing.lg,
  },
  skipText: {
    ...theme.typography.button,
    color: theme.colors.textMuted,
  },
  nextButton: {
    backgroundColor: theme.colors.primary,
    paddingVertical: theme.spacing.md,
    paddingHorizontal: theme.spacing.xl,
    borderRadius: theme.borderRadius.md,
    minWidth: 120,
    alignItems: 'center',
  },
  getStartedButton: {
    backgroundColor: theme.colors.accent,
    flex: 1,
    marginLeft: theme.spacing.md,
  },
  nextText: {
    ...theme.typography.button,
    color: theme.colors.textInverse,
  },
});
