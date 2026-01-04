import torch
import torchvision.transforms as transforms
from torchvision.models import efficientnet_b0, EfficientNet_B0_Weights
from PIL import Image
import numpy as np
from typing import BinaryIO


class EmbeddingService:
    """Service for creating image embeddings using EfficientNet-B0."""
    
    def __init__(self):
        # Load pre-trained EfficientNet-B0 model
        self.model = efficientnet_b0(weights=EfficientNet_B0_Weights.IMAGENET1K_V1)
        
        # Remove the classification head to get embeddings
        self.model = torch.nn.Sequential(*list(self.model.children())[:-1])
        
        self.model.eval()
        
        # Use GPU if available
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        
        # Image preprocessing pipeline
        self.transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
    
    def create_embedding(self, image_file: BinaryIO) -> bytes:
        """
        Create an embedding for an image.
        
        Args:
            image_file: File-like object containing the image
            
        Returns:
            bytes: The embedding as bytes
        """
        try:
            # Load and preprocess image
            image = Image.open(image_file).convert('RGB')
            image_tensor = self.transform(image).unsqueeze(0)
            
            # Always use CPU for inference to avoid device issues
            # This is more reliable across different environments
            image_tensor = image_tensor.cpu()
            
            # Generate embedding
            with torch.no_grad():
                embedding = self.model.cpu()(image_tensor)
                
            # Flatten and convert to numpy
            embedding = embedding.squeeze().numpy()
            
            # Normalize the embedding
            embedding = embedding / np.linalg.norm(embedding)
            
            # Convert to bytes for storage
            return embedding.tobytes()
        except Exception as e:
            print(f"Error in create_embedding: {type(e).__name__}: {str(e)}")
            raise
    
    @staticmethod
    def embedding_from_bytes(embedding_bytes: bytes) -> np.ndarray:
        """Convert stored embedding bytes back to numpy array."""
        return np.frombuffer(embedding_bytes, dtype=np.float32)
    
    @staticmethod
    def calculate_similarity(embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding
            embedding2: Second embedding
            
        Returns:
            float: Similarity score between 0 and 1
        """
        # Normalize embeddings
        embedding1 = embedding1 / np.linalg.norm(embedding1)
        embedding2 = embedding2 / np.linalg.norm(embedding2)
        
        # Calculate cosine similarity
        similarity = np.dot(embedding1, embedding2)
        
        return float(similarity)


# Singleton instance
_embedding_service = None


def get_embedding_service() -> EmbeddingService:
    """Get or create the embedding service singleton."""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
