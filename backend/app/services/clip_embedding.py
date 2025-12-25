"""
Backend wrapper for CLIP Embedding Service

This module provides a thin wrapper around the sock_matcher model package,
integrating it with the backend's configuration and logging systems.
"""

from typing import Optional
import numpy as np
from sock_matcher import CLIPEmbeddingService as ModelCLIPService
from sock_matcher.config import ModelConfig
from sock_matcher import logging_config as model_logging
from app.config import settings
from app.logging_config import get_logger

# Set backend logger for model package
model_logging.set_logger(get_logger())


class CLIPEmbeddingService:
    """Backend wrapper for CLIP embedding service"""
    
    def __init__(self):
        # Create model config from backend settings
        model_config = ModelConfig.from_backend_settings(settings)
        
        # Initialize model service
        self._service = ModelCLIPService(config=model_config)
        
        # Expose device for compatibility
        self.device = self._service.device
    
    async def generate_embedding(self, image_path: str) -> Optional[np.ndarray]:
        """Generate CLIP embedding for an image"""
        return await self._service.generate_embedding(image_path)
    
    async def extract_features(self, image_path: str) -> dict:
        """Extract visual features from sock image"""
        return await self._service.extract_features(image_path)
    
    def calculate_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Calculate cosine similarity between two embeddings"""
        return self._service.calculate_similarity(embedding1, embedding2)
    
    def calculate_color_similarity(self, hex_color1: str, hex_color2: str) -> float:
        """Calculate color similarity between two hex colors"""
        return self._service.calculate_color_similarity(hex_color1, hex_color2)


# Singleton instance
clip_service = CLIPEmbeddingService()

