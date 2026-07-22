PNPM ?= pnpm
UV ?= uv
FRONTEND := frontend
BACKEND := backend
COMPOSE_FILE := infra/compose/compose.yaml
COMPOSE_ENV := infra/compose/.env.example
COMPOSE := docker compose --env-file $(COMPOSE_ENV) -f $(COMPOSE_FILE)
THIEF_DATABASE_URL ?= postgresql+psycopg://thief:thief_local@localhost:5432/thief
THIEF_RABBITMQ_MANAGEMENT_URL ?= http://localhost:15672
THIEF_RABBITMQ_URL ?= amqp://thief:thief_local@localhost:5672//

.PHONY: bootstrap build dev infra-config infra-down infra-up lint migrate \
	migrate-down run-api run-scheduler run-web run-worker test-architecture \
	test-integration test-runtime test-unit typecheck verify

bootstrap:
	$(PNPM) --dir $(FRONTEND) install --frozen-lockfile
	$(UV) sync --directory $(BACKEND) --frozen

build:
	$(PNPM) --dir $(FRONTEND) build
	$(UV) run --directory $(BACKEND) python -m compileall -q \
		apps migrations packages tools

dev:
	$(PNPM) --dir $(FRONTEND) dev

infra-config:
	$(COMPOSE) config --quiet

infra-up: infra-config
	$(COMPOSE) up --detach --wait --wait-timeout 180

infra-down:
	$(COMPOSE) down

migrate:
	THIEF_DATABASE_URL=$(THIEF_DATABASE_URL) $(UV) run --directory $(BACKEND) \
		alembic -c alembic.ini upgrade heads

migrate-down:
	THIEF_DATABASE_URL=$(THIEF_DATABASE_URL) $(UV) run --directory $(BACKEND) \
		alembic -c alembic.ini downgrade base

run-web:
	$(PNPM) --dir $(FRONTEND) start --port 3000

run-api:
	$(UV) run --directory $(BACKEND) uvicorn thief_api.main:app \
		--app-dir apps/api/src --host 127.0.0.1 --port 8000

run-worker:
	PYTHONPATH=$(CURDIR)/$(BACKEND)/apps/worker/src \
		THIEF_RABBITMQ_URL=$(THIEF_RABBITMQ_URL) \
		$(UV) run --directory $(BACKEND) celery -A thief_worker.app:app worker \
		--loglevel=WARNING --pool=solo --queues=generation \
		--without-gossip --without-heartbeat --without-mingle

run-scheduler:
	PYTHONPATH=$(CURDIR)/$(BACKEND)/apps/scheduler/src \
		THIEF_RABBITMQ_URL=$(THIEF_RABBITMQ_URL) \
		$(UV) run --directory $(BACKEND) celery -A thief_scheduler.app:app beat \
		--loglevel=WARNING

lint:
	$(PNPM) --dir $(FRONTEND) lint
	$(UV) run --directory $(BACKEND) ruff check \
		apps migrations packages tests tools

typecheck:
	$(PNPM) --dir $(FRONTEND) typecheck
	$(UV) run --directory $(BACKEND) mypy apps migrations packages tools

test-architecture:
	PYTHONDONTWRITEBYTECODE=1 $(UV) run --directory $(BACKEND) \
		python -m unittest discover \
		-s tests/architecture -p 'test_*.py'

test-integration:
	THIEF_DATABASE_URL=$(THIEF_DATABASE_URL) PYTHONDONTWRITEBYTECODE=1 \
		$(UV) run --directory $(BACKEND) python -m unittest discover \
		-s tests/integration -p 'test_*.py'

test-runtime: build
	THIEF_RABBITMQ_MANAGEMENT_URL=$(THIEF_RABBITMQ_MANAGEMENT_URL) \
		THIEF_RABBITMQ_URL=$(THIEF_RABBITMQ_URL) $(UV) run --directory $(BACKEND) \
		python tools/runtime_smoke.py

test-unit:
	PYTHONDONTWRITEBYTECODE=1 $(UV) run --directory $(BACKEND) \
		python -m unittest discover \
		-s tests/unit -p 'test_*.py'

verify: infra-config test-unit test-architecture lint typecheck build
