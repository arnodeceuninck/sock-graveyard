"""
Model evaluation logic for sock matching task.
"""

import time
import numpy as np
from typing import Dict

from .dataset import SockPairDataset
from .model_wrappers import EmbeddingModelWrapper
from .results import ModelResult

# Check for optional dependencies
try:
    from sklearn.metrics import roc_auc_score, average_precision_score
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False


class ModelEvaluator:
    """Evaluate embedding models on sock matching task"""
    
    def __init__(self, dataset: SockPairDataset):
        """
        Initialize evaluator with a dataset.
        
        Args:
            dataset: SockPairDataset containing sock images
        """
        self.dataset = dataset
    
    def compute_similarity(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        """
        Compute cosine similarity between embeddings.
        
        Args:
            emb1: First embedding vector
            emb2: Second embedding vector
            
        Returns:
            Cosine similarity score between -1 and 1
        """
        return np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2) + 1e-8)
    
    def evaluate_model(self, model: EmbeddingModelWrapper) -> ModelResult:
        """
        Evaluate a single model on all metrics.
        
        Metrics computed:
        - Same-pair accuracy: Correct identification of matching socks
        - Different-pair accuracy: Correct identification of non-matching socks
        - Top-1 accuracy: Given a query sock, is its pair ranked first?
        - Average Precision: Overall ranking quality
        - ROC-AUC: Area under receiver operating characteristic curve
        
        Args:
            model: Model wrapper to evaluate
            
        Returns:
            ModelResult containing all metrics
        """
        print(f"\n{'='*60}")
        print(f"Evaluating: {model.name} (preprocessing: {model.preprocessing})")
        print(f"{'='*60}")
        
        # Generate embeddings for all images
        print("Generating embeddings...")
        embeddings = {}
        start_time = time.time()
        
        # Use tqdm if available for progress bar
        if HAS_TQDM:
            image_iterator = tqdm(self.dataset.all_images, desc="Embedding images", unit="img")
        else:
            image_iterator = self.dataset.all_images
        
        for img_path in image_iterator:
            emb = model.embed_image(img_path)
            if emb is not None:
                embeddings[img_path] = emb
        
        total_time = time.time() - start_time
        avg_time_ms = (total_time / len(embeddings)) * 1000 if embeddings else 0
        
        print(f"✓ Generated {len(embeddings)} embeddings in {total_time:.2f}s")
        print(f"  Average: {avg_time_ms:.2f}ms per image")
        
        if len(embeddings) < len(self.dataset.all_images):
            print(f"⚠ Warning: Failed to embed {len(self.dataset.all_images) - len(embeddings)} images")
        
        # Evaluate on positive pairs
        positive_pairs = self.dataset.get_positive_pairs()
        positive_sims = []
        for img1, img2 in positive_pairs:
            if img1 in embeddings and img2 in embeddings:
                sim = self.compute_similarity(embeddings[img1], embeddings[img2])
                positive_sims.append(sim)
        
        # Evaluate on negative pairs
        negative_pairs = self.dataset.get_negative_pairs()
        negative_sims = []
        for img1, img2 in negative_pairs:
            if img1 in embeddings and img2 in embeddings:
                sim = self.compute_similarity(embeddings[img1], embeddings[img2])
                negative_sims.append(sim)
        
        print(f"\nSimilarity scores:")
        print(f"  Positive pairs (same sock): {np.mean(positive_sims):.4f} ± {np.std(positive_sims):.4f}")
        print(f"  Negative pairs (different): {np.mean(negative_sims):.4f} ± {np.std(negative_sims):.4f}")
        
        # Find optimal threshold
        all_sims = positive_sims + negative_sims
        all_labels = [1] * len(positive_sims) + [0] * len(negative_sims)
        
        # Try different thresholds
        best_threshold = 0.5
        best_accuracy = 0
        for threshold in np.linspace(min(all_sims), max(all_sims), 100):
            predictions = [1 if s >= threshold else 0 for s in all_sims]
            accuracy = sum(p == l for p, l in zip(predictions, all_labels)) / len(all_labels)
            if accuracy > best_accuracy:
                best_accuracy = accuracy
                best_threshold = threshold
        
        print(f"  Optimal threshold: {best_threshold:.4f} (accuracy: {best_accuracy:.4f})")
        
        # Compute metrics with optimal threshold
        same_pair_correct = sum(1 for s in positive_sims if s >= best_threshold)
        same_pair_accuracy = same_pair_correct / len(positive_sims) if positive_sims else 0
        
        diff_pair_correct = sum(1 for s in negative_sims if s < best_threshold)
        diff_pair_accuracy = diff_pair_correct / len(negative_sims) if negative_sims else 0
        
        # ROC-AUC and Average Precision
        if HAS_SKLEARN and len(all_sims) > 0:
            roc_auc = roc_auc_score(all_labels, all_sims)
            avg_precision = average_precision_score(all_labels, all_sims)
        else:
            roc_auc = 0.0
            avg_precision = 0.0
        
        # Top-1 retrieval accuracy
        queries = self.dataset.get_retrieval_queries()
        top1_correct = 0
        for query_img, relevant_imgs in queries:
            if query_img not in embeddings:
                continue
            
            query_emb = embeddings[query_img]
            
            # Compute similarities to all other images
            similarities = []
            for img_path in self.dataset.all_images:
                if img_path != query_img and img_path in embeddings:
                    sim = self.compute_similarity(query_emb, embeddings[img_path])
                    similarities.append((img_path, sim))
            
            # Sort by similarity
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            # Check if top-1 is relevant
            if similarities and similarities[0][0] in relevant_imgs:
                top1_correct += 1
        
        top1_accuracy = top1_correct / len(queries) if queries else 0
        
        # Print results
        print(f"\n📊 Results:")
        print(f"  Same-pair accuracy:      {same_pair_accuracy:.2%}")
        print(f"  Different-pair accuracy: {diff_pair_accuracy:.2%}")
        print(f"  Top-1 accuracy:          {top1_accuracy:.2%}")
        print(f"  Average Precision:       {avg_precision:.4f}")
        print(f"  ROC-AUC:                 {roc_auc:.4f}")
        
        return ModelResult(
            model_name=model.name,
            preprocessing=model.preprocessing,
            same_pair_accuracy=same_pair_accuracy,
            different_pair_accuracy=diff_pair_accuracy,
            top1_accuracy=top1_accuracy,
            average_precision=avg_precision,
            roc_auc=roc_auc,
            inference_time_ms=avg_time_ms,
            embedding_dimension=model.get_dimension()
        )
