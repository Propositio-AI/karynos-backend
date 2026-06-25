# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

See README.md for
project overview/setup; this file covers architecture, workflows, and gotchas.

## Architecture

Request flow: **Router → Service → Gateway → Prisma → PostgreSQL**, with
`Algorithm` (pure compute, no I/O) and the OpenAI client as side branches off
Service. Five domains: Dreamer, Onboarding, Matching, Job, Chat. Domains must
not depend on each other directly — cross-domain access goes through a
Gateway.

- **GatewayResult convention**: every DB-layer call returns
  `{"success", "message", "data"}`. The Service layer inspects this and
  raises `HTTPException` on failure — gateways never raise HTTP errors
  themselves.
- **Sync-over-async bridge**: FastAPI endpoints are defined as sync `def`,
  but Prisma Client Python is async-only. `app/gateways/db/prisma_client.py`
  runs a background event loop in a separate thread and bridges calls via
  `asyncio.run_coroutine_threadsafe`. Be careful when touching this file.
- `app/algorithm/` is expected to stay side-effect-free (pure functions) —
  this is a convention, not enforced by tooling/CI.
- DB: PostgreSQL 17.5. `db/init.sql` is the single source of truth for
  schema (Alembic is present in the repo but currently unused/dormant).
  Prisma Client Python is the ORM. Vector search uses Qdrant
  (1536-dim embeddings, `text-embedding-3-small`).
- Documented known gaps: no real auth (a dummy UUID stands in), no automated
  test suite yet, no type-checking in CI, Chat service bypasses the Gateway
  via its own HTTP API, and the prod docker-compose config lacks Qdrant.

## Dev Commands

There is no automated test suite yet — don't assume `pytest` is wired up.

- Format: `uvx black .` (check only: `uvx black --check .`) — line-length 88,
  excludes `app/gen`.
- Lint: `uvx ruff check .` (autofix: `uvx ruff check --fix .`) — rules
  `E,F,I,UP`; `E501` ignored.
- Makefile targets: `fmt`, `lint`, `build-base`, `build`, `up`, `down`,
  `shell-app`, `shell-db`, `logs`, `prisma`, `db-clean`, `db-import`,
  `qdrant-clean`, `sync-vectordb`, `sync-vectordb-rebuild`.

## Required Environment Variables

`DB_USER`, `DB_PASS`, `DB_HOST`, `DB_PORT`, `DB_NAME`, `OPENAI_API_KEY`.
(Everything else in docs/environment-variables.md has a default.)

## CI

`.github/workflows/ci.yml` ("Lint & Format") runs on push/PR to
`develop`/`main`: checkout → setup-python 3.12 → setup-uv → install
black/ruff via `uv tool install` → `uvx black --check .` →
`uvx ruff check .`. There is no test, type-check, build, or deploy step in
CI currently — don't assume changes are tested automatically.

## Important: `services/` vs `app/services/` — do not confuse these

There are two directories that look similar but are NOT related:

- **`app/services/`** (chat, dreamer, job, matching, onboarding) is the
  real, git-tracked business-logic layer used in the
  Router → Service → Gateway flow described above. This is what you should
  be editing.
- **Top-level `services/`** (`chat_service`, `dreamer_service`,
  `job_service`, `mentor_service`, `organization_service`,
  `textbook_service`) is **stale leftover code from a previous
  microservices-style architecture, not active microservices**.
  - The repo's `pyproject.toml` description literally says: "Unified
    backend application migrated from service-based structure" — confirming
    these per-domain services were consolidated into the current monolith.
  - This directory is **entirely untracked by git** (the karynos-backend
    repo itself has origin `Propositio-AI/karynos-backend`).
  - Subdirectories contain no `pyproject.toml`, `Dockerfile`, or `README` —
    just leftover `.env`-style files (e.g. `.job_env`, `.chat_env`),
    `.DS_Store`, and stale local Postgres data dirs (`db-data/` with
    `PG_VERSION`, `pg_wal`, etc.).
  - Python source is largely gone — e.g. `services/job_service/app/route/`
    only has compiled `.pyc` files in `__pycache__`, no `.py` source left.
  - These are not git submodules (no `.gitmodules`, no nested `.git` dirs).

**Do not write new code into top-level `services/`.** If asked to clean up
the repo, this directory is a reasonable candidate for deletion — confirm
with the user first since it contains live-looking (if stale) DB data
directories.

## Cursor / Copilot Rules

None present — no `.cursor/rules/`, `.cursorrules`, or
`.github/copilot-instructions.md` exist in this repo.
