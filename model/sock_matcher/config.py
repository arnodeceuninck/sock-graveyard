"""
Configuration for Sock Matcher ML Models

This module provides configuration settings for the ML models.
It can work standalone or integrate with existing backend configurations.
"""

import os
from typing import Optional


class ModelConfig:
    """Configuration for ML models"""
    
    def __init__(
        self,
        clip_model_name: Optional[str] = None,
        clip_pretrained: Optional[str] = None
    ):
        """
        Initialize model configuration
        
        Args:
            clip_model_name: CLIP model name (default: ViT-B-32)
            clip_pretrained: CLIP pretrained dataset (default: openai)
        """
        # CLIP Model Configuration
        self.CLIP_MODEL_NAME = clip_model_name or os.getenv("CLIP_MODEL_NAME", "ViT-B-32")
        self.CLIP_PRETRAINED = clip_pretrained or os.getenv("CLIP_PRETRAINED", "openai")
    
    @classmethod
    def from_env(cls) -> "ModelConfig":
        """Create configuration from environment variables"""
        return cls()
    
    @classmethod
    def from_backend_settings(cls, settings) -> "ModelConfig":
        """
        Create configuration from backend settings object
        
        Args:
            settings: Backend settings object with CLIP_MODEL_NAME and CLIP_PRETRAINED
            
        Returns:
            ModelConfig instance
        """
        return cls(
            clip_model_name=getattr(settings, "CLIP_MODEL_NAME", None),
            clip_pretrained=getattr(settings, "CLIP_PRETRAINED", None)
        )
