#!/bin/sh
set -eu

export PYTHONPATH=/app

mkdir -p "${CHROMA_PERSIST_DIRECTORY:-/app/ChromaDB}"

exec uvicorn app.main:app --host 0.0.0.0 --port 8000
