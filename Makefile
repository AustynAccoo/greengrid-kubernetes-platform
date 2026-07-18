.DEFAULT_GOAL := help

.PHONY: help validate test format lint run-api run-generator

help: ## List local application commands
	@echo "Use .venv/bin/make-style commands documented in the README."

validate: format lint test ## Run all local application quality gates

test: ## Run unit tests
	PYTHONPATH=applications/telemetry-api/src:applications/telemetry-generator/src .venv/bin/pytest

format: ## Check source formatting
	.venv/bin/ruff format --check applications tests

lint: ## Run static lint checks
	.venv/bin/ruff check applications tests

run-api: ## Run the telemetry API locally on port 8000
	PYTHONPATH=applications/telemetry-api/src .venv/bin/uvicorn telemetry_api.main:app --host 0.0.0.0 --port 8000

run-generator: ## Run the local telemetry generator
	PYTHONPATH=applications/telemetry-generator/src .venv/bin/python -m telemetry_generator.main
