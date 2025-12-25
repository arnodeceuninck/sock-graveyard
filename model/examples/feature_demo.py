"""
Feature extraction demo

Shows all the visual features that can be extracted from sock images.

Usage:
    python examples/feature_demo.py <image_path>
"""

import asyncio
import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from sock_matcher import CLIPEmbeddingService, ImagePreprocessor


async def main():
    if len(sys.argv) < 2:
        print("Usage: python feature_demo.py <image_path>")
        print("\nExample:")
        print("  python feature_demo.py my_sock.jpg")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    if not Path(image_path).exists():
        print(f"❌ File not found: {image_path}")
        sys.exit(1)
    
    print("="*60)
    print("🎨 Feature Extraction Demo")
    print("="*60)
    print(f"\nImage: {image_path}")
    print()
    
    # Initialize services
    preprocessor = ImagePreprocessor()
    clip_service = CLIPEmbeddingService()
    
    print(f"✓ Using device: {clip_service.device}")
    print()
    
    # Preprocess image
    print("Step 1: Preprocessing...")
    print("-" * 60)
    
    with open(image_path, 'rb') as f:
        image_bytes = f.read()
    
    output_path = "output/demo_processed.jpg"
    Path("output").mkdir(exist_ok=True)
    
    processed_path, error = await preprocessor.preprocess_image(
        image_bytes,
        output_path
    )
    
    if error:
        print(f"❌ Preprocessing failed: {error}")
        sys.exit(1)
    
    print(f"✓ Processed image saved to: {processed_path}")
    print()
    
    # Generate embedding
    print("Step 2: Generating CLIP Embedding...")
    print("-" * 60)
    
    embedding = await clip_service.generate_embedding(processed_path)
    
    if embedding is None:
        print("❌ Embedding generation failed")
        sys.exit(1)
    
    print(f"✓ Embedding shape: {embedding.shape}")
    print(f"✓ Embedding range: [{embedding.min():.4f}, {embedding.max():.4f}]")
    print(f"✓ Embedding norm: {(embedding**2).sum()**0.5:.4f}")
    print()
    
    # Extract features
    print("Step 3: Extracting Visual Features...")
    print("-" * 60)
    
    features = await clip_service.extract_features(processed_path)
    
    print("\n🎨 COLOR FEATURES")
    print(f"  Dominant Color: {features['dominant_color']}")
    print(f"  → RGB: {hex_to_rgb(features['dominant_color'])}")
    print(f"  → Preview: {color_preview(features['dominant_color'])}")
    
    print("\n📐 PATTERN FEATURES")
    print(f"  Pattern Type: {features['pattern_type']}")
    pattern_descriptions = {
        'solid': 'Uniform color with minimal variation',
        'striped': 'Regular repeating pattern (stripes)',
        'textured': 'Irregular texture or small patterns',
        'complex': 'Complex patterns or multiple designs',
        'unknown': 'Could not determine pattern'
    }
    if features['pattern_type'] in pattern_descriptions:
        print(f"  → {pattern_descriptions[features['pattern_type']]}")
    
    print("\n🔬 TEXTURE FEATURES")
    texture_data = json.loads(features['texture_features'])
    if texture_data:
        print(f"  Mean Intensity: {texture_data.get('mean_intensity', 'N/A'):.2f}")
        print(f"  Std Intensity: {texture_data.get('std_intensity', 'N/A'):.2f}")
        print(f"  Mean Gradient: {texture_data.get('mean_gradient', 'N/A'):.2f}")
        if 'lbp_histogram' in texture_data:
            print(f"  LBP Features: {len(texture_data['lbp_histogram'])} bins")
    
    # Save features to JSON
    output_json = "output/demo_features.json"
    with open(output_json, 'w') as f:
        json.dump({
            'image': image_path,
            'embedding_shape': embedding.shape,
            'features': features
        }, f, indent=2)
    
    print(f"\n💾 Features saved to: {output_json}")
    print("\n✓ Done!")


def hex_to_rgb(hex_color: str) -> tuple:
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def color_preview(hex_color: str) -> str:
    """Generate a text preview of a color"""
    r, g, b = hex_to_rgb(hex_color)
    
    # Use ANSI color codes to show the color (if terminal supports it)
    try:
        return f"\033[48;2;{r};{g};{b}m  \033[0m {hex_color}"
    except:
        return hex_color


if __name__ == "__main__":
    asyncio.run(main())
