#!/usr/bin/env python
"""
scripts/seed_users.py - Seeds default demonstration accounts with roles:
- operator1   (OPERATOR)
- supervisor1 (SUPERVISOR)
- admin1      (ADMIN)
"""

import os
import sys
from pathlib import Path

# Setup Django environment
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / 'backend'))
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from apps.accounts.models import User

USERS = [
    {
        'username': 'operator1',
        'password': 'Operator123!',
        'email': 'operator1@plate-inspect.local',
        'role': User.Role.OPERATOR,
        'is_staff': False,
        'is_superuser': False,
    },
    {
        'username': 'supervisor1',
        'password': 'Supervisor123!',
        'email': 'supervisor1@plate-inspect.local',
        'role': User.Role.SUPERVISOR,
        'is_staff': False,
        'is_superuser': False,
    },
    {
        'username': 'admin1',
        'password': 'Admin123!',
        'email': 'admin1@plate-inspect.local',
        'role': User.Role.ADMIN,
        'is_staff': True,
        'is_superuser': True,
    },
]


def seed_users():
    print("=" * 60)
    print("Seeding demo users for BIT-PLATE-CV-1.0...")
    print("=" * 60)
    created_count = 0
    updated_count = 0

    for u_data in USERS:
        username = u_data['username']
        password = u_data['password']
        role = u_data['role']
        email = u_data['email']

        user, created = User.objects.get_or_create(username=username, defaults={'email': email, 'role': role})
        user.set_password(password)
        user.role = role
        user.email = email
        user.is_staff = u_data['is_staff']
        user.is_superuser = u_data['is_superuser']
        user.save()

        action = "Created" if created else "Updated"
        if created:
            created_count += 1
        else:
            updated_count += 1
        print(f"[{action}] Username: {username:<12} | Role: {role:<10} | Password: {password}")

    print("=" * 60)
    print(f"Seeding completed: {created_count} created, {updated_count} updated.")
    print("=" * 60)


if __name__ == '__main__':
    seed_users()

