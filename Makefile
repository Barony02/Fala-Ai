# Makefile
.PHONY: up down build logs tests

up:
	docker compose up -d

down:
	docker compose down

build:
	docker compose up -d --build

logs:
	docker compose logs -f

tests:
	docker compose exec backend env PYTHONPATH=. pytest tests/unit-tests/ -v