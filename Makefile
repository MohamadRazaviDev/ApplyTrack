.PHONY: install-backend install-frontend run-backend run-frontend

install-backend:
	cd backend && pip install poetry && poetry install

install-frontend:
	cd frontend && npm install

run-backend:
	cd backend && poetry run uvicorn applytrack.main:app --reload

run-frontend:
	cd frontend && npm run dev

test-backend:
	cd backend && poetry run pytest

lint:
	cd backend && poetry run black .
	cd backend && poetry run isort .
