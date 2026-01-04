# Sock Graveyard Mobile

A React Native Expo Go app for finding matching socks using AI image recognition.

## Features

- **User Authentication**: Register and login with username/password
- **Upload Socks**: Take photos or select from gallery
- **Smart Matching**: Automatically finds similar socks using EfficientNet embeddings
- **Collection Management**: View all your unmatched socks
- **Detailed View**: See sock details including upload date and time

## Prerequisites

- Node.js (v18 or later)
- Expo Go app installed on your mobile device
- Backend API running (see [backend/README.md](../backend/README.md))

## Installation

1. Install dependencies:
```powershell
cd frontend
npm install
```

2. Configure the API endpoint:
```powershell
# Edit .env file
API_BASE_URL=http://YOUR_COMPUTER_IP:8000
```

**Important**: For Expo Go to work, you need to use your computer's local IP address (e.g., `http://192.168.1.100:8000`), not `localhost`.

## Running the App

1. Make sure the backend is running:
```powershell
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

2. Start the Expo development server:
```powershell
cd frontend
npm start
```

3. Scan the QR code with:
   - **iOS**: Camera app
   - **Android**: Expo Go app

## Project Structure

```
frontend/
├── src/
│   ├── contexts/
│   │   └── AuthContext.tsx      # Authentication state management
│   ├── navigation/
│   │   └── AppNavigator.tsx     # Navigation configuration
│   ├── screens/
│   │   ├── LoginScreen.tsx      # Login page
│   │   ├── RegisterScreen.tsx   # Registration page
│   │   ├── UploadScreen.tsx     # Upload & match socks
│   │   ├── SocksScreen.tsx      # Collection overview
│   │   └── SockDetailScreen.tsx # Sock details page
│   ├── services/
│   │   └── api.ts               # API client & endpoints
│   ├── config.ts                # App configuration
│   └── types.ts                 # TypeScript types
├── App.tsx                      # Root component
├── package.json
└── app.json
```

## App Flow

1. **Register/Login**: Create an account or login
2. **Upload**: Take/select a sock photo
3. **Auto-Match**: App automatically searches for similar socks
4. **Review**: See similarity scores for each match
5. **Add to Collection**: If no match, add to your collection
6. **Browse**: View all unmatched socks in your collection
7. **Details**: Tap any sock to see full details

## Screens

### Upload Screen
- Take photo with camera or choose from gallery
- Automatically searches for similar socks after upload
- Shows similarity percentage for each match
- Option to add sock to collection if no match found

### My Socks Screen
- Grid view of all unmatched socks
- Pull to refresh
- Shows upload date for each sock
- Tap to view details

### Sock Detail Screen
- Full-size image view
- Date and time added
- Match status
- Option to find similar socks

## Configuration

### API Endpoint
Update the `.env` file with your backend URL:
```
API_BASE_URL=http://192.168.1.100:8000
```

Find your local IP:
- **Windows**: `ipconfig` (look for IPv4 Address)
- **Mac/Linux**: `ifconfig` (look for inet)

## Troubleshooting

### Cannot connect to backend
- Ensure backend is running with `--host 0.0.0.0`
- Use your computer's IP address, not `localhost`
- Check that both devices are on the same network
- Temporarily disable firewall if needed

### Image upload fails
- Grant camera/photo library permissions
- Check network connection
- Verify backend is accessible

### Authentication issues
- Clear app data and re-login
- Check backend logs for errors
- Verify token is being saved correctly

## Technologies Used

- **React Native**: Mobile framework
- **Expo**: Development platform
- **React Navigation**: Navigation library
- **Axios**: HTTP client
- **Expo Image Picker**: Camera & gallery access
- **Expo Secure Store**: Secure token storage
- **TypeScript**: Type safety

## Development

### Running on different platforms

```powershell
# iOS Simulator (requires macOS)
npm run ios

# Android Emulator
npm run android

# Web (for testing)
npm run web
```

## License

See [LICENSE](../LICENSE) file.
