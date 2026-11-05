"""
backend/services/model_service.py - Thin wrapper around Model/inference.py
Strictly preserves Model contract: imports and calls predict(path) unchanged.
"""

import sys
from pathlib import Path
from django.conf import settings

# Ensure Model package is discoverable
MODEL_DIR = Path(getattr(settings, 'MODEL_DIR', settings.BASE_DIR / 'Model'))
PARENT_DIR = MODEL_DIR.parent
if str(PARENT_DIR) not in sys.path:
    sys.path.insert(0, str(PARENT_DIR))

try:
    from Model.inference import predict as model_predict, MODEL_VERSION
except ImportError:
    # Fallback to direct import if Model is in sys.path
    from inference import predict as model_predict, MODEL_VERSION


def predict_plate(image_path):
    """
    Runs authoritative model inference on the given image path.
    
    Args:
        image_path (str or Path): Path to validated metal plate image.
        
    Returns:
        dict: {
            'predicted_class': int (0 for Normal, 1 for Defective),
            'confidence': float (0.0 to 1.0),
            'defect_probability': float (0.0 to 1.0),
            'model_version': str ('BIT-PLATE-CV-1.0')
        }
    """
    predicted_class, confidence, defect_probability, version = model_predict(str(image_path))
    
    return {
        'predicted_class': int(predicted_class),
        'confidence': float(confidence),
        'defect_probability': float(defect_probability),
        'model_version': str(version)
    }

