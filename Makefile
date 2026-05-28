.PHONY: setup product-pipeline product-api product-ui product-demo product-sample-pipeline validate-product validate-all academic-db-up wait-postgres academic-db-schema academic-etl academic-services-up academic-demo academic-validate validate-academic db-up db-schema db-reset db-migrate etl-demo extract-demo build score mongo-load services-up api api-docker dashboard demo demo-full test test-integration lint report validate-final

PYTHON := uv run --python 3.11 --extra dev
PRODUCT_SOURCE_MODE ?= sample

setup:
	uv sync --python 3.11 --extra dev

product-pipeline:
	PRODUCT_SOURCE_MODE=$(PRODUCT_SOURCE_MODE) $(PYTHON) python -m src.extract.secop_api
	PRODUCT_SOURCE_MODE=$(PRODUCT_SOURCE_MODE) $(PYTHON) python -m src.transform.build_process_master
	PRODUCT_SOURCE_MODE=$(PRODUCT_SOURCE_MODE) $(PYTHON) python -m src.scoring.score_processes

product-sample-pipeline:
	$(MAKE) product-pipeline PRODUCT_SOURCE_MODE=sample

product-api:
	PUBLIC_READ_ONLY=true $(PYTHON) uvicorn src.api.main:app --host 0.0.0.0 --port 8000

product-ui:
	$(PYTHON) streamlit run src/app/streamlit_app.py

product-demo:
	$(MAKE) product-pipeline
	@echo "Run product-ui and product-api in separate terminals."

validate-product:
	$(PYTHON) python -m etl.validate_product

academic-db-up:
	docker compose up -d postgres mongo
	$(MAKE) wait-postgres

wait-postgres:
	@for i in $$(seq 1 60); do \
		docker compose exec -T postgres pg_isready -U contratia -d contratia >/dev/null 2>&1 && exit 0; \
		sleep 2; \
	done; \
	echo "PostgreSQL no estuvo listo despues de 120s"; \
	exit 1

academic-db-schema:
	$(PYTHON) python -m etl.apply_schema

db-reset:
	$(PYTHON) python -m etl.apply_schema --reset

db-up: academic-db-up

db-schema: academic-db-schema

db-migrate: academic-db-schema

academic-etl:
	$(PYTHON) python -m etl.validate_sources
	$(PYTHON) python -m etl.build_demo_dataset
	$(PYTHON) python -m etl.load_to_postgres --limit 20000
	$(PYTHON) python -m etl.load_to_mongo

etl-demo: academic-etl

extract-demo:
	EXTRACT_SCOPE=demo $(PYTHON) python -m src.extract.secop_api

build:
	$(PYTHON) python -m src.transform.build_process_master

score:
	$(PYTHON) python -m src.scoring.score_processes

mongo-load:
	$(PYTHON) python -m etl.load_to_mongo

academic-services-up:
	docker compose up -d contracts_service risk_service analytics_service dash_dashboard

services-up: academic-services-up

api:
	$(PYTHON) uvicorn services.contracts_service.main:app --host 0.0.0.0 --port 8001 & \
	$(PYTHON) uvicorn services.risk_service.main:app --host 0.0.0.0 --port 8002 & \
	$(PYTHON) uvicorn services.analytics_service.main:app --host 0.0.0.0 --port 8003 & \
	wait

api-docker:
	docker compose up contracts_service risk_service analytics_service

dashboard:
	$(PYTHON) python -m dashboard.dash_app

demo: academic-etl

academic-demo:
	$(MAKE) academic-db-up
	$(MAKE) db-reset
	$(MAKE) academic-etl
	$(MAKE) academic-services-up

demo-full: academic-demo

test:
	$(PYTHON) pytest -q -m "not integration"

test-integration:
	$(PYTHON) pytest -q -m integration

lint:
	$(PYTHON) ruff check .

report:
	$(PYTHON) python -m etl.validate_sources

validate-academic:
	$(PYTHON) python -m etl.validate_final

academic-validate: validate-academic

sync-product-to-academic:
	$(PYTHON) python -m etl.sync_product_to_academic

validate-final:
	$(MAKE) product-pipeline
	$(MAKE) sync-product-to-academic
	$(MAKE) validate-product
	$(MAKE) validate-academic

validate-all:
	$(MAKE) product-pipeline
	$(MAKE) validate-product
	$(MAKE) validate-academic
