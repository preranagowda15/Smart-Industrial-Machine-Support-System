import pytest
import os
import tempfile
import shutil
from pathlib import Path
from services.integrity_service import verify_integrity


def test_integrity_check_detects_tampered_and_clean_files():
    """
    Test 7:
    - Integrity check verifies clean files (100% match)
    - Integrity check detects a tampered file (tested on temp copy)
    """
    # 1. Clean verification
    clean_report = verify_integrity()
    assert clean_report['is_valid'] is True
    assert clean_report['total_files'] == 67
    assert clean_report['matched_count'] == 67
    assert clean_report['mismatch_count'] == 0
    assert clean_report['missing_count'] == 0
    assert clean_report['model_version'] == 'BIT-PLATE-CV-1.0'

    # 2. Tampered verification using temporary file copy
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)

        # Copy SHA256SUMS.txt
        shutil.copy('SHA256SUMS.txt', temp_dir_path / 'SHA256SUMS.txt')

        # Copy Model folder
        shutil.copytree('Model', temp_dir_path / 'Model')

        # Tamper Model/inference.py in temp dir
        tampered_inference = temp_dir_path / 'Model' / 'inference.py'
        with open(tampered_inference, 'a') as f:
            f.write("\n# TAMPERED LINE INJECTED\n")

        # Run integrity check on tampered temp dir
        tampered_report = verify_integrity(
            checksums_file=temp_dir_path / 'SHA256SUMS.txt',
            base_path=temp_dir_path
        )

        assert tampered_report['is_valid'] is False
        assert tampered_report['mismatch_count'] >= 1

        # Locate tampered file entry in report details
        mismatched_entries = [
            d for d in tampered_report['details']
            if d['path'] == 'Model/inference.py' and d['status'] == 'MISMATCH'
        ]
        assert len(mismatched_entries) == 1, "Failed to identify tampered Model/inference.py"

