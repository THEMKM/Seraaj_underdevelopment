.PHONY: seed makemigrations migrate test lint

seed:
	APP_ENV=development PYTHONPATH=apps/api python -m apps.api.services.unified_seeding_service

makemigrations:
	alembic revision --autogenerate -m "migration"

migrate:
	alembic upgrade head

test:
	pytest -q

lint:
	ruff .
	mypy .
