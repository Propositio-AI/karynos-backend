#!/bin/sh
set -eu

export PYTHONPATH=/app

mkdir -p "${CHROMA_PERSIST_DIRECTORY:-/app/ChromaDB}"

# Prisma バイナリ確認 (なければ1回だけ取得 → named volume に永続化)
python3 /app/scripts/ensure-prisma-binary.py

exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
