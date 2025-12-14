"""
Minimal configuration for standalone/local testing

This module provides the minimal configuration needed to run
backend services outside of the full application context.
"""

import os
from typing import Optional


class StandaloneSettings:
    """Minimal settings for standalone execution"""
    
    # CLIP Model
    CLIP_MODEL_NAME: str = "ViT-B-32"
    CLIP_PRETRAINED: str = "openai"
    
    # Similarity threshold
    MATCH_THRESHOLD: float = 0.85
    
    # Environment
    ENVIRONMENT: str = "local"
    
    # Upload directory (for local testing)
    UPLOAD_DIR: str = "test_output"


# Create singleton instance
settings = StandaloneSettings()


# Minimal logger for standalone use
class StandaloneLogger:
    """Minimal logger that prints to console"""
    
    def debug(self, msg):
        pass  # Skip debug in standalone
    
    def info(self, msg):
        print(f"ℹ️  {msg}")
    
    def warning(self, msg):
        print(f"⚠️  {msg}")
    
    def error(self, msg):
        print(f"❌ {msg}")


def get_logger():
    return StandaloneLogger()
