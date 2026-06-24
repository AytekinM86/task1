# Hospital data generator — task runner.
# Run `make help` (or just `make`) for the full list.

.DEFAULT_GOAL := help

.PHONY: install lint format format-check typecheck test test-int test-all check \
        run run-dry docker-build docker-run help

install: ## Install dependencies (incl. dev) via Poetry
	poetry install

lint: ## Ruff lint
	poetry run ruff check src tests

format: ## Ruff format (write)
	poetry run ruff format src tests

format-check: ## Ruff format (check only, for CI)
	poetry run ruff format --check src tests

typecheck: ## mypy strict
	poetry run mypy

test: ## Unit tests only (no DB required)
	poetry run pytest -m "not integration"

test-int: ## Integration tests (requires `make up` at repo root)
	poetry run pytest -m integration

test-all: ## All tests + coverage
	poetry run pytest

check: lint format-check typecheck test ## Lint + format-check + typecheck + unit tests

run: ## Seed the DB with defaults
	poetry run hospital-datagen seed

run-dry: ## Generate + validate, roll back (insert nothing)
	poetry run hospital-datagen seed --dry-run

docker-build: ## Build the standalone Docker image
	docker build -t dbmig-datagen:local .

docker-run: ## Run the image (override args with ARGS=, e.g. ARGS="seed --last-90-days")
	docker run --rm --network host dbmig-datagen:local $(ARGS)

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'
