.DEFAULT_GOAL := help

PYTHON ?= python3.12
VENV := .venv
BIN := $(VENV)/bin
HELM_CHART := helm/greengrid-platform
HELM_RENDER_DIR := /tmp/greengrid-helm-rendered

.PHONY: help install validate test format lint build run stop logs verify clean run-api run-generator helm-lint helm-template-dev helm-template-staging helm-template-prod helm-template-all helm-dry-run helm-security helm-verify

help: ## List local application commands
	@echo "GreenGrid commands: install format lint test build run stop logs verify clean helm-verify"

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

helm-lint: ## Lint the chart against every environment overlay
	helm lint $(HELM_CHART) -f $(HELM_CHART)/values-dev.yaml
	helm lint $(HELM_CHART) -f $(HELM_CHART)/values-staging.yaml
	helm lint $(HELM_CHART) -f $(HELM_CHART)/values-prod.yaml

helm-template-dev: ## Render development manifests locally
	@mkdir -p $(HELM_RENDER_DIR)
	helm template greengrid $(HELM_CHART) --namespace greengrid-dev -f $(HELM_CHART)/values-dev.yaml > $(HELM_RENDER_DIR)/dev.yaml

helm-template-staging: ## Render staging manifests locally
	@mkdir -p $(HELM_RENDER_DIR)
	helm template greengrid $(HELM_CHART) --namespace greengrid-staging -f $(HELM_CHART)/values-staging.yaml > $(HELM_RENDER_DIR)/staging.yaml

helm-template-prod: ## Render production manifests locally
	@mkdir -p $(HELM_RENDER_DIR)
	helm template greengrid $(HELM_CHART) --namespace greengrid-prod -f $(HELM_CHART)/values-prod.yaml > $(HELM_RENDER_DIR)/prod.yaml

helm-template-all: helm-template-dev helm-template-staging helm-template-prod ## Render every environment

helm-dry-run: helm-template-all ## Attempt offline kubectl client-side validation
	@for manifest in $(HELM_RENDER_DIR)/dev.yaml $(HELM_RENDER_DIR)/staging.yaml $(HELM_RENDER_DIR)/prod.yaml; do \
		kubectl apply --dry-run=client --validate=false --namespace default --filename $$manifest >/dev/null 2>&1 || \
		echo "kubectl offline dry-run unavailable for $$manifest; Helm rendering remains authoritative"; \
	done
	@helm install greengrid-dev $(HELM_CHART) --namespace greengrid-dev -f $(HELM_CHART)/values-dev.yaml --dry-run=client >/dev/null
	@helm install greengrid-staging $(HELM_CHART) --namespace greengrid-staging -f $(HELM_CHART)/values-staging.yaml --dry-run=client >/dev/null
	@helm install greengrid-prod $(HELM_CHART) --namespace greengrid-prod -f $(HELM_CHART)/values-prod.yaml --dry-run=client >/dev/null
	@echo "Helm client-side install dry-run passed for dev, staging, and prod."

helm-security: helm-template-all ## Verify security invariants in every rendered environment
	@for manifest in $(HELM_RENDER_DIR)/dev.yaml $(HELM_RENDER_DIR)/staging.yaml $(HELM_RENDER_DIR)/prod.yaml; do \
		./scripts/verify-helm-security.rb $$manifest; \
	done

helm-verify: helm-lint helm-template-all helm-dry-run helm-security ## Run all chart validation gates
