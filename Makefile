.PHONY: up down run-api test

up:
	docker-compose up -d

down:
	docker-compose down

run-api:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000


test:
	cd backend && pytest -v tests/
