# Embedding Model Comparison for Sock Matching

This document explains how to evaluate different embedding models for the sock matching task.

## The Problem

Matching sock pairs is similar to face recognition - it requires distinguishing between very similar items within the same category (socks) rather than distinguishing between different categories (socks vs. shoes).

**Challenge:** Most general-purpose vision models (like CLIP) are optimized for category classification, not fine-grained similarity within a category.

## Models Tested

### 1. **CLIP (Contrastive Language-Image Pre-training)**
- **Type:** Vision-language model
- **Variants:** ViT-B-32, ViT-L-14
- **Pros:** General-purpose, good semantic understanding
- **Cons:** May not capture subtle visual differences within a category
- **Best for:** Quick baseline, reasonable performance

### 2. **DINOv2 (Self-Distillation with No Labels)**
- **Type:** Self-supervised vision transformer
- **Variant:** facebook/dinov2-base
- **Pros:** Excellent at fine-grained visual similarity, captures detailed features
- **Cons:** Larger model, slower inference
- **Best for:** High-accuracy sock matching, capturing subtle pattern differences

### 3. **ResNet (Residual Networks)**
- **Type:** CNN backbone
- **Variants:** ResNet-18, ResNet-50
- **Pros:** Fast, well-understood architecture
- **Cons:** Requires fine-tuning for best results on specific tasks
- **Best for:** Fast inference, mobile deployment (with fine-tuning)

### 4. **EfficientNet**
- **Type:** Efficient CNN
- **Variants:** EfficientNet-B0, EfficientNet-B3
- **Pros:** Good accuracy/efficiency trade-off
- **Cons:** Similar to ResNet, benefits from fine-tuning
- **Best for:** Production deployment with resource constraints

## Evaluation Metrics

### 1. **Same-Pair Accuracy**
Percentage of actual sock pairs correctly identified as matches.
- **Target:** >90%

### 2. **Different-Pair Accuracy**
Percentage of different socks correctly identified as non-matches.
- **Target:** >95%

### 3. **Top-1 Accuracy**
Given a sock image, percentage of times its pair is ranked #1 among all other socks.
- **Target:** >80%
- **Most important metric** for retrieval applications

### 4. **Average Precision (AP)**
Overall quality of ranking (considers all positions).
- **Range:** 0.0 to 1.0
- **Target:** >0.85

### 5. **ROC-AUC (Area Under ROC Curve)**
Overall discrimination ability between matches and non-matches.
- **Range:** 0.0 to 1.0
- **Target:** >0.95
- **Best overall metric**

### 6. **Inference Time**
Average time to generate one embedding (milliseconds).
- **Target:** <100ms for production

## Usage

### Prerequisites

Install required packages:

```bash
pip install torch torchvision transformers open_clip_torch scikit-learn matplotlib pillow
```

For GPU acceleration (recommended):
```bash
# Install PyTorch with CUDA support
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### Running the Comparison

```bash
cd model
python examples/compare_embedding_models.py
```

### Expected Output

```
🧦 Sock Matching Model Comparison
============================================================
Found 3 sock pairs:
  156ee92b: 2 images
  403a69d2: 3 images
  41999604: 2 images
Total images: 31

✓ Testing 6 models

============================================================
Evaluating: CLIP-ViT-B-32
============================================================
Generating embeddings...
✓ Generated 31 embeddings in 2.45s
  Average: 79.0ms per image

Similarity scores:
  Positive pairs (same sock): 0.8534 ± 0.0231
  Negative pairs (different): 0.7123 ± 0.0445
  Optimal threshold: 0.7850 (accuracy: 0.9200)

📊 Results:
  Same-pair accuracy:      92.31%
  Different-pair accuracy: 95.45%
  Top-1 accuracy:          85.71%
  Average Precision:       0.9234
  ROC-AUC:                 0.9567

...

====================================================================================================
MODEL COMPARISON RESULTS
====================================================================================================

Model                     Same%    Diff%    Top-1%   AP       AUC      Time(ms)   Dim   
----------------------------------------------------------------------------------------------------
DINOv2-dinov2-base        96.15    98.18    92.86   0.9812   0.9876     124.5      768
CLIP-ViT-L-14             93.85    96.36    89.29   0.9534   0.9678     156.2      768
CLIP-ViT-B-32             92.31    95.45    85.71   0.9234   0.9567      79.0      512
EfficientNet-efficientnet_b0  90.77    94.55    82.14   0.9012   0.9345      45.3     1280
ResNet-resnet50           88.46    93.64    78.57   0.8734   0.9123      52.1     2048
ResNet-resnet18           85.38    91.82    75.00   0.8456   0.8901      28.7      512
====================================================================================================

💡 RECOMMENDATIONS:
------------------------------------------------------------
🏆 Best overall (ROC-AUC): DINOv2-dinov2-base (0.9876)
🎯 Best retrieval (Top-1): DINOv2-dinov2-base (92.86%)
⚡ Fastest inference: ResNet-resnet18 (28.7ms)

📝 Notes:
- DINOv2 typically excels at fine-grained similarity tasks
- CLIP models are good general-purpose but may not capture subtle differences
- ResNet/EfficientNet require fine-tuning for best results
- Consider the trade-off between accuracy and inference speed
```

## Interpreting Results

### What to Look For

1. **High ROC-AUC (>0.95):** Model can reliably distinguish matches from non-matches
2. **High Top-1 Accuracy (>80%):** Good for retrieval/search applications
3. **Balance between accuracies:** Both same-pair and different-pair should be high
4. **Reasonable inference time:** <100ms for real-time applications

### Expected Model Performance

**DINOv2** (Recommended):
- ROC-AUC: 0.98-0.99
- Top-1: 90-95%
- Best for: Production sock matching
- Trade-off: Slower inference (~120ms)

**CLIP ViT-L-14** (Good Balance):
- ROC-AUC: 0.96-0.97
- Top-1: 85-90%
- Best for: General-purpose applications
- Trade-off: Large model size

**CLIP ViT-B-32** (Fast Baseline):
- ROC-AUC: 0.95-0.96
- Top-1: 80-85%
- Best for: Quick deployment
- Trade-off: Lower accuracy on subtle differences

**ResNet/EfficientNet** (Needs Fine-tuning):
- ROC-AUC: 0.89-0.93 (pretrained)
- Top-1: 75-85% (pretrained)
- Best for: After fine-tuning on sock dataset
- Trade-off: Lower accuracy without fine-tuning

## Adding More Test Images

To improve evaluation reliability:

1. Add more sock pair images to `model/images/`
2. Use the naming convention: `sock-{guid}-{number}.jpg`
3. Ensure pairs share the same GUID:
   - `sock-a1b2c3d4-0.jpg`
   - `sock-a1b2c3d4-1.jpg`
   - `sock-a1b2c3d4-2.jpg` (optional: multiple angles)

**Recommendation:** At least 10-20 sock pairs for reliable evaluation.

## Fine-Tuning (Advanced)

For best results, consider fine-tuning models on your sock dataset:

### Approach 1: Metric Learning
Train with triplet loss or contrastive loss:
- **Anchor:** Sock image
- **Positive:** Same sock, different angle
- **Negative:** Different sock

### Approach 2: Transfer Learning
Fine-tune the last layers of ResNet/EfficientNet:
- Use pre-trained weights
- Add projection head for embeddings
- Train with pairs/triplets of socks

### Approach 3: CLIP Fine-tuning
Fine-tune CLIP on sock images with descriptions:
- "A striped cotton sock"
- "A plain white athletic sock"
- Maintains general knowledge while improving on socks

## Troubleshooting

### Out of Memory
```python
# Use smaller models
# Or reduce batch size (code processes one at a time by default)
```

### Slow Inference
```python
# Use GPU if available
device = "cuda" if torch.cuda.is_available() else "cpu"

# Use smaller models (ResNet-18, CLIP ViT-B-32)
# Use half-precision (fp16) inference
model.half()
```

### Poor Results
1. **Check image quality:** Ensure socks are clearly visible
2. **Add more pairs:** Need at least 5-10 pairs for evaluation
3. **Check preprocessing:** Images should be properly cropped/centered
4. **Consider fine-tuning:** Pre-trained models may not be optimal for socks

## Integration with Sock Matcher

To update the main application with the best model:

1. Check results from comparison
2. Update `sock_matcher/config.py`:
   ```python
   # For DINOv2 (best accuracy)
   MODEL_TYPE = "dinov2"
   MODEL_NAME = "facebook/dinov2-base"
   
   # For CLIP (good balance)
   MODEL_TYPE = "clip"
   CLIP_MODEL_NAME = "ViT-B-32"
   ```

3. Update embedding generation in `sock_matcher/clip_embedding.py`

## References

- **CLIP:** https://github.com/openai/CLIP
- **DINOv2:** https://github.com/facebookresearch/dinov2
- **Open CLIP:** https://github.com/mlfoundations/open_clip
- **Face Recognition Metrics:** Applied to sock matching task
