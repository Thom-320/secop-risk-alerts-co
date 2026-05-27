.PHONY: setup db-up db-schema db-reset db-migrate etl-demo extract-demo build score mongo-load services-up api api-docker dashboard demo demo-full test test-integration lint report validate-final

PYTHON := uv run --python 3.11 --extra dev

setup:
	uv sync --python 3.11 --extra dev

db-up:
	docker compose up -d postgres mongo

db-schema:
	$(PYTHON) python -m etl.apply_schema

db-reset:
	$(PYTHON) python -m etl.apply_schema --reset

db-migrate: db-schema

etl-demo:
	$(PYTHON) python -m etl.validate_sources
	$(PYTHON) python -m etl.build_demo_dataset
	$(PYTHON) python -m etl.load_to_postgres --limit 20000

extract-demo:
	EXTRACT_SCOPE=demo $(PYTHON) python -m src.extract.secop_api

build:
	$(PYTHON) python -m src.transform.build_process_master

score:
	$(PYTHON) python -m src.scoring.score_processes

mongo-load:
	$(PYTHON) python -m etl.load_to_mongo

services-up:
	docker compose up -d contracts_service risk_service analytics_service dash_dashboard

api:
	$(PYTHON) uvicorn services.contracts_service.main:app --host 0.0.0.0 --port 8001 & \
	$(PYTHON) uvicorn services.risk_service.main:app --host 0.0.0.0 --port 8002 & \
	$(PYTHON) uvicorn services.analytics_service.main:app --host 0.0.0.0 --port 8003 & \
	wait

api-docker:
	docker compose up contracts_service risk_service analytics_service

dashboard:
	$(PYTHON) python -m dashboard.dash_app

demo: etl-demo mongo-load

demo-full: db-up db-reset etl-demo mongo-load services-up

test:
	$(PYTHON) pytest -q -m "not integration"

test-integration:
	$(PYTHON) pytest -q -m integration

lint:
	$(PYTHON) ruff check .

report:
	$(PYTHON) python -m etl.validate_sources

validate-final:
	$(PYTHON) python -m etl.validate_final
