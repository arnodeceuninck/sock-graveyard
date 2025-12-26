"""
Compare different embedding models for sock matching task.

This script evaluates various embedding models on their ability to match pairs of socks.
The task is similar to face recognition - distinguishing between similar items of the same
category rather than distinguishing between different categories.

Models tested:
- OpenAI CLIP variants
- DINOv2 (self-supervised fine-grained similarity)
- ResNet/EfficientNet (CNN baselines with cosine similarity)

Metrics:
- Same-pair accuracy: How often pairs are correctly identified as matches
- Different-pair accuracy: How often non-pairs are correctly identified as non-matches
- Average Precision (AP): Overall ranking quality
- Top-1 Accuracy: Given a sock, is its pair ranked first?
- ROC-AUC: Area under receiver operating characteristic curve

Usage:
    python examples/compare_embedding_models.py

Note: This script now uses the compare module for better organization.
      See model/compare/ for the modular implementation.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import from the compare module
from compare.run_comparison import main


if __name__ == "__main__":
    asyncio.run(main())

