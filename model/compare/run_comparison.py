"""
Main script for running model comparisons.

Usage:
    python -m compare.run_comparison
    
    or from another directory:
    python compare/run_comparison.py
"""

import asyncio
import json
from pathlib import Path

# Check for optional dependencies
try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False
    print("⚠ PyTorch not available")

try:
    import open_clip
    HAS_OPEN_CLIP = True
except ImportError:
    HAS_OPEN_CLIP = False
    print("⚠ OpenCLIP not available")

try:
    from transformers import AutoImageProcessor, AutoModel
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False
    print("⚠ Transformers not available")

try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False

from .dataset import SockPairDataset
from .evaluator import ModelEvaluator
from .results import create_comparison_table, print_recommendations
from .model_wrappers import (
    CLIPModelWrapper,
    DINOModelWrapper,
    ResNetModelWrapper,
    EfficientNetModelWrapper,
)
from .preprocessing import ImagePreprocessor


async def main():
    """Main evaluation function"""
    print("🧦 Sock Matching Model Comparison")
    print("="*60)
    
    # Setup dataset
    image_dir = Path(__file__).parent.parent / "images"
    if not image_dir.exists():
        print(f"❌ Image directory not found: {image_dir}")
        return
    
    dataset = SockPairDataset(str(image_dir))
    
    if len(dataset.pairs) == 0:
        print("❌ No sock pairs found!")
        print("   Make sure you have images named like: sock-{guid}-0.jpg, sock-{guid}-1.jpg")
        return
    
    evaluator = ModelEvaluator(dataset)
    
    # List of models to test
    models_to_test = []
    
    # Test each model with and without preprocessing
    preprocessing_modes = ["none"]
    if ImagePreprocessor.is_available():
        preprocessing_modes.append("full")
        print("✓ Preprocessing available - will test with and without\n")
    else:
        print("⚠ Preprocessing not available - testing without preprocessing only\n")
    
    # CLIP variants (general vision-language models)
    if HAS_OPEN_CLIP:
        for preproc in preprocessing_modes:
            try:
                models_to_test.append(CLIPModelWrapper("ViT-B-32", "openai", preproc))
            except Exception as e:
                print(f"⚠ Could not load CLIP ViT-B-32 ({preproc}): {e}")
        
        # Only test ViT-L-14 without preprocessing (it's slow)
        try:
            models_to_test.append(CLIPModelWrapper("ViT-L-14", "openai", "none"))
        except Exception as e:
            print(f"⚠ Could not load CLIP ViT-L-14: {e}")
    
    # DINOv2 (self-supervised, excellent for fine-grained similarity)
    if HAS_TRANSFORMERS:
        for preproc in preprocessing_modes:
            try:
                models_to_test.append(DINOModelWrapper("facebook/dinov2-base", preproc))
            except Exception as e:
                print(f"⚠ Could not load DINOv2 ({preproc}): {e}")
    
    # ResNet (standard CNN baseline)
    if HAS_TORCH:
        for preproc in preprocessing_modes:
            try:
                models_to_test.append(ResNetModelWrapper("resnet50", preproc))
            except Exception as e:
                print(f"⚠ Could not load ResNet50 ({preproc}): {e}")
        
        # Only test ResNet18 without preprocessing (for speed comparison)
        try:
            models_to_test.append(ResNetModelWrapper("resnet18", "none"))
        except Exception as e:
            print(f"⚠ Could not load ResNet18: {e}")
    
    # EfficientNet (efficient CNN)
    if HAS_TORCH:
        for preproc in preprocessing_modes:
            try:
                models_to_test.append(EfficientNetModelWrapper("efficientnet_b0", preproc))
            except Exception as e:
                print(f"⚠ Could not load EfficientNet-B0 ({preproc}): {e}")
    
    if not models_to_test:
        print("❌ No models available to test!")
        return
    
    print(f"\n✓ Testing {len(models_to_test)} models\n")
    
    # Evaluate all models
    results = []
    
    # Use tqdm if available for progress bar
    if HAS_TQDM:
        model_iterator = tqdm(models_to_test, desc="Evaluating models", unit="model")
    else:
        model_iterator = models_to_test
    
    for model in model_iterator:
        try:
            result = evaluator.evaluate_model(model)
            results.append(result)
        except Exception as e:
            print(f"❌ Error evaluating {model.name}: {e}")
            import traceback
            traceback.print_exc()
    
    # Display results
    if results:
        print(create_comparison_table(results))
        
        # Save results
        output_file = Path(__file__).parent.parent / "examples" / "model_comparison_results.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w') as f:
            json.dump([r.to_dict() for r in results], f, indent=2)
        print(f"✓ Results saved to: {output_file}")
        
        # Print recommendations
        print_recommendations(results)
    else:
        print("❌ No results to display")


if __name__ == "__main__":
    asyncio.run(main())
