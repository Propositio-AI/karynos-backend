# 環境変数

環境変数は `.env.local`（開発）または `.env`（本番）に定義し、Docker Compose の `env_file` ディレクティブ経由でコンテナに渡される。

テンプレートファイル: `.env.example`

---

## 一覧

### アプリケーション設定

| 変数名 | 必須 | デフォルト | 説明 | 利用箇所 |
|---|---|---|---|---|
| `APP_NAME` | 任意 | `karynos-backend` | FastAPI アプリ名（Swagger UI タイトル） | `settings.py` |
| `CORS_ORIGINS` | 任意 | `http://localhost:3000` | 許可する CORS オリジン（カンマ区切り複数指定可） | `settings.py` → `app/main.py` |

### PostgreSQL（コンテナ設定用）

以下は Docker Compose が PostgreSQL コンテナを起動する際に使用する。

| 変数名 | 必須 | デフォルト | 説明 |
|---|---|---|---|
| `POSTGRES_USER` | 任意 | `karynos` | PostgreSQL の初期ユーザー名 |
| `POSTGRES_PASSWORD` | 任意 | `karynos` | PostgreSQL の初期パスワード |
| `POSTGRES_DB` | 任意 | `karynos` | 初期データベース名 |
| `POSTGRES_SERVER` | 任意 | `karynos-db` | コンテナ名（`container_name` に使用） |

### PostgreSQL（アプリ接続設定）

以下は `settings.py` の `Settings` クラスが読み込む。すべて **必須**。

| 変数名 | 必須 | デフォルト | 説明 | 利用箇所 |
|---|---|---|---|---|
| `DB_USER` | **必須** | — | DB 接続ユーザー | `settings.py` |
| `DB_PASS` | **必須** | — | DB 接続パスワード | `settings.py` |
| `DB_HOST` | **必須** | — | DB ホスト名（コンテナ名: `karynos-db`） | `settings.py` |
| `DB_PORT` | **必須** | — | DB ポート（通常: `5432`） | `settings.py` |
| `DB_NAME` | **必須** | — | DB 名（通常: `karynos`） | `settings.py` |
| `DATABASE_URL` | 任意 | `settings.database_url` で構築 | Prisma が直接参照する接続 URL | Prisma スキーマ |

> `DATABASE_URL` は `settings.py` の `database_url` プロパティが `DB_*` 変数から自動構築するが、Prisma はスキーマで直接 `env("DATABASE_URL")` を参照するため明示的に設定すること。

### Qdrant

| 変数名 | 必須 | デフォルト | 説明 | 利用箇所 |
|---|---|---|---|---|
| `QDRANT_HOST` | 任意 | `qdrant` | Qdrant のホスト名（コンテナ名） | `app/algorithm/job_suggestion/recommendation.py` |
| `QDRANT_PORT` | 任意 | `6333` | Qdrant の HTTP ポート | 同上 |
| `QDRANT_JOB_COLLECTION` | 任意 | `job_vector_db` | 職業ベクトルを保存するコレクション名 | 同上 |

### OpenAI

| 変数名 | 必須 | デフォルト | 説明 | 利用箇所 |
|---|---|---|---|---|
| `OPENAI_API_KEY` | **必須** | — | OpenAI API キー | `app/services/chat/openai_client.py`, `app/algorithm/job_suggestion/recommendation.py` |
| `OPENAI_CHAT_MODEL` | 任意 | `gpt-4o` | チャット用モデル ID | `app/services/chat/openai_client.py` |
| `OPENAI_EMBEDDING_MODEL` | 任意 | `text-embedding-3-small` | ベクトル化用モデル ID | `app/algorithm/job_suggestion/recommendation.py` |

### CSV インポート

| 変数名 | 必須 | デフォルト | 説明 | 利用箇所 |
|---|---|---|---|---|
| `CSV_IMPORT_CONFIG_JSON` | 任意 | `/app/db/import/table_sources.json` | インポート設定 JSON のパス | `db/import/import_from_gdrive.py` |
| `CSV_IMPORT_SKIP_IF_TABLE_HAS_DATA` | 任意 | `true` | テーブルにデータがある場合スキップ | 同上 |

### その他（参考）

| 変数名 | 説明 |
|---|---|
| `PRISMA_QUERY_ENGINE_BINARY` | Prisma クエリエンジンバイナリのパス。起動スクリプト (`prisma_client.py`) が自動設定するため通常は不要。 |
| `CHROMA_PERSIST_DIRECTORY` | 旧 ChromaDB のデータディレクトリ。起動スクリプトが `mkdir -p` するが現在は未使用。 |

---

## .env.local の最小構成（開発）

```env
# ── アプリ
APP_NAME=Karynos-Backend
CORS_ORIGINS=http://localhost:3000

# ── PostgreSQL（コンテナ設定）
POSTGRES_USER=karynos
POSTGRES_PASSWORD=karynos
POSTGRES_DB=karynos

# ── PostgreSQL（アプリ接続）
DB_USER=karynos
DB_PASS=karynos
DB_HOST=karynos-db
DB_PORT=5432
DB_NAME=karynos
DATABASE_URL=postgresql://karynos:karynos@karynos-db:5432/karynos

# ── Qdrant
QDRANT_HOST=qdrant
QDRANT_PORT=6333
QDRANT_JOB_COLLECTION=job_vector_db

# ── CSV インポート
CSV_IMPORT_CONFIG_JSON=/app/db/import/table_sources.json
CSV_IMPORT_SKIP_IF_TABLE_HAS_DATA=true

# ── OpenAI（必須）
OPENAI_CHAT_MODEL=gpt-4o
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
```

---

## 注意事項

- `.env.local` および `.env` は `.gitignore` で管理されているため、**絶対にコミットしないこと**。
- `OPENAI_API_KEY` の漏洩に注意する。ローカル以外の環境では Secrets Manager 等を利用すること。
- `OPENAI_CHAT_MODEL` / `OPENAI_EMBEDDING_MODEL` を変更する場合、埋め込みモデルのベクトル次元数（`_VECTOR_DIM = 1536`）が変わる場合は Qdrant コレクションを再構築すること (`make qdrant-clean && make sync-vectordb-rebuild`)。
