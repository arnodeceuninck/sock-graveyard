# Preprocessing Impact on Sock Matching Models

This document explains the preprocessing comparison feature added to the model evaluation script.

## What is Preprocessing?

Preprocessing includes two stages:
1. **Basic preprocessing**: Standard image transformations (resize, normalize) - built into each model
2. **Full preprocessing**: Advanced sock-specific processing:
   - **Background removal** using rembg (removes distracting backgrounds)
   - **Auto-cropping** to sock boundaries (focuses on the sock itself)
   - **White background** standardization

## Why Test With and Without Preprocessing?

### Potential Benefits of Preprocessing:
1. **Removes background noise** - Focus on the sock, not the floor/table
2. **Consistent framing** - All socks centered and properly cropped
3. **Better feature extraction** - Models can focus on sock patterns/colors

### Potential Drawbacks:
1. **Slower inference** - Background removal adds processing time
2. **Potential artifacts** - Imperfect background removal might hurt accuracy
3. **Over-cropping** - Might lose important context

## How the Comparison Works

The updated script tests each model in two modes:

### Mode 1: "none" (No preprocessing)
- Uses original images as-is
- Only applies model's standard transforms
- Fast inference

### Mode 2: "full" (Full preprocessing)
- Removes background using rembg
- Auto-crops to sock boundaries
- Adds white background
- Then applies model's transforms
- Slower inference

## Reading the Results

### Results Table

```
Model                     Preproc  Same%    Diff%    Top-1%   AP       AUC      Time(ms)   Dim
CLIP-ViT-B-32             none     100.00   66.67   100.00   0.9667   0.9333    380.7     512
CLIP-ViT-B-32             full      95.00   85.00    90.00   0.9500   0.9200    650.3     512
```

**Columns:**
- **Preproc**: Preprocessing mode (none/full)
- **Same%**: Accuracy on matching pairs (higher is better)
- **Diff%**: Accuracy on different pairs (higher is better)
- **Top-1%**: Retrieval accuracy (higher is better)
- **AP**: Average Precision (higher is better)
- **AUC**: ROC-AUC score (higher is better, 0-1 range)
- **Time(ms)**: Inference time per image
- **Dim**: Embedding dimension

### Preprocessing Impact Analysis

The script automatically analyzes the impact:

```
PREPROCESSING IMPACT ANALYSIS
------------------------------------------------------
CLIP-ViT-B-32:
  ROC-AUC: 0.9333 → 0.9200 (-1.33%)
  Top-1:   100.00% → 90.00% (-10.00%)
  Time:    380.7ms → 650.3ms (+269.6ms)
```

**Interpretation:**
- **Negative ROC-AUC change**: Preprocessing hurt accuracy
- **Negative Top-1 change**: Worse retrieval performance
- **Positive time change**: Slower (as expected)

## Expected Results

Based on similar fine-grained matching tasks:

### Models That May Benefit from Preprocessing:

**1. CLIP Models**
- Trained on diverse web images with various backgrounds
- May benefit from consistent white backgrounds
- Expected improvement: +2-5% ROC-AUC

**2. ResNet/EfficientNet**
- Trained on ImageNet (centered objects)
- May benefit from auto-cropping
- Expected improvement: +3-8% ROC-AUC

### Models That May Not Need Preprocessing:

**1. DINOv2**
- Self-supervised training handles various backgrounds
- Strong feature extraction regardless of background
- Expected impact: Minimal (+/- 1%)

**2. Fine-tuned Models**
- If already trained on sock images
- May have learned to handle backgrounds
- Expected impact: Depends on training data

## Installation Requirements

To enable preprocessing comparison:

```bash
pip install rembg opencv-python-headless onnxruntime
```

Without these packages, the script will run but only test "none" mode.

## Performance Considerations

### Preprocessing Overhead:

Typical preprocessing times:
- **Background removal**: +200-400ms per image
- **Auto-cropping**: +10-20ms per image
- **Total overhead**: ~250-450ms per image

### When to Use Preprocessing:

**Use preprocessing if:**
- ✅ Images have cluttered backgrounds
- ✅ Socks are not consistently framed
- ✅ You care more about accuracy than speed
- ✅ Preprocessing improves your metrics by >5%

**Skip preprocessing if:**
- ❌ Images already have clean backgrounds
- ❌ Real-time inference is required (<100ms)
- ❌ Preprocessing doesn't improve metrics
- ❌ Background removal creates artifacts

## Integration with Main App

After comparing results, update your configuration:

### If preprocessing helps:

```python
# backend/app/config.py
USE_PREPROCESSING = True
```

### If preprocessing doesn't help:

```python
# backend/app/config.py
USE_PREPROCESSING = False
```

## Example Results Analysis

### Scenario 1: Preprocessing Helps

```
ResNet-resnet50:
  ROC-AUC: 0.9123 → 0.9567 (+4.44%)
  Top-1:   78.57% → 89.29% (+10.72%)
  Time:    339.6ms → 598.2ms (+258.6ms)
```

**Decision**: ✅ Use preprocessing
**Reason**: +4.4% ROC-AUC and +10.7% retrieval accuracy worth 259ms overhead

### Scenario 2: Preprocessing Hurts

```
CLIP-ViT-B-32:
  ROC-AUC: 0.9333 → 0.9200 (-1.33%)
  Top-1:   100.00% → 90.00% (-10.00%)
  Time:    380.7ms → 650.3ms (+269.6ms)
```

**Decision**: ❌ Don't use preprocessing
**Reason**: Accuracy dropped and slower - no benefit

### Scenario 3: Minimal Impact

```
DINOv2-dinov2-base:
  ROC-AUC: 1.0000 → 1.0000 (+0.00%)
  Top-1:   33.33% → 35.71% (+2.38%)
  Time:    817.9ms → 1089.4ms (+271.5ms)
```

**Decision**: ⚠️ Optional
**Reason**: Minimal improvement, depends on speed requirements

## Advanced: Custom Preprocessing

You can modify the preprocessing in the script:

```python
def preprocess_image_file(self, image_path: str) -> Image.Image:
    image = Image.open(image_path).convert('RGB')
    
    if self.preprocessing == "custom":
        # Add your custom preprocessing here
        # Example: Enhance contrast
        from PIL import ImageEnhance
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.5)
        
        # Example: Apply blur to reduce noise
        image = image.filter(ImageFilter.GaussianBlur(radius=1))
    
    return image
```

Then test with `preprocessing="custom"`.

## Troubleshooting

### "rembg/cv2 not available"
```bash
pip install rembg opencv-python-headless onnxruntime
```

### Preprocessing is very slow
- **Expected**: Background removal adds 200-400ms
- **Solution**: Only use preprocessing if accuracy gains justify the cost
- **Alternative**: Pre-process images once and save them

### Background removal artifacts
- White halos around socks
- Incomplete background removal
- **Solution**: May need to adjust rembg model or skip preprocessing

### Out of memory during preprocessing
```python
# Reduce image size before preprocessing
image = image.resize((512, 512))
```

## Summary

The preprocessing comparison helps you make data-driven decisions:

1. **Run comparison** with and without preprocessing
2. **Analyze impact** on accuracy and speed
3. **Choose configuration** based on your priorities:
   - High accuracy → Use preprocessing if it helps
   - Low latency → Skip preprocessing unless significant gains
4. **Update your app** configuration accordingly

The best choice depends on your specific images and requirements!
