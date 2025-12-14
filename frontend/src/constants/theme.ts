// API Configuration
export const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:80/api';

// Theme Colors - Most Wanted Style
export const Colors = {
  light: {
    background: '#F4E4C1', // Aged paper
    surface: '#FFF8E7',
    primary: '#8B4513', // Saddle brown
    secondary: '#D2691E', // Chocolate
    accent: '#FFD700', // Gold
    text: '#2C1810',
    textSecondary: '#5C4033',
    border: '#8B7355',
    error: '#B22222',
    success: '#2E8B57',
    stamp: '#DC143C', // Crimson for stamps
    wanted: '#8B0000', // Dark red for "WANTED" text
  },
  dark: {
    background: '#1A1A1A',
    surface: '#2D2D2D',
    primary: '#FFD700', // Gold (reversed from light)
    secondary: '#FFA500', // Orange
    accent: '#FF6347', // Tomato
    text: '#F4E4C1',
    textSecondary: '#C4B5A0',
    border: '#4A4A4A',
    error: '#FF6B6B',
    success: '#51CF66',
    stamp: '#FF4444',
    wanted: '#FF6B6B',
  },
};

// Typography - Western/Wanted Poster Style
export const Typography = {
  fontFamily: {
    regular: 'System',
    bold: 'System',
    poster: 'System', // In production, use custom western font
  },
  fontSize: {
    xs: 12,
    sm: 14,
    md: 16,
    lg: 18,
    xl: 24,
    xxl: 32,
    poster: 48,
  },
};

// Spacing
export const Spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
};

// Border Radius
export const BorderRadius = {
  sm: 4,
  md: 8,
  lg: 16,
  xl: 24,
  round: 9999,
};

// Shadow (for wanted poster effect)
export const Shadow = {
  small: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  medium: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 8,
    elevation: 4,
  },
  large: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.2,
    shadowRadius: 16,
    elevation: 8,
  },
};
