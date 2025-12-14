import io
import json
from typing import List, Tuple, Optional
import numpy as np
import torch
import open_clip
from PIL import Image
import cv2
from sklearn.cluster import KMeans
from app.config import settings
from app.logging_config import get_logger

logger = get_logger()


class CLIPEmbeddingService:
    """Service for generating CLIP embeddings and extracting features"""
    
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Initializing CLIP model on device: {self.device}")
        
        # Load CLIP model
        self.model, _, self.preprocess = open_clip.create_model_and_transforms(
            settings.CLIP_MODEL_NAME,
            pretrained=settings.CLIP_PRETRAINED
        )
        self.model.to(self.device)
        self.model.eval()
        
        logger.info(f"CLIP model {settings.CLIP_MODEL_NAME} loaded successfully")
    
    async def generate_embedding(self, image_path: str) -> Optional[np.ndarray]:
        """
        Generate CLIP embedding for an image
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Numpy array of embedding (512 dimensions) or None on error
        """
        try:
            logger.debug(f"Generating embedding for {image_path}")
            
            # Load and preprocess image
            image = Image.open(image_path).convert('RGB')
            image_tensor = self.preprocess(image).unsqueeze(0).to(self.device)
            
            # Generate embedding
            with torch.no_grad():
                embedding = self.model.encode_image(image_tensor)
                embedding = embedding.cpu().numpy()[0]
            
            # Normalize embedding
            embedding = embedding / np.linalg.norm(embedding)
            
            logger.debug(f"Generated embedding with shape {embedding.shape}")
            return embedding
            
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            return None
    
    async def extract_features(self, image_path: str) -> dict:
        """
        Extract visual features from sock image:
        - Dominant color
        - Pattern type
        - Texture features
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary of extracted features
        """
        try:
            logger.debug(f"Extracting features for {image_path}")
            
            # Load image
            image = cv2.imread(image_path)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Extract dominant color
            dominant_color = self._extract_dominant_color(image_rgb)
            
            # Detect pattern type
            pattern_type = self._detect_pattern(image)
            
            # Extract texture features
            texture_features = self._extract_texture_features(image)
            
            features = {
                "dominant_color": dominant_color,
                "pattern_type": pattern_type,
                "texture_features": json.dumps(texture_features)
            }
            
            logger.debug(f"Extracted features: {features}")
            return features
            
        except Exception as e:
            logger.error(f"Failed to extract features: {e}")
            return {
                "dominant_color": None,
                "pattern_type": "unknown",
                "texture_features": json.dumps({})
            }
    
    def _extract_dominant_color(self, image: np.ndarray, n_colors: int = 5) -> str:
        """Extract dominant color using K-means clustering"""
        try:
            # Reshape image to list of pixels
            pixels = image.reshape(-1, 3)
            
            # Remove white and near-white pixels (background)
            mask = np.all(pixels < 240, axis=1)
            pixels = pixels[mask]
            
            if len(pixels) == 0:
                return "#808080"  # Gray as default
            
            # Apply K-means
            kmeans = KMeans(n_clusters=min(n_colors, len(pixels)), random_state=42, n_init=10)
            kmeans.fit(pixels)
            
            # Get most common color
            labels = kmeans.labels_
            counts = np.bincount(labels)
            dominant_cluster = np.argmax(counts)
            dominant_color_rgb = kmeans.cluster_centers_[dominant_cluster].astype(int)
            
            # Convert to hex
            hex_color = "#{:02x}{:02x}{:02x}".format(*dominant_color_rgb)
            
            logger.debug(f"Dominant color: {hex_color}")
            return hex_color
            
        except Exception as e:
            logger.warning(f"Dominant color extraction failed: {e}")
            return "#808080"
    
    def _detect_pattern(self, image: np.ndarray) -> str:
        """Detect pattern type (solid, striped, dotted, etc.)"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Calculate edge density
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / edges.size
            
            # Calculate frequency domain features
            f_transform = np.fft.fft2(gray)
            f_shift = np.fft.fftshift(f_transform)
            magnitude_spectrum = np.abs(f_shift)
            
            # Simple heuristics for pattern detection
            if edge_density < 0.05:
                pattern = "solid"
            elif edge_density < 0.15:
                # Check for periodic patterns
                center_y, center_x = np.array(magnitude_spectrum.shape) // 2
                outer_region = magnitude_spectrum.copy()
                outer_region[center_y-20:center_y+20, center_x-20:center_x+20] = 0
                
                if np.max(outer_region) > np.mean(magnitude_spectrum) * 10:
                    pattern = "striped"
                else:
                    pattern = "textured"
            else:
                pattern = "complex"
            
            logger.debug(f"Detected pattern: {pattern} (edge_density: {edge_density:.3f})")
            return pattern
            
        except Exception as e:
            logger.warning(f"Pattern detection failed: {e}")
            return "unknown"
    
    def _extract_texture_features(self, image: np.ndarray) -> dict:
        """Extract texture features using GLCM and other methods"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Calculate basic statistics
            mean_intensity = float(np.mean(gray))
            std_intensity = float(np.std(gray))
            
            # Calculate gradient features
            sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            gradient_magnitude = np.sqrt(sobelx**2 + sobely**2)
            mean_gradient = float(np.mean(gradient_magnitude))
            
            # Calculate local binary pattern (simplified)
            lbp = self._simple_lbp(gray)
            lbp_histogram = np.histogram(lbp, bins=10, range=(0, 255))[0]
            lbp_features = [float(x) for x in lbp_histogram]
            
            features = {
                "mean_intensity": mean_intensity,
                "std_intensity": std_intensity,
                "mean_gradient": mean_gradient,
                "lbp_histogram": lbp_features
            }
            
            return features
            
        except Exception as e:
            logger.warning(f"Texture feature extraction failed: {e}")
            return {}
    
    def _simple_lbp(self, image: np.ndarray, radius: int = 1) -> np.ndarray:
        """Simple Local Binary Pattern implementation"""
        height, width = image.shape
        lbp = np.zeros_like(image)
        
        for i in range(radius, height - radius):
            for j in range(radius, width - radius):
                center = image[i, j]
                code = 0
                
                # 8-neighbor pattern
                code |= (image[i-1, j-1] > center) << 7
                code |= (image[i-1, j] > center) << 6
                code |= (image[i-1, j+1] > center) << 5
                code |= (image[i, j+1] > center) << 4
                code |= (image[i+1, j+1] > center) << 3
                code |= (image[i+1, j] > center) << 2
                code |= (image[i+1, j-1] > center) << 1
                code |= (image[i, j-1] > center) << 0
                
                lbp[i, j] = code
        
        return lbp
    
    def calculate_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Similarity score between 0 and 1
        """
        try:
            # Cosine similarity
            similarity = np.dot(embedding1, embedding2) / (
                np.linalg.norm(embedding1) * np.linalg.norm(embedding2)
            )
            
            # Convert from [-1, 1] to [0, 1]
            similarity = (similarity + 1) / 2
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Similarity calculation failed: {e}")
            return 0.0
    
    def calculate_color_similarity(self, hex_color1: str, hex_color2: str) -> float:
        """
        Calculate color similarity between two hex colors using perceptual color distance
        
        Args:
            hex_color1: First hex color (e.g., "#FF0000")
            hex_color2: Second hex color (e.g., "#FE0101")
            
        Returns:
            Similarity score between 0 and 1 (1 = identical colors)
        """
        try:
            # Convert hex to RGB
            def hex_to_rgb(hex_color):
                hex_color = hex_color.lstrip('#')
                return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            
            r1, g1, b1 = hex_to_rgb(hex_color1)
            r2, g2, b2 = hex_to_rgb(hex_color2)
            
            # Calculate perceptual color distance (weighted Euclidean)
            # Human eye is more sensitive to green, then red, then blue
            # Using a simplified weighted formula
            r_mean = (r1 + r2) / 2
            delta_r = r1 - r2
            delta_g = g1 - g2
            delta_b = b1 - b2
            
            # Weighted color distance formula
            weight_r = 2 + r_mean / 256
            weight_g = 4.0
            weight_b = 2 + (255 - r_mean) / 256
            
            distance = np.sqrt(
                weight_r * delta_r ** 2 +
                weight_g * delta_g ** 2 +
                weight_b * delta_b ** 2
            )
            
            # Normalize to [0, 1] range
            # Maximum possible distance is roughly 765 (for weighted RGB)
            max_distance = 765
            similarity = 1.0 - min(distance / max_distance, 1.0)
            
            return float(similarity)
            
        except Exception as e:
            logger.warning(f"Color similarity calculation failed: {e}")
            return 0.0


# Singleton instance
clip_service = CLIPEmbeddingService()
