from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import auth, singles, matches
from app.config import get_settings

settings = get_settings()

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="Sock Graveyard API",
    description="A minimal API for matching lost socks",
    version="1.0.0",
    root_path="/api"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(singles.router)
app.include_router(matches.router)


@app.get("/")
def root():
    """Root endpoint."""
    return {"message": "Welcome to Sock Graveyard API"}


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
