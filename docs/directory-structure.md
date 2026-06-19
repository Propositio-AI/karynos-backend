# ディレクトリ構成

```
karynos-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                   ← ルーター登録・統一エラーハンドラ
│   ├── algorithm/
│   │   └── job_suggestion/
│   │       ├── __init__.py
│   │       └── recommendation.py
│   ├── exceptions/
│   │   ├── exception.py
│   │   └── generate.py
│   ├── gateways/
│   │   ├── __init__.py
│   │   ├── chat_gateway.py
│   │   ├── dream_action_gateway.py  ← GeneratedMaterial / GenerationJob
│   │   ├── dreamer_gateway.py
│   │   ├── job_gateway.py
│   │   ├── mentor_gateway.py        ← Mentor / Class / Enrollment / LessonMaterial
│   │   ├── result.py
│   │   └── db/
│   │       ├── base_prisma_gateway.py
│   │       └── prisma_client.py
│   ├── gen/
│   │   └── prisma/               ← 自動生成（編集禁止）
│   ├── lib/
│   │   └── auth.py               ← Cognito JWT 検証・ロール判定・依存関係
│   ├── prompts/
│   │   └── dream_action/
│   │       ├── generate_material.txt   ← 補助教材生成プロンプト
│   │       └── moderation_check.txt    ← モデレーションチェックプロンプト
│   ├── router/
│   │   ├── chats.py
│   │   ├── dream_action.py       ← Dreamer 向け Dream Action エンドポイント
│   │   ├── dreamers.py
│   │   ├── jobs.py
│   │   ├── matching.py
│   │   ├── mentor.py             ← Mentor 向け全エンドポイント（Class / 生徒 / 資料 / Dream Action）
│   │   └── onboarding.py
│   ├── schemas/
│   │   ├── chats.py
│   │   ├── dreamers.py
│   │   └── jobs.py
│   ├── services/
│   │   ├── chat/
│   │   ├── dream_action/
│   │   │   ├── __init__.py
│   │   │   ├── schemas.py        ← GenerationJob / GeneratedMaterial スキーマ
│   │   │   └── service.py        ← 生成パイプライン・配布・Dreamer 向け取得
│   │   ├── dreamer/
│   │   ├── job/
│   │   ├── matching/
│   │   ├── mentor/
│   │   │   ├── schemas.py        ← Class / Student / LessonMaterial スキーマ
│   │   │   └── service.py        ← クラス管理・生徒管理・資料管理・集計
│   │   └── onboarding/
│   └── utils/
│       ├── file_storage.py       ← ファイル検証・保存・テキスト抽出
│       ├── prompt_loader.py      ← プロンプトテンプレートのロードと変数差し込み
│       └── security.py
├── db/
│   ├── init.sql                  ← スキーマの唯一の正（Mentor / Dream Action テーブル含む）
│   └── import/
├── docs/
│   ├── api.md                    ← API 仕様（エンドポイント一覧）
│   ├── architecture.md           ← システム構成・Dream Action パイプライン
│   ├── auth.md                   ← 認証・認可設計・JWT クレーム設計
│   ├── database.md               ← データモデル・ER 図
│   ├── development.md
│   ├── directory-structure.md    ← このファイル
│   └── environment-variables.md
├── docker/
├── scripts/
│   ├── seed_dev_data.py          ← 開発用シードデータ投入
│   ├── sync-job-vectordb.py
│   └── ...
├── tests/
│   ├── __init__.py
│   ├── test_auth.py              ← 認証ユーティリティのユニットテスト
│   ├── test_dream_action_service.py  ← Dream Action サービスのユニットテスト
│   └── test_mentor_service.py    ← Mentor サービスのユニットテスト
├── Makefile                      ← seed / test ターゲット追加
├── pyproject.toml
└── settings.py
```

---

## 各ディレクトリの説明

---

### `app/main.py`

**責務**: FastAPI アプリケーションインスタンスの生成・ミドルウェア設定・ルーター登録。

**依存**: `app/router/` の全ルーター、`settings.py`

**編集時の注意**:
- 新しいドメインを追加した際は `v1.include_router(...)` を追加する。
- プレフィックス (`/api/v1`) はここで一元管理されている。

---

### `app/router/`

**責務**: HTTP エンドポイントの定義、リクエスト/レスポンスの型宣言、依存注入（認証など）。

**依存**: `app/services/*/service.py`、`app/lib/auth.py`

**設計ルール**:
- ビジネスロジックを書かない。処理はすべて Service に委譲する。
- 例外は `HTTPException` として Router で catch・再 raise する。
- `response_model` は必ず宣言する。

| ファイル | エンドポイント接頭辞 | サービス |
|---|---|---|
| `chats.py` | `/api/v1/chat` | `ConversationService` |
| `dreamers.py` | `/api/v1/dreamer` | `DreamerService` |
| `jobs.py` | `/api/v1/job` | `JobService` |
| `matching.py` | `/api/v1/matching` | `MatchingService` |
| `onboarding.py` | `/api/v1/onboarding` | `OnboardingService` |

---

### `app/services/`

**責務**: ビジネスロジックの実装。複数 Gateway の呼び出し調整、データ変換、例外の HTTPException への変換。

**依存**: `app/gateways/`、`app/algorithm/`（matching のみ）、外部 API（chat のみ）

**設計ルール**:
- 直接 Prisma を呼び出さない。必ず Gateway を経由する。
- 各サービスはモジュール末尾でシングルトンインスタンスを生成する（例: `dreamer_service = DreamerService()`）。
- ドメイン間の直接依存を持たない。他ドメインのデータが必要な場合は Gateway 経由でアクセスする。

#### `services/dreamer/`
Dreamer（ユーザー）エンティティとグループの CRUD。認証・診断・マッチングの責任は持たない。

#### `services/onboarding/`
初期診断フロー専用。質問の取得・回答の保存・回答履歴の取得のみ担当する。Matching との結合を避けるため独立モジュールとして設計されている。

#### `services/matching/`
マッチング専用。Onboarding の回答と閲覧履歴を Gateway 経由で取得し、`RuleBasedProfileGenerator` でプロファイルを生成し、`VectorSearchRecommender` で類似職業を返す。

#### `services/job/`
職業情報の取得・閲覧履歴・テキスト意味検索・Qdrant 同期（管理者機能）を担当する。プロファイルベースの推薦（マッチング）は担当しない。

#### `services/chat/`
AI チャット専用。会話・メッセージの CRUD と OpenAI Streaming 応答の管理。

| ファイル | 役割 |
|---|---|
| `conversation.py` | `ConversationService` — 会話・メッセージの CRUD と AI 応答ストリーム |
| `openai_client.py` | `OpenAIClient` — OpenAI Chat Completions の非同期ラッパー |
| `context.py` | メッセージ一覧と職業データからシステムプロンプトを構築 |
| `job_api.py` | 自己 API (`http://backend-app:8000`) への HTTP 呼び出しで職業データ取得 |
| `character.py` | AI キャラクター名のランダム生成 |
| `prompts/character_prompt.txt` | AI システムプロンプトのテンプレート |
| `names.json` | 名前候補リスト（character.py が参照） |

> **注意**: `job_api.py` の自己 API 呼び出しは設計上の問題（ネットワーク RTT・起動順序依存）。将来的に Gateway 経由に変更すること。

---

### `app/gateways/`

**責務**: DB アクセスの抽象化。Prisma の非同期 API を同期的に呼び出すラッパーを提供する。すべての返り値は `GatewayResult` 型（`{"success": bool, "message": list, "data": T}`）。

**依存**: `app/gateways/db/prisma_client.py`、`app/gen/prisma/`

**設計ルール**:
- `BasePrismaGateway` を継承して各ドメインの Gateway を実装する。
- `BasePrismaGateway` が提供するメソッド: `create`, `find_many`, `update_many_and_fetch`, `delete_many_and_return_before`
- 複雑なクエリ（include / join）が必要な場合は Gateway に直接メソッドを追加する（`JobGateway.get_job` 参照）。
- Gateway は例外を握りつぶさず `{"success": False, "message": [str(exc)], "data": None}` として返す。

#### `db/prisma_client.py`

Prisma の非同期 API と FastAPI の同期エンドポイントを橋渡しするための専用スレッドイベントループを実装している。

```
FastAPI (def 関数)
    → run_prisma(coro)
        → asyncio.run_coroutine_threadsafe(coro, loop)
            → 専用デーモンスレッド上のイベントループ
                → Prisma async API
```

ARM64 環境での Prisma バイナリ自動検出（`_maybe_set_prisma_query_engine_binary`）もここで行う。

---

### `app/algorithm/`

**責務**: 純粋な計算アルゴリズム。外部 I/O（DB アクセス・HTTP リクエスト）を一切持たない。

**依存**: `qdrant-client`、`openai`（ライブラリのみ）

**編集時の注意**:
- このディレクトリに `from app.gateways import ...` や HTTP 呼び出しを追加してはならない。
- データの取得は Service 層の責任。Algorithm はデータを受け取って計算結果を返すだけ。

#### `algorithm/job_suggestion/recommendation.py`

| クラス | 役割 |
|---|---|
| `RuleBasedProfileGenerator` | 回答と閲覧履歴からプロファイルテキストを生成（純粋関数） |
| `VectorSearchRecommender` | Qdrant との接続管理・バッチベクトル化・類似検索・同期 |
| `RecommendationProcessor` | 閲覧済みジョブのフィルタリングと上位 N 件の抽出 |

> ベクトル次元数は `_VECTOR_DIM = 1536`（text-embedding-3-small のデフォルト）。モデル変更時は Qdrant コレクションの再構築が必要。

---

### `app/gen/prisma/`

**責務**: Prisma CLI が自動生成する ORM コード。

**⚠️ 編集禁止**: `make prisma` で上書きされる。手動変更は消失する。

スキーマ変更は `schema.prisma` を編集し `make prisma` を実行すること。

---

### `app/lib/`

**責務**: Router から参照するユーティリティ関数（依存注入用）。

#### `auth.py`

**現状**: `get_current_user_id()` はハードコードされた UUID `00000000-0000-0000-0000-000000000001` を返す。認証は未実装。

**⚠️ TODO**: JWT / セッション認証の実装が必要。このファイルを変更して実際のユーザー ID を返すようにすること。

---

### `app/schemas/`

**責務**: Router が直接参照するリクエスト/レスポンス Pydantic スキーマ。現在は Chat ドメインと一部 Job/Dreamer ドメインで使用。

> 各 Service ディレクトリ（`services/*/schemas.py`）とこのディレクトリの両方にスキーマが存在している。整理が必要な場合は `docs/architecture.md` の設計方針を参照。

---

### `app/utils/`

**責務**: ドメイン非依存の汎用ユーティリティ。

- `security.py`: ランダム文字列生成（`login_id` の生成に使用）

---

### `db/`

**責務**: データベースの初期化と初期データ投入。

| ファイル | 役割 |
|---|---|
| `init.sql` | **スキーマの唯一の正**。テーブル定義・ENUM・トリガー・インデックスをすべて含む |
| `import/table_sources.json` | Google Drive の CSV URL とインポート先テーブルのマッピング |
| `import/import_from_gdrive.py` | Google Drive からCSV をダウンロードして DB にインポートするスクリプト |

`init.sql` は Docker コンテナ初回起動時に `docker-entrypoint-initdb.d` 経由で自動実行される。

---

### `docker/`

| ファイル | 用途 |
|---|---|
| `base/Dockerfile` | ベースイメージ定義（pip + Prisma CLI）。`pyproject.toml` 変更時に再ビルド |
| `dev/docker-compose.yml` | 開発環境（PostgreSQL + Qdrant + backend-app + ホットリロード） |
| `prod/docker-compose.yml` | 本番環境（PostgreSQL + backend-app）※ Qdrant 未追加 |

---

### `scripts/`

| ファイル | 役割 | 実行タイミング |
|---|---|---|
| `start-backend-dev.sh` | 開発用コンテナ起動スクリプト（Prisma バイナリ確認 → uvicorn --reload） | コンテナ起動時 |
| `start-backend.sh` | 本番用コンテナ起動スクリプト（uvicorn のみ） | コンテナ起動時 |
| `ensure-prisma-binary.py` | Prisma クエリエンジンバイナリの存在確認・ダウンロード（Node.js 経由） | 起動スクリプトから呼び出し |
| `generate-prisma-artifacts.py` | Prisma クライアント生成のヘルパー | 手動・CI |
| `patch-prisma-platform.py` | Prisma バイナリのプラットフォーム設定パッチ | 必要時 |
| `sync-job-vectordb.py` | 職業データを Qdrant に同期（`--rebuild` オプション付き） | `make sync-vectordb` から呼び出し |

---

### `settings.py`

**責務**: pydantic-settings を使った環境変数の読み込みと型変換。

`DB_*` 変数から `database_url` プロパティを構築する。`CORS_ORIGINS` のカンマ区切りパースも行う。

**依存**: `.env.local` / `.env`

詳細は [docs/environment-variables.md](environment-variables.md) を参照。

---

### `openapi.py`

**責務**: `openapi.json` の生成と `karynos-backend-client/` の自動生成。

```bash
PYTHONPATH=. python openapi.py
```

エンドポイント変更時は必ず実行し `openapi.json` をコミットすること。

---

### `Makefile`

**責務**: 全開発作業の入口。Docker Compose コマンドのラッパー。

よく使うターゲットの一覧は [README.md](../README.md) を参照。
