"""
Standalone sock matching test script - runs locally without Docker

This script uses the EXACT same backend code as the FastAPI application,
ensuring consistent behavior between local testing and production.

Requirements:
    pip install torch torchvision open-clip-torch pillow rembg opencv-python numpy scikit-learn loguru

Usage:
    python local_test_matching.py <image1> <image2> [additional_images...]
    
Examples:
    # Test a pair
    python local_test_matching.py sample_images/sock1.jpg sample_images/sock2.jpg
    
    # Test multiple images
    python local_test_matching.py sample_images/*.jpg
"""

import sys
import os
from pathlib import Path
from typing import Optional, Tuple, Dict, List
import numpy as np

# Add backend to Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

# Check if required packages are installed
try:
    import torch
    import open_clip
    from rembg import remove
    import cv2
    from sklearn.preprocessing import normalize
except ImportError as e:
    print(f"❌ Missing required package: {e}")
    print("\nPlease install required packages:")
    print("pip install torch torchvision open-clip-torch pillow rembg opencv-python numpy scikit-learn loguru")
    sys.exit(1)

# Monkey-patch config and logging before importing backend services
import standalone_config
sys.modules['app.config'] = standalone_config
sys.modules['app.logging_config'] = standalone_config

# Now import backend services
try:
    from app.services.standalone_adapter import (
        StandaloneImagePreprocessor,
        StandaloneCLIPEmbeddingService
    )
except ImportError as e:
    print(f"❌ Failed to import backend services: {e}")
    print("\nMake sure you're running this script from the project root directory.")
    sys.exit(1)


# Use backend services via adapters
ImagePreprocessor = StandaloneImagePreprocessor
CLIPEmbeddingService = StandaloneCLIPEmbeddingService


class MatchingTester:
    """Test harness for sock matching algorithm"""
    
    def __init__(self):
        self.preprocessor = ImagePreprocessor()
        self.clip_service = CLIPEmbeddingService()
        print()
    
    def test_image_pair(self, image1_path: str, image2_path: str):
        """Test matching between two images"""
        print("=" * 80)
        print(f"🧦 Testing Sock Pair")
        print("=" * 80)
        print(f"Image 1: {image1_path}")
        print(f"Image 2: {image2_path}")
        print()
        
        # Preprocess images
        print("Step 1: PREPROCESSING")
        print("-" * 80)
        proc1 = self.preprocessor.preprocess_image(image1_path, "test_proc_1.jpg")
        proc2 = self.preprocessor.preprocess_image(image2_path, "test_proc_2.jpg")
        
        if not proc1 or not proc2:
            print("❌ Preprocessing failed")
            return
        
        print()
        
        # Generate embeddings
        print("Step 2: GENERATING EMBEDDINGS")
        print("-" * 80)
        print("  🧠 Generating embedding for image 1...")
        emb1 = self.clip_service.generate_embedding(proc1)
        print("  🧠 Generating embedding for image 2...")
        emb2 = self.clip_service.generate_embedding(proc2)
        
        if emb1 is None or emb2 is None:
            print("❌ Embedding generation failed")
            return
        
        print(f"  ✅ Embedding 1: shape {emb1.shape}, norm {np.linalg.norm(emb1):.4f}")
        print(f"  ✅ Embedding 2: shape {emb2.shape}, norm {np.linalg.norm(emb2):.4f}")
        print()
        
        # Calculate similarity
        print("Step 3: SIMILARITY CALCULATION")
        print("-" * 80)
        similarity = self.clip_service.calculate_similarity(emb1, emb2)
        print(f"  📊 Similarity Score: {similarity:.4f}")
        print()
        
        if similarity >= 0.85:
            print("  ✅ STRONG MATCH! These socks are very likely a pair (≥ 0.85)")
        elif similarity >= 0.75:
            print("  ⚠️  POSSIBLE MATCH. These socks might be a pair (≥ 0.75)")
        else:
            print("  ❌ NO MATCH. These socks are probably not a pair (< 0.75)")
        
        print()
        
        # Extract features
        print("Step 4: FEATURE EXTRACTION")
        print("-" * 80)
        features1 = self.clip_service.extract_features(proc1)
        features2 = self.clip_service.extract_features(proc2)
        
        color1 = features1.get('dominant_color', 'unknown')
        color2 = features2.get('dominant_color', 'unknown')
        pattern1 = features1.get('pattern_type', 'unknown')
        pattern2 = features2.get('pattern_type', 'unknown')
        
        print(f"  Image 1:")
        print(f"    Color: {color1}")
        print(f"    Pattern: {pattern1}")
        
        print(f"  Image 2:")
        print(f"    Color: {color2}")
        print(f"    Pattern: {pattern2}")
        
        print()
        
        # Calculate color similarity (perceptual, not exact match)
        if color1 and color2 and color1 != 'unknown' and color2 != 'unknown':
            color_similarity = self.clip_service.calculate_color_similarity(color1, color2)
            color_match = color_similarity >= 0.90  # 90% similarity threshold
            print(f"  Color similarity: {color_similarity:.3f} {'✅' if color_match else '❌'}")
        else:
            color_match = False
            print(f"  Color similarity: unknown ❌")
        
        pattern_match = pattern1 == pattern2
        print(f"  Pattern match: {'✅' if pattern_match else '❌'}")
        
        print()
        print("=" * 80)
        print()
    
    def test_multiple_images(self, image_paths: List[str]):
        """Test matching across multiple images"""
        print("=" * 80)
        print(f"🧦 Testing {len(image_paths)} Sock Images")
        print("=" * 80)
        print()
        
        # Preprocess all images
        print("Step 1: PREPROCESSING ALL IMAGES")
        print("-" * 80)
        processed = []
        embeddings = []
        
        for i, img_path in enumerate(image_paths):
            proc_path = f"test_proc_{i}.jpg"
            proc = self.preprocessor.preprocess_image(img_path, proc_path)
            
            if proc:
                processed.append((img_path, proc))
            else:
                print(f"  ⚠️  Skipping {img_path}")
        
        print()
        
        # Generate embeddings
        print("Step 2: GENERATING EMBEDDINGS")
        print("-" * 80)
        for img_path, proc_path in processed:
            print(f"  🧠 {os.path.basename(img_path)}...")
            emb = self.clip_service.generate_embedding(proc_path)
            if emb is not None:
                embeddings.append(emb)
            else:
                print(f"    ❌ Failed")
        
        print(f"  ✅ Generated {len(embeddings)} embeddings")
        print()
        
        # Create similarity matrix
        print("Step 3: SIMILARITY MATRIX")
        print("-" * 80)
        print("        ", end="")
        for i in range(len(embeddings)):
            print(f"  Sock{i+1:2d}", end="")
        print()
        print("        " + "-" * (9 * len(embeddings)))
        
        for i in range(len(embeddings)):
            print(f"Sock{i+1:2d} |", end="")
            for j in range(len(embeddings)):
                if i == j:
                    print("    --  ", end="")
                else:
                    sim = self.clip_service.calculate_similarity(embeddings[i], embeddings[j])
                    print(f"  {sim:.3f} ", end="")
            print()
        
        print()
        
        # Find best matches
        print("Step 4: TOP MATCHES")
        print("-" * 80)
        matches = []
        for i in range(len(embeddings)):
            for j in range(i + 1, len(embeddings)):
                sim = self.clip_service.calculate_similarity(embeddings[i], embeddings[j])
                matches.append((i, j, sim))
        
        matches.sort(key=lambda x: x[2], reverse=True)
        
        print("Top 10 most similar pairs:")
        for i, j, sim in matches[:10]:
            status = "✅" if sim >= 0.85 else "⚠️ " if sim >= 0.75 else "❌"
            img1_name = os.path.basename(processed[i][0])
            img2_name = os.path.basename(processed[j][0])
            print(f"  {status} Sock{i+1:2d} <-> Sock{j+1:2d}: {sim:.4f}")
            print(f"       {img1_name}")
            print(f"       {img2_name}")
            print()
        
        print("=" * 80)
        print()
        
        # Show likely pairs
        print("LIKELY SOCK PAIRS (similarity ≥ 0.85):")
        print("-" * 80)
        found_pairs = False
        for i, j, sim in matches:
            if sim >= 0.85:
                found_pairs = True
                img1_name = os.path.basename(processed[i][0])
                img2_name = os.path.basename(processed[j][0])
                print(f"  ✅ Pair found! (similarity: {sim:.4f})")
                print(f"     • {img1_name}")
                print(f"     • {img2_name}")
                print()
        
        if not found_pairs:
            print("  No strong matches found (all similarities < 0.85)")
        
        print()


def main():
    """Main test function"""
    print()
    print("=" * 80)
    print("🧦 SOCK MATCHING ALGORITHM - LOCAL TEST")
    print("=" * 80)
    print()
    
    if len(sys.argv) < 2:
        print("Usage: python local_test_matching.py <image1> <image2> [additional_images...]")
        print()
        print("Examples:")
        print("  # Test a single pair")
        print("  python local_test_matching.py sample_images/sock1.jpg sample_images/sock2.jpg")
        print()
        print("  # Test multiple images")
        print("  python local_test_matching.py sample_images/*.jpg")
        print()
        sys.exit(1)
    
    image_paths = sys.argv[1:]
    
    # Validate images exist
    valid_paths = []
    for img_path in image_paths:
        if os.path.exists(img_path):
            valid_paths.append(img_path)
        else:
            print(f"⚠️  Image not found: {img_path}")
    
    if not valid_paths:
        print("❌ No valid images found")
        sys.exit(1)
    
    print(f"Found {len(valid_paths)} valid images")
    print()
    
    # Initialize tester
    tester = MatchingTester()
    
    # Run tests
    if len(valid_paths) == 2:
        tester.test_image_pair(valid_paths[0], valid_paths[1])
    else:
        tester.test_multiple_images(valid_paths)
    
    print("✅ Test completed!")
    print()


if __name__ == "__main__":
    main()
