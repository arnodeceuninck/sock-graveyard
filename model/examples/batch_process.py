"""
Batch processing example

Process a directory of sock images and save embeddings to a file.

Usage:
    python examples/batch_process.py <input_dir> [output_file]
    
Example:
    python examples/batch_process.py ./sock_images embeddings.npz
"""

import asyncio
import sys
from pathlib import Path
import numpy as np
from typing import Dict, List
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from sock_matcher import CLIPEmbeddingService, ImagePreprocessor


async def process_directory(input_dir: Path, output_file: Path):
    """Process all images in a directory"""
    
    # Find all image files
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif'}
    image_files = [
        f for f in input_dir.iterdir() 
        if f.is_file() and f.suffix.lower() in image_extensions
    ]
    
    if not image_files:
        print(f"❌ No image files found in {input_dir}")
        sys.exit(1)
    
    print(f"Found {len(image_files)} images to process")
    print()
    
    # Initialize services
    preprocessor = ImagePreprocessor()
    clip_service = CLIPEmbeddingService()
    
    print(f"✓ Using device: {clip_service.device}")
    print()
    
    # Create output directory for processed images
    processed_dir = Path("output/processed_batch")
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    # Process images
    embeddings = {}
    features_list = {}
    processed_paths = {}
    
    print("Processing images...")
    print("-" * 60)
    
    for idx, image_file in enumerate(image_files, 1):
        print(f"[{idx}/{len(image_files)}] {image_file.name}")
        
        try:
            # Read image
            with open(image_file, 'rb') as f:
                image_bytes = f.read()
            
            # Preprocess
            processed_path = str(processed_dir / f"processed_{image_file.stem}.jpg")
            result_path, error = await preprocessor.preprocess_image(
                image_bytes,
                processed_path
            )
            
            if error:
                print(f"  ❌ Preprocessing failed: {error}")
                continue
            
            # Generate embedding
            embedding = await clip_service.generate_embedding(result_path)
            if embedding is None:
                print(f"  ❌ Embedding generation failed")
                continue
            
            # Extract features
            features = await clip_service.extract_features(result_path)
            
            # Store results
            key = image_file.stem
            embeddings[key] = embedding
            features_list[key] = features
            processed_paths[key] = result_path
            
            print(f"  ✓ Color: {features['dominant_color']}, Pattern: {features['pattern_type']}")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    if not embeddings:
        print("\n❌ No images were successfully processed")
        sys.exit(1)
    
    print()
    print(f"✓ Successfully processed {len(embeddings)}/{len(image_files)} images")
    print()
    
    # Save embeddings
    print("Saving results...")
    print("-" * 60)
    
    # Save embeddings as numpy archive
    np.savez_compressed(
        output_file,
        **{k: v for k, v in embeddings.items()}
    )
    print(f"✓ Embeddings saved to: {output_file}")
    
    # Save features as JSON
    features_file = output_file.with_suffix('.json')
    with open(features_file, 'w') as f:
        json.dump({
            'features': features_list,
            'processed_paths': processed_paths,
            'count': len(embeddings)
        }, f, indent=2)
    print(f"✓ Features saved to: {features_file}")
    
    # Calculate similarity matrix
    print()
    print("Calculating similarity matrix...")
    print("-" * 60)
    
    names = list(embeddings.keys())
    n = len(names)
    similarity_matrix = np.zeros((n, n))
    
    for i in range(n):
        for j in range(n):
            if i == j:
                similarity_matrix[i, j] = 1.0
            elif i < j:
                sim = clip_service.calculate_similarity(
                    embeddings[names[i]],
                    embeddings[names[j]]
                )
                similarity_matrix[i, j] = sim
                similarity_matrix[j, i] = sim
    
    # Save similarity matrix
    similarity_file = output_file.parent / f"{output_file.stem}_similarity.npz"
    np.savez_compressed(
        similarity_file,
        matrix=similarity_matrix,
        names=names
    )
    print(f"✓ Similarity matrix saved to: {similarity_file}")
    
    # Find best matches
    print()
    print("🔍 Top 5 Most Similar Pairs:")
    print("-" * 60)
    
    pairs = []
    for i in range(n):
        for j in range(i + 1, n):
            pairs.append((i, j, similarity_matrix[i, j]))
    
    pairs.sort(key=lambda x: x[2], reverse=True)
    
    for i, j, sim in pairs[:5]:
        print(f"  {names[i]} ↔ {names[j]}: {sim:.2%}")
    
    if len(pairs) > 5:
        print()
        print("🔍 Top 5 Least Similar Pairs:")
        print("-" * 60)
        
        for i, j, sim in pairs[-5:]:
            print(f"  {names[i]} ↔ {names[j]}: {sim:.2%}")
    
    print()
    print("=" * 60)
    print("✓ Batch processing complete!")
    print("=" * 60)
    print(f"\nOutput files:")
    print(f"  - Embeddings: {output_file}")
    print(f"  - Features: {features_file}")
    print(f"  - Similarity matrix: {similarity_file}")
    print(f"  - Processed images: {processed_dir}/")


async def main():
    if len(sys.argv) < 2:
        print("Usage: python batch_process.py <input_dir> [output_file]")
        print("\nExample:")
        print("  python batch_process.py ./sock_images")
        print("  python batch_process.py ./sock_images embeddings.npz")
        sys.exit(1)
    
    input_dir = Path(sys.argv[1])
    
    if not input_dir.exists():
        print(f"❌ Directory not found: {input_dir}")
        sys.exit(1)
    
    if not input_dir.is_dir():
        print(f"❌ Not a directory: {input_dir}")
        sys.exit(1)
    
    # Output file
    if len(sys.argv) >= 3:
        output_file = Path(sys.argv[2])
    else:
        output_file = Path("output") / "embeddings.npz"
    
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    print("="*60)
    print("📦 Batch Processing Tool")
    print("="*60)
    print(f"\nInput directory: {input_dir}")
    print(f"Output file: {output_file}")
    print()
    
    await process_directory(input_dir, output_file)


if __name__ == "__main__":
    asyncio.run(main())
