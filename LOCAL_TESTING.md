# Local Testing Guide

Run the sock matching algorithm locally without Docker!

**IMPORTANT**: The local test script uses the **exact same backend code** as the FastAPI application, ensuring consistent behavior between local testing and production.

## Architecture

```
local_test_matching.py  →  standalone_adapter.py  →  backend/app/services/
                                                      ├── image_preprocessing.py
                                                      └── clip_embedding.py
```

No code duplication! The test script imports production services through lightweight adapters.

## Quick Start

### 1. Install Python Dependencies

```bash
pip install -r local_requirements.txt
```

This will install:
- PyTorch (deep learning framework)
- OpenCLIP (CLIP model for embeddings)
- rembg (background removal)
- OpenCV (image processing)
- PIL/Pillow (image handling)
- NumPy & scikit-learn (numerical operations)
- loguru (logging)
- pydantic-settings (configuration)

### 2. Run Tests

**Test a single pair:**
```bash
python local_test_matching.py sample_images/PXL_20251214_192708921.jpg sample_images/PXL_20251214_192712389.jpg
```

**Test multiple images:**
```bash
python local_test_matching.py sample_images/PXL_20251214_192708921.jpg sample_images/PXL_20251214_192712389.jpg sample_images/PXL_20251214_192714743.jpg sample_images/PXL_20251214_192716974.jpg
```

**Test all images in a folder (PowerShell):**
```powershell
python local_test_matching.py (Get-ChildItem sample_images\*.jpg | Select-Object -First 10).FullName
```

Or simpler:
```powershell
$images = Get-ChildItem sample_images\*.jpg | Select-Object -First 10
python local_test_matching.py $images.FullName
```

## What the Script Does

1. **Preprocessing**
   - Removes background using AI (rembg with U2-Net model)
   - Auto-crops to sock boundaries
   - Resizes to 224x224 with padding
   - Saves processed images as `test_proc_*.jpg`

2. **Embedding Generation**
   - Uses OpenAI's CLIP model (ViT-B-32)
   - Generates 512-dimensional feature vectors
   - Normalizes embeddings for comparison

3. **Similarity Calculation**
   - Computes cosine similarity between embeddings
   - Scores: 1.0 = identical, 0.0 = completely different
   - Thresholds:
     - ≥ 0.85 = Strong match (likely a pair)
     - ≥ 0.75 = Possible match
     - < 0.75 = No match

4. **Feature Extraction**
   - Detects dominant colors
   - Identifies patterns (solid, textured, patterned)
   - Uses OpenCV edge detection

## Output

The script will show:
- Preprocessing progress for each image
- Embedding generation details
- Similarity scores
- Feature comparisons (color, pattern)
- Match recommendations
- For multiple images: similarity matrix and top matches

## Notes

- First run will download the CLIP model (~350MB)
- First run will download the rembg model (~176MB)
- GPU recommended but not required (will use CPU if no CUDA available)
- Processed images are saved in the current directory
- Processing time: ~2-5 seconds per image (CPU), ~0.5-1 second (GPU)

## Troubleshooting

**Import errors:**
```bash
pip install --upgrade -r local_requirements.txt
```

**Out of memory:**
- Process fewer images at once
- Close other applications
- Use CPU instead of GPU if having CUDA issues

**Slow processing:**
- First run downloads models (one-time)
- Background removal is the slowest step
- Consider reducing image count for testing
