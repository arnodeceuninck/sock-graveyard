"""
Model wrapper classes for different embedding architectures.

Each wrapper provides a unified interface for generating embeddings
from images using different pre-trained models.
"""

import numpy as np
from typing import Optional
from PIL import Image

from .preprocessing import ImagePreprocessor

# Check for optional dependencies
try:
    import torch
    import torch.nn as nn
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False

try:
    import open_clip
    HAS_OPEN_CLIP = True
except ImportError:
    HAS_OPEN_CLIP = False

try:
    from transformers import AutoImageProcessor, AutoModel
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False

try:
    from torchvision import models, transforms
    HAS_TORCHVISION = True
except ImportError:
    HAS_TORCHVISION = False


class EmbeddingModelWrapper:
    """Base class for embedding model wrappers"""
    
    def __init__(self, name: str, preprocessing: str = "none"):
        self.name = name
        self.preprocessing = preprocessing
        self.preprocessor = ImagePreprocessor(preprocessing)
        
        if HAS_TORCH:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = "cpu"
    
    def embed_image(self, image_path: str) -> Optional[np.ndarray]:
        """
        Generate embedding for an image.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Normalized embedding as numpy array, or None on failure
        """
        raise NotImplementedError
    
    def get_dimension(self) -> int:
        """Get embedding dimension"""
        raise NotImplementedError


class CLIPModelWrapper(EmbeddingModelWrapper):
    """Wrapper for OpenAI CLIP models"""
    
    def __init__(self, model_name: str = "ViT-B-32", pretrained: str = "openai", preprocessing: str = "none"):
        super().__init__(f"CLIP-{model_name}", preprocessing)
        if not HAS_OPEN_CLIP:
            raise ImportError("open_clip not available. Install with: pip install open_clip_torch")
        
        self.model, _, self.preprocess = open_clip.create_model_and_transforms(
            model_name, pretrained=pretrained
        )
        self.model.to(self.device)
        self.model.eval()
        print(f"✓ Loaded {self.name} (preprocessing: {preprocessing})")
    
    def embed_image(self, image_path: str) -> Optional[np.ndarray]:
        try:
            # Apply our preprocessing first
            image = self.preprocessor.preprocess_image_file(image_path)
            
            # Then apply CLIP's preprocessing
            image_tensor = self.preprocess(image).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                embedding = self.model.encode_image(image_tensor)
                embedding = embedding.cpu().numpy()[0]
            
            # Normalize
            embedding = embedding / (np.linalg.norm(embedding) + 1e-8)
            return embedding
        except Exception as e:
            print(f"Error embedding {image_path}: {e}")
            return None
    
    def get_dimension(self) -> int:
        return 512  # Most CLIP models use 512


class DINOModelWrapper(EmbeddingModelWrapper):
    """Wrapper for Facebook DINO models (self-supervised, good for fine-grained similarity)"""
    
    def __init__(self, model_name: str = "facebook/dinov2-base", preprocessing: str = "none"):
        super().__init__(f"DINOv2-{model_name.split('/')[-1]}", preprocessing)
        if not HAS_TRANSFORMERS:
            raise ImportError("transformers not available. Install with: pip install transformers")
        
        self.processor = AutoImageProcessor.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.model.to(self.device)
        self.model.eval()
        print(f"✓ Loaded {self.name} (preprocessing: {preprocessing})")
    
    def embed_image(self, image_path: str) -> Optional[np.ndarray]:
        try:
            # Apply our preprocessing first
            image = self.preprocessor.preprocess_image_file(image_path)
            
            # Then apply DINO's preprocessing
            inputs = self.processor(images=image, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                # Use CLS token embedding
                embedding = outputs.last_hidden_state[:, 0].cpu().numpy()[0]
            
            # Normalize
            embedding = embedding / (np.linalg.norm(embedding) + 1e-8)
            return embedding
        except Exception as e:
            print(f"Error embedding {image_path}: {e}")
            return None
    
    def get_dimension(self) -> int:
        return 768  # DINOv2-base


class ResNetModelWrapper(EmbeddingModelWrapper):
    """Wrapper for ResNet models with custom embedding layer"""
    
    def __init__(self, model_name: str = "resnet50", preprocessing: str = "none"):
        super().__init__(f"ResNet-{model_name}", preprocessing)
        if not HAS_TORCHVISION:
            raise ImportError("torchvision not available. Install with: pip install torchvision")
        
        # Load pretrained model and remove classification head
        if model_name == "resnet50":
            base_model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V2)
            embed_dim = 2048
        elif model_name == "resnet18":
            base_model = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
            embed_dim = 512
        else:
            raise ValueError(f"Unknown model: {model_name}")
        
        # Remove final FC layer
        self.model = nn.Sequential(*list(base_model.children())[:-1])
        self.model.to(self.device)
        self.model.eval()
        self.embed_dim = embed_dim
        
        # Standard ImageNet transforms
        self.transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        print(f"✓ Loaded {self.name} (preprocessing: {preprocessing})")
    
    def embed_image(self, image_path: str) -> Optional[np.ndarray]:
        try:
            # Apply our preprocessing first
            image = self.preprocessor.preprocess_image_file(image_path)
            
            # Then apply ResNet's preprocessing
            image_tensor = self.transform(image).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                embedding = self.model(image_tensor)
                embedding = embedding.squeeze().cpu().numpy()
            
            # Normalize
            embedding = embedding / (np.linalg.norm(embedding) + 1e-8)
            return embedding
        except Exception as e:
            print(f"Error embedding {image_path}: {e}")
            return None
    
    def get_dimension(self) -> int:
        return self.embed_dim


class EfficientNetModelWrapper(EmbeddingModelWrapper):
    """Wrapper for EfficientNet models"""
    
    def __init__(self, model_name: str = "efficientnet_b0", preprocessing: str = "none"):
        super().__init__(f"EfficientNet-{model_name}", preprocessing)
        if not HAS_TORCHVISION:
            raise ImportError("torchvision not available. Install with: pip install torchvision")
        
        if model_name == "efficientnet_b0":
            base_model = models.efficientnet_b0(weights=models.EfficientNet_B0_Weights.IMAGENET1K_V1)
            embed_dim = 1280
        elif model_name == "efficientnet_b3":
            base_model = models.efficientnet_b3(weights=models.EfficientNet_B3_Weights.IMAGENET1K_V1)
            embed_dim = 1536
        else:
            raise ValueError(f"Unknown model: {model_name}")
        
        # Remove classifier
        self.model = nn.Sequential(
            base_model.features,
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten()
        )
        self.model.to(self.device)
        self.model.eval()
        self.embed_dim = embed_dim
        
        self.transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        print(f"✓ Loaded {self.name} (preprocessing: {preprocessing})")
    
    def embed_image(self, image_path: str) -> Optional[np.ndarray]:
        try:
            # Apply our preprocessing first
            image = self.preprocessor.preprocess_image_file(image_path)
            
            # Then apply EfficientNet's preprocessing
            image_tensor = self.transform(image).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                embedding = self.model(image_tensor)
                embedding = embedding.cpu().numpy()[0]
            
            # Normalize
            embedding = embedding / (np.linalg.norm(embedding) + 1e-8)
            return embedding
        except Exception as e:
            print(f"Error embedding {image_path}: {e}")
            return None
    
    def get_dimension(self) -> int:
        return self.embed_dim
