"""
Image preprocessing utilities for sock matching.

Supports different preprocessing strategies:
- none: No preprocessing, use original image
- basic: Basic resize and normalization
- full: Background removal and auto-cropping
"""

import io
import numpy as np
from PIL import Image
from typing import Optional

# Check for optional dependencies
try:
    from rembg import remove
    import cv2
    HAS_PREPROCESSING = True
except ImportError:
    HAS_PREPROCESSING = False


class ImagePreprocessor:
    """Handles image preprocessing for embedding models."""
    
    def __init__(self, mode: str = "none"):
        """
        Initialize preprocessor.
        
        Args:
            mode: Preprocessing mode ("none", "basic", or "full")
        """
        if mode not in ["none", "basic", "full"]:
            raise ValueError(f"Invalid preprocessing mode: {mode}. Must be 'none', 'basic', or 'full'")
        
        self.mode = mode
        
        if mode == "full" and not HAS_PREPROCESSING:
            print(f"⚠ Warning: Full preprocessing requested but rembg/cv2 not available")
            print(f"  Install with: pip install rembg opencv-python")
            self.mode = "none"
    
    def preprocess_image_file(self, image_path: str) -> Image.Image:
        """
        Apply preprocessing to image before embedding.
        
        Args:
            image_path: Path to image file
            
        Returns:
            PIL Image (preprocessed or original)
        """
        image = Image.open(image_path).convert('RGB')
        
        if self.mode == "none":
            return image
        
        elif self.mode == "basic":
            # Basic preprocessing: resize and normalize
            # (Model-specific transforms will be applied later)
            return image
        
        elif self.mode == "full":
            # Full preprocessing: background removal + cropping
            return self._full_preprocess(image)
        
        return image
    
    def _full_preprocess(self, image: Image.Image) -> Image.Image:
        """
        Apply full preprocessing: background removal and auto-cropping.
        
        Args:
            image: Input PIL Image
            
        Returns:
            Preprocessed PIL Image
        """
        if not HAS_PREPROCESSING:
            print(f"⚠ Warning: Full preprocessing requested but dependencies not available")
            return image
        
        try:
            # Remove background
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            
            output = remove(img_byte_arr)
            result = Image.open(io.BytesIO(output))
            
            # Create white background
            background = Image.new('RGB', result.size, (255, 255, 255))
            if result.mode == 'RGBA':
                background.paste(result, (0, 0), result.split()[-1])
            else:
                background = result.convert('RGB')
            
            # Auto-crop to content (remove extra white space)
            img_array = np.array(background)
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            
            # Find non-white pixels
            _, thresh = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY_INV)
            coords = cv2.findNonZero(thresh)
            
            if coords is not None:
                x, y, w, h = cv2.boundingRect(coords)
                # Add padding
                padding = 20
                x = max(0, x - padding)
                y = max(0, y - padding)
                w = min(img_array.shape[1] - x, w + 2 * padding)
                h = min(img_array.shape[0] - y, h + 2 * padding)
                
                cropped = img_array[y:y+h, x:x+w]
                background = Image.fromarray(cropped)
            
            return background
            
        except Exception as e:
            print(f"⚠ Warning: Preprocessing failed ({e}), using original")
            return image
    
    @staticmethod
    def is_available() -> bool:
        """Check if full preprocessing capabilities are available."""
        return HAS_PREPROCESSING
