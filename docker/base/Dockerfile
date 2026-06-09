FROM python:3.12-slim-bookworm

LABEL org.opencontainers.image.title="karynos-be-python-base"
LABEL org.opencontainers.image.description="Python base image: all pip packages + Prisma CLI"

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends libatomic1 \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir .
