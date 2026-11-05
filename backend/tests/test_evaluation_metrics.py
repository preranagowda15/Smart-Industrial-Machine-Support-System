import pytest
import os
import tempfile
import inspect
from services.metrics_service import evaluate_samples, FN_ZERO_STATEMENT
from services import model_service


def test_evaluation_metrics_and_matrix_orientation():
    """
    Test 6:
    - 2x2 confusion matrix orientation: rows = actual, columns = predicted, order Normal, Defective
    - Recall formula: TP / (TP + FN)
    - Failed predictions reported explicitly and counted
    - Labels are never passed to inference
    """
    # 1. Verify inspect.signature of predict_plate does not take 'label'
    sig = inspect.signature(model_service.predict_plate)
    assert 'label' not in sig.parameters, "Model predict must never accept a label parameter"

    # 2. Run real evaluation
    report = evaluate_samples()

    assert report['total_samples'] == 60
    assert report['successful_count'] == 60
    assert report['failed_count'] == 0
    assert report['model_version'] == 'BIT-PLATE-CV-1.0'

    tp = report['tp']
    fn = report['fn']
    fp = report['fp']
    tn = report['tn']

    # 3. Check confusion matrix orientation:
    # rows = actual, columns = predicted, order Normal, Defective
    cm = report['confusion_matrix']
    assert len(cm) == 2 and len(cm[0]) == 2 and len(cm[1]) == 2

    # Row 0: Actual Normal (0) -> [Predicted Normal (TN), Predicted Defective (FP)]
    assert cm[0][0] == tn, f"Expected cm[0][0] == TN ({tn}), got {cm[0][0]}"
    assert cm[0][1] == fp, f"Expected cm[0][1] == FP ({fp}), got {cm[0][1]}"

    # Row 1: Actual Defective (1) -> [Predicted Normal (FN), Predicted Defective (TP)]
    assert cm[1][0] == fn, f"Expected cm[1][0] == FN ({fn}), got {cm[1][0]}"
    assert cm[1][1] == tp, f"Expected cm[1][1] == TP ({tp}), got {cm[1][1]}"

    # 4. Recall formula check
    expected_recall = tp / (tp + fn)
    assert abs(report['defect_recall'] - expected_recall) < 1e-4

    # 5. FN=0 statement check
    if fn == 0:
        assert report['fn_zero_caveat'] == FN_ZERO_STATEMENT

    # 6. Explicit tracking of missing / failed samples
    with tempfile.NamedTemporaryFile('w', delete=False, suffix='.csv') as f:
        f.write('relative_path,label\n')
        f.write('images/inspection_001.png,0\n')
        f.write('images/missing_plate_999.png,1\n')
        temp_csv = f.name

    fail_report = evaluate_samples(labels_path=temp_csv)
    os.remove(temp_csv)

    assert fail_report['total_samples'] == 2
    assert fail_report['successful_count'] == 1
    assert fail_report['failed_count'] == 1
    assert len(fail_report['failed_predictions']) == 1
    assert 'missing_plate_999.png' in fail_report['failed_predictions'][0]['path']
    assert 'File not found' in fail_report['failed_predictions'][0]['error']

