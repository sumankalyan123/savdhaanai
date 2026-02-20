.PHONY: dev test lint format migrate seed clean install

# Start local dev environment
dev:
	docker compose -f infra/docker/docker-compose.yml up --build

# Stop local dev environment
down:
	docker compose -f infra/docker/docker-compose.yml down

# Install dependencies (dev)
install:
	pip install -e ".[dev]"

# Run all tests
test:
	pytest tests/ -v --tb=short

# Run tests with coverage
test-cov:
	pytest tests/ -v --tb=short --cov=src --cov-report=term-missing

# Lint check
lint:
	ruff check src/ tests/
	ruff format --check src/ tests/

# Auto-fix lint issues
format:
	ruff check --fix src/ tests/
	ruff format src/ tests/

# Run Alembic migrations
migrate:
	alembic upgrade head

# Create a new migration
migration:
	@read -p "Migration message: " msg; \
	alembic revision --autogenerate -m "$$msg"

# Seed scam taxonomy data
seed:
	python scripts/seed_scam_taxonomy.py

# Run the API server locally (without Docker)
serve:
	uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Run Celery worker locally
worker:
	celery -A src.workers worker --loglevel=info

# Clean up
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .pytest_cache .coverage htmlcov .mypy_cache .ruff_cache
