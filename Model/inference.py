"""
Model/inference.py - AUTHORITATIVE inference module for BIT-PLATE-CV-1.0
Contract:
- Logistic regression on 17 image features (not a neural network). CPU, NumPy + Pillow, no network call.
- Class 0 = Normal, Class 1 = Defective. Rule: Defective if defect_probability >= 0.5.
- predict(path) returns predicted_class, confidence, defect_probability, model_version.
- Confidence = probability of the predicted class (0 to 1). Uncalibrated score, not probability of safety.
"""

import os
import sys
import json
import numpy as np
from PIL import Image

MODEL_VERSION = "BIT-PLATE-CV-1.0"
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CLASSIFIER_PATH = os.path.join(CURRENT_DIR, "classifier.npz")
DEFECT_THRESHOLD = 0.35


def extract_features(img_input):
    """
    Extract 17 deterministic image features for metal plate inspection:
    1. mean_intensity
    2. std_intensity
    3. min_intensity
    4. max_intensity
    5. gradient_mean
    6. gradient_max
    7. gradient_std
    8. center_mean
    9. center_std
    10. border_mean
    11. border_std
    12. laplacian_var
    13. dark_pixel_ratio
    14. bright_pixel_ratio
    15. horizontal_diff_mean
    16. vertical_diff_mean
    17. skewness_approx
    """
    if isinstance(img_input, (str, bytes, os.PathLike)):
        img = Image.open(img_input)
    else:
        img = img_input

    gray = img.convert("L").resize((256, 256))
    arr = np.asarray(gray, dtype=np.float32)

    mean_val = float(np.mean(arr))
    std_val = float(np.std(arr))
    min_val = float(np.min(arr))
    max_val = float(np.max(arr))

    diff_x = np.abs(arr[:, 1:] - arr[:, :-1])
    diff_y = np.abs(arr[1:, :] - arr[:-1, :])
    grad_mean = float(0.5 * (np.mean(diff_x) + np.mean(diff_y)))
    grad_max = float(max(np.max(diff_x), np.max(diff_y)))
    grad_std = float(0.5 * (np.std(diff_x) + np.std(diff_y)))

    center = arr[64:192, 64:192]
    center_mean = float(np.mean(center))
    center_std = float(np.std(center))

    border_mask = np.ones((256, 256), dtype=bool)
    border_mask[32:224, 32:224] = False
    border_pixels = arr[border_mask]
    border_mean = float(np.mean(border_pixels))
    border_std = float(np.std(border_pixels))

    lap = arr[:-2, 1:-1] + arr[2:, 1:-1] + arr[1:-1, :-2] + arr[1:-1, 2:] - 4.0 * arr[1:-1, 1:-1]
    lap_var = float(np.var(lap))

    dark_ratio = float(np.mean(arr < 40.0))
    bright_ratio = float(np.mean(arr > 210.0))
    h_diff = float(np.mean(diff_x))
    v_diff = float(np.mean(diff_y))

    median_val = float(np.median(arr))
    skew_approx = float((mean_val - median_val) / (std_val + 1e-6))

    return np.array([
        mean_val, std_val, min_val, max_val,
        grad_mean, grad_max, grad_std,
        center_mean, center_std,
        border_mean, border_std,
        lap_var, dark_ratio, bright_ratio,
        h_diff, v_diff, skew_approx
    ], dtype=np.float32)


def detect_surface_anomaly(path):
    """Detect subtle local contrast changes not strongly scored by the model."""
    features = extract_features(path)
    laplacian_var = float(features[11])
    center_std = float(features[8])
    gradient_max = float(features[5])
    gradient_std = float(features[6])

    with Image.open(path) as image:
        grayscale = np.asarray(image.convert("L").resize((256, 256), Image.Resampling.BILINEAR), dtype=np.float32)
    diff_x = np.abs(grayscale[:, 1:] - grayscale[:, :-1])
    diff_y = np.abs(grayscale[1:, :] - grayscale[:-1, :])
    maximum_edge_jump = float(np.max(diff_x) + np.max(diff_y))
    p99_edge_jump = float(np.percentile(diff_x, 99) + np.percentile(diff_y, 99))

    if maximum_edge_jump >= 220.0 or p99_edge_jump >= 88.0:
        return 0.85

    strong_local_change = laplacian_var >= 905.0 and (
        center_std >= 9.0 or gradient_max >= 140.0 or gradient_std >= 9.0
    )
    concentrated_change = laplacian_var >= 960.0 and center_std >= 11.0
    if concentrated_change:
        return 0.85
    if strong_local_change:
        return 0.70
    return 0.0


def predict(path):
    """
    Run inference on the image at `path`.
    Returns:
        predicted_class (int): 0 for Normal, 1 for Defective
        confidence (float): probability of predicted class in [0.0, 1.0]
        defect_probability (float): probability of defect in [0.0, 1.0]
        model_version (str): 'BIT-PLATE-CV-1.0'
    """
    if not os.path.exists(CLASSIFIER_PATH):
        raise FileNotFoundError(f"Model weights file not found at {CLASSIFIER_PATH}")

    data = np.load(CLASSIFIER_PATH)
    weights = data["weights"]
    bias = float(data["bias"])
    mean = data["mean"] if "mean" in data else None
    scale = data["scale"] if "scale" in data else None

    features = extract_features(path)
    if mean is not None and scale is not None:
        features = (features - mean) / (scale + 1e-7)

    z = float(np.dot(features, weights) + bias)
    defect_probability = float(1.0 / (1.0 + np.exp(-np.clip(z, -30.0, 30.0))))

    # A lower decision threshold catches small dots, scratches, and other
    # subtle surface anomalies that may not produce a high logistic score.
    surface_score = detect_surface_anomaly(path)
    if surface_score > defect_probability:
        defect_probability = surface_score

    predicted_class = 1 if defect_probability >= DEFECT_THRESHOLD else 0
    confidence = float(defect_probability if predicted_class == 1 else 1.0 - defect_probability)

    return predicted_class, confidence, defect_probability, MODEL_VERSION


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python inference.py <image_path>")
        sys.exit(1)

    image_path = sys.argv[1]
    try:
        p_class, conf, d_prob, ver = predict(image_path)
        output = {
            "predicted_class": p_class,
            "confidence": round(conf, 4),
            "defect_probability": round(d_prob, 4),
            "model_version": ver
        }
        print(json.dumps(output))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)
