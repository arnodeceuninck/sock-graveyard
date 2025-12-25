# Example Scripts

This directory contains example scripts demonstrating how to use the `sock_matcher` package.

## Scripts

### 1. `compare_socks.py` - Compare Multiple Socks

Compare two or more sock images to find matching pairs.

```bash
python examples/compare_socks.py sock1.jpg sock2.jpg sock3.jpg
```

**Features:**
- Preprocesses all images
- Generates embeddings
- Extracts visual features (color, pattern)
- Compares all pairs
- Shows best and worst matches

**Output:**
- Processed images in `output/` directory
- Similarity scores for all pairs
- Match recommendations

---

### 2. `test_models.py` - Model Performance Comparison

Test different CLIP model configurations to find the best one for your use case.

```bash
python examples/test_models.py sock1.jpg sock2.jpg
```

**Features:**
- Tests multiple CLIP models (ViT-B-32, ViT-B-16, ViT-L-14, RN50)
- Benchmarks initialization and inference time
- Compares similarity scores across models
- Provides recommendations

**Models Tested:**
- `ViT-B-32`: Default, good balance
- `ViT-B-16`: Better accuracy, slower
- `ViT-L-14`: Best accuracy, slowest
- `RN50`: Fastest, lower accuracy

---

### 3. `feature_demo.py` - Feature Extraction Demo

Extract and display all visual features from a sock image.

```bash
python examples/feature_demo.py my_sock.jpg
```

**Features:**
- Shows preprocessing steps
- Displays CLIP embedding info
- Extracts color features (dominant color with RGB)
- Identifies pattern type (solid, striped, textured, complex)
- Shows texture statistics
- Saves features to JSON

**Output:**
- Processed image: `output/demo_processed.jpg`
- Features JSON: `output/demo_features.json`

---

## Setup

Before running the examples, make sure the package is installed:

```bash
cd model
pip install -e .
```

## Tips

### Using Custom Model Configuration

All scripts support custom configuration:

```python
from sock_matcher.config import ModelConfig

config = ModelConfig(
    clip_model_name="ViT-B-16",
    clip_pretrained="openai"
)

# Pass to services
clip_service = CLIPEmbeddingService(config=config)
```

### GPU Acceleration

The scripts automatically use GPU if available. To check:

```python
clip_service = CLIPEmbeddingService()
print(f"Device: {clip_service.device}")  # 'cuda' or 'cpu'
```

### Batch Processing

For processing many images, modify `compare_socks.py` to process in batches:

```python
# Process images in parallel
tasks = [comparison.process_image(path) for path in image_paths]
results = await asyncio.gather(*tasks)
```

## Example Workflow

1. **Start with feature demo** to understand what the model extracts:
   ```bash
   python examples/feature_demo.py test_sock.jpg
   ```

2. **Compare some socks** to see matching in action:
   ```bash
   python examples/compare_socks.py sock*.jpg
   ```

3. **Optimize performance** by testing different models:
   ```bash
   python examples/test_models.py sock1.jpg sock2.jpg
   ```

## Troubleshooting

### Import Errors

If you get import errors, ensure the package is installed:
```bash
cd model
pip install -e .
```

### Out of Memory (GPU)

If you run out of GPU memory:
- Process images one at a time
- Use a smaller model (RN50 or ViT-B-32)
- Force CPU: `export CUDA_VISIBLE_DEVICES=""`

### Slow Performance

- GPU not detected: Check `torch.cuda.is_available()`
- Use faster model: Try RN50
- Reduce image resolution (automatically handled)

## Next Steps

- Modify scripts for your specific use case
- Integrate with your own pipeline
- See `../GETTING_STARTED.md` for library usage
- Check `../README.md` for full API documentation
