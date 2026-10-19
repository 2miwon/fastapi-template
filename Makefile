.PHONY: install run db db-down migrate migration downgrade test cov lint format typecheck deps audit security check

install:
	uv sync
	uv run pre-commit install

run:
	uv run fastapi dev src/main.py

db:
	docker compose up -d db

db-down:
	docker compose down

migrate:
	uv run alembic upgrade head

# usage: make migration m="add post_like table"
migration:
	uv run alembic revision --autogenerate -m "$(m)"

downgrade:
	uv run alembic downgrade -1

test:
	uv run pytest

cov:
	uv run pytest --cov --cov-report=term --cov-report=html

lint:
	uv run ruff format --check .
	uv run ruff check .

format:
	uv run ruff format .
	uv run ruff check --fix .

typecheck:
	uv run mypy src tests

# unused / missing / transitive dependencies
deps:
	uv run deptry .

# known CVEs in locked dependencies
audit:
	uv audit --preview-features audit-command

# bandit rules (ruff "S") + dependency CVEs
security:
	uv run ruff check --select S .
	$(MAKE) audit

check: lint typecheck deps audit test
