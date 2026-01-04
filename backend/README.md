# Sock Graveyard Backend

A minimal FastAPI backend for matching lost socks using image embeddings.

## Features

- **Authentication**: Register/login with username and password (using bcrypt password hashing)
- **Sock Upload**: Upload sock images and automatically generate embeddings using EfficientNet-B0
- **Sock Management**: List unmatched socks, view sock details and images
- **Similar Sock Search**: Find similar socks using vector similarity search

## Tech Stack

- FastAPI >= 0.128.0
- SQLAlchemy with Alembic for database migrations
- PostgreSQL or SQLite (for debugging)
- EfficientNet-B0 for image embeddings
- JWT for authentication
- Bcrypt for password hashing

## Installation

1. Create a virtual environment:
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

2. Install dependencies:
```powershell
pip install -r requirements.txt
```

3. Configure environment variables:
```powershell
cp .env.example .env
# Edit .env with your settings
```

4. Run database migrations:
```powershell
alembic upgrade head
```

## Running the Server

```powershell
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Authentication
- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login and receive JWT token
- `GET /auth/me` - Get current user info

### Socks
- `POST /socks/upload` - Upload a sock image (authenticated)
- `GET /socks/list` - List all unmatched socks (authenticated)
- `GET /socks/{sock_id}` - Get sock details (authenticated)
- `GET /socks/{sock_id}/image` - Get sock image file (authenticated)
- `POST /socks/search` - Search for similar socks (authenticated)

## Database

The backend uses SQLite by default for easy debugging. To use PostgreSQL:

1. Update `DATABASE_URL` in `.env`:
```
DATABASE_URL=postgresql://user:password@localhost:5432/sock_graveyard
```

2. Run migrations:
```powershell
alembic upgrade head
```

## Project Structure

```
backend/
├── alembic/              # Database migrations
│   ├── versions/
│   └── env.py
├── app/
│   ├── routers/          # API endpoints
│   │   ├── auth.py       # Authentication endpoints
│   │   └── socks.py      # Sock management endpoints
│   ├── auth.py           # Authentication logic
│   ├── config.py         # Configuration
│   ├── database.py       # Database setup
│   ├── embedding.py      # EfficientNet embedding service
│   ├── main.py           # FastAPI app
│   ├── models.py         # SQLAlchemy models
│   └── schemas.py        # Pydantic schemas
├── alembic.ini           # Alembic configuration
├── requirements.txt      # Python dependencies
└── README.md
```

## Security Notes

- Passwords are hashed using bcrypt with automatic salt generation
- JWT tokens are used for authentication
- Change the `SECRET_KEY` in production to a secure random string
- Consider using HTTPS in production
- Configure CORS appropriately for your frontend origin
