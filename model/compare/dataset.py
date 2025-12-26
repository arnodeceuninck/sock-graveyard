"""
Dataset handling for sock pair matching evaluation.
"""

from pathlib import Path
from typing import List, Tuple, Dict
from collections import defaultdict


class SockPairDataset:
    """Dataset of sock pairs for evaluation"""
    
    def __init__(self, image_dir: str):
        """
        Initialize dataset from directory of sock images.
        
        Images should be named: sock-{guid}-{index}.jpg
        where guid identifies the sock and index (0, 1, 2...) identifies different views.
        
        Args:
            image_dir: Directory containing sock images
        """
        self.image_dir = Path(image_dir)
        self.pairs = defaultdict(list)  # guid -> list of image paths
        self.all_images = []
        
        # Scan directory for sock images
        for img_path in sorted(self.image_dir.glob("sock-*-*.jpg")):
            # Extract GUID (e.g., "sock-156ee92b-0.jpg" -> "156ee92b")
            parts = img_path.stem.split('-')
            if len(parts) >= 3:
                guid = parts[1]
                self.pairs[guid].append(str(img_path))
                self.all_images.append(str(img_path))
        
        # Filter to only pairs (2+ images with same GUID)
        self.pairs = {k: v for k, v in self.pairs.items() if len(v) >= 2}
        
        print(f"Found {len(self.pairs)} sock pairs:")
        for guid, images in self.pairs.items():
            print(f"  {guid}: {len(images)} images")
        print(f"Total images: {len(self.all_images)}")
    
    def get_positive_pairs(self) -> List[Tuple[str, str]]:
        """
        Get all positive pairs (same sock).
        
        Returns:
            List of (image_path1, image_path2) tuples for matching socks
        """
        pairs = []
        for guid, images in self.pairs.items():
            # All combinations within a group
            for i in range(len(images)):
                for j in range(i + 1, len(images)):
                    pairs.append((images[i], images[j]))
        return pairs
    
    def get_negative_pairs(self, num_samples: int = None) -> List[Tuple[str, str]]:
        """
        Get negative pairs (different socks).
        
        Args:
            num_samples: Maximum number of pairs to return (None = all)
            
        Returns:
            List of (image_path1, image_path2) tuples for non-matching socks
        """
        pairs = []
        guids = list(self.pairs.keys())
        
        # Sample pairs from different GUIDs
        for i, guid1 in enumerate(guids):
            for guid2 in guids[i+1:]:
                # Take one image from each GUID
                pairs.append((self.pairs[guid1][0], self.pairs[guid2][0]))
        
        if num_samples and len(pairs) > num_samples:
            import random
            pairs = random.sample(pairs, num_samples)
        
        return pairs
    
    def get_retrieval_queries(self) -> List[Tuple[str, List[str]]]:
        """
        Get queries for retrieval evaluation.
        
        Returns:
            List of (query_image, relevant_images) tuples
        """
        queries = []
        for guid, images in self.pairs.items():
            if len(images) >= 2:
                # Use first image as query, rest as relevant
                queries.append((images[0], images[1:]))
        return queries
