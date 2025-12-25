"""
Test different CLIP model configurations

This script compares different CLIP models to help you choose
the best one for your use case.

Usage:
    python examples/test_models.py <image1> <image2>
"""

import asyncio
import sys
import time
from pathlib import Path
from typing import List, Tuple

sys.path.insert(0, str(Path(__file__).parent.parent))

from sock_matcher import CLIPEmbeddingService
from sock_matcher.config import ModelConfig


# Different CLIP model configurations to test
MODELS_TO_TEST = [
    ("ViT-B-32", "openai"),       # Default - good balance
    ("ViT-B-16", "openai"),       # More accurate but slower
    ("ViT-L-14", "openai"),       # Best accuracy, slowest
    ("RN50", "openai"),           # ResNet-based, faster
]


async def benchmark_model(model_name: str, pretrained: str, image_path: str) -> dict:
    """Test a single model configuration"""
    print(f"\n{'='*60}")
    print(f"Testing: {model_name} ({pretrained})")
    print('='*60)
    
    try:
        # Initialize model
        config = ModelConfig(
            clip_model_name=model_name,
            clip_pretrained=pretrained
        )
        
        init_start = time.time()
        service = CLIPEmbeddingService(config=config)
        init_time = time.time() - init_start
        
        print(f"✓ Initialization time: {init_time:.2f}s")
        print(f"✓ Device: {service.device}")
        
        # Generate embedding
        embed_start = time.time()
        embedding = await service.generate_embedding(image_path)
        embed_time = time.time() - embed_start
        
        if embedding is None:
            print("❌ Failed to generate embedding")
            return None
        
        print(f"✓ Embedding generation time: {embed_time:.2f}s")
        print(f"✓ Embedding shape: {embedding.shape}")
        
        # Extract features
        feature_start = time.time()
        features = await service.extract_features(image_path)
        feature_time = time.time() - feature_start
        
        print(f"✓ Feature extraction time: {feature_time:.2f}s")
        print(f"✓ Dominant color: {features['dominant_color']}")
        print(f"✓ Pattern: {features['pattern_type']}")
        
        return {
            'model': f"{model_name} ({pretrained})",
            'init_time': init_time,
            'embed_time': embed_time,
            'feature_time': feature_time,
            'total_time': init_time + embed_time + feature_time,
            'embedding': embedding,
            'features': features,
            'device': service.device
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


async def compare_models(image1_path: str, image2_path: str):
    """Compare embeddings from different models"""
    print("\n" + "="*60)
    print("Comparing similarity scores across models")
    print("="*60)
    
    for model_name, pretrained in MODELS_TO_TEST:
        try:
            config = ModelConfig(
                clip_model_name=model_name,
                clip_pretrained=pretrained
            )
            service = CLIPEmbeddingService(config=config)
            
            # Generate embeddings for both images
            emb1 = await service.generate_embedding(image1_path)
            emb2 = await service.generate_embedding(image2_path)
            
            if emb1 is not None and emb2 is not None:
                similarity = service.calculate_similarity(emb1, emb2)
                print(f"{model_name:20} → Similarity: {similarity:.4f} ({similarity:.2%})")
            
        except Exception as e:
            print(f"{model_name:20} → Error: {e}")


async def main():
    if len(sys.argv) < 3:
        print("Usage: python test_models.py <image1> <image2>")
        print("\nThis script tests different CLIP models to help you choose the best one.")
        sys.exit(1)
    
    image1_path = sys.argv[1]
    image2_path = sys.argv[2]
    
    if not Path(image1_path).exists():
        print(f"❌ File not found: {image1_path}")
        sys.exit(1)
    
    if not Path(image2_path).exists():
        print(f"❌ File not found: {image2_path}")
        sys.exit(1)
    
    print("="*60)
    print("🧠 CLIP Model Comparison Tool")
    print("="*60)
    print(f"\nTest image 1: {image1_path}")
    print(f"Test image 2: {image2_path}")
    
    # Benchmark each model with first image
    print("\n" + "="*60)
    print("PHASE 1: Performance Benchmarks (using image 1)")
    print("="*60)
    
    results = []
    for model_name, pretrained in MODELS_TO_TEST:
        result = await benchmark_model(model_name, pretrained, image1_path)
        if result:
            results.append(result)
    
    # Compare similarity scores
    print("\n" + "="*60)
    print("PHASE 2: Similarity Comparison (image 1 vs image 2)")
    print("="*60)
    await compare_models(image1_path, image2_path)
    
    # Summary
    print("\n" + "="*60)
    print("📊 SUMMARY & RECOMMENDATIONS")
    print("="*60)
    
    if results:
        print("\nPerformance Comparison:")
        print(f"{'Model':<30} {'Total Time':<12} {'Device':<8}")
        print("-" * 60)
        
        for r in sorted(results, key=lambda x: x['total_time']):
            print(f"{r['model']:<30} {r['total_time']:>10.2f}s  {r['device']:<8}")
        
        fastest = min(results, key=lambda x: x['total_time'])
        slowest = max(results, key=lambda x: x['total_time'])
        
        print(f"\n⚡ Fastest: {fastest['model']} ({fastest['total_time']:.2f}s)")
        print(f"🐌 Slowest: {slowest['model']} ({slowest['total_time']:.2f}s)")
        
        print("\n💡 Recommendations:")
        print("  • ViT-B-32 (openai): Good balance of speed and accuracy [DEFAULT]")
        print("  • ViT-B-16 (openai): Better accuracy, slightly slower")
        print("  • ViT-L-14 (openai): Best accuracy, much slower")
        print("  • RN50 (openai): Fastest, lower accuracy")
        
        print("\n📝 To use a different model, update your config:")
        print("  config = ModelConfig(")
        print("      clip_model_name='ViT-B-16',")
        print("      clip_pretrained='openai'")
        print("  )")
    
    print("\n✓ Done!")


if __name__ == "__main__":
    asyncio.run(main())
