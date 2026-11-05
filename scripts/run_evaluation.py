#!/usr/bin/env python
"""
scripts/run_evaluation.py - Standalone evaluation runner
"""

import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / 'backend'))
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.core.management import call_command

if __name__ == '__main__':
    call_command('run_evaluation')

