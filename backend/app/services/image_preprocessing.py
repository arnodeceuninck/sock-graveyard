"""
Backend wrapper for Image Preprocessing Service

This module provides a thin wrapper around the sock_matcher model package,
integrating it with the backend's configuration and logging systems.
"""

from typing import Tuple, Optional
from sock_matcher import ImagePreprocessor as ModelImagePreprocessor
from sock_matcher.config import ModelConfig
from sock_matcher import logging_config as model_logging
from app.config import settings
from app.logging_config import get_logger

# Set backend logger for model package
model_logging.set_logger(get_logger())


class ImagePreprocessor:
    """Backend wrapper for image preprocessing service"""
    
    def __init__(self):
        # Create model config from backend settings
        model_config = ModelConfig.from_backend_settings(settings)
        
        # Initialize model service
        self._service = ModelImagePreprocessor(config=model_config)
    
    async def preprocess_image(
        self,
        image_bytes: bytes,
        output_path: str
    ) -> Tuple[str, Optional[str]]:
        """
        Preprocess sock image
        
        Args:
            image_bytes: Raw image bytes
            output_path: Path to save processed image
            
        Returns:
            Tuple of (processed_image_path, error_message)
        """
        return await self._service.preprocess_image(image_bytes, output_path)
    
    async def preprocess_image(
        self,
        image_bytes: bytes,
        output_path: str
    ) -> Tuple[str, Optional[str]]:
        """
        Preprocess sock image
        
        Args:
            image_bytes: Raw image bytes
            output_path: Path to save processed image
            
        Returns:
            Tuple of (processed_image_path, error_message)
        """
        return await self._service.preprocess_image(image_bytes, output_path)


# Singleton instance
image_preprocessor = ImagePreprocessor()
