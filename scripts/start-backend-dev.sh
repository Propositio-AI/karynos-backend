#!/bin/sh
set -eu

SCHEMA_PATH="/app/app/gen/prisma/schema.prisma"
CACHE_DIR="/var/cache/karynos"
HASH_FILE="${CACHE_DIR}/prisma-schema.sha256"
CURRENT_HASH="$(sha256sum "${SCHEMA_PATH}" | awk '{print $1}')"
CHROMA_DIR="${CHROMA_PERSIST_DIRECTORY:-/app/ChromaDB}"

mkdir -p "${CACHE_DIR}"
mkdir -p "${CHROMA_DIR}"

if [ "${FORCE_PRISMA_GENERATE:-0}" = "1" ] || [ ! -f "${HASH_FILE}" ] || [ "$(cat "${HASH_FILE}")" != "${CURRENT_HASH}" ]; then
    echo "[startup] Prisma schema changed or cache missing. Running prisma generate..."
    python /app/scripts/generate_prisma_artifacts.py
    printf "%s" "${CURRENT_HASH}" > "${HASH_FILE}"
else
    echo "[startup] Prisma schema unchanged. Skipping prisma generate."
fi

exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
