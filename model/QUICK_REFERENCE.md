# Model Package - Quick Reference

## Installation
```bash
cd model
pip install -e .
```

## Basic Usage

### Import
```python
from sock_matcher import CLIPEmbeddingService, ImagePreprocessor
```

### Initialize
```python
preprocessor = ImagePreprocessor()
clip_service = CLIPEmbeddingService()
```

### Preprocess Image
```python
with open("sock.jpg", "rb") as f:
    image_bytes = f.read()

processed_path, error = await preprocessor.preprocess_image(
    image_bytes, 
    "processed.jpg"
)
```

### Generate Embedding
```python
embedding = await clip_service.generate_embedding("processed.jpg")
# Returns numpy array of shape (512,)
```

### Extract Features
```python
features = await clip_service.extract_features("processed.jpg")
# Returns: {
#   'dominant_color': '#FF5733',
#   'pattern_type': 'striped',
#   'texture_features': {...}
# }
```

### Compare Similarity
```python
similarity = clip_service.calculate_similarity(embedding1, embedding2)
# Returns float between 0 and 1
```

### Color Similarity
```python
similarity = clip_service.calculate_color_similarity('#FF5733', '#FE5832')
# Returns float between 0 and 1
```

## Example Scripts

### Compare Socks
```bash
python examples/compare_socks.py sock1.jpg sock2.jpg
```

### Test Models
```bash
python examples/test_models.py sock1.jpg sock2.jpg
```

### Extract Features
```bash
python examples/feature_demo.py sock.jpg
```

### Batch Process
```bash
python examples/batch_process.py ./sock_images
```

## Configuration

### Environment Variables
```bash
export CLIP_MODEL_NAME="ViT-B-32"
export CLIP_PRETRAINED="openai"
```

### Programmatic
```python
from sock_matcher.config import ModelConfig

config = ModelConfig(
    clip_model_name="ViT-B-16",
    clip_pretrained="openai"
)

clip_service = CLIPEmbeddingService(config=config)
```

## Available Models

| Model | Speed | Accuracy | Best For |
|-------|-------|----------|----------|
| **ViT-B-32** | ⚡⚡⚡ | ★★★ | Default, balanced |
| **ViT-B-16** | ⚡⚡ | ★★★★ | Better accuracy |
| **ViT-L-14** | ⚡ | ★★★★★ | Best accuracy |
| **RN50** | ⚡⚡⚡⚡ | ★★ | Speed critical |

## Pattern Types

- `solid` - Uniform color
- `striped` - Regular stripes
- `textured` - Irregular texture
- `complex` - Multiple patterns
- `unknown` - Could not determine

## Similarity Scores

- **> 0.9** - Very likely match 🎯
- **0.8 - 0.9** - Probably match 👍
- **0.7 - 0.8** - Possibly similar 🤔
- **< 0.7** - Likely different ❌

## Common Issues

### Import Error
```bash
cd model && pip install -e .
```

### GPU Not Detected
```python
import torch
print(torch.cuda.is_available())  # Should be True
```

### Out of Memory
- Process images sequentially
- Use smaller model (RN50)
- Force CPU: `export CUDA_VISIBLE_DEVICES=""`

## More Info

- 📖 Full docs: [README.md](README.md)
- 🚀 Getting started: [GETTING_STARTED.md](GETTING_STARTED.md)
- 🧪 Examples: [examples/README.md](examples/README.md)
