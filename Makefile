.PHONY: help dev up down build test lint fmt migrate backend-test frontend-test

help:
	@echo "Litmus — common commands"
	@echo "  make dev        Start the full stack with hot-reload"
	@echo "  make up         Start the full stack (built images)"
	@echo "  make down       Stop the stack"
	@echo "  make build      Build all docker images"
	@echo "  make test       Run backend + frontend test suites"
	@echo "  make lint       Run all linters/formatters (check only)"
	@echo "  make migrate    Apply DB migrations inside the backend container"

dev:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up

up:
	docker compose up

down:
	docker compose down

build:
	docker compose build

migrate:
	docker compose run --rm backend alembic upgrade head

backend-test:
	cd backend && uv run ruff check . && uv run ruff format --check . && uv run mypy && uv run pytest

frontend-test:
	cd frontend && npm run lint && npm run typecheck && npm run test && npm run build

test: backend-test frontend-test

lint:
	cd backend && uv run ruff check . && uv run ruff format --check .
	cd frontend && npm run lint

fmt:
	cd backend && uv run ruff check --fix . && uv run ruff format .
	cd frontend && npm run format
