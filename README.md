# 🧦 Sock Graveyard

> A "Most Wanted" style sock matching application using AI-powered image recognition

## 📖 Overview

**Sock Graveyard** is an intelligent sock matching application that helps you find pairs of lost socks using advanced computer vision and machine learning. When you can't find a matching pair after doing laundry, simply take a picture of the lonely sock and let our AI find its match!

### Key Features

- 📸 **Camera Integration**: Take photos or upload from gallery directly in the app
- 🎯 **AI-Powered Matching**: Uses OpenAI CLIP embeddings for highly accurate sock matching
- �️ **Smart Image Processing**: Automatic background removal and sock cropping
- 🎨 **Feature Extraction**: Analyzes color, pattern, and texture
- 🔒 **Secure Authentication**: JWT-based auth with bcrypt password hashing
- 📱 **Cross-Platform**: Works on iOS, Android, and Web (via React Native/Expo)
- 🎭 **Most Wanted Theme**: Unique wanted poster aesthetic with dark/light mode
- 🐳 **Docker-Ready**: One command deployment with docker-compose
- 🔍 **Vector Search**: Powered by PostgreSQL with pgvector extension

> **New!** Full camera and image upload functionality is now available! See [CAMERA_GUIDE.md](CAMERA_GUIDE.md) for details.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Nginx Reverse Proxy                      │
│                        (Port 80)                             │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ├─────────────> Static Files
                 │
                 ├─────────────> /api/* ──────────┐
                 │                                  │
                 └─────────────> /docs, /health    │
                                                    ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                           │
│                      (Port 8000)                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  • Authentication (JWT)                              │  │
│  │  • Image Upload & Processing                         │  │
│  │  • CLIP Embedding Generation                         │  │
│  │  • Feature Extraction (Color, Pattern, Texture)      │  │
│  │  • Similarity Search                                 │  │
│  └──────────────────────────────────────────────────────┘  │
└──┬────────────────────────────────────────┬─────────────────┘
   │                                        │
   │                                        │
   ▼                                        ▼
┌──────────────────────────┐    ┌──────────────────────────┐
│  PostgreSQL + pgvector   │    │      Redis Cache         │
│      (Port 5432)         │    │      (Port 6379)         │
│                          │    │                          │
│  • Users                 │    │  • Sessions              │
│  • Socks                 │    │  • Temp Data             │
│  • Vector Embeddings     │    └──────────────────────────┘
└──────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 18+ (for frontend development)
- Python 3.11+ (for local backend development)

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/sock-graveyard.git
cd sock-graveyard
```

### 2. Set Up Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and set a secure `SECRET_KEY`:

```bash
# Generate a secure key (on Windows PowerShell):
# [System.Convert]::ToBase64String([System.Security.Cryptography.RandomNumberGenerator]::GetBytes(32))

# Or use Python:
# python -c "import secrets; print(secrets.token_hex(32))"
```

### 3. Start the Application

```bash
docker-compose up -d
```

This will start:
- PostgreSQL with pgvector (port 5432)
- Redis (port 6379)
- FastAPI Backend (port 8000)
- Nginx Reverse Proxy (port 80)

### 4. Verify Installation

```bash
# Check health endpoint
curl http://localhost/health

# Access API documentation
# Open in browser: http://localhost/docs
```

### 5. Run Database Migrations

Migrations run automatically on container startup, but you can also run manually:

```bash
docker-compose exec backend alembic upgrade head
```

## 📱 Frontend Setup (React Native / Expo)

The frontend will be created using Expo for cross-platform support. To set it up locally:

```bash
cd frontend
npm install
npm start
```

This opens Expo DevTools where you can:
- Run on iOS Simulator
- Run on Android Emulator  
- Scan QR code to run on physical device
- Run in web browser

## 🧪 Testing

### Backend API Tests

```bash
# Run pytest tests
docker-compose exec backend pytest tests/test_e2e.py -v

# Run with coverage
docker-compose exec backend pytest --cov=app tests/
```

### Matching Algorithm Test Script

Test the CLIP embedding and matching algorithm with sample images:

```bash
docker-compose exec backend python test_matching.py sock1.jpg sock2.jpg
```

### Selenium E2E Tests

```bash
# Install ChromeDriver first, then:
cd backend
python tests/test_selenium.py
```

## 📚 API Documentation

Once the application is running, visit:

- **Swagger UI**: http://localhost/docs
- **ReDoc**: http://localhost/redoc

### Key Endpoints

#### Authentication

```
POST /api/auth/register
POST /api/auth/login
GET  /api/users/me
```

#### Sock Operations

```
POST   /api/socks/              # Upload a sock image
GET    /api/socks/              # List all socks
GET    /api/socks/{id}          # Get specific sock
GET    /api/socks/{id}/image    # Get sock image
POST   /api/socks/search        # Search for similar socks
POST   /api/socks/match         # Confirm a match
DELETE /api/socks/{id}          # Remove from graveyard
```

### Example Usage

#### 1. Register a User

```bash
curl -X POST http://localhost/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "sockfinder",
    "password": "SecurePass123"
  }'
```

#### 2. Login

```bash
curl -X POST http://localhost/api/auth/login \
  -F "username=sockfinder" \
  -F "password=SecurePass123"
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

#### 3. Upload a Sock

```bash
curl -X POST http://localhost/api/socks/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@mysock.jpg" \
  -F "description=Blue striped sock"
```

#### 4. Search for Matches

```bash
curl -X POST "http://localhost/api/socks/search?sock_id=1&threshold=0.85" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🎨 Most Wanted Theme

The application features a unique "Most Wanted" poster aesthetic:

- **Typography**: Western/wanted poster fonts
- **Colors**: 
  - Light mode: Aged paper tones (#F4E4C1, #8B4513)
  - Dark mode: Noir with aged accents (#1A1A1A, #FFD700)
- **Design Elements**:
  - Torn paper edges
  - Vintage stamps and badges
  - Wanted poster frames
  - "REWARD" banners for matches

## 🔧 Development

### Project Structure

```
sock-graveyard/
├── backend/
│   ├── alembic/                 # Database migrations
│   ├── app/
│   │   ├── routers/             # API endpoints
│   │   ├── services/            # Business logic
│   │   ├── models.py            # SQLAlchemy models
│   │   ├── schemas.py           # Pydantic schemas
│   │   ├── auth.py              # Authentication
│   │   ├── config.py            # Configuration
│   │   └── main.py              # FastAPI app
│   ├── tests/                   # Test files
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                    # React Native Expo app
│   ├── src/
│   │   ├── screens/
│   │   ├── components/
│   │   ├── navigation/
│   │   └── services/
│   ├── package.json
│   └── app.json
├── nginx/                       # Nginx configuration
├── docker-compose.yml
└── README.md
```

### Adding New Features

1. **Backend**: Add routes in `backend/app/routers/`
2. **Database**: Create migrations with `alembic revision --autogenerate -m "description"`
3. **Frontend**: Add screens in `frontend/src/screens/`
4. **Tests**: Add tests in `backend/tests/`

### Code Quality

The project follows:
- **PEP 8** for Python code
- **Type hints** throughout Python code
- **Comprehensive error handling** with proper logging
- **No code duplication** - DRY principle
- **Security best practices** - bcrypt hashing, JWT tokens, CORS configuration

## 🔒 Security

- **Password Hashing**: Bcrypt with automatic salting
- **JWT Tokens**: Secure token-based authentication
- **CORS**: Configurable cross-origin resource sharing
- **SQL Injection Protection**: SQLAlchemy ORM
- **File Upload Validation**: Type and size checks
- **Rate Limiting**: Can be added via middleware (future enhancement)

## 🐛 Troubleshooting

### Container Issues

```bash
# View logs
docker-compose logs -f backend

# Restart services
docker-compose restart

# Rebuild containers
docker-compose up -d --build
```

### Database Issues

```bash
# Connect to PostgreSQL
docker-compose exec db psql -U sockuser -d sockgraveyard

# Reset database
docker-compose down -v
docker-compose up -d
```

### Python Dependencies

```bash
# Install new dependency
docker-compose exec backend pip install package-name

# Update requirements.txt
docker-compose exec backend pip freeze > requirements.txt
```

## 📊 Performance Considerations

- **Vector Search**: pgvector provides efficient similarity search
- **Image Caching**: Redis caches frequently accessed data
- **Background Processing**: Can add Celery for async tasks (future enhancement)
- **Connection Pooling**: SQLAlchemy pools database connections

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **OpenAI CLIP**: For the powerful image embedding model
- **pgvector**: For efficient vector similarity search in PostgreSQL
- **rembg**: For background removal
- **FastAPI**: For the excellent Python web framework
- **Expo**: For simplifying cross-platform mobile development

## 📞 Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Check existing documentation
- Review API docs at `/docs`

---

**Happy Sock Matching!** 🧦✨
