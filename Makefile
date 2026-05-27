.PHONY: setup db-up db-reset db-migrate etl-demo extract-demo build score mongo-load api api-docker dashboard demo test lint report validate-final

PYTHON := uv run --python 3.11

setup:
	uv sync --python 3.11 --extra dev

db-up:
	docker compose up -d postgres mongo

db-reset:
	$(PYTHON) python -m etl.load_to_postgres --reset --limit 20000

db-migrate:
	$(PYTHON) python -m etl.load_to_postgres --limit 1

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

test:
	$(PYTHON) pytest -q

lint:
	$(PYTHON) ruff check .

report:
	$(PYTHON) python -m etl.validate_sources

validate-final:
	$(PYTHON) python -m etl.validate_final
