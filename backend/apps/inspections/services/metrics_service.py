"""
Evaluation and metrics service for Round 2 benchmarks.
Calculates 2x2 confusion matrix, accuracy, precision, and defect recall on the 60 sample dataset.
"""
import csv
from pathlib import Path
from typing import Dict, Any, List
from django.conf import settings
from apps.inspections.services.classifier_service import ClassifierService

BASE_DIR = Path(settings.BASE_DIR)
LABELS_PATH = BASE_DIR / "data" / "Round2" / "Samples" / "labels.csv"
SAMPLES_DIR = BASE_DIR / "data" / "Round2" / "Samples"

class MetricsService:
    @staticmethod
    def evaluate_benchmark_samples() -> Dict[str, Any]:
        """
        Runs the frozen classifier over all 60 labeled sample images.
        Computes TP, FP, TN, FN, Defect Recall, Precision, and Accuracy.
        """
        if not LABELS_PATH.exists():
            return {
                "error": f"Labels file not found at {LABELS_PATH}",
                "total_samples": 0,
            }

        tp = 0  # Actual Defective, Predicted Defective
        fn = 0  # Actual Defective, Predicted Normal
        fp = 0  # Actual Normal, Predicted Defective
        tn = 0  # Actual Normal, Predicted Normal

        samples_evaluated: List[Dict[str, Any]] = []

        with open(LABELS_PATH, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                img_path = SAMPLES_DIR / row["relative_path"]
                actual = row["label"]
                image_id = row.get("image_id", "")
                product_id = row.get("product_id", "P-PLATE01")

                if not img_path.exists():
                    samples_evaluated.append({
                        "image_id": image_id,
                        "product_id": product_id,
                        "actual_label": actual,
                        "predicted_class": "FILE_NOT_FOUND",
                        "confidence": 0.0,
                        "status": "FAILED",
                    })
                    continue

                res = ClassifierService.run_inference(str(img_path))
                pred = res["predicted_class"]
                conf = res["confidence"]
                prob = res["defect_probability"]

                if actual == "Defective" and pred == "Defective":
                    tp += 1
                elif actual == "Defective" and pred == "Normal":
                    fn += 1
                elif actual == "Normal" and pred == "Defective":
                    fp += 1
                elif actual == "Normal" and pred == "Normal":
                    tn += 1

                samples_evaluated.append({
                    "image_id": image_id,
                    "product_id": product_id,
                    "relative_path": row["relative_path"],
                    "actual_label": actual,
                    "predicted_class": pred,
                    "confidence": conf,
                    "defect_probability": prob,
                    "is_correct": (actual == pred),
                })

        total = tp + fp + tn + fn
        recall = round(tp / (tp + fn), 4) if (tp + fn) > 0 else 0.0
        precision = round(tp / (tp + fp), 4) if (tp + fp) > 0 else 0.0
        accuracy = round((tp + tn) / total, 4) if total > 0 else 0.0

        return {
            "total_samples": total,
            "metrics": {
                "true_positives": tp,
                "false_positives": fp,
                "true_negatives": tn,
                "false_negatives": fn,
                "defect_recall": recall,
                "defect_recall_percent": round(recall * 100, 1),
                "precision": precision,
                "precision_percent": round(precision * 100, 1),
                "accuracy": accuracy,
                "accuracy_percent": round(accuracy * 100, 1),
            },
            "confusion_matrix": {
                "rows": ["Actual Normal", "Actual Defective"],
                "columns": ["Predicted Normal", "Predicted Defective"],
                "values": [
                    [tn, fp],  # Actual Normal
                    [fn, tp],  # Actual Defective
                ],
            },
            "samples": samples_evaluated,
            "model_version": "BIT-PLATE-CV-1.0",
        }

