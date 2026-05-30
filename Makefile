.PHONY: help install sync up down logs shell migrate test lint format build clean

# Variables
COMPOSE = docker compose
UV = uv run

# Colores
GREEN  := \033[0;32m
YELLOW := \033[0;33m
NC     := \033[0m

help: ## Muestra este mensaje de ayuda
	@echo "$(GREEN)FinSight AI — Comandos disponibles:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-22s$(NC) %s\n", $$1, $$2}'


# === ENTORNO ===
install: ## Instala Python 3.12 y crea el venv con UV
	uv python install 3.12
	uv venv --python 3.12

sync: ## Sincroniza dependencias desde uv.lock (prod + dev)
	uv sync --all-groups

sync-prod: ## Sincroniza solo dependencias de producción
	uv sync


# === DESARROLLO LOCAL ===
run: ## Levanta la app en local (sin Docker)
	$(UV) uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-llm: ## Ejecuta un script del llm_layer (uso: make run-llm SCRIPT=01_llm_basics.py)
	$(UV) python llm_layer/$(SCRIPT)


# === DOCKER (activo desde Semana 3) ===
up: ## Levanta la app + BD en Docker
	$(COMPOSE) up --build -d
	@echo "$(GREEN) App disponible en http://localhost:8000$(NC)"

down: ## Para todos los contenedores
	$(COMPOSE) down

down-v: ## Para contenedores y borra volúmenes (resetea la BD)
	$(COMPOSE) down -v

logs: ## Muestra logs de la app en tiempo real
	$(COMPOSE) logs -f app

shell: ## Abre una shell dentro del contenedor de la app
	$(COMPOSE) exec app bash

rebuild: ## Reconstruye imagen sin cache
	$(COMPOSE) build --no-cache
	$(COMPOSE) up -d


# === BASE DE DATOS ===
migrate: ## Aplica migraciones pendientes (local)
	$(UV) alembic upgrade head

migrate-docker: ## Aplica migraciones dentro del contenedor
	$(COMPOSE) exec app alembic upgrade head

new-migration: ## Genera nueva migración (uso: make new-migration MSG="descripción")
	$(UV) alembic revision --autogenerate -m "$(MSG)"

db-shell: ## Abre psql dentro del contenedor de BD
	$(COMPOSE) exec db psql -U finsight -d finsight_db


# === TESTS ===
test: ## Ejecuta tests con cobertura
	$(UV) pytest tests/ -v --cov=app --cov-report=term-missing

test-cov: ## Tests con reporte HTML de cobertura
	$(UV) pytest tests/ -v --cov=app --cov-report=html
	@open htmlcov/index.html 2>/dev/null || xdg-open htmlcov/index.html 2>/dev/null || true

test-unit: ## Solo tests unitarios
	$(UV) pytest tests/unit/ -v

test-integration: ## Solo tests de integración
	$(UV) pytest tests/integration/ -v

test-llm: ## Tests del llm_layer
	$(UV) pytest tests/ -v -k "llm"


# === CALIDAD DE CÓDIGO ===
lint: ## Ejecuta el linter (ruff)
	$(UV) ruff check .

format: ## Formatea el código con ruff
	$(UV) ruff format .

lint-fix: ## Corrige automáticamente problemas de lint
	$(UV) ruff check . --fix
	$(UV) ruff format .

typecheck: ## Type checking con mypy (activo desde Semana 3)
	$(UV) mypy app/


# === DOCUMENTACIÓN ===
export-openapi: ## Exporta el esquema OpenAPI a docs/openapi.json
	mkdir -p docs
	$(UV) python scripts/export_openapi.py

docs-html: export-openapi ## Genera docs/api-reference.html
	docker run --rm \
		-v "$(CURDIR)/docs:/spec" \
		redocly/cli build-docs /spec/openapi.json -o /spec/api-reference.html
	@echo "$(GREEN) API reference en docs/api-reference.html$(NC)"
	@open docs/api-reference.html 2>/dev/null || xdg-open docs/api-reference.html 2>/dev/null || true


# === LIMPIEZA ===
clean: ## Limpia cachés, pyc y artefactos
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete
	rm -rf htmlcov/ .coverage coverage.xml .pytest_cache
	@echo "$(GREEN) Limpieza completada$(NC)"

clean-docker: ## Limpia contenedores e imágenes Docker
	docker system prune -f

clean-venv: ## Elimina el venv (para recrearlo desde cero)
	rm -rf .venv