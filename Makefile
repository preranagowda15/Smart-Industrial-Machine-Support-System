.PHONY: install migrate seed run test evaluate integrity-check clean

PYTHON = python
MANAGE = $(PYTHON) backend/manage.py

install:
	$(PYTHON) -m pip install -r requirements.txt

migrate:
	$(MANAGE) makemigrations
	$(MANAGE) migrate

seed:
	$(PYTHON) scripts/seed_users.py

run:
	$(MANAGE) runserver 127.0.0.1:8000

test:
	pytest backend/tests/ -v

evaluate:
	$(MANAGE) runevaluation

integrity-check:
	$(PYTHON) -c "import sys; sys.path.insert(0, 'backend'); from services.integrity_service import verify_integrity; r = verify_integrity(); print(r); sys.exit(0 if r['is_valid'] else 1)"

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +

