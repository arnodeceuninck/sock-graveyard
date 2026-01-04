from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/sock_graveyard"
    
    # Security
    secret_key: str = "your-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 hours
    
    # CORS
    cors_origins: list[str] = ["https://socks.arnodece.com", "http://localhost", "http://localhost:19006"]
    
    # Storage
    upload_dir: str = "./uploads"
    
    # Model
    embedding_dim: int = 1280  # EfficientNet-B0 output dimension
    
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()
