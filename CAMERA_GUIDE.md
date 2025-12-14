# 📸 Camera & Image Upload Guide

The Sock Graveyard app now has fully functional camera and image upload capabilities!

## Features Implemented

### ✅ Camera Screen
- **Take Photo**: Use device camera to capture sock images
- **Choose from Gallery**: Select existing photos from your device
- **Camera Controls**:
  - Flip camera (front/back)
  - Cancel capture
  - Instant preview after capture
- **Permission Handling**: Automatically requests camera and photo library permissions

### ✅ Image Upload Screen
- **Image Preview**: Review your photo before uploading
- **Add Description**: Optional 200-character description for your sock
- **Upload Progress**: Visual feedback during upload and processing
- **Smart Navigation**: After upload, choose to view matches or add another sock

### ✅ Backend Integration
- Images are automatically preprocessed (background removal, cropping)
- CLIP embeddings generated for AI-powered matching
- Visual features extracted (color, pattern, texture)
- Immediate similarity search for potential matches

## How to Use

### 1. Start the App

```powershell
# Start both backend and frontend
.\run_local_dev.ps1
```

This will:
- Start backend API at http://localhost:8000
- Start frontend (Expo will open automatically)
- You can scan QR code for mobile or press 'w' for web

### 2. Take a Photo

1. Navigate to the **Camera** tab
2. Choose one of two options:
   - **📷 Take Photo**: Opens camera to capture a new image
   - **🖼️ Choose from Gallery**: Select an existing photo

### 3. For Taking a Photo:

1. Grant camera permissions when prompted
2. Point camera at your sock (follow the tips!)
3. Tap the large capture button (center)
4. Review the photo
5. Use ✕ to cancel or 🔄 to flip camera

### 4. Review & Upload

1. After capturing/selecting, you'll see the **Review & Upload** screen
2. Preview your image
3. Optionally add a description (e.g., "Blue striped athletic sock")
4. Tap **🔍 Upload & Find Matches**
5. Wait while the image is processed and matches are found
6. Choose to view matches or add another sock

## Photography Tips

For best matching results:
- **Good Lighting**: Use natural light or bright indoor lighting
- **Flat Surface**: Lay sock flat on a solid-colored background
- **Full Sock**: Show the entire sock including heel and toe
- **No Shadows**: Avoid harsh shadows or glare
- **Clear Focus**: Ensure the sock is in sharp focus

## API Configuration

The frontend automatically connects to the backend based on your configuration:

**Default**: `http://localhost:8000/api`

To change the API URL, create/edit `.env` in the frontend directory:

```
EXPO_PUBLIC_API_URL=http://your-backend-url/api
```

## Platform Support

### Mobile (iOS/Android)
- Full camera functionality
- Gallery access
- Native image picker
- Automatic permission requests

### Web
- Gallery selection works
- Camera functionality may be limited (browser dependent)
- Recommended to use mobile for full experience

## Troubleshooting

### "Camera permission is required"
- Grant camera permissions in your device settings
- App will prompt you automatically

### "Failed to upload sock"
- Check backend is running (`http://localhost:8000/docs`)
- Verify API_BASE_URL in `frontend/src/constants/theme.ts`
- Check image size (max 10MB)
- Ensure file is a valid image format (JPG, PNG)

### Image processing takes too long
- First upload may take longer (downloads AI models)
- Subsequent uploads should be faster
- Background removal and AI processing take 5-10 seconds

### Can't see uploaded socks
- Navigate to the **Home** tab
- Pull down to refresh the list
- Check backend logs for errors

## Technical Details

### Frontend Stack
- **expo-camera** (v14.0.0): Camera functionality
- **expo-image-picker** (v14.7.1): Gallery selection
- React Native permissions handling
- TypeScript for type safety

### Backend Processing
1. Image validation (type, size)
2. Save original image
3. Background removal (rembg)
4. Auto-crop to sock boundaries
5. Generate CLIP embedding (512-dim vector)
6. Extract visual features (color, pattern, texture)
7. Store in database with vector index
8. Search for similar socks

### Supported Image Formats
- JPEG/JPG
- PNG
- Maximum file size: 10MB (configurable in backend)

## Next Steps

After uploading socks, you can:
1. View your sock collection in the **Home** tab
2. Browse all socks in the **Graveyard** tab
3. See matching suggestions automatically
4. Confirm matches when you find your sock's partner

## Development Notes

### File Structure
```
frontend/src/screens/
├── CameraScreen.tsx        # Camera interface with gallery option
├── ImageUploadScreen.tsx   # Preview and upload flow
└── HomeScreen.tsx          # Display uploaded socks

frontend/src/services/
└── api.ts                  # API client with uploadSock method

frontend/App.tsx            # Navigation setup
```

### Testing Locally

Test the upload API directly:
```bash
curl -X POST "http://localhost:8000/api/socks/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@/path/to/sock.jpg" \
  -F "description=Test sock"
```

View API documentation:
```
http://localhost:8000/docs
```

## Known Limitations

- Web camera support depends on browser
- Large images may take time to process
- First-time model download can take 30+ seconds
- Background removal works best with solid backgrounds

Enjoy finding your sock matches! 🧦🔍
