from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import auth, socks

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="Sock Graveyard API",
    description="A minimal API for matching lost socks",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(socks.router)


@app.get("/")
def root():
    """Root endpoint."""
    return {"message": "Welcome to Sock Graveyard API"}


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
