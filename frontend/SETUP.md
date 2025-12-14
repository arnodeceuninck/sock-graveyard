# Frontend Setup Guide

## Prerequisites

- Node.js 18+ installed
- npm or yarn package manager
- Expo CLI (will be installed with dependencies)
- For iOS: macOS with Xcode
- For Android: Android Studio with emulator or physical device
- Expo Go app on your mobile device (optional)

## Installation Steps

### 1. Navigate to Frontend Directory

```powershell
cd frontend
```

### 2. Install Dependencies

```powershell
npm install
```

This will install all required packages including:
- React Native
- Expo
- React Navigation
- Axios for API calls
- AsyncStorage for local storage

### 3. Configure API URL

Create a `.env` file in the frontend directory (optional):

```
EXPO_PUBLIC_API_URL=http://your-backend-url/api
```

Or edit `src/constants/theme.ts` to change the default API URL.

### 4. Start the Development Server

```powershell
npm start
```

This will start the Expo development server and show a QR code.

## Running the App

### On Physical Device

1. Install "Expo Go" from App Store (iOS) or Play Store (Android)
2. Scan the QR code shown in the terminal
3. The app will load on your device

### On iOS Simulator (macOS only)

```powershell
npm run ios
```

### On Android Emulator

```powershell
npm run android
```

### On Web Browser

```powershell
npm run web
```

## Project Structure

```
frontend/
├── App.tsx                          # Main app component
├── app.json                         # Expo configuration
├── package.json                     # Dependencies
├── src/
│   ├── components/                  # Reusable components
│   │   ├── Button.tsx
│   │   └── WantedPosterCard.tsx
│   ├── constants/                   # App constants
│   │   └── theme.ts                 # Theme colors and styles
│   ├── contexts/                    # React contexts
│   │   ├── AuthContext.tsx          # Authentication state
│   │   └── ThemeContext.tsx         # Theme state
│   ├── screens/                     # App screens
│   │   ├── LoginScreen.tsx
│   │   ├── RegisterScreen.tsx
│   │   ├── HomeScreen.tsx
│   │   ├── CameraScreen.tsx
│   │   ├── GraveyardScreen.tsx
│   │   └── ProfileScreen.tsx
│   └── services/                    # API services
│       └── api.ts                   # API client
└── assets/                          # Images, fonts, etc.
```

## Features Implemented

✅ Authentication (Login/Register)
✅ Most Wanted theme with light/dark mode
✅ API integration with FastAPI backend
✅ Navigation structure
✅ Reusable components
✅ TypeScript support

## Features To Implement

- Camera integration with expo-camera
- Image picker from gallery
- Sock upload with progress
- Match search results
- Match confirmation flow
- Graveyard management
- Custom fonts for western theme
- Animations and transitions

## Troubleshooting

### TypeScript Errors

The TypeScript errors shown during file creation are normal and will be resolved once you run `npm install` to install all dependencies.

### API Connection Issues

Make sure:
1. Backend is running (`docker-compose up` in root directory)
2. API URL is correct in `src/constants/theme.ts`
3. For physical devices, use your computer's IP address instead of `localhost`
4. Check CORS settings in backend if getting CORS errors

### Metro Bundler Issues

If you encounter caching issues:

```powershell
npx expo start -c
```

### iOS Simulator Not Working

Make sure Xcode is installed and command line tools are configured:

```bash
xcode-select --install
```

### Android Emulator Not Working

Make sure:
1. Android Studio is installed
2. At least one AVD (Android Virtual Device) is created
3. ANDROID_HOME environment variable is set

## Testing

To test the frontend:

1. Start the backend: `docker-compose up` (in root directory)
2. Start the frontend: `npm start` (in frontend directory)
3. Test user registration and login
4. Navigate through the app screens

## Building for Production

### iOS Build

```powershell
npx expo build:ios
```

### Android Build

```powershell
npx expo build:android
```

### Web Build

```powershell
npm run web
npx expo export:web
```

## Next Steps

1. Implement camera screen with expo-camera
2. Add image upload functionality
3. Create match results screen
4. Add loading states and error handling
5. Implement proper navigation between screens
6. Add animations for transitions
7. Test on multiple devices and screen sizes

## Support

For issues with:
- Expo: https://docs.expo.dev/
- React Native: https://reactnative.dev/
- React Navigation: https://reactnavigation.org/

---

**Note:** This is a foundational frontend structure. Additional development is needed for full functionality including camera integration, image handling, and complete user workflows.
