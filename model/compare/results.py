"""
Result formatting and comparison utilities.
"""

from dataclasses import dataclass, asdict
from typing import List, Dict


@dataclass
class ModelResult:
    """Results for a single model evaluation"""
    model_name: str
    preprocessing: str  # "none", "basic", or "full"
    same_pair_accuracy: float
    different_pair_accuracy: float
    top1_accuracy: float
    average_precision: float
    roc_auc: float
    inference_time_ms: float
    embedding_dimension: int
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)


def create_comparison_table(results: List[ModelResult]) -> str:
    """
    Create a formatted comparison table from results.
    
    Args:
        results: List of ModelResult objects
        
    Returns:
        Formatted string table
    """
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


def print_recommendations(results: List[ModelResult]):
    """
    Print recommendations based on evaluation results.
    
    Args:
        results: List of ModelResult objects
    """
    if not results:
        print("❌ No results to analyze")
        return
    
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
