.PHONY: up down run-api run-worker test

up:
	docker-compose up -d

down:
	docker-compose down

run-api:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-worker:
	cd backend && python -m app.worker

test:
	cd backend && pytest -v tests/
