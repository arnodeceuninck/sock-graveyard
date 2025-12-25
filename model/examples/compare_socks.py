"""
Example script demonstrating sock_matcher model usage

This script shows how to use the sock_matcher package for:
- Image preprocessing
- Embedding generation
- Feature extraction
- Similarity comparison

Usage:
    python examples/compare_socks.py <image1> <image2> [image3] ...
    
Example:
    python examples/compare_socks.py sock1.jpg sock2.jpg sock3.jpg
"""

import asyncio
import sys
from pathlib import Path
from typing import List, Tuple
import numpy as np

# Add parent directory to path to import sock_matcher
sys.path.insert(0, str(Path(__file__).parent.parent))

from sock_matcher import CLIPEmbeddingService, ImagePreprocessor
from sock_matcher.config import ModelConfig


class SockComparison:
    """Helper class for comparing socks using the model"""
    
    def __init__(self, config: ModelConfig = None):
        self.preprocessor = ImagePreprocessor(config=config)
        self.clip_service = CLIPEmbeddingService(config=config)
        print(f"✓ Initialized on device: {self.clip_service.device}")
        print(f"✓ Using CLIP model: {self.clip_service._service.config.CLIP_MODEL_NAME}")
        print()
    
    async def process_image(self, image_path: str) -> Tuple[str, np.ndarray, dict]:
        """
        Process a single image
        
        Returns:
            (processed_path, embedding, features)
        """
        print(f"📸 Processing: {Path(image_path).name}")
        
        # Read image
        with open(image_path, 'rb') as f:
            image_bytes = f.read()
        
        # Preprocess
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        processed_filename = f"processed_{Path(image_path).stem}.jpg"
        processed_path = str(output_dir / processed_filename)
        
        result_path, error = await self.preprocessor.preprocess_image(
            image_bytes,
            processed_path
        )
        
        if error:
            print(f"  ❌ Preprocessing failed: {error}")
            return None, None, None
        
        print(f"  ✓ Preprocessed → {processed_path}")
        
        # Generate embedding
        embedding = await self.clip_service.generate_embedding(result_path)
        if embedding is None:
            print(f"  ❌ Embedding generation failed")
            return result_path, None, None
        
        print(f"  ✓ Embedding generated (shape: {embedding.shape})")
        
        # Extract features
        features = await self.clip_service.extract_features(result_path)
        print(f"  ✓ Dominant color: {features['dominant_color']}")
        print(f"  ✓ Pattern type: {features['pattern_type']}")
        print()
        
        return result_path, embedding, features
    
    def compare_embeddings(self, embedding1: np.ndarray, embedding2: np.ndarray, 
                          name1: str, name2: str):
        """Compare two embeddings"""
        similarity = self.clip_service.calculate_similarity(embedding1, embedding2)
        
        print(f"🔍 Similarity between {name1} and {name2}:")
        print(f"  Visual similarity: {similarity:.2%}")
        
        # Interpretation
        if similarity > 0.9:
            print(f"  ✓ Very likely a match! 🎯")
        elif similarity > 0.8:
            print(f"  ✓ Probably a match 👍")
        elif similarity > 0.7:
            print(f"  ~ Possibly similar 🤔")
        else:
            print(f"  ✗ Likely different socks ❌")
        
        return similarity
    
    def compare_colors(self, color1: str, color2: str, name1: str, name2: str):
        """Compare two colors"""
        similarity = self.clip_service.calculate_color_similarity(color1, color2)
        
        print(f"  Color similarity: {similarity:.2%}")
        if similarity > 0.9:
            print(f"  ✓ Very similar colors")
        elif similarity > 0.7:
            print(f"  ~ Somewhat similar colors")
        else:
            print(f"  ✗ Different colors")


async def main():
    """Main function"""
    if len(sys.argv) < 3:
        print("Usage: python compare_socks.py <image1> <image2> [image3] ...")
        print("\nExample:")
        print("  python compare_socks.py sock1.jpg sock2.jpg")
        print("  python compare_socks.py *.jpg")
        sys.exit(1)
    
    image_paths = sys.argv[1:]
    
    # Validate images exist
    for path in image_paths:
        if not Path(path).exists():
            print(f"❌ File not found: {path}")
            sys.exit(1)
    
    print("=" * 60)
    print("🧦 Sock Matcher - Example Script")
    print("=" * 60)
    print()
    
    # Optional: Use custom configuration
    # config = ModelConfig(
    #     clip_model_name="ViT-B-32",
    #     clip_pretrained="openai"
    # )
    # comparison = SockComparison(config=config)
    
    comparison = SockComparison()
    
    # Process all images
    print("Step 1: Processing images...")
    print("-" * 60)
    
    results = []
    for image_path in image_paths:
        processed_path, embedding, features = await comparison.process_image(image_path)
        results.append({
            'original': image_path,
            'processed': processed_path,
            'embedding': embedding,
            'features': features,
            'name': Path(image_path).stem
        })
    
    # Filter out failed processing
    results = [r for r in results if r['embedding'] is not None]
    
    if len(results) < 2:
        print("❌ Need at least 2 successfully processed images to compare")
        sys.exit(1)
    
    # Compare all pairs
    print("Step 2: Comparing all pairs...")
    print("-" * 60)
    
    similarities = []
    for i in range(len(results)):
        for j in range(i + 1, len(results)):
            r1 = results[i]
            r2 = results[j]
            
            similarity = comparison.compare_embeddings(
                r1['embedding'], r2['embedding'],
                r1['name'], r2['name']
            )
            
            comparison.compare_colors(
                r1['features']['dominant_color'],
                r2['features']['dominant_color'],
                r1['name'], r2['name']
            )
            
            print()
            
            similarities.append({
                'pair': (r1['name'], r2['name']),
                'similarity': similarity
            })
    
    # Summary
    print("=" * 60)
    print("📊 Summary")
    print("=" * 60)
    
    # Sort by similarity
    similarities.sort(key=lambda x: x['similarity'], reverse=True)
    
    print("\nBest matches:")
    for item in similarities[:3]:
        name1, name2 = item['pair']
        sim = item['similarity']
        print(f"  {name1} ↔ {name2}: {sim:.2%}")
    
    if len(similarities) > 3:
        print("\nWorst matches:")
        for item in similarities[-3:]:
            name1, name2 = item['pair']
            sim = item['similarity']
            print(f"  {name1} ↔ {name2}: {sim:.2%}")
    
    print(f"\nProcessed images saved to: output/")
    print("✓ Done!")


if __name__ == "__main__":
    asyncio.run(main())
