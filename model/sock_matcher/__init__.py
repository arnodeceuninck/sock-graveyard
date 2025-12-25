"""
Sock Matcher ML Models Package

This package contains machine learning models and image processing utilities
for the Sock Graveyard application. It can be used as a standalone library
or imported by the backend service.
"""

from .clip_embedding import CLIPEmbeddingService
from .image_preprocessing import ImagePreprocessor

__version__ = "0.1.0"

__all__ = [
    "CLIPEmbeddingService",
    "ImagePreprocessor",
]
