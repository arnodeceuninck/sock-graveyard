import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://sockuser:sockpassword@db:5432/sockgraveyard"
    
    # Redis
    REDIS_URL: str = "redis://redis:6379"
    
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Environment
    ENVIRONMENT: str = "development"
    
    # Application
    APP_NAME: str = "Sock Graveyard"
    APP_VERSION: str = "1.0.0"
    
    # File Storage
    UPLOAD_DIR: str = "images"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # CLIP Model
    CLIP_MODEL_NAME: str = "ViT-B-32"
    CLIP_PRETRAINED: str = "openai"
    
    # Similarity threshold
    MATCH_THRESHOLD: float = 0.85
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields like VITE_API_URL that are for frontend


settings = Settings()
