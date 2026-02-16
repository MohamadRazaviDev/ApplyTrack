.PHONY: install-backend install-frontend run-backend run-frontend run-worker test lint seed docker-up

# ── Install ──
install-backend:
	cd backend && python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt

install-frontend:
	cd frontend && npm install

# ── Run (local dev) ──
run-backend:
	cd backend && . .venv/bin/activate && uvicorn applytrack.main:app --reload

run-frontend:
	cd frontend && npm run dev

run-worker:
	cd backend && . .venv/bin/activate && celery -A applytrack.workers.celery_app worker --loglevel=info

# ── Docker ──
docker-up:
	docker compose up --build

# ── Quality ──
test:
	cd backend && . .venv/bin/activate && pytest

lint:
	cd backend && . .venv/bin/activate && ruff check src/ tests/ --fix
	cd backend && . .venv/bin/activate && ruff format src/ tests/

# ── Data ──
seed:
	cd backend && . .venv/bin/activate && python -m applytrack.seed
