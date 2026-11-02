"""
Create administrator user utility.
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

def create_admin(username="admin", email="admin@manufacturing.local", password="AdminPassword!2026"):
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            "email": email,
            "role": User.Role.ADMIN,
            "is_staff": True,
            "is_superuser": True,
        }
    )
    user.set_password(password)
    user.role = User.Role.ADMIN
    user.is_staff = True
    user.is_superuser = True
    user.save()
    action = "Created" if created else "Updated"
    print(f"{action} admin user '{username}' (Password: {password})")

if __name__ == "__main__":
    u = sys.argv[1] if len(sys.argv) > 1 else "admin"
    p = sys.argv[2] if len(sys.argv) > 2 else "AdminPassword!2026"
    create_admin(username=u, password=p)
