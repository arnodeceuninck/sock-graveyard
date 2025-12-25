# Sock Matcher ML Models

Machine learning models and image processing utilities for the Sock Graveyard application.

## Overview

This package contains:
- **CLIP Embedding Service**: Generate embeddings for sock images using OpenAI's CLIP model
- **Image Preprocessing**: Remove backgrounds, crop, resize, and enhance sock images
- **Feature Extraction**: Extract visual features like dominant color, patterns, and textures

## Installation

### As a library (for backend integration)

```bash
cd model
pip install -e .
```

### For development

```bash
cd model
pip install -r requirements.txt
```

## Usage

### Basic Usage

```python
from sock_matcher import CLIPEmbeddingService, ImagePreprocessor

# Initialize services
preprocessor = ImagePreprocessor()
clip_service = CLIPEmbeddingService()

# Preprocess an image
with open("sock.jpg", "rb") as f:
    image_bytes = f.read()

processed_path, error = await preprocessor.preprocess_image(
    image_bytes, 
    "processed_sock.jpg"
)

# Generate embedding
embedding = await clip_service.generate_embedding(processed_path)

# Extract features
features = await clip_service.extract_features(processed_path)
print(f"Dominant color: {features['dominant_color']}")
print(f"Pattern: {features['pattern_type']}")
```

### With Custom Configuration

```python
from sock_matcher import CLIPEmbeddingService, ImagePreprocessor
from sock_matcher.config import ModelConfig

# Create custom config
config = ModelConfig(
    clip_model_name="ViT-B-32",
    clip_pretrained="openai"
)

# Initialize services with config
clip_service = CLIPEmbeddingService(config=config)
preprocessor = ImagePreprocessor(config=config)
```

### Integration with Backend

```python
# In your backend code
from sock_matcher import CLIPEmbeddingService, ImagePreprocessor
from sock_matcher.config import ModelConfig
from app.config import settings  # Your backend settings

# Create config from backend settings
model_config = ModelConfig.from_backend_settings(settings)

# Initialize services
clip_service = CLIPEmbeddingService(config=model_config)
preprocessor = ImagePreprocessor(config=model_config)
```

## Features

### Image Preprocessing
- Background removal using rembg
- Auto-cropping to sock boundaries
- Resize to standard size (512x512) with padding
- Contrast enhancement

### CLIP Embeddings
- Generate 512-dimensional embeddings
- Calculate similarity between embeddings
- GPU acceleration when available

### Feature Extraction
- **Dominant Color**: Extract primary color using K-means clustering
- **Pattern Detection**: Detect solid, striped, textured, or complex patterns
- **Texture Features**: Extract statistical texture features (LBP, gradients, etc.)
- **Color Similarity**: Calculate perceptual color distance

## Model Architecture

The package uses:
- **CLIP Model**: ViT-B-32 from OpenAI (default)
- **Background Removal**: U²-Net model via rembg
- **Feature Extraction**: Computer vision algorithms (K-means, edge detection, LBP)

## GPU Support

The package automatically detects and uses GPU when available:
```python
clip_service = CLIPEmbeddingService()
print(f"Using device: {clip_service.device}")  # cuda or cpu
```

## Configuration Options

| Parameter | Default | Description |
|-----------|---------|-------------|
| `CLIP_MODEL_NAME` | `ViT-B-32` | CLIP model architecture |
| `CLIP_PRETRAINED` | `openai` | Pretrained weights dataset |

## Development

### Running Tests

```bash
cd model
pytest tests/
```

### Code Structure

```
model/
├── sock_matcher/
│   ├── __init__.py           # Package exports
│   ├── clip_embedding.py     # CLIP model and feature extraction
│   ├── image_preprocessing.py # Image preprocessing pipeline
│   ├── config.py             # Configuration management
│   └── logging_config.py     # Logging utilities
├── setup.py                  # Package setup
├── requirements.txt          # Dependencies
└── README.md                 # This file
```

## License

See LICENSE file in the root directory.
