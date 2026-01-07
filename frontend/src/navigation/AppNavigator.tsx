import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { TouchableOpacity, Text, Image } from 'react-native';
import { useAuth } from '../contexts/AuthContext';
import { theme, GHOST_EMOJIS, SOCK_EMOJIS } from '../theme';

// Screens
import LoginScreen from '../screens/LoginScreen';
import RegisterScreen from '../screens/RegisterScreen';
import UploadScreen from '../screens/UploadScreen';
import SocksScreen from '../screens/SocksScreen';
import SockDetailScreen from '../screens/SockDetailScreen';
import MatchesScreen from '../screens/MatchesScreen';
import MatchDetailScreen from '../screens/MatchDetailScreen';
import TermsScreen from '../screens/TermsScreen';
import PrivacyPolicyScreen from '../screens/PrivacyPolicyScreen';

const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

function MainTabs() {
  const { logout } = useAuth();

  return (
    <Tab.Navigator
      screenOptions={{
        tabBarActiveTintColor: theme.colors.accent,
        tabBarInactiveTintColor: theme.colors.textMuted,
        tabBarStyle: {
          backgroundColor: theme.colors.surface,
          borderTopColor: theme.colors.tombstone,
          borderTopWidth: 1,
        },
        headerStyle: {
          backgroundColor: theme.colors.surface,
        },
        headerTintColor: theme.colors.primary,
        headerShadowVisible: true,
      }}
    >
      <Tab.Screen
        name="Upload"
        component={UploadScreen}
        options={{
          tabBarLabel: 'Upload',
          tabBarIcon: ({ color, focused }) => (
            <Image
              source={require('../../assets/upload.png')}
              style={{
                width: 28,
                height: 28,
                opacity: focused ? 1 : 0.6,
              }}
            />
          ),
          headerRight: () => (
            <TouchableOpacity
              onPress={logout}
              style={{ marginRight: 15 }}
            >
              <Text style={{ color: theme.colors.danger, fontSize: 16 }}>Logout</Text>
            </TouchableOpacity>
          ),
        }}
      />
      <Tab.Screen
        name="Socks"
        component={SocksScreen}
        options={{
          tabBarLabel: 'Singles',
          tabBarIcon: ({ color, focused }) => (
            <Image
              source={require('../../assets/single.png')}
              style={{
                width: 28,
                height: 28,
                opacity: focused ? 1 : 0.6,
              }}
            />
          ),
          headerRight: () => (
            <TouchableOpacity
              onPress={logout}
              style={{ marginRight: 15 }}
            >
              <Text style={{ color: theme.colors.danger, fontSize: 16 }}>Logout</Text>
            </TouchableOpacity>
          ),
        }}
      />
      <Tab.Screen
        name="Matches"
        component={MatchesScreen}
        options={{
          tabBarLabel: 'Reunions',
          tabBarIcon: ({ color, focused }) => (
            <Image
              source={require('../../assets/matches.png')}
              style={{
                width: 28,
                height: 28,
                opacity: focused ? 1 : 0.6,
              }}
            />
          ),
          headerRight: () => (
            <TouchableOpacity
              onPress={logout}
              style={{ marginRight: 15 }}
            >
              <Text style={{ color: theme.colors.danger, fontSize: 16 }}>Logout</Text>
            </TouchableOpacity>
          ),
        }}
      />
    </Tab.Navigator>
  );
}

function AuthStack() {
  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: false,
      }}
    >
      <Stack.Screen name="Login" component={LoginScreen} />
      <Stack.Screen name="Register" component={RegisterScreen} />
      <Stack.Screen 
        name="Terms" 
        component={TermsScreen}
        options={{
          headerShown: true,
          title: 'Terms of Service',
          headerStyle: {
            backgroundColor: theme.colors.surface,
          },
          headerTintColor: theme.colors.primary,
        }}
      />
      <Stack.Screen 
        name="PrivacyPolicy" 
        component={PrivacyPolicyScreen}
        options={{
          headerShown: true,
          title: 'Privacy Policy',
          headerStyle: {
            backgroundColor: theme.colors.surface,
          },
          headerTintColor: theme.colors.primary,
        }}
      />
    </Stack.Navigator>
  );
}

function MainStack() {
  return (
    <Stack.Navigator>
      <Stack.Screen
        name="MainTabs"
        component={MainTabs}
        options={{ headerShown: false }}
      />
      <Stack.Screen
        name="SockDetail"
        component={SockDetailScreen}
        options={{
          title: 'Soul Details',
          headerStyle: {
            backgroundColor: theme.colors.surface,
          },
          headerTintColor: theme.colors.primary,
        }}
      />
      <Stack.Screen
        name="MatchDetail"
        component={MatchDetailScreen}
        options={{
          title: 'Soul Mates',
          headerStyle: {
            backgroundColor: theme.colors.surface,
          },
          headerTintColor: theme.colors.heartGlow,
        }}
      />
    </Stack.Navigator>
  );
}

export default function AppNavigator() {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return null; // Or a loading screen
  }

  return (
    <NavigationContainer>
      {user ? <MainStack /> : <AuthStack />}
    </NavigationContainer>
  );
}
