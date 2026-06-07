# karynos-backend

[システム設計](https://www.notion.so/Karynos-backend-module-1b39a9038f388050816afe733aa3cdfc?source=copy_link)

## フォルダ構成

```
├─app                             // 統合 FastAPI アプリ
│  ├─router                       // ドメイン別ルータ
│  ├─gateways                     // DB ゲートウェイ公開層
│  ├─schemas                      // ルート集約スキーマ
│  └─services                     // 既存実装を保った各機能群
├─algorithm                       // レコメンド・探索ロジック
├─backend                         // 共通ライブラリ・ユーティリティ
├─db                              // 単一DB初期化・データ投入
│  ├─init.sql                     // 全テーブル定義（初回のみ実行）
│  └─import
│     ├─import_from_gdrive.py     // Google Drive CSV -> DBインポート
│     └─table_sources.json        // テーブルごとのCSV URL設定
├─db-data                         // PostgreSQL 永続ボリューム
├─docker                          // docker-compose関連
│  ├─dev                          // 開発用
│  └─prod                         // 本番用
├─migrations                      // マイグレーション関連
├─shared                          // Prisma スキーマなど移行中の共有資産
└─services                        // 旧構成の参照用コピー
```

## 環境構築方法
1. ### Gitからダウンロード

    ```cmd
    git clone https://github.com/Propositio-AI/karynos-backend.git
    cd karynos-backend
    ```

2. ### .envファイルのダウンロード

    ルートの `.env.local` を配置してください。最低限、以下があれば統合バックエンドは起動できます。

    ```env
    APP_NAME=karynos-backend
    DATABASE_URL=postgresql://karynos:karynos@karynos-db:5432/karynos
    CORS_ORIGINS=http://localhost:3000
    ```

3. ### 共通イメージのビルド

    ```cmd
    docker build -t karynos/be-python-base:latest -f ./docker/python-base.Dockerfile .
    ```

## 開発環境の起動方法

```cmd
docker compose -f ./docker/dev/docker-compose.yml up --build
```

または Make コマンドで Docker 実行に統一できます。

```cmd
make run
```

`backend-app` は `shared/prisma/schema.prisma` のハッシュを見て、変更があったときだけ `prisma generate` を実行します。
強制的に再生成したい場合は `FORCE_PRISMA_GENERATE=1` を指定して起動してください。

## 新しいアーキテクチャ（単一DB + 単一バックエンド + Prisma）

- DBは `karynos-db` の1コンテナのみです。
- 初回起動時に `db/init.sql` が自動実行され、全テーブルが作成されます。
- `db-csv-import` が `db/import/table_sources.json` を読み、Google Drive CSVをインポートします。
- `backend-app` が `app.main:app` を起動し、`/job` `/dreamer` `/mentor` `/organization` `/chat` を1プロセスで提供します。
- Prisma Client Python は `shared/prisma/schema.prisma` をソースに生成します。

## Google Drive CSVインポート設定

1. `db/import/table_sources.json` の `REPLACE_WITH_FILE_ID` を実ファイルIDに置換
2. CSVヘッダーはDBのカラム名と一致させる
3. 既存データがあるテーブルはデフォルトでスキップ（`truncate: true` の場合は再投入）

## 環境変数（単一DB）

`docker/dev/docker-compose.yml` では以下を利用します（未指定時はデフォルト値あり）。

- `KARYNOS_DB_SERVER_NAME`
- `KARYNOS_DB_USER`
- `KARYNOS_DB_PASSWORD`
- `KARYNOS_DB_NAME`
- `KARYNOS_DB_PORT`
- `CHROMA_PERSIST_DIRECTORY`（既定: `/app/ChromaDB`）

## 補足

- `app/`, `backend/`, `algorithm/` が新しいルート構成です。
- `services/` と `shared/` には移管元コードも残してあり、差分確認や段階的削除に使えます。

## Docker 内での開発用コマンド

以下はすべて Docker コンテナ内で実行されます。

1. Prisma Client の生成

```cmd
make prisma
```

1. OpenAPI 設定ファイル（`openapi.json`）の生成

```cmd
make openapi
```

1. 職業データから ChromaDB（ベクトルDB）を再構築

```cmd
make sync-job-vectordb
```

1. Google Drive CSV からDBへ再インポート

```cmd
docker compose -f ./docker/dev/docker-compose.yml run --rm db-csv-import
```

1. バックグラウンド起動・停止・ログ

```cmd
make up
make logs
make down
```

## Windows (PowerShell) 用コマンド

Windows で `make` が使えない場合は、以下の `docker compose` を直接実行してください。

1. Prisma Client の生成

```powershell
docker compose -f .\docker\dev\docker-compose.yml build backend-app
docker compose -f .\docker\dev\docker-compose.yml run --rm --no-deps backend-app prisma generate --schema /app/app/gen/prisma/schema.prisma
```

1. OpenAPI 設定ファイル（`openapi.json`）の生成

```powershell
docker compose -f .\docker\dev\docker-compose.yml build backend-app
docker compose -f .\docker\dev\docker-compose.yml run --rm --no-deps backend-app python /app/openapi.py
```

1. 職業データから ChromaDB（ベクトルDB）を再構築

```powershell
docker compose -f .\docker\dev\docker-compose.yml build backend-app
docker compose -f .\docker\dev\docker-compose.yml run --rm backend-app sh -lc "set -e; prisma generate --schema /app/app/gen/prisma/schema.prisma; PYTHONPATH=/app python /app/scripts/sync_job_chromadb.py"
```

1. Google Drive CSV からDBへ再インポート

```powershell
docker compose -f .\docker\dev\docker-compose.yml run --rm db-csv-import
```

1. 起動・ログ・停止

```powershell
docker compose -f .\docker\dev\docker-compose.yml up -d --build
docker compose -f .\docker\dev\docker-compose.yml logs -f backend-app
docker compose -f .\docker\dev\docker-compose.yml down
```

## 共通イメージの内容

```
FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir .
```

