from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    # Default to SQLite for local development, PostgreSQL for Docker production
    database_url: str = "sqlite:///./sock_graveyard.db"
    
    # Security
    secret_key: str = "your-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 hours
    
    # Google OAuth
    google_client_id: str = "458929815388-10a0rbli2n82gr61elor6eg3m83ncs23.apps.googleusercontent.com"
    google_android_client_id: str = "458929815388-ar26q0t2mmqi5r70g8scikncrjri4mei.apps.googleusercontent.com"
    
    # CORS
    cors_origins: list[str] = [
        "https://socks.arnodece.com", 
        "http://localhost", 
        "http://localhost:19006",
        "http://192.168.0.148:19006",  # Local network access for mobile dev
        "http://localhost:8081",        # Expo dev server
        "http://192.168.0.148:8081",   # Expo dev server on network
    ]
    
    # Storage
    upload_dir: str = "./uploads"
    
    # Model
    embedding_dim: int = 1280  # EfficientNet-B0 output dimension
    
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()
