"""
backend/services/integrity_service.py - SHA256 file integrity verification
Enforces Section 6.5:
On startup and via admin endpoint, verify files against SHA256SUMS.txt and report mismatches.
"""

import os
import hashlib
from pathlib import Path
from django.conf import settings

try:
    from Model.inference import MODEL_VERSION
except ImportError:
    MODEL_VERSION = "BIT-PLATE-CV-1.0"


def verify_integrity(checksums_file=None, base_path=None):
    """
    Verifies all files listed in SHA256SUMS.txt.
    
    Args:
        checksums_file (Path, optional): Path to SHA256SUMS.txt
        base_path (Path, optional): Base directory containing relative paths
        
    Returns:
        dict: {
            'is_valid': bool,
            'model_version': str,
            'total_files': int,
            'matched_count': int,
            'mismatch_count': int,
            'missing_count': int,
            'details': list of dicts: [{'path': str, 'status': 'OK'|'MISMATCH'|'MISSING', 'expected': str, 'actual': str}]
        }
    """
    if base_path is None:
        base_path = Path(settings.BASE_DIR)
    else:
        base_path = Path(base_path)

    if checksums_file is None:
        checksums_file = base_path / 'SHA256SUMS.txt'
    else:
        checksums_file = Path(checksums_file)

    if not checksums_file.exists():
        return {
            'is_valid': False,
            'model_version': MODEL_VERSION,
            'error': f"SHA256SUMS.txt not found at {checksums_file}",
            'total_files': 0,
            'matched_count': 0,
            'mismatch_count': 0,
            'missing_count': 0,
            'details': []
        }

    details = []
    matched_count = 0
    mismatch_count = 0
    missing_count = 0

    with open(checksums_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split(None, 1)
            if len(parts) != 2:
                continue
            expected_hash, rel_path = parts
            rel_path = rel_path.strip().replace('/', os.sep)
            file_path = base_path / rel_path

            if not file_path.exists():
                missing_count += 1
                details.append({
                    'path': rel_path.replace(os.sep, '/'),
                    'status': 'MISSING',
                    'expected': expected_hash,
                    'actual': None
                })
                continue

            hasher = hashlib.sha256()
            try:
                with open(file_path, 'rb') as target_f:
                    while chunk := target_f.read(65536):
                        hasher.update(chunk)
                actual_hash = hasher.hexdigest()

                if actual_hash == expected_hash:
                    matched_count += 1
                    details.append({
                        'path': rel_path.replace(os.sep, '/'),
                        'status': 'OK',
                        'expected': expected_hash,
                        'actual': actual_hash
                    })
                else:
                    mismatch_count += 1
                    details.append({
                        'path': rel_path.replace(os.sep, '/'),
                        'status': 'MISMATCH',
                        'expected': expected_hash,
                        'actual': actual_hash
                    })
            except Exception as e:
                mismatch_count += 1
                details.append({
                    'path': rel_path.replace(os.sep, '/'),
                    'status': 'ERROR',
                    'expected': expected_hash,
                    'actual': str(e)
                })

    total_files = len(details)
    is_valid = (mismatch_count == 0 and missing_count == 0 and total_files > 0)

    return {
        'is_valid': is_valid,
        'model_version': MODEL_VERSION,
        'total_files': total_files,
        'matched_count': matched_count,
        'mismatch_count': mismatch_count,
        'missing_count': missing_count,
        'details': details
    }

