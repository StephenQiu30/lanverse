PNPM ?= pnpm
UV ?= uv

.PHONY: bootstrap build dev lint test-architecture typecheck

bootstrap:
	$(PNPM) install --frozen-lockfile
	$(UV) sync --frozen

build:
	$(PNPM) build
	$(UV) run python -m compileall -q apps packages tools

dev:
	$(PNPM) dev

lint:
	$(PNPM) lint
	$(UV) run ruff check apps packages tests tools

typecheck:
	$(PNPM) typecheck
	$(UV) run mypy apps packages tools

test-architecture:
	PYTHONDONTWRITEBYTECODE=1 $(UV) run python -m unittest discover \
		-s tests/architecture -p 'test_*.py'
