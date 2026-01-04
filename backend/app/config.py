from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./sock_graveyard.db"  # Default to SQLite for debugging
    # database_url: str = "postgresql://user:password@localhost/sock_graveyard"  # Uncomment for PostgreSQL
    
    # Security
    secret_key: str = "your-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 hours
    
    # Storage
    upload_dir: str = "./uploads"
    
    # Model
    embedding_dim: int = 1280  # EfficientNet-B0 output dimension
    
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()
