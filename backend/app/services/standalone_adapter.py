"""
Adapter to make backend services work in standalone mode (without FastAPI/database)

This module provides wrappers that allow the backend services to run
outside of the FastAPI context, useful for local testing and CLI tools.
"""

import os
import sys
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image
import io


# Make async services work synchronously in standalone mode
def sync_wrapper(async_func):
    """Wrapper to run async functions synchronously"""
    import asyncio
    
    def wrapper(*args, **kwargs):
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(async_func(*args, **kwargs))
    
    return wrapper


class StandaloneImagePreprocessor:
    """Adapter for ImagePreprocessor that works with file paths instead of bytes"""
    
    def __init__(self):
        from app.services.image_preprocessing import ImagePreprocessor
        self._preprocessor = ImagePreprocessor()
    
    def preprocess_image(self, image_path: str, output_path: Optional[str] = None) -> Optional[str]:
        """
        Preprocess image from file path
        
        Args:
            image_path: Path to input image
            output_path: Optional path to save processed image
            
        Returns:
            Path to processed image or None if failed
        """
        try:
            print(f"  📸 Processing: {os.path.basename(image_path)}")
            
            # Read image bytes
            with open(image_path, 'rb') as f:
                image_bytes = f.read()
            
            # Generate output path if not provided
            if output_path is None:
                output_path = f"processed_{os.path.basename(image_path)}"
            
            # Ensure output path is absolute and has a directory
            output_path = os.path.abspath(output_path)
            
            # Call backend preprocessor (wrapped to run synchronously)
            @sync_wrapper
            async def process():
                return await self._preprocessor.preprocess_image(image_bytes, output_path)
            
            result_path, error = process()
            
            if error:
                print(f"    ❌ Error: {error}")
                return None
            
            print(f"    ✅ Saved to: {result_path}")
            return result_path
            
        except Exception as e:
            print(f"    ❌ Error processing image: {e}")
            import traceback
            traceback.print_exc()
            return None


class StandaloneCLIPEmbeddingService:
    """Adapter for CLIPEmbeddingService that works with file paths"""
    
    def __init__(self):
        from app.services.clip_embedding import CLIPEmbeddingService
        self._clip_service = CLIPEmbeddingService()
    
    def generate_embedding(self, image_path: str):
        """Generate embedding from file path"""
        @sync_wrapper
        async def generate():
            return await self._clip_service.generate_embedding(image_path)
        
        return generate()
    
    def extract_features(self, image_path: str) -> dict:
        """Extract features from file path"""
        @sync_wrapper
        async def extract():
            return await self._clip_service.extract_features(image_path)
        
        return extract()
    
    def calculate_similarity(self, embedding1, embedding2) -> float:
        """Calculate similarity (this is already synchronous)"""
        return self._clip_service.calculate_similarity(embedding1, embedding2)
    
    def calculate_color_similarity(self, hex_color1: str, hex_color2: str) -> float:
        """Calculate color similarity (this is already synchronous)"""
        return self._clip_service.calculate_color_similarity(hex_color1, hex_color2)
