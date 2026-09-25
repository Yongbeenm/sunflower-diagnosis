.PHONY: up down logs migrate revision seed test lint gen-api cleanup-users

up:            ; docker compose up --build
down:          ; docker compose down
logs:          ; docker compose logs -f api web
migrate:       ; docker compose exec api alembic upgrade head
revision:      ; docker compose exec api alembic revision --autogenerate -m "$(m)"
seed:          ; docker compose exec api python -m scripts.seed
cleanup-users: ; docker compose exec api python -m scripts.cleanup_users
test:          ; docker compose exec api pytest -q && cd frontend && npm run test -- --run
lint:          ; docker compose exec api sh -c "ruff format . && ruff check --fix ." && cd frontend && npm run lint
gen-api:       ; cd frontend && npm run gen:api
