"""
Compare module for evaluating different embedding models on sock matching task.

This module provides tools to:
- Load and evaluate various embedding models (CLIP, DINOv2, ResNet, EfficientNet)
- Preprocess images for optimal matching
- Evaluate model performance on sock pair datasets
- Generate comparison reports

Usage:
    from compare import ModelEvaluator, SockPairDataset
    from compare.model_wrappers import CLIPModelWrapper, DINOModelWrapper
    
    dataset = SockPairDataset("path/to/images")
    evaluator = ModelEvaluator(dataset)
    
    model = CLIPModelWrapper("ViT-B-32", preprocessing="full")
    result = evaluator.evaluate_model(model)
"""

from .dataset import SockPairDataset
from .evaluator import ModelEvaluator
from .results import ModelResult, create_comparison_table
from .model_wrappers import (
    EmbeddingModelWrapper,
    CLIPModelWrapper,
    DINOModelWrapper,
    ResNetModelWrapper,
    EfficientNetModelWrapper,
)
from .preprocessing import ImagePreprocessor

__all__ = [
    "SockPairDataset",
    "ModelEvaluator",
    "ModelResult",
    "create_comparison_table",
    "EmbeddingModelWrapper",
    "CLIPModelWrapper",
    "DINOModelWrapper",
    "ResNetModelWrapper",
    "EfficientNetModelWrapper",
    "ImagePreprocessor",
]
