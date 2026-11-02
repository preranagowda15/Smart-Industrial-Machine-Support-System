"""
Interactive CLI script to register new users with roles (Administrator, Engineer, Supervisor).
Usage:
    python scripts/register_user.py
Or with arguments:
    python scripts/register_user.py <username> <password> <role> [email]
"""
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.config.settings")

import django
django.setup()

from backend.apps.accounts.models import User

def register_user(username, password, role="ENGINEER", email=""):
    role = role.upper()
    valid_roles = [User.Role.ADMIN, User.Role.ENGINEER, User.Role.SUPERVISOR]
    if role not in valid_roles:
        print(f"Error: Invalid role '{role}'. Choose from: ADMIN, ENGINEER, SUPERVISOR")
        return

    is_staff = (role == User.Role.ADMIN)
    is_super = (role == User.Role.ADMIN)

    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            "email": email or f"{username}@manufacturing.local",
            "role": role,
            "is_staff": is_staff,
            "is_superuser": is_super,
        }
    )
    user.set_password(password)
    user.role = role
    user.is_staff = is_staff
    user.is_superuser = is_super
    if email:
        user.email = email
    user.save()

    status_str = "Created new" if created else "Updated existing"
    print("\n" + "=" * 50)
    print(f"SUCCESS: {status_str} User!")
    print(f"Username: {user.username}")
    print(f"Role:     {user.get_role_display()} ({user.role})")
    print(f"Email:    {user.email}")
    print(f"Password: {password}")
    print("=" * 50 + "\n")

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        u = sys.argv[1]
        p = sys.argv[2]
        r = sys.argv[3] if len(sys.argv) > 3 else "ENGINEER"
        e = sys.argv[4] if len(sys.argv) > 4 else ""
        register_user(u, p, r, e)
    else:
        print("--- Register New User ---")
        u = input("Enter Username: ").strip()
        p = input("Enter Password: ").strip()
        print("Roles: 1) ENGINEER (default)  2) SUPERVISOR  3) ADMIN")
        choice = input("Select Role (1/2/3 or type name): ").strip()
        role_map = {"1": "ENGINEER", "2": "SUPERVISOR", "3": "ADMIN"}
        r = role_map.get(choice, choice.upper() or "ENGINEER")
        e = input("Enter Email (optional): ").strip()
        register_user(u, p, r, e)

