import os
import io
from typing import Tuple, Optional
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np
from rembg import remove
from .config import ModelConfig
from .logging_config import get_logger

logger = get_logger()


class ImagePreprocessor:
    """Service for preprocessing sock images"""
    
    def __init__(self, config: Optional[ModelConfig] = None):
        self.config = config or ModelConfig()
        self.target_size = (512, 512)
        self.background_color = (255, 255, 255)  # White background
    
    async def preprocess_image(
        self,
        image_bytes: bytes,
        output_path: str
    ) -> Tuple[str, Optional[str]]:
        """
        Preprocess sock image:
        1. Remove background
        2. Auto-crop to sock boundaries
        3. Resize to standard size
        4. Enhance contrast
        
        Args:
            image_bytes: Raw image bytes
            output_path: Path to save processed image
            
        Returns:
            Tuple of (processed_image_path, error_message)
        """
        try:
            logger.info("Starting image preprocessing")
            
            # Load image
            image = Image.open(io.BytesIO(image_bytes))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                logger.debug(f"Converting image from {image.mode} to RGB")
                image = image.convert('RGB')
            
            # Remove background
            logger.debug("Removing background")
            image_no_bg = self._remove_background(image)
            
            # Auto-crop to content
            logger.debug("Auto-cropping to content")
            cropped_image = self._auto_crop(image_no_bg)
            
            # Resize while maintaining aspect ratio
            logger.debug(f"Resizing to {self.target_size}")
            resized_image = self._resize_with_padding(cropped_image)
            
            # Enhance contrast
            logger.debug("Enhancing contrast")
            enhanced_image = self._enhance_contrast(resized_image)
            
            # Save processed image
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            enhanced_image.save(output_path, 'JPEG', quality=95)
            
            logger.info(f"Image preprocessing completed: {output_path}")
            return output_path, None
            
        except Exception as e:
            error_msg = f"Image preprocessing failed: {str(e)}"
            logger.error(error_msg)
            return None, error_msg
    
    def _remove_background(self, image: Image.Image) -> Image.Image:
        """Remove background using rembg"""
        try:
            # Convert to bytes
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            
            # Remove background
            output = remove(img_byte_arr)
            
            # Convert back to PIL Image
            result = Image.open(io.BytesIO(output))
            
            # Create white background
            background = Image.new('RGBA', result.size, (*self.background_color, 255))
            background.paste(result, (0, 0), result)
            
            return background.convert('RGB')
            
        except Exception as e:
            logger.warning(f"Background removal failed: {e}. Using original image.")
            return image
    
    def _auto_crop(self, image: Image.Image) -> Image.Image:
        """Auto-crop image to content boundaries"""
        try:
            # Convert to numpy array
            img_array = np.array(image)
            
            # Find non-white pixels
            mask = np.any(img_array != 255, axis=-1)
            
            if not mask.any():
                # If all white, return original
                return image
            
            # Get bounding box
            coords = np.argwhere(mask)
            y0, x0 = coords.min(axis=0)
            y1, x1 = coords.max(axis=0) + 1
            
            # Add padding (10% on each side)
            height, width = img_array.shape[:2]
            padding_y = int((y1 - y0) * 0.1)
            padding_x = int((x1 - x0) * 0.1)
            
            y0 = max(0, y0 - padding_y)
            y1 = min(height, y1 + padding_y)
            x0 = max(0, x0 - padding_x)
            x1 = min(width, x1 + padding_x)
            
            # Crop
            cropped = image.crop((x0, y0, x1, y1))
            return cropped
            
        except Exception as e:
            logger.warning(f"Auto-crop failed: {e}. Using original image.")
            return image
    
    def _resize_with_padding(self, image: Image.Image) -> Image.Image:
        """Resize image to target size with padding to maintain aspect ratio"""
        # Calculate scaling factor
        width_ratio = self.target_size[0] / image.width
        height_ratio = self.target_size[1] / image.height
        scale = min(width_ratio, height_ratio)
        
        # Calculate new dimensions
        new_width = int(image.width * scale)
        new_height = int(image.height * scale)
        
        # Resize image
        resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Create new image with padding
        new_image = Image.new('RGB', self.target_size, self.background_color)
        
        # Calculate paste position (center)
        paste_x = (self.target_size[0] - new_width) // 2
        paste_y = (self.target_size[1] - new_height) // 2
        
        # Paste resized image
        new_image.paste(resized, (paste_x, paste_y))
        
        return new_image
    
    def _enhance_contrast(self, image: Image.Image, factor: float = 1.2) -> Image.Image:
        """Enhance image contrast"""
        try:
            enhancer = ImageEnhance.Contrast(image)
            return enhancer.enhance(factor)
        except Exception as e:
            logger.warning(f"Contrast enhancement failed: {e}. Using original image.")
            return image
