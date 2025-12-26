# Compare Module

This module provides tools for comparing different embedding models on the sock matching task.

## Structure

```
compare/
├── __init__.py              # Module exports
├── preprocessing.py         # Image preprocessing utilities
├── model_wrappers.py        # Wrapper classes for different models
├── dataset.py               # Dataset handling for sock pairs
├── evaluator.py             # Model evaluation logic
├── results.py               # Results formatting and comparison
└── run_comparison.py        # Main comparison script
```

## Usage

### Running the comparison script

From the `model` directory:

```bash
python -m compare.run_comparison
```

Or directly:

```bash
python compare/run_comparison.py
```

**With tqdm installed, you'll see progress bars:**
```
Evaluating models: 100%|██████████| 5/5 [05:23<00:00, 64.7s/model]
Embedding images: 100%|██████████| 24/24 [00:12<00:00, 1.92img/s]
```

### Using as a library

```python
from compare import (
    SockPairDataset,
    ModelEvaluator,
    CLIPModelWrapper,
    DINOModelWrapper,
    create_comparison_table
)

# Load dataset
dataset = SockPairDataset("path/to/images")

# Create evaluator
evaluator = ModelEvaluator(dataset)

# Test a model
model = CLIPModelWrapper("ViT-B-32", preprocessing="full")
result = evaluator.evaluate_model(model)

print(f"ROC-AUC: {result.roc_auc:.4f}")
print(f"Top-1 Accuracy: {result.top1_accuracy:.2%}")
```

## Modules

### `preprocessing.py`

Handles image preprocessing with three modes:
- **none**: No preprocessing
- **basic**: Basic resize and normalization
- **full**: Background removal and auto-cropping (requires `rembg` and `opencv-python`)

### `model_wrappers.py`

Provides wrapper classes for different embedding models:
- `CLIPModelWrapper`: OpenAI CLIP models (ViT-B-32, ViT-L-14, etc.)
- `DINOModelWrapper`: Facebook DINOv2 models (excellent for fine-grained similarity)
- `ResNetModelWrapper`: ResNet models (CNN baseline)
- `EfficientNetModelWrapper`: EfficientNet models (efficient CNN)

Each wrapper:
- Loads the pre-trained model
- Applies preprocessing
- Generates normalized embeddings
- Provides embedding dimensions

### `dataset.py`

`SockPairDataset` class for loading and managing sock image pairs:
- Automatically groups images by GUID (from `sock-{guid}-{index}.jpg` format)
- Generates positive pairs (same sock) and negative pairs (different socks)
- Provides retrieval queries for Top-1 accuracy evaluation

### `evaluator.py`

`ModelEvaluator` class for comprehensive model evaluation:

**Metrics computed:**
- Same-pair accuracy: Correct identification of matching socks
- Different-pair accuracy: Correct identification of non-matching socks
- Top-1 accuracy: Given a query sock, is its pair ranked first?
- Average Precision (AP): Overall ranking quality
- ROC-AUC: Area under receiver operating characteristic curve
- Inference time: Average time per image

### `results.py`

Result formatting utilities:
- `ModelResult` dataclass: Stores all metrics for a model
- `create_comparison_table()`: Generates formatted comparison table
- `print_recommendations()`: Suggests best models for different use cases

### `run_comparison.py`

Main script that:
1. Loads the sock pair dataset
2. Tests multiple models with/without preprocessing
3. Evaluates each model on all metrics
4. Generates comparison table
5. Saves results to JSON
6. Provides recommendations

## Dependencies

**Required:**
- `torch`, `torchvision`: For all models
- `numpy`: For embedding operations
- `Pillow`: For image loading
- `sklearn`: For evaluation metrics

**Optional (for specific models):**
- `open_clip_torch`: For CLIP models
- `transformers`: For DINOv2 models
- `rembg`, `opencv-python`: For full preprocessing
- `tqdm`: For progress bars during evaluation

## Adding New Models

To add a new model:

1. Create a wrapper class in `model_wrappers.py`:

```python
class MyModelWrapper(EmbeddingModelWrapper):
    def __init__(self, model_name: str = "my-model", preprocessing: str = "none"):
        super().__init__(f"MyModel-{model_name}", preprocessing)
        # Load model here
        
    def embed_image(self, image_path: str) -> Optional[np.ndarray]:
        # Generate embedding
        # Apply preprocessing with self.preprocessor
        # Return normalized embedding
        
    def get_dimension(self) -> int:
        return 512  # Your embedding dimension
```

2. Add to `__init__.py` exports

3. Add to `run_comparison.py` test list

## Performance Tips

- **DINOv2** typically gives the best results for fine-grained matching tasks
- **CLIP** is faster and good for general-purpose matching
- **Full preprocessing** improves accuracy but adds ~100-200ms per image
- Batch processing can significantly speed up evaluation (not yet implemented)

## Future Improvements

- [ ] Batch embedding generation for faster evaluation
- [ ] Support for custom distance metrics beyond cosine similarity
- [ ] Cross-validation and confidence intervals
- [ ] Model fine-tuning utilities
- [ ] GPU memory optimization for large datasets
