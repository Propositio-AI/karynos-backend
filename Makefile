COMPOSE_FILE := ./docker/dev/docker-compose.yml
COMPOSE := docker compose -f $(COMPOSE_FILE)

.PHONY: run up down logs build-backend prisma openapi sync-job-vectordb

run:
	$(COMPOSE) up --build

up:
	$(COMPOSE) up -d --build

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f backend-app

build-backend:
	$(COMPOSE) build backend-app

prisma: build-backend
	$(COMPOSE) run --rm --no-deps backend-app prisma generate --schema /app/app/gen/prisma/schema.prisma

openapi: build-backend
	$(COMPOSE) run --rm --no-deps backend-app python /app/openapi.py

sync-job-vectordb: build-backend
	$(COMPOSE) run --rm backend-app sh -lc "set -e; export CHROMA_PERSIST_DIRECTORY=$${CHROMA_PERSIST_DIRECTORY:-/app/ChromaDB}; prisma generate --schema /app/app/gen/prisma/schema.prisma; PYTHONPATH=/app python /app/scripts/sync_job_chromadb.py"
