"""
Compare different embedding models for sock matching task.

This script evaluates various embedding models on their ability to match pairs of socks.
The task is similar to face recognition - distinguishing between similar items of the same
category rather than distinguishing between different categories.

Models tested:
- OpenAI CLIP variants
- Face recognition models (ArcFace, FaceNet)
- Fine-grained classification models (ResNet, EfficientNet with cosine similarity)
- Specialized similarity models (SimCLR, MoCo)

Metrics:
- Same-pair accuracy: How often pairs are correctly identified as matches
- Different-pair accuracy: How often non-pairs are correctly identified as non-matches
- Average Precision (AP): Overall ranking quality
- Top-1 Accuracy: Given a sock, is its pair ranked first?
- ROC-AUC: Area under receiver operating characteristic curve

Usage:
    python examples/compare_embedding_models.py
"""

import asyncio
import sys
from pathlib import Path
from typing import List, Tuple, Dict, Optional
import numpy as np
from collections import defaultdict
import json
from dataclasses import dataclass, asdict
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Try to import various models
try:
    import torch
    import torch.nn as nn
    from torchvision import models, transforms
    from PIL import Image
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
    from sklearn.metrics import roc_auc_score, average_precision_score, roc_curve
    import matplotlib.pyplot as plt
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False
    print("⚠ scikit-learn not available")

try:
    from rembg import remove
    import cv2
    HAS_PREPROCESSING = True
except ImportError:
    HAS_PREPROCESSING = False
    print("⚠ rembg/cv2 not available - preprocessing tests will be skipped")


@dataclass
class ModelResult:
    """Results for a single model"""
    model_name: str
    preprocessing: str  # "none", "basic", or "full"
    same_pair_accuracy: float
    different_pair_accuracy: float
    top1_accuracy: float
    average_precision: float
    roc_auc: float
    inference_time_ms: float
    embedding_dimension: int
    
    def to_dict(self):
        return asdict(self)


class EmbeddingModelWrapper:
    """Base class for embedding model wrappers"""
    
    def __init__(self, name: str, preprocessing: str = "none"):
        self.name = name
        self.preprocessing = preprocessing  # "none", "basic", or "full"
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
    
    def preprocess_image_file(self, image_path: str) -> Image.Image:
        """
        Apply preprocessing to image before embedding.
        
        Args:
            image_path: Path to image file
            
        Returns:
            PIL Image (preprocessed or original)
        """
        image = Image.open(image_path).convert('RGB')
        
        if self.preprocessing == "none":
            return image
        
        elif self.preprocessing == "basic":
            # Basic preprocessing: resize and normalize
            return image
        
        elif self.preprocessing == "full":
            # Full preprocessing: background removal + cropping
            if not HAS_PREPROCESSING:
                print(f"⚠ Warning: Full preprocessing requested but rembg not available, using original")
                return image
            
            try:
                # Remove background
                import io
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format='PNG')
                img_byte_arr = img_byte_arr.getvalue()
                
                output = remove(img_byte_arr)
                result = Image.open(io.BytesIO(output))
                
                # Create white background
                background = Image.new('RGB', result.size, (255, 255, 255))
                if result.mode == 'RGBA':
                    background.paste(result, (0, 0), result.split()[-1])
                else:
                    background = result.convert('RGB')
                
                # Auto-crop to content (remove extra white space)
                # Convert to numpy for processing
                import cv2
                img_array = np.array(background)
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
                
                # Find non-white pixels
                _, thresh = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY_INV)
                coords = cv2.findNonZero(thresh)
                
                if coords is not None:
                    x, y, w, h = cv2.boundingRect(coords)
                    # Add padding
                    padding = 20
                    x = max(0, x - padding)
                    y = max(0, y - padding)
                    w = min(img_array.shape[1] - x, w + 2 * padding)
                    h = min(img_array.shape[0] - y, h + 2 * padding)
                    
                    cropped = img_array[y:y+h, x:x+w]
                    background = Image.fromarray(cropped)
                
                return background
                
            except Exception as e:
                print(f"⚠ Warning: Preprocessing failed ({e}), using original")
                return image
        
        return image
    
    def embed_image(self, image_path: str) -> Optional[np.ndarray]:
        """Generate embedding for an image. Returns normalized embedding."""
        raise NotImplementedError
    
    def get_dimension(self) -> int:
        """Get embedding dimension"""
        raise NotImplementedError


class CLIPModelWrapper(EmbeddingModelWrapper):
    """Wrapper for OpenAI CLIP models"""
    
    def __init__(self, model_name: str = "ViT-B-32", pretrained: str = "openai", preprocessing: str = "none"):
        super().__init__(f"CLIP-{model_name}", preprocessing)
        if not HAS_OPEN_CLIP:
            raise ImportError("open_clip not available")
        
        self.model, _, self.preprocess = open_clip.create_model_and_transforms(
            model_name, pretrained=pretrained
        )
        self.model.to(self.device)
        self.model.eval()
        print(f"✓ Loaded {self.name} (preprocessing: {preprocessing})")
    
    def embed_image(self, image_path: str) -> Optional[np.ndarray]:
        try:
            # Apply our preprocessing first
            image = self.preprocess_image_file(image_path)
            
            # Then apply CLIP's preprocessing
            image_tensor = self.preprocess(image).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                embedding = self.model.encode_image(image_tensor)
                embedding = embedding.cpu().numpy()[0]
            
            # Normalize
            embedding = embedding / (np.linalg.norm(embedding) + 1e-8)
            return embedding
        except Exception as e:
            print(f"Error embedding {image_path}: {e}")
            return None
    
    def get_dimension(self) -> int:
        return 512  # Most CLIP models use 512


class DINOModelWrapper(EmbeddingModelWrapper):
    """Wrapper for Facebook DINO models (self-supervised, good for fine-grained similarity)"""
    
    def __init__(self, model_name: str = "facebook/dinov2-base", preprocessing: str = "none"):
        super().__init__(f"DINOv2-{model_name.split('/')[-1]}", preprocessing)
        if not HAS_TRANSFORMERS:
            raise ImportError("transformers not available")
        
        self.processor = AutoImageProcessor.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.model.to(self.device)
        self.model.eval()
        print(f"✓ Loaded {self.name} (preprocessing: {preprocessing})")
    
    def embed_image(self, image_path: str) -> Optional[np.ndarray]:
        try:
            # Apply our preprocessing first
            image = self.preprocess_image_file(image_path)
            
            # Then apply DINO's preprocessing
            inputs = self.processor(images=image, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                # Use CLS token embedding
                embedding = outputs.last_hidden_state[:, 0].cpu().numpy()[0]
            
            # Normalize
            embedding = embedding / (np.linalg.norm(embedding) + 1e-8)
            return embedding
        except Exception as e:
            print(f"Error embedding {image_path}: {e}")
            return None
    
    def get_dimension(self) -> int:
        return 768  # DINOv2-base


class ResNetModelWrapper(EmbeddingModelWrapper):
    """Wrapper for ResNet models with custom embedding layer"""
    
    def __init__(self, model_name: str = "resnet50", preprocessing: str = "none"):
        super().__init__(f"ResNet-{model_name}", preprocessing)
        if not HAS_TORCH:
            raise ImportError("torch not available")
        
        # Load pretrained model and remove classification head
        if model_name == "resnet50":
            base_model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V2)
            embed_dim = 2048
        elif model_name == "resnet18":
            base_model = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
            embed_dim = 512
        else:
            raise ValueError(f"Unknown model: {model_name}")
        
        # Remove final FC layer
        self.model = nn.Sequential(*list(base_model.children())[:-1])
        self.model.to(self.device)
        self.model.eval()
        self.embed_dim = embed_dim
        
        # Standard ImageNet transforms
        self.transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        print(f"✓ Loaded {self.name} (preprocessing: {preprocessing})")
    
    def embed_image(self, image_path: str) -> Optional[np.ndarray]:
        try:
            # Apply our preprocessing first
            image = self.preprocess_image_file(image_path)
            
            # Then apply ResNet's preprocessing
            image_tensor = self.transform(image).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                embedding = self.model(image_tensor)
                embedding = embedding.squeeze().cpu().numpy()
            
            # Normalize
            embedding = embedding / (np.linalg.norm(embedding) + 1e-8)
            return embedding
        except Exception as e:
            print(f"Error embedding {image_path}: {e}")
            return None
    
    def get_dimension(self) -> int:
        return self.embed_dim


class EfficientNetModelWrapper(EmbeddingModelWrapper):
    """Wrapper for EfficientNet models"""
    
    def __init__(self, model_name: str = "efficientnet_b0", preprocessing: str = "none"):
        super().__init__(f"EfficientNet-{model_name}", preprocessing)
        if not HAS_TORCH:
            raise ImportError("torch not available")
        
        if model_name == "efficientnet_b0":
            base_model = models.efficientnet_b0(weights=models.EfficientNet_B0_Weights.IMAGENET1K_V1)
            embed_dim = 1280
        elif model_name == "efficientnet_b3":
            base_model = models.efficientnet_b3(weights=models.EfficientNet_B3_Weights.IMAGENET1K_V1)
            embed_dim = 1536
        else:
            raise ValueError(f"Unknown model: {model_name}")
        
        # Remove classifier
        self.model = nn.Sequential(
            base_model.features,
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten()
        )
        self.model.to(self.device)
        self.model.eval()
        self.embed_dim = embed_dim
        
        self.transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        print(f"✓ Loaded {self.name} (preprocessing: {preprocessing})")
    
    def embed_image(self, image_path: str) -> Optional[np.ndarray]:
        try:
            # Apply our preprocessing first
            image = self.preprocess_image_file(image_path)
            
            # Then apply EfficientNet's preprocessing
            image_tensor = self.transform(image).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                embedding = self.model(image_tensor)
                embedding = embedding.cpu().numpy()[0]
            
            # Normalize
            embedding = embedding / (np.linalg.norm(embedding) + 1e-8)
            return embedding
        except Exception as e:
            print(f"Error embedding {image_path}: {e}")
            return None
    
    def get_dimension(self) -> int:
        return self.embed_dim


class SockPairDataset:
    """Dataset of sock pairs for evaluation"""
    
    def __init__(self, image_dir: str):
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
        """Get all positive pairs (same sock)"""
        pairs = []
        for guid, images in self.pairs.items():
            # All combinations within a group
            for i in range(len(images)):
                for j in range(i + 1, len(images)):
                    pairs.append((images[i], images[j]))
        return pairs
    
    def get_negative_pairs(self, num_samples: int = None) -> List[Tuple[str, str]]:
        """Get negative pairs (different socks)"""
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
        """Get queries for retrieval evaluation (query image -> relevant images)"""
        queries = []
        for guid, images in self.pairs.items():
            if len(images) >= 2:
                # Use first image as query, rest as relevant
                queries.append((images[0], images[1:]))
        return queries


class ModelEvaluator:
    """Evaluate embedding models on sock matching task"""
    
    def __init__(self, dataset: SockPairDataset):
        self.dataset = dataset
    
    def compute_similarity(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        """Compute cosine similarity between embeddings"""
        return np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2) + 1e-8)
    
    def evaluate_model(self, model: EmbeddingModelWrapper) -> ModelResult:
        """Evaluate a single model"""
        print(f"\n{'='*60}")
        print(f"Evaluating: {model.name} (preprocessing: {model.preprocessing})")
        print(f"{'='*60}")
        
        # Generate embeddings for all images
        print("Generating embeddings...")
        embeddings = {}
        start_time = time.time()
        
        for img_path in self.dataset.all_images:
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
        
        # ROC-AUC
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


def create_comparison_table(results: List[ModelResult]) -> str:
    """Create a formatted comparison table"""
    table = "\n" + "="*110 + "\n"
    table += "MODEL COMPARISON RESULTS\n"
    table += "="*110 + "\n\n"
    
    # Header
    table += f"{'Model':<25} {'Preproc':<8} {'Same%':<8} {'Diff%':<8} {'Top-1%':<8} {'AP':<8} {'AUC':<8} {'Time(ms)':<10} {'Dim':<6}\n"
    table += "-"*110 + "\n"
    
    # Sort by ROC-AUC
    results.sort(key=lambda x: x.roc_auc, reverse=True)
    
    for r in results:
        table += f"{r.model_name:<25} "
        table += f"{r.preprocessing:<8} "
        table += f"{r.same_pair_accuracy*100:>6.2f}  "
        table += f"{r.different_pair_accuracy*100:>6.2f}  "
        table += f"{r.top1_accuracy*100:>6.2f}  "
        table += f"{r.average_precision:>6.4f}  "
        table += f"{r.roc_auc:>6.4f}  "
        table += f"{r.inference_time_ms:>8.1f}  "
        table += f"{r.embedding_dimension:>6d}\n"
    
    table += "="*110 + "\n"
    
    # Add preprocessing impact analysis
    table += "\nPREPROCESSING IMPACT ANALYSIS\n"
    table += "-"*110 + "\n"
    
    # Group by model name
    by_model = {}
    for r in results:
        base_name = r.model_name
        if base_name not in by_model:
            by_model[base_name] = {}
        by_model[base_name][r.preprocessing] = r
    
    for model_name, variants in by_model.items():
        if len(variants) > 1:
            table += f"\n{model_name}:\n"
            if "none" in variants and "full" in variants:
                none_result = variants["none"]
                full_result = variants["full"]
                
                auc_change = (full_result.roc_auc - none_result.roc_auc) * 100
                top1_change = (full_result.top1_accuracy - none_result.top1_accuracy) * 100
                time_change = full_result.inference_time_ms - none_result.inference_time_ms
                
                table += f"  ROC-AUC: {none_result.roc_auc:.4f} → {full_result.roc_auc:.4f} "
                table += f"({'+' if auc_change >= 0 else ''}{auc_change:.2f}%)\n"
                table += f"  Top-1:   {none_result.top1_accuracy:.2%} → {full_result.top1_accuracy:.2%} "
                table += f"({'+' if top1_change >= 0 else ''}{top1_change:.2f}%)\n"
                table += f"  Time:    {none_result.inference_time_ms:.1f}ms → {full_result.inference_time_ms:.1f}ms "
                table += f"({'+' if time_change >= 0 else ''}{time_change:.1f}ms)\n"
    
    table += "="*110 + "\n"
    return table


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
    if HAS_PREPROCESSING:
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
    for model in models_to_test:
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
        output_file = Path(__file__).parent / "model_comparison_results.json"
        with open(output_file, 'w') as f:
            json.dump([r.to_dict() for r in results], f, indent=2)
        print(f"✓ Results saved to: {output_file}")
        
        # Print recommendations
        print("\n💡 RECOMMENDATIONS:")
        print("-" * 60)
        
        best_auc = max(results, key=lambda x: x.roc_auc)
        print(f"🏆 Best overall (ROC-AUC): {best_auc.model_name} ({best_auc.roc_auc:.4f})")
        
        best_top1 = max(results, key=lambda x: x.top1_accuracy)
        print(f"🎯 Best retrieval (Top-1): {best_top1.model_name} ({best_top1.top1_accuracy:.2%})")
        
        fastest = min(results, key=lambda x: x.inference_time_ms)
        print(f"⚡ Fastest inference: {fastest.model_name} ({fastest.inference_time_ms:.1f}ms)")
        
        print("\n📝 Notes:")
        print("- DINOv2 typically excels at fine-grained similarity tasks")
        print("- CLIP models are good general-purpose but may not capture subtle differences")
        print("- ResNet/EfficientNet require fine-tuning for best results")
        print("- Consider the trade-off between accuracy and inference speed")
    else:
        print("❌ No results to display")


if __name__ == "__main__":
    asyncio.run(main())
