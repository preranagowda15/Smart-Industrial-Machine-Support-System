"""
Interactive CLI script to register a new machine.
Usage:
    python scripts/register_machine.py
Or with arguments:
    python scripts/register_machine.py <machine_code> <machine_name> [manufacturer] [description]
"""
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.config.settings")

import django
django.setup()

from backend.apps.machines.models import Machine

def register_machine(machine_code, machine_name, manufacturer="Apex Machining Systems", description=""):
    machine, created = Machine.objects.get_or_create(
        machine_code=machine_code,
        defaults={
            "machine_name": machine_name,
            "manufacturer": manufacturer,
            "description": description or f"{machine_name} industrial unit.",
            "is_active": True,
        }
    )
    if not created:
        machine.machine_name = machine_name
        machine.manufacturer = manufacturer
        if description:
            machine.description = description
        machine.is_active = True
        machine.save()

    status_str = "Created new" if created else "Updated existing"
    print("\n" + "=" * 50)
    print(f"SUCCESS: {status_str} Machine!")
    print(f"Machine Code: {machine.machine_code}")
    print(f"Machine Name: {machine.machine_name}")
    print(f"Manufacturer: {machine.manufacturer}")
    print(f"Status:       Active")
    print("=" * 50 + "\n")

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        code = sys.argv[1]
        name = sys.argv[2]
        mfr = sys.argv[3] if len(sys.argv) > 3 else "Apex Machining Systems"
        desc = sys.argv[4] if len(sys.argv) > 4 else ""
        register_machine(code, name, mfr, desc)
    else:
        print("--- Register New Machine ---")
        code = input("Enter Machine Code (e.g. M-CNC500): ").strip()
        name = input("Enter Machine Name / Model: ").strip()
        mfr = input("Enter Manufacturer (default: Apex Machining Systems): ").strip() or "Apex Machining Systems"
        desc = input("Enter Description (optional): ").strip()
        register_machine(code, name, mfr, desc)
