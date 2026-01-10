# Sock Graveyard

Find your missing socks using AI-powered image matching!

## Overview

Sock Graveyard is a full-stack application that helps you organize and match your lost socks using computer vision. Upload photos of your socks, and the app will automatically find similar matches using deep learning embeddings.

## Project Structure

```
sock-graveyard/
├── backend/          # FastAPI backend with EfficientNet
├── frontend/         # React Native Expo Go mobile app
└── README.md
```

## Features

### Backend
- **FastAPI** REST API (>=0.128.0)
- **SQLAlchemy** with Alembic for database migrations
- **PostgreSQL** or SQLite support
- **JWT Authentication** with bcrypt password hashing
- **EfficientNet-B0** for image embeddings
- **Vector Similarity Search** using cosine similarity

### Frontend
- **React Native** with Expo Go
- **TypeScript** for type safety
- **React Navigation** for routing
- **Camera & Gallery** integration
- **Secure token storage**
- **Auto-matching** after upload

## Quick Start

### Prerequisites

Before starting, you need to configure the following files manually:

#### Required Configuration Files

1. **Backend Environment Variables**
   - Copy `backend/.env.example` to `backend/.env`
   - Set `SECRET_KEY`, `DATABASE_URL`, and Google OAuth credentials

2. **Frontend Google OAuth (Required for Google Sign-In)**
   
   **credentials.json**:
   - Copy `frontend/credentials.json.template` to `frontend/credentials.json`
   - Fill in your Android keystore details:
     - `keystorePassword`: Your keystore password
     - `keyAlias`: Your key alias name
     - `keyPassword`: Your key password
   - Get these from your keystore with: `keytool -list -v -keystore path/to/keystore.jks`
   
   **google-services.json**:
   - Copy `frontend/google-services.json.template` to `frontend/google-services.json`
   - Download the actual file from [Firebase Console](https://console.firebase.google.com/)
   - Add Android app with package name: `com.arnodece.socks`
   - Download `google-services.json` and place in `frontend/` directory

   **Google Cloud Console Setup**:
   - Create OAuth 2.0 credentials for Android (package: `com.arnodece.socks`)
   - Add your keystore's SHA-1 fingerprint to the Android OAuth client
   - Update client IDs in `backend/app/config.py` and `frontend/src/screens/LoginScreen.tsx`

3. **Android Keystore**
   - Place your keystore file at `authentication/siwg/sock-graveyard.jks`
   - Or update the path in `frontend/credentials.json`

### Backend Setup

```powershell
cd backend

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --host 0.0.0.0 --reload
```

API will be available at `http://localhost:8000`

### Frontend Setup

```powershell
cd frontend

# Install dependencies
npm install

# Configure API endpoint (use your computer's IP)
# Edit .env: API_BASE_URL=http://192.168.1.XXX:8000

# Start Expo
npm start
```

Scan QR code with Expo Go app to run on your device.

## How It Works

1. **Register/Login**: Create an account with username and password
2. **Upload Sock**: Take a photo or select from gallery
3. **AI Processing**: Backend generates embedding using EfficientNet-B0
4. **Smart Matching**: Compares with your collection using cosine similarity
5. **View Results**: See similarity scores for potential matches
6. **Manage Collection**: Add to collection if no match found

## Tech Stack

### Backend
- FastAPI
- SQLAlchemy + Alembic
- PostgreSQL / SQLite
- PyTorch + torchvision (EfficientNet-B0)
- python-jose (JWT)
- passlib (bcrypt)

### Frontend
- React Native
- Expo
- TypeScript
- React Navigation
- Axios
- Expo Image Picker
- Expo Secure Store
- Expo Auth Session (Google Sign-In)

## Features

- 🔐 **Authentication**: Email/password and Google Sign-In support
- 📸 **Image Upload**: Camera or gallery integration
- 🤖 **AI Matching**: EfficientNet-B0 embeddings with cosine similarity
- 🧦 **Smart Organization**: Auto-match similar socks
- 📱 **Mobile First**: React Native app with Expo
- 🔒 **Secure**: JWT tokens with Argon2 password hashing

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get JWT token
- `POST /auth/google` - Authenticate with Google ID token
- `GET /auth/me` - Get current user info

### Socks
- `POST /socks/upload` - Upload sock image
- `GET /socks/list` - List unmatched socks
- `GET /socks/{id}` - Get sock details
- `GET /socks/{id}/image` - Get sock image
- `POST /socks/search` - Search similar socks

## Documentation

- [Backend Documentation](backend/README.md)
- [Frontend Documentation](frontend/README.md)
- [Google Sign-In Setup Guide](GOOGLE_SIGNIN_SETUP.md)

## Important Notes

⚠️ **Configuration Files Not Included**

The following files are required but not included in the repository for security:
- `frontend/credentials.json` (use `credentials.json.template`)
- `frontend/google-services.json` (use `google-services.json.template`)
- `authentication/siwg/sock-graveyard.jks` (your Android keystore)
- `backend/.env` (backend environment variables)

See the **Prerequisites** section above for setup instructions.

## Development

### Backend Development
```powershell
# Run with auto-reload
uvicorn app.main:app --reload

# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

### Frontend Development
```powershell
# Start development server
npm start

# Run on specific platform
npm run ios
npm run android
npm run web
```

## Network Configuration

For Expo Go to connect to your backend:

1. Backend must listen on `0.0.0.0`:
   ```powershell
   uvicorn app.main:app --host 0.0.0.0
   ```

2. Frontend must use your computer's IP:
   ```
   API_BASE_URL=http://192.168.1.XXX:8000
   ```

Find your IP:
- Windows: `ipconfig`
- Mac/Linux: `ifconfig`

## Deployment
Fix env files, you can work this out yourself (do not forget sign in with google credentials)
```
docker swarm init
chmod +x deploy-swarm.sh
./deploy-swarm.sh
```

## Troubleshooting

### Backend Issues
- Ensure PostgreSQL is running (if not using SQLite)
- Check database connection string in `.env`
- Verify PyTorch installation for your system

### Frontend Issues
- Both devices must be on same network
- Use computer's IP address, not `localhost`
- Grant camera/photo permissions in phone settings

## License

MIT License - See LICENSE file for details

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
