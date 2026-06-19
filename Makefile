BASE_IMAGE      := karynos/be-python-base:latest
BASE_DOCKERFILE := ./docker/base/Dockerfile

DEV_COMPOSE := docker compose -f ./docker/dev/docker-compose.yml --env-file .env.local

SCHEMA_PATH := /app/app/gen/prisma/schema.prisma

.PHONY: build-base build up down shell-app shell-db logs prisma db-clean db-import sync-vectordb sync-vectordb-rebuild qdrant-clean fmt lint seed test

# ────────────────────────────────────────────
# イメージビルド
# ────────────────────────────────────────────

# ────────────────────────────────────────────
# コード品質
# ────────────────────────────────────────────

## コードフォーマット (Black)
fmt:
	uvx black .

## Lint チェック (Ruff)
lint:
	uvx ruff check .

# ────────────────────────────────────────────
# イメージビルド
# ────────────────────────────────────────────

## ベースイメージをビルド (pip + Prisma binary) — pyproject.toml 変更時に実行
build-base:
	docker build -f $(BASE_DOCKERFILE) -t $(BASE_IMAGE) .

## docker-compose サービスイメージをビルド
build:
	$(DEV_COMPOSE) build

# ────────────────────────────────────────────
# Docker 起動 / 停止
# ────────────────────────────────────────────

## コンテナ起動 → Prisma 再生成 → DB インポート → Qdrant 同期
up:
	$(DEV_COMPOSE) up -d
	$(MAKE) prisma
	$(MAKE) db-import
	$(MAKE) sync-vectordb

## コンテナ停止
down:
	$(DEV_COMPOSE) down

# ────────────────────────────────────────────
# Shell アクセス
# ────────────────────────────────────────────

## backend-app コンテナに入る
shell-app:
	$(DEV_COMPOSE) exec backend-app sh

## karynos-db コンテナに入る
shell-db:
	$(DEV_COMPOSE) exec karynos-db psql -U karynos -d karynos

# ────────────────────────────────────────────
# ログ監視
# ────────────────────────────────────────────

## backend-app のログをフォロー
logs:
	$(DEV_COMPOSE) logs -f backend-app

# ────────────────────────────────────────────
# Prisma
# ────────────────────────────────────────────

## Prisma クライアント再生成 — schema.prisma 変更後に実行
prisma:
	$(DEV_COMPOSE) run --rm --no-deps backend-app \
	  sh -c "prisma generate --schema $(SCHEMA_PATH) && prisma py fetch"

# ────────────────────────────────────────────
# DB データ操作
# ────────────────────────────────────────────

## DB データを削除 (コンテナ停止 → db-data 削除 → コンテナ再起動)
db-clean:
	$(DEV_COMPOSE) down
	rm -rf ./db-data/postgres
	$(DEV_COMPOSE) up -d

## Google Drive から DB にデータをインポート
db-import:
	$(DEV_COMPOSE) run --rm backend-app python /app/db/import/import_from_gdrive.py

## Qdrant のデータをすべて削除してコンテナを再起動（モデル変更時などに使用）
qdrant-clean:
	$(DEV_COMPOSE) stop qdrant
	$(DEV_COMPOSE) rm -sf qdrant
	@docker volume ls -qf name=qdrant-data | xargs -r docker volume rm
	$(DEV_COMPOSE) up -d qdrant

## 職業データを Qdrant に差分同期（make up から自動呼び出し）
sync-vectordb:
	$(DEV_COMPOSE) run --rm backend-app sh -c "PYTHONPATH=/app python /app/scripts/sync-job-vectordb.py"

## 職業データを Qdrant に全件再構築（スキーマ変更・データ完全刷新時）
sync-vectordb-rebuild:
	$(DEV_COMPOSE) run --rm backend-app sh -c "PYTHONPATH=/app python /app/scripts/sync-job-vectordb.py --rebuild"

## 開発用シードデータ投入（Mentor / Class / Dreamer / Enrollment / LessonMaterial）
seed:
	$(DEV_COMPOSE) run --rm backend-app sh -c "PYTHONPATH=/app python /app/scripts/seed_dev_data.py"

## ユニットテスト実行
test:
	$(DEV_COMPOSE) run --rm --no-deps backend-app sh -c "PYTHONPATH=/app python -m pytest tests/ -v"
