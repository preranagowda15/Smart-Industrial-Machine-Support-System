import pytest
import os
from services.model_service import predict_plate
from Model.inference import predict as direct_predict


def test_model_service_parity_with_inference_py():
    """
    Test 3: model_service output equals Model/inference.py output for the same file
    (no preprocessing drift).
    """
    sample_files = [
        'Samples/images/inspection_001.png',
        'Samples/images/inspection_015.png',
        'Samples/images/inspection_035.png',
        'Samples/images/inspection_055.png'
    ]

    for img_path in sample_files:
        assert os.path.exists(img_path), f"Sample file not found: {img_path}"

        direct_class, direct_conf, direct_prob, direct_ver = direct_predict(img_path)
        service_res = predict_plate(img_path)

        assert service_res['predicted_class'] == direct_class, f"Class drift on {img_path}"
        assert abs(service_res['confidence'] - direct_conf) < 1e-6, f"Confidence drift on {img_path}"
        assert abs(service_res['defect_probability'] - direct_prob) < 1e-6, f"Defect prob drift on {img_path}"
        assert service_res['model_version'] == direct_ver, f"Version drift on {img_path}"

