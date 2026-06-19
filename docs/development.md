# 開発ガイド

## 開発環境の構築

### 前提条件

| ツール | 最低バージョン | 用途 |
|---|---|---|
| Docker Desktop | 最新推奨 | コンテナ実行環境 |
| GNU Make | 3.81+ | タスクランナー |
| Python | 3.12 | ローカルの lint 実行 |
| uv | 最新推奨 | ローカルの lint ツールインストール |
| Node.js (任意) | 18+ | `npx openapi-markdown` による API ドキュメント生成 |

---

## Windows での実行方法

このプロジェクトは `Makefile` をタスクランナーとして使用している。Windows では `make` がデフォルトで利用できないため、以下のいずれかの方法で対応すること。

### 方法 A: make をインストールして使う（推奨）

**Chocolatey を使う場合**（PowerShell を管理者権限で実行）:
```powershell
choco install make
```

**Scoop を使う場合**:
```powershell
scoop install make
```

インストール後はターミナルを再起動し、通常通り `make <target>` を実行できる。

### 方法 B: PowerShell で直接実行する

`make` をインストールしない場合は、以下の PowerShell コマンドを使用する。

> `$DEV_COMPOSE` は共通変数として最初に定義しておくと便利。

```powershell
$DEV_COMPOSE = "docker compose -f ./docker/dev/docker-compose.yml --env-file .env.local"
```

#### コード品質

| Makefile | PowerShell 相当 |
|---|---|
| `make fmt` | `uvx black .` |
| `make lint` | `uvx ruff check .` |

#### イメージビルド

| Makefile | PowerShell 相当 |
|---|---|
| `make build-base` | `docker build -f ./docker/base/Dockerfile -t karynos/be-python-base:latest .` |
| `make build` | `Invoke-Expression "$DEV_COMPOSE build"` |

#### Docker 起動 / 停止

`make up` は複数のステップを順に実行する。以下を順番に実行すること:

```powershell
# 1. コンテナ起動
Invoke-Expression "$DEV_COMPOSE up -d"

# 2. Prisma クライアント再生成
Invoke-Expression "$DEV_COMPOSE run --rm --no-deps backend-app sh -c 'prisma generate --schema /app/app/gen/prisma/schema.prisma && prisma py fetch'"

# 3. DB データインポート
Invoke-Expression "$DEV_COMPOSE run --rm backend-app python /app/db/import/import_from_gdrive.py"

# 4. Qdrant 同期
Invoke-Expression "$DEV_COMPOSE run --rm backend-app sh -c 'PYTHONPATH=/app python /app/scripts/sync-job-vectordb.py'"
```

| Makefile | PowerShell 相当 |
|---|---|
| `make down` | `Invoke-Expression "$DEV_COMPOSE down"` |

#### Shell アクセス / ログ

| Makefile | PowerShell 相当 |
|---|---|
| `make shell-app` | `Invoke-Expression "$DEV_COMPOSE exec backend-app sh"` |
| `make shell-db` | `Invoke-Expression "$DEV_COMPOSE exec karynos-db psql -U karynos -d karynos"` |
| `make logs` | `Invoke-Expression "$DEV_COMPOSE logs -f backend-app"` |

#### Prisma

| Makefile | PowerShell 相当 |
|---|---|
| `make prisma` | `Invoke-Expression "$DEV_COMPOSE run --rm --no-deps backend-app sh -c 'prisma generate --schema /app/app/gen/prisma/schema.prisma && prisma py fetch'"` |

#### DB データ操作

`make db-clean`（`rm -rf` は PowerShell では `Remove-Item` を使用）:

```powershell
Invoke-Expression "$DEV_COMPOSE down"
Remove-Item -Recurse -Force ./db-data/postgres
Invoke-Expression "$DEV_COMPOSE up -d"
```

| Makefile | PowerShell 相当 |
|---|---|
| `make db-import` | `Invoke-Expression "$DEV_COMPOSE run --rm backend-app python /app/db/import/import_from_gdrive.py"` |

#### Qdrant 操作

`make qdrant-clean`（`xargs` は使えないため個別に対応）:

```powershell
Invoke-Expression "$DEV_COMPOSE stop qdrant"
Invoke-Expression "$DEV_COMPOSE rm -sf qdrant"
# qdrant-data ボリュームを削除
docker volume ls --filter name=qdrant-data -q | ForEach-Object { docker volume rm $_ }
Invoke-Expression "$DEV_COMPOSE up -d qdrant"
```

| Makefile | PowerShell 相当 |
|---|---|
| `make sync-vectordb` | `Invoke-Expression "$DEV_COMPOSE run --rm backend-app sh -c 'PYTHONPATH=/app python /app/scripts/sync-job-vectordb.py'"` |
| `make sync-vectordb-rebuild` | `Invoke-Expression "$DEV_COMPOSE run --rm backend-app sh -c 'PYTHONPATH=/app python /app/scripts/sync-job-vectordb.py --rebuild'"` |

---

### 初回セットアップ

```bash
# 1. リポジトリをクローン
git clone <repo-url>
cd karynos-backend

# 2. 環境変数ファイルを作成
cp .env.example .env.local
# OPENAI_API_KEY を必ず設定すること

# 3. ベースイメージをビルド（pip インストール + Prisma CLI）
make build-base

# 4. アプリイメージをビルド
make build

# 5. 起動（DB 起動 → Prisma 再生成 → データインポート → Qdrant 同期）
make up
```

### 動作確認

```
http://localhost:8000/docs    # Swagger UI
http://localhost:8000/redoc   # ReDoc
http://localhost:6333         # Qdrant Dashboard（Web UI）
```

---

## Docker 構成

### コンテナ一覧（開発環境）

| コンテナ名 | イメージ | ポート | 役割 |
|---|---|---|---|
| `karynos-db` | `postgres:17.5` | 5432 | PostgreSQL |
| `karynos-qdrant` | `qdrant/qdrant:latest` | 6333 | ベクトル DB |
| `backend-app` | `karynos/be-python-base:latest` | 8000 | FastAPI アプリ |

### 起動・停止

```bash
make up           # バックグラウンド起動（全後続タスク含む）
make down         # 全コンテナ停止

make logs         # backend-app のログを tail
make shell-app    # backend-app に sh で入る
make shell-db     # PostgreSQL に psql で接続
```

### イメージ構成

**ベースイメージ** (`docker/base/Dockerfile`)
- `python:3.12-slim-bookworm` ベース
- `pyproject.toml` の全依存パッケージをインストール
- Prisma CLI 込み
- 変更頻度: `pyproject.toml` 変更時のみ → `make build-base`

**アプリイメージ** (`docker/dev/docker-compose.yml`)
- ベースイメージをそのまま利用し、ソースコードをボリュームマウント (`..:/app`)
- Uvicorn の `--reload` フラグでホットリロード
- 初回起動時に `scripts/start-backend-dev.sh` が実行される

### 永続ボリューム

| ボリューム名 | マウント先 | 用途 |
|---|---|---|
| `prisma-binary` | `/root/.cache/prisma-python` | Prisma クエリエンジンバイナリ |
| `qdrant-data` | `/qdrant/storage` | Qdrant データ |
| `../../db-data/postgres` | `/var/lib/postgresql/data` | PostgreSQL データ（ホストパス） |

### Qdrant データのリセット

```bash
make qdrant-clean    # コンテナ停止 → 削除 → ボリューム削除 → 再起動
make sync-vectordb-rebuild    # 全件再構築（Qdrant が空のときに使用）
```

---

## Prisma

### クライアント再生成

`app/gen/prisma/schema.prisma` を変更した後に実行する。

```bash
make prisma
# → コンテナ内で以下を実行:
#   prisma generate --schema /app/app/gen/prisma/schema.prisma
#   prisma py fetch
```

`prisma py fetch` は Prisma クエリエンジンバイナリをダウンロードする（`prisma-binary` ボリュームに永続化）。

### バイナリのトラブルシューティング

ARM64 (Apple M シリーズ) 環境で CDN からのバイナリ取得が 403 になる場合は `scripts/ensure-prisma-binary.py` が Node.js 経由で再試行する（起動スクリプトが自動実行）。

---

## Lint / Format

CI は `develop` / `main` への push および PR で自動実行される。
ローカルでも **Push 前に必ず実行** すること。

### Black（フォーマッター）

```bash
# チェックのみ（CI と同じ）
uvx black --check .

# 自動修正
uvx black .
```

設定: `pyproject.toml` の `[tool.black]` セクション（行長 88、`app/gen` 除外）。

### Ruff（リンター）

```bash
# チェックのみ（CI と同じ）
uvx ruff check .

# 自動修正
uvx ruff check --fix .
```

設定: `pyproject.toml` の `[tool.ruff]`（TODO: 現時点では設定セクションが未設定のためデフォルト）。キャッシュは `.ruff_cache/` に保存される。

### 型チェック（未導入）

mypy / pyright は現時点で CI に含まれていない。導入する場合は以下を参照。

```bash
# 例: pyright を使う場合
pip install pyright
pyright app/
```

---

## テスト（未導入）

テストコードが存在しない。導入する場合は `pytest` を推奨する。

```bash
# 例: インストール
pip install pytest pytest-asyncio

# 実行
pytest tests/
```

---

## OpenAPI スキーマ管理

```bash
# openapi.json を最新化（エンドポイント変更時は必ず実行）
PYTHONPATH=. python openapi.py
# → openapi.json を上書き
# → karynos-backend-client/ を再生成

# API ドキュメントを生成（Node.js が必要）
npx openapi-markdown openapi.json > docs/api.md
```

`openapi.json` はリポジトリにコミットする。エンドポイント追加・変更時は **コミット前に再生成** すること。

---

## CI/CD

### GitHub Actions ワークフロー

**ファイル**: `.github/workflows/ci.yml`

**トリガー**:
- `develop` / `main` への push
- `develop` / `main` への Pull Request

**ジョブ**:

```
lint-and-format
  ├── actions/checkout@v4
  ├── actions/setup-python@v5 (Python 3.12)
  ├── astral-sh/setup-uv@v4 (最新版)
  ├── Black format check (uvx black --check .)
  └── Ruff lint check (uvx ruff check .)
```

### 現在の品質ゲート

| チェック | 自動 (CI) | 手動推奨 |
|---|---|---|
| Black フォーマット | ✅ | ✅ |
| Ruff lint | ✅ | ✅ |
| テスト | ❌ 未導入 | — |
| 型チェック | ❌ 未導入 | — |
| Docker build | ❌ 未導入 | ✅ |
| openapi.json 更新 | ❌ 未導入 | ✅ |
| DB スキーマ整合性 | ❌ 未導入 | ✅ |

### PR 前の確認事項

1. `uvx black --check .` が通ること
2. `uvx ruff check .` が通ること
3. エンドポイント変更時は `PYTHONPATH=. python openapi.py` を実行し `openapi.json` をコミットすること
4. `db/init.sql` を変更した場合は `app/gen/prisma/schema.prisma` も同期させること
5. `pyproject.toml` の依存を変更した場合は `make build-base` でベースイメージを再ビルドすること

---

## デプロイ手順

### 本番環境（TODO: 要整備）

`docker/prod/docker-compose.yml` に本番用 Compose ファイルが存在するが、以下の点が未整備。

- Qdrant サービスが **含まれていない**（dev との差異）
- `.env` ファイル（本番用シークレット）の管理方法が未定義
- `ChromaDB` ボリュームの記述が残っている（旧仕様の残滓）

本番環境にデプロイする前に以下を確認すること。

1. `.env` ファイルに本番用 `OPENAI_API_KEY` と DB 認証情報を設定
2. `docker/prod/docker-compose.yml` に Qdrant サービスを追加
3. `make build-base` でイメージをビルドし、レジストリに push
4. サーバー上で `docker compose -f docker/prod/docker-compose.yml up -d` を実行

### 起動スクリプトの違い

| 環境 | スクリプト | uvicorn オプション |
|---|---|---|
| 開発 | `scripts/start-backend-dev.sh` | `--reload` 付き |
| 本番 | `scripts/start-backend.sh` | リロードなし |

---

## デバッグ

### ログ確認

```bash
make logs    # docker compose logs -f backend-app
```

### コンテナに入る

```bash
make shell-app   # sh /app 配下で自由に操作可
```

### Prisma クエリのデバッグ

```bash
# コンテナ内で環境変数を設定してから起動
DEBUG=* uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### DB の直接確認

```bash
make shell-db
# psql プロンプトが開く
\dt           # テーブル一覧
\d jobs       # jobs テーブルの定義
SELECT * FROM jobs LIMIT 5;
```
