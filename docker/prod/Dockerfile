# 本番用アプリイメージ (karynos/be-app)
#
# 設計方針:
# - 自己完結型 (FROM python:3.12-slim-bookworm)。ベースイメージ
#   (karynos/be-python-base) の事前ビルドに依存しないため、EC2 上で
#   `git pull` → `docker compose build` だけで完結する。
# - 生成済み Prisma クライアント (app/gen/prisma) は Git 管理されているので
#   ビルド時の再生成は必須ではないが、インストールされた prisma CLI との
#   バージョン整合を取るため `prisma generate` を実行する。
# - Prisma クエリエンジンのバイナリは gitignore されているため、ビルド時に
#   取得してイメージへ焼き込む (実行時にネットワークが不要になる)。
# - レイヤキャッシュ最適化: 依存解決 (pyproject.toml) を先に行い、アプリ
#   コードの COPY を後段に置く。コードのみの変更では pip install が再実行
#   されない。

FROM python:3.12-slim-bookworm

LABEL org.opencontainers.image.title="karynos-be-app"
LABEL org.opencontainers.image.description="Karynos backend (FastAPI) production image"

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

# Prisma クエリエンジンの実行に libatomic1 が必要。ca-certificates は
# エンジンバイナリのダウンロード (HTTPS) に必要。
RUN apt-get update \
    && apt-get install -y --no-install-recommends libatomic1 ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 1) 依存解決 (pyproject.toml 変更時のみ再実行されるレイヤ)
COPY pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir .

# 2) アプリコード一式 (committed Prisma client は app/gen/prisma に含まれる)
COPY . .

# Windows でチェックアウトされた場合の CRLF 改行を正規化する。
# dash は行末の \r を解釈できず起動スクリプトが落ちるため、必ず LF に揃える。
RUN sed -i 's/\r$//' /app/scripts/*.sh

# 3) Prisma クライアント生成 + クエリエンジンバイナリの焼き込み
#    ensure-prisma-binary.py は CDN が urllib を拒否する問題を Node.js 経由で
#    回避しつつ、native (debian) 向けエンジンを ~/.cache/prisma-python に配置する。
# DATABASE_URL はビルド時には不要 (generate は DB 接続しない) が、schema の
# env("DATABASE_URL") 解決で警告/失敗を避けるためダミー値を与える。
RUN prisma py fetch \
    && DATABASE_URL="postgresql://build:build@localhost:5432/build" \
       prisma generate --schema /app/app/gen/prisma/schema.prisma \
    && python3 /app/scripts/ensure-prisma-binary.py

EXPOSE 8000

# 本番起動スクリプト (uvicorn, --reload なし)
CMD ["sh", "/app/scripts/start-backend.sh"]
