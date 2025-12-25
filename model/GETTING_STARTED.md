# Getting Started with Sock Matcher ML Models

This guide helps you get started with developing and using the Sock Matcher ML models.

## Installation

### Option 1: Install as Editable Package (Recommended for Development)

From the project root:

```bash
cd model
pip install -e .
```

This installs the package in editable mode, so changes to the code are immediately available.

### Option 2: Install from Requirements

```bash
cd model
pip install -r requirements.txt
```

## Quick Start

### Standalone Usage

```python
import asyncio
from sock_matcher import CLIPEmbeddingService, ImagePreprocessor

async def main():
    # Initialize services
    preprocessor = ImagePreprocessor()
    clip_service = CLIPEmbeddingService()
    
    # Load and preprocess image
    with open("my_sock.jpg", "rb") as f:
        image_bytes = f.read()
    
    processed_path, error = await preprocessor.preprocess_image(
        image_bytes,
        "processed_sock.jpg"
    )
    
    if error:
        print(f"Error: {error}")
        return
    
    # Generate embedding
    embedding = await clip_service.generate_embedding(processed_path)
    print(f"Embedding shape: {embedding.shape}")
    
    # Extract features
    features = await clip_service.extract_features(processed_path)
    print(f"Dominant color: {features['dominant_color']}")
    print(f"Pattern: {features['pattern_type']}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Backend Integration

The backend already integrates the model package through wrapper services in `backend/app/services/`.

## Development

### Running Tests

```bash
cd model
pytest tests/
```

### Code Structure

```
model/
├── sock_matcher/           # Main package
│   ├── __init__.py        # Package exports
│   ├── clip_embedding.py   # CLIP model service
│   ├── image_preprocessing.py  # Image preprocessing
│   ├── config.py          # Configuration
│   └── logging_config.py   # Logging setup
├── tests/                 # Test directory (to be added)
├── setup.py               # Package setup
├── requirements.txt       # Dependencies
├── README.md             # Full documentation
└── GETTING_STARTED.md    # This file
```

### Adding New Features

1. **Add ML models**: Create new modules in `sock_matcher/`
2. **Export in `__init__.py`**: Add to `__all__` list
3. **Update setup.py**: Increment version if needed
4. **Document**: Update README.md

### GPU Support

The CLIP service automatically uses GPU if available:

```python
from sock_matcher import CLIPEmbeddingService

service = CLIPEmbeddingService()
print(f"Using device: {service.device}")  # 'cuda' or 'cpu'
```

To force CPU:
```python
import os
os.environ['CUDA_VISIBLE_DEVICES'] = ''
```

## Configuration

### Environment Variables

```bash
# CLIP model configuration
export CLIP_MODEL_NAME="ViT-B-32"
export CLIP_PRETRAINED="openai"
```

### Programmatic Configuration

```python
from sock_matcher import CLIPEmbeddingService
from sock_matcher.config import ModelConfig

config = ModelConfig(
    clip_model_name="ViT-L-14",
    clip_pretrained="openai"
)

service = CLIPEmbeddingService(config=config)
```

## Common Tasks

### Extract Color from Sock

```python
features = await clip_service.extract_features("sock.jpg")
color = features['dominant_color']  # Hex color like "#FF5733"
```

### Calculate Similarity

```python
embedding1 = await clip_service.generate_embedding("sock1.jpg")
embedding2 = await clip_service.generate_embedding("sock2.jpg")

similarity = clip_service.calculate_similarity(embedding1, embedding2)
print(f"Similarity: {similarity:.2%}")
```

### Batch Processing

```python
import asyncio
from pathlib import Path

async def process_batch(image_paths):
    clip_service = CLIPEmbeddingService()
    
    tasks = [clip_service.generate_embedding(p) for p in image_paths]
    embeddings = await asyncio.gather(*tasks)
    
    return embeddings

# Usage
paths = list(Path("sock_images").glob("*.jpg"))
embeddings = asyncio.run(process_batch(paths))
```

## Troubleshooting

### Out of Memory (GPU)

Reduce batch size or process images sequentially:

```python
for image_path in image_paths:
    embedding = await clip_service.generate_embedding(image_path)
    # Process one at a time
```

### Slow Performance

1. Ensure GPU is being used: `print(clip_service.device)`
2. Check CUDA installation: `torch.cuda.is_available()`
3. Reduce image resolution (handled automatically)

### Import Errors

Make sure the package is installed:
```bash
pip list | grep sock-matcher
```

If not found:
```bash
cd model
pip install -e .
```

## Next Steps

- Read the full [README.md](README.md) for detailed API documentation
- See [../backend/app/services/](../backend/app/services/) for backend integration examples
- Check [../backend/test_matching.py](../backend/test_matching.py) for usage examples
