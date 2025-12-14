import React, { createContext, useState, useContext, ReactNode } from 'react';
import { useColorScheme } from 'react-native';
import { Colors } from '../constants/theme';

type ColorScheme = 'light' | 'dark';

interface ThemeContextType {
  colorScheme: ColorScheme;
  colors: typeof Colors.light;
  toggleTheme: () => void;
  isDark: boolean;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const ThemeProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const systemColorScheme = useColorScheme() as ColorScheme;
  const [colorScheme, setColorScheme] = useState<ColorScheme>(systemColorScheme || 'light');

  const toggleTheme = () => {
    setColorScheme((prev) => (prev === 'light' ? 'dark' : 'light'));
  };

  const colors = colorScheme === 'light' ? Colors.light : Colors.dark;
  const isDark = colorScheme === 'dark';

  return (
    <ThemeContext.Provider
      value={{
        colorScheme,
        colors,
        toggleTheme,
        isDark,
      }}
    >
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};
