"""
Classifier service for AI visual defect detection.
Uses the frozen logistic regression model and reference preprocessing.
"""
from pathlib import Path
from typing import Dict, Any
from apps.inspections.cv_model.inference import predict, MODEL_VERSION, CLASS_NAMES

MODEL_PATH = Path(__file__).resolve().parent.parent / "cv_model" / "classifier.npz"

class ClassifierService:
    @staticmethod
    def run_inference(image_path: str) -> Dict[str, Any]:
        """
        Executes inference on the given image path.
        Returns:
            predicted_class: "Normal" | "Defective"
            confidence: float (0.0 - 1.0)
            defect_probability: float (0.0 - 1.0)
            model_version: "BIT-PLATE-CV-1.0"
        """
        result = predict(image_path, model_path=str(MODEL_PATH))
        return {
            "predicted_class": result["predicted_class"],
            "confidence": round(float(result["confidence"]), 4),
            "defect_probability": round(float(result["defect_probability"]), 4),
            "model_version": result.get("model_version", MODEL_VERSION),
        }

