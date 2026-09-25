.PHONY: dev migrate revision seed cleanup-users test lint typecheck

dev:           ; uvicorn app.main:app --reload
migrate:       ; alembic upgrade head
revision:      ; alembic revision --autogenerate -m "$(m)"
downgrade:     ; alembic downgrade -1
seed:          ; python -m scripts.seed
cleanup-users: ; python -m scripts.cleanup_users
test:          ; pytest
lint:          ; ruff format . && ruff check --fix .
typecheck:     ; mypy app
