import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { TouchableOpacity, Text } from 'react-native';
import { useAuth } from '../contexts/AuthContext';

// Screens
import LoginScreen from '../screens/LoginScreen';
import RegisterScreen from '../screens/RegisterScreen';
import UploadScreen from '../screens/UploadScreen';
import SocksScreen from '../screens/SocksScreen';
import SockDetailScreen from '../screens/SockDetailScreen';
import MatchesScreen from '../screens/MatchesScreen';
import MatchDetailScreen from '../screens/MatchDetailScreen';

const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

function MainTabs() {
  const { logout } = useAuth();

  return (
    <Tab.Navigator
      screenOptions={{
        tabBarActiveTintColor: '#007AFF',
        tabBarInactiveTintColor: '#8E8E93',
        headerStyle: {
          backgroundColor: '#fff',
        },
        headerShadowVisible: true,
      }}
    >
      <Tab.Screen
        name="Upload"
        component={UploadScreen}
        options={{
          tabBarLabel: 'Upload',
          tabBarIcon: ({ color }) => <Text style={{ fontSize: 24 }}>📤</Text>,
          headerRight: () => (
            <TouchableOpacity
              onPress={logout}
              style={{ marginRight: 15 }}
            >
              <Text style={{ color: '#007AFF', fontSize: 16 }}>Logout</Text>
            </TouchableOpacity>
          ),
        }}
      />
      <Tab.Screen
        name="Socks"
        component={SocksScreen}
        options={{
          tabBarLabel: 'Singles',
          tabBarIcon: ({ color }) => <Text style={{ fontSize: 24 }}>🧦</Text>,
          headerRight: () => (
            <TouchableOpacity
              onPress={logout}
              style={{ marginRight: 15 }}
            >
              <Text style={{ color: '#007AFF', fontSize: 16 }}>Logout</Text>
            </TouchableOpacity>
          ),
        }}
      />
      <Tab.Screen
        name="Matches"
        component={MatchesScreen}
        options={{
          tabBarLabel: 'Matches',
          tabBarIcon: ({ color }) => <Text style={{ fontSize: 24 }}>💕</Text>,
          headerRight: () => (
            <TouchableOpacity
              onPress={logout}
              style={{ marginRight: 15 }}
            >
              <Text style={{ color: '#007AFF', fontSize: 16 }}>Logout</Text>
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
          title: 'Sock Details',
          headerStyle: {
            backgroundColor: '#fff',
          },
          headerTintColor: '#007AFF',
        }}
      />
      <Stack.Screen
        name="MatchDetail"
        component={MatchDetailScreen}
        options={{
          title: 'Match Details',
          headerStyle: {
            backgroundColor: '#fff',
          },
          headerTintColor: '#007AFF',
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
