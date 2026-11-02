.PHONY: install migrate seed test run docker-up docker-down clean

PYTHON = python
MANAGE = $(PYTHON) manage.py

install:
	pip install -r requirements.txt

migrate:
	$(MANAGE) makemigrations accounts machines manuals history dashboard
	$(MANAGE) migrate

seed:
	$(PYTHON) scripts/seed_data.py

test:
	$(MANAGE) test tests

run:
	$(MANAGE) runserver 127.0.0.1:8000

docker-up:
	docker compose up --build -d

docker-down:
	docker compose down

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

