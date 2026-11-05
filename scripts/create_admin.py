#!/usr/bin/env python
"""
scripts/create_admin.py - Create or update primary admin user
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

from apps.accounts.models import User

ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'Admin123!')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@plate-inspect.local')


def create_admin():
    user, created = User.objects.get_or_create(
        username=ADMIN_USERNAME,
        defaults={'email': ADMIN_EMAIL, 'role': User.Role.ADMIN}
    )
    user.set_password(ADMIN_PASSWORD)
    user.role = User.Role.ADMIN
    user.is_staff = True
    user.is_superuser = True
    user.save()

    status = "Created" if created else "Updated"
    print(f"[{status}] Administrator: {ADMIN_USERNAME} with role {user.role}")


if __name__ == '__main__':
    create_admin()

