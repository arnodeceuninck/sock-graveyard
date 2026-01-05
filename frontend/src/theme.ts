// Sock Graveyard Theme - Spooky Dark Mode Design System

export const theme = {
  // Core Colors - Dark graveyard palette
  colors: {
    // Backgrounds - Night sky theme
    background: '#0a0a1f', // Deep midnight blue background
    surface: '#15152d', // Card/surface background with blue tint
    surfaceLight: '#1f1f3d', // Lighter surface with night sky feel
    overlay: 'rgba(10, 10, 31, 0.95)', // Semi-transparent overlay
    
    // Primary - Ghost/ethereal colors
    primary: '#8b7aff', // Ghostly purple
    primaryLight: '#a99aff', // Lighter ghost purple
    primaryDark: '#6b5acc', // Darker ghost purple
    
    // Accent - Spooky green/cyan for highlights
    accent: '#4dffaa', // Eerie green glow
    accentDark: '#2dd88a', // Darker glow
    
    // Graveyard colors
    tombstone: '#2d2d4a', // Dark blue-gray for borders
    mist: 'rgba(77, 255, 170, 0.1)', // Misty glow
    fog: 'rgba(139, 122, 255, 0.15)', // Purple fog
    nightSky: '#0d0d28', // Deep night sky
    starLight: 'rgba(255, 255, 255, 0.05)', // Subtle star shimmer
    
    // Status colors
    success: '#4dffaa', // Matched/success
    warning: '#ffa94d', // Warning
    danger: '#ff4d6d', // Delete/danger
    info: '#4d9dff', // Info
    
    // Text
    text: '#e8e8f0', // Primary text
    textSecondary: '#b8b8cc', // Secondary text
    textMuted: '#7a7a8a', // Muted text
    textInverse: '#0a0a0f', // Text on light backgrounds
    
    // Ghost-specific
    ghostWhite: '#f0f0ff',
    ghostGlow: 'rgba(139, 122, 255, 0.3)',
    
    // Match/heart colors
    heartGlow: '#ff6b9d',
    heartDark: '#cc4d7a',
  },
  
  // Typography
  typography: {
    h1: {
      fontSize: 32,
      fontWeight: '700' as const,
      letterSpacing: 0.5,
    },
    h2: {
      fontSize: 24,
      fontWeight: '600' as const,
      letterSpacing: 0.3,
    },
    h3: {
      fontSize: 20,
      fontWeight: '600' as const,
    },
    body: {
      fontSize: 16,
      fontWeight: '400' as const,
    },
    bodySmall: {
      fontSize: 14,
      fontWeight: '400' as const,
    },
    caption: {
      fontSize: 12,
      fontWeight: '400' as const,
    },
    button: {
      fontSize: 16,
      fontWeight: '600' as const,
    },
  },
  
  // Spacing
  spacing: {
    xs: 4,
    sm: 8,
    md: 16,
    lg: 24,
    xl: 32,
    xxl: 48,
  },
  
  // Border radius
  borderRadius: {
    sm: 8,
    md: 12,
    lg: 16,
    xl: 24,
    round: 999,
  },
  
  // Shadows - Glowing effects for dark theme
  shadows: {
    small: {
      shadowColor: '#8b7aff',
      shadowOffset: { width: 0, height: 2 },
      shadowOpacity: 0.2,
      shadowRadius: 4,
      elevation: 2,
    },
    medium: {
      shadowColor: '#8b7aff',
      shadowOffset: { width: 0, height: 4 },
      shadowOpacity: 0.3,
      shadowRadius: 8,
      elevation: 4,
    },
    large: {
      shadowColor: '#8b7aff',
      shadowOffset: { width: 0, height: 8 },
      shadowOpacity: 0.4,
      shadowRadius: 16,
      elevation: 8,
    },
    glow: {
      shadowColor: '#4dffaa',
      shadowOffset: { width: 0, height: 0 },
      shadowOpacity: 0.5,
      shadowRadius: 12,
      elevation: 6,
    },
  },
  
  // Animations
  animations: {
    fast: 200,
    normal: 300,
    slow: 500,
  },
};

// Ghost emoji variations for different states
export const GHOST_EMOJIS = {
  default: '👻',
  happy: '😊👻',
  sad: '😢👻',
  search: '🔍👻',
  upload: '📤👻',
  matched: '💕👻',
  lonely: '🥺👻',
};

// Sock-related emojis
export const SOCK_EMOJIS = {
  single: '🧦',
  pair: '🧦',
  ghost: '👻',
  matched: '💕',
  heart: '❤️',
  sparkle: '✨',
  rip: '🪦',
  moon: '🌙',
  star: '⭐',
};

export type Theme = typeof theme;
