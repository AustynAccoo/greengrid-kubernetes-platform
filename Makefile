.DEFAULT_GOAL := help

PYTHON ?= python3.12
VENV := .venv
BIN := $(VENV)/bin

.PHONY: help install validate test format lint build run stop logs verify clean run-api run-generator

help: ## List local application commands
	@echo "GreenGrid local commands: install format lint test build run stop logs verify clean"

install: ## Create the Python 3.12 environment and install pinned dependencies
	@test -x $(BIN)/python || $(PYTHON) -m venv $(VENV)
	@$(BIN)/python -c 'import sys; assert sys.version_info[:2] == (3, 12), "Python 3.12 is required; recreate .venv with python3.12"'
	$(BIN)/python -m pip install --requirement requirements-dev.txt

validate: format lint test ## Run all local application quality gates

test: ## Run unit tests
	PYTHONPATH=applications/telemetry-api/src:applications/telemetry-generator/src $(BIN)/pytest

format: ## Check source formatting
	$(BIN)/ruff format --check applications tests

lint: ## Run static lint checks
	$(BIN)/ruff check applications tests

build: ## Build both pinned local container images
	docker compose build

run: ## Start both services and wait until healthy
	docker compose up --detach --wait

stop: ## Stop and remove the local Compose environment
	docker compose down --remove-orphans

logs: ## Follow local service logs
	docker compose logs --follow

verify: validate ## Verify tests, images, health, telemetry flow, and runtime users
	./scripts/verify-containers.sh

clean: stop ## Remove local service images and Python caches
	docker image rm greengrid-telemetry-api:local greengrid-telemetry-generator:local 2>/dev/null || true
	find applications tests -type d -name __pycache__ -prune -exec rm -rf {} +
	find applications tests -type d -name .pytest_cache -prune -exec rm -rf {} +

run-api: ## Run the telemetry API locally on port 8000
	PYTHONPATH=applications/telemetry-api/src $(BIN)/uvicorn telemetry_api.main:app --host 0.0.0.0 --port 8000

run-generator: ## Run the local telemetry generator
	PYTHONPATH=applications/telemetry-generator/src $(BIN)/python -m telemetry_generator.main
