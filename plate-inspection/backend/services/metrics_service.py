"""
backend/services/metrics_service.py - Authoritative Evaluation Metrics Service
Enforces Section 6.4:
- Defective = positive class (1). Normal = negative class (0).
- 2x2 confusion matrix: rows = actual, columns = predicted, order Normal, Defective:
    Row 0 (Actual Normal):    [TN, FP]
    Row 1 (Actual Defective): [FN, TP]
- Defect recall = TP / (TP + FN)
- Accuracy = (TP + TN) / Total
- Precision = TP / (TP + FP)
- Explicit tracking of missing / failed predictions.
- Exact statement when FN == 0:
  'no false negatives occurred, but 60 synthetic development images cannot establish real-world reliability.'
- Excludes Validation/* fixtures.
- Computes from actual runs; never hardcoded.
"""

import os
import csv
from datetime import datetime, timezone
from pathlib import Path
from django.conf import settings
from .model_service import predict_plate

FN_ZERO_STATEMENT = "no false negatives occurred, but 60 synthetic development images cannot establish real-world reliability."


def evaluate_samples(base_dir=None, labels_path=None):
    """
    Evaluates the model against all labeled images in Samples/labels.csv.
    
    Returns:
        dict: Complete evaluation report with confusion matrix, metrics, and itemized results.
    """
    if base_dir is None:
        base_dir = Path(settings.BASE_DIR)
    else:
        base_dir = Path(base_dir)

    samples_dir = base_dir / 'Samples'
    if labels_path is None:
        labels_path = samples_dir / 'labels.csv'
    else:
        labels_path = Path(labels_path)

    if not labels_path.exists():
        return {
            'error': f"Labels file not found at {labels_path}",
            'evaluated_at': datetime.now(timezone.utc).isoformat(),
            'total_samples': 0,
            'successful_count': 0,
            'failed_count': 0,
            'failed_predictions': [],
            'tp': 0, 'fn': 0, 'fp': 0, 'tn': 0,
            'confusion_matrix': [[0, 0], [0, 0]],
            'defect_recall': 0.0,
            'accuracy': 0.0,
            'precision': 0.0,
            'fn_zero_caveat': None,
            'model_version': 'BIT-PLATE-CV-1.0'
        }

    tp = 0
    fn = 0
    fp = 0
    tn = 0
    failed_predictions = []
    itemized_results = []
    model_version = 'BIT-PLATE-CV-1.0'

    with open(labels_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rel_path = row['relative_path'].strip().replace('/', os.sep)
            raw_label = row['label'].strip()

            # Map actual label to integer 0 or 1
            if raw_label.lower() in ('1', 'defective', 'true'):
                actual_class = 1
                actual_name = 'Defective'
            else:
                actual_class = 0
                actual_name = 'Normal'

            img_path = samples_dir / rel_path
            norm_rel_path = f"Samples/{rel_path.replace(os.sep, '/')}"

            # Check for file existence
            if not img_path.exists():
                failed_predictions.append({
                    'path': norm_rel_path,
                    'actual_class': actual_class,
                    'actual_name': actual_name,
                    'error': f"File not found on disk: {img_path}"
                })
                itemized_results.append({
                    'path': norm_rel_path,
                    'actual_class': actual_class,
                    'actual_name': actual_name,
                    'predicted_class': None,
                    'predicted_name': 'FAILED',
                    'confidence': 0.0,
                    'defect_probability': 0.0,
                    'status': 'MISSING_FILE'
                })
                continue

            # Run inference directly using model_service
            try:
                pred = predict_plate(img_path)
                p_class = pred['predicted_class']
                conf = pred['confidence']
                d_prob = pred['defect_probability']
                model_version = pred['model_version']

                # Compute confusion matrix elements
                if actual_class == 1 and p_class == 1:
                    tp += 1
                    status_label = 'TP'
                elif actual_class == 1 and p_class == 0:
                    fn += 1
                    status_label = 'FN'
                elif actual_class == 0 and p_class == 1:
                    fp += 1
                    status_label = 'FP'
                else:  # actual_class == 0 and p_class == 0
                    tn += 1
                    status_label = 'TN'

                itemized_results.append({
                    'path': norm_rel_path,
                    'actual_class': actual_class,
                    'actual_name': actual_name,
                    'predicted_class': p_class,
                    'predicted_name': 'Defective' if p_class == 1 else 'Normal',
                    'confidence': round(conf, 4),
                    'defect_probability': round(d_prob, 4),
                    'status': status_label
                })

            except Exception as e:
                failed_predictions.append({
                    'path': norm_rel_path,
                    'actual_class': actual_class,
                    'actual_name': actual_name,
                    'error': f"Inference failure: {str(e)}"
                })
                itemized_results.append({
                    'path': norm_rel_path,
                    'actual_class': actual_class,
                    'actual_name': actual_name,
                    'predicted_class': None,
                    'predicted_name': 'FAILED',
                    'confidence': 0.0,
                    'defect_probability': 0.0,
                    'status': 'INFERENCE_FAILED'
                })

    successful_count = tp + fn + fp + tn
    total_evaluated = successful_count + len(failed_predictions)

    # 2x2 confusion matrix: rows = actual, columns = predicted, order Normal, Defective
    # Row 0: Actual Normal    -> [TN, FP]
    # Row 1: Actual Defective -> [FN, TP]
    confusion_matrix = [
        [tn, fp],
        [fn, tp]
    ]

    # Metrics computation
    recall = round(tp / (tp + fn), 4) if (tp + fn) > 0 else 0.0
    accuracy = round((tp + tn) / successful_count, 4) if successful_count > 0 else 0.0
    precision = round(tp / (tp + fp), 4) if (tp + fp) > 0 else 0.0

    fn_zero_caveat = FN_ZERO_STATEMENT if fn == 0 and successful_count > 0 else None

    return {
        'evaluated_at': datetime.now(timezone.utc).isoformat(),
        'model_version': model_version,
        'total_samples': total_evaluated,
        'successful_count': successful_count,
        'failed_count': len(failed_predictions),
        'failed_predictions': failed_predictions,
        'tp': tp,
        'fn': fn,
        'fp': fp,
        'tn': tn,
        'confusion_matrix': confusion_matrix,
        'confusion_matrix_schema': {
            'rows': ['Actual Normal (0)', 'Actual Defective (1)'],
            'columns': ['Predicted Normal (0)', 'Predicted Defective (1)'],
            'cells': [['TN', 'FP'], ['FN', 'TP']]
        },
        'defect_recall': recall,
        'accuracy': accuracy,
        'precision': precision,
        'fn_zero_caveat': fn_zero_caveat,
        'items': itemized_results
    }
