"""
Test script for sock matching algorithm

This script validates the CLIP embedding generation,
feature extraction, and similarity search functionality.

Usage:
    python test_matching.py <image1_path> <image2_path> [additional_images...]
"""

import sys
import os
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.clip_embedding import CLIPEmbeddingService
from app.services.image_preprocessing import ImagePreprocessor
import numpy as np


class MatchingTester:
    """Test harness for sock matching algorithm"""
    
    def __init__(self):
        self.clip_service = CLIPEmbeddingService()
        self.preprocessor = ImagePreprocessor()
        print("✓ Services initialized")
        print(f"✓ Using device: {self.clip_service.device}")
        print()
    
    async def test_image_pair(self, image1_path: str, image2_path: str):
        """Test matching between two images"""
        print("=" * 80)
        print(f"Testing pair:")
        print(f"  Image 1: {image1_path}")
        print(f"  Image 2: {image2_path}")
        print("-" * 80)
        
        # Test preprocessing
        print("\n1. PREPROCESSING")
        print("-" * 40)
        
        with open(image1_path, 'rb') as f:
            img1_bytes = f.read()
        
        with open(image2_path, 'rb') as f:
            img2_bytes = f.read()
        
        processed1_path = "test_processed_1.jpg"
        processed2_path = "test_processed_2.jpg"
        
        proc1, err1 = await self.preprocessor.preprocess_image(img1_bytes, processed1_path)
        proc2, err2 = await self.preprocessor.preprocess_image(img2_bytes, processed2_path)
        
        if err1 or err2:
            print(f"✗ Preprocessing failed: {err1 or err2}")
            return
        
        print(f"✓ Image 1 preprocessed: {proc1}")
        print(f"✓ Image 2 preprocessed: {proc2}")
        
        # Test embedding generation
        print("\n2. EMBEDDING GENERATION")
        print("-" * 40)
        
        embedding1 = await self.clip_service.generate_embedding(proc1)
        embedding2 = await self.clip_service.generate_embedding(proc2)
        
        if embedding1 is None or embedding2 is None:
            print("✗ Embedding generation failed")
            return
        
        print(f"✓ Embedding 1 shape: {embedding1.shape}")
        print(f"✓ Embedding 2 shape: {embedding2.shape}")
        print(f"  Embedding 1 norm: {np.linalg.norm(embedding1):.4f}")
        print(f"  Embedding 2 norm: {np.linalg.norm(embedding2):.4f}")
        
        # Test similarity calculation
        print("\n3. SIMILARITY CALCULATION")
        print("-" * 40)
        
        similarity = self.clip_service.calculate_similarity(embedding1, embedding2)
        print(f"✓ Similarity score: {similarity:.4f}")
        
        if similarity >= 0.85:
            print(f"  ✓ STRONG MATCH (>= 0.85)")
        elif similarity >= 0.75:
            print(f"  ~ POSSIBLE MATCH (>= 0.75)")
        else:
            print(f"  ✗ NO MATCH (< 0.75)")
        
        # Test feature extraction
        print("\n4. FEATURE EXTRACTION")
        print("-" * 40)
        
        features1 = await self.clip_service.extract_features(proc1)
        features2 = await self.clip_service.extract_features(proc2)
        
        print(f"Image 1 features:")
        print(f"  Color: {features1.get('dominant_color')}")
        print(f"  Pattern: {features1.get('pattern_type')}")
        
        print(f"\nImage 2 features:")
        print(f"  Color: {features2.get('dominant_color')}")
        print(f"  Pattern: {features2.get('pattern_type')}")
        
        # Compare features
        color_match = features1.get('dominant_color') == features2.get('dominant_color')
        pattern_match = features1.get('pattern_type') == features2.get('pattern_type')
        
        print(f"\nFeature matching:")
        print(f"  Color match: {'✓' if color_match else '✗'}")
        print(f"  Pattern match: {'✓' if pattern_match else '✗'}")
        
        # Cleanup
        try:
            os.remove(proc1)
            os.remove(proc2)
        except:
            pass
        
        print("\n" + "=" * 80)
        print()
    
    async def test_multiple_images(self, image_paths: list):
        """Test matching across multiple images"""
        print("=" * 80)
        print(f"Testing {len(image_paths)} images")
        print("=" * 80)
        print()
        
        # Preprocess all images
        print("Preprocessing all images...")
        processed_paths = []
        embeddings = []
        
        for i, img_path in enumerate(image_paths):
            with open(img_path, 'rb') as f:
                img_bytes = f.read()
            
            proc_path = f"test_processed_{i}.jpg"
            proc, err = await self.preprocessor.preprocess_image(img_bytes, proc_path)
            
            if err:
                print(f"✗ Failed to process {img_path}: {err}")
                continue
            
            processed_paths.append(proc)
            
            embedding = await self.clip_service.generate_embedding(proc)
            if embedding is not None:
                embeddings.append(embedding)
                print(f"✓ Processed: {os.path.basename(img_path)}")
            else:
                print(f"✗ Failed embedding: {os.path.basename(img_path)}")
        
        print(f"\nSuccessfully processed {len(embeddings)} images")
        print()
        
        # Create similarity matrix
        print("Similarity Matrix:")
        print("-" * 80)
        print("       ", end="")
        for i in range(len(embeddings)):
            print(f"  Img{i+1:2d}", end="")
        print()
        
        for i in range(len(embeddings)):
            print(f"Img{i+1:2d} ", end="")
            for j in range(len(embeddings)):
                if i == j:
                    print("   --  ", end="")
                else:
                    similarity = self.clip_service.calculate_similarity(
                        embeddings[i], embeddings[j]
                    )
                    print(f"  {similarity:.2f} ", end="")
            print()
        
        print()
        
        # Find best matches
        print("Best Matches:")
        print("-" * 80)
        
        matches = []
        for i in range(len(embeddings)):
            for j in range(i + 1, len(embeddings)):
                similarity = self.clip_service.calculate_similarity(
                    embeddings[i], embeddings[j]
                )
                matches.append((i, j, similarity))
        
        matches.sort(key=lambda x: x[2], reverse=True)
        
        for i, j, sim in matches[:5]:  # Top 5 matches
            status = "✓" if sim >= 0.85 else "~" if sim >= 0.75 else "✗"
            print(f"{status} Img{i+1:2d} <-> Img{j+1:2d}: {sim:.4f}")
        
        # Cleanup
        for proc in processed_paths:
            try:
                os.remove(proc)
            except:
                pass
        
        print("\n" + "=" * 80)


async def main():
    """Main test function"""
    if len(sys.argv) < 3:
        print("Usage: python test_matching.py <image1> <image2> [additional_images...]")
        print()
        print("Examples:")
        print("  python test_matching.py sock1.jpg sock2.jpg")
        print("  python test_matching.py sock1.jpg sock2.jpg sock3.jpg sock4.jpg")
        sys.exit(1)
    
    image_paths = sys.argv[1:]
    
    # Validate all images exist
    for img_path in image_paths:
        if not os.path.exists(img_path):
            print(f"Error: Image not found: {img_path}")
            sys.exit(1)
    
    print("\n" + "=" * 80)
    print("SOCK MATCHING ALGORITHM TEST")
    print("=" * 80)
    print()
    
    tester = MatchingTester()
    
    if len(image_paths) == 2:
        # Test single pair
        await tester.test_image_pair(image_paths[0], image_paths[1])
    else:
        # Test multiple images
        await tester.test_multiple_images(image_paths)
    
    print("\nTest completed!")


if __name__ == "__main__":
    asyncio.run(main())
