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

reset:
	@echo "ATENÇÃO: Isso apagará permanentemente todos os dados do banco de dados!"
	@read -p "Você tem certeza que deseja continuar? [s/N]: " resposta; \
	if [ "$$resposta" = "s" ] || [ "$$resposta" = "S" ]; then \
		echo "Iniciando limpeza e reconstrução..."; \
		docker compose down -v; \
		docker compose up --build; \
	else \
		echo "Operação cancelada pelo usuário."; \
	fi