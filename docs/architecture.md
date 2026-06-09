# アーキテクチャ

## システム構成

```
                   ┌────────────────────────────┐
  クライアント      │        backend-app          │
  (Next.js)  ──▶│     FastAPI / Uvicorn       │◀── :8000
                   │      (Python 3.12)          │
                   └──────────┬─────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
       ┌─────────────┐ ┌─────────────┐ ┌──────────────┐
       │ PostgreSQL  │ │   Qdrant    │ │  OpenAI API  │
       │   17.5      │ │ (vector DB) │ │ gpt-4o       │
       │ :5432       │ │ :6333       │ │ text-emb-3-s │
       └─────────────┘ └─────────────┘ └──────────────┘
```

すべてのコンポーネントは `karynos-network` ブリッジネットワーク内に存在する（開発環境）。

---

## レイヤ構造

```
Router  →  Service  →  Gateway  →  Prisma Client  →  PostgreSQL
                   ↘  Algorithm  →  Qdrant
                   ↘  OpenAI Client  →  OpenAI API
```

| レイヤ | 場所 | 責務 |
|---|---|---|
| **Router** | `app/router/` | HTTP の受け口・レスポンス型宣言・依存注入 |
| **Service** | `app/services/` | ビジネスロジック・複数 Gateway の調整・例外変換 |
| **Gateway** | `app/gateways/` | DB アクセスの抽象化・Prisma 呼び出しの同期ラッパー |
| **Algorithm** | `app/algorithm/` | 純粋計算（ベクトル化・類似検索・プロファイル生成）。DB・HTTP 呼び出し禁止 |
| **Prisma Client** | `app/gen/prisma/` | 自動生成 ORM コード |

---

## ドメイン設計

アプリケーションは 5 つのドメインに分割されている。

### 1. Dreamer（ユーザー管理）
- `app/router/dreamers.py` → `app/services/dreamer/`
- Dreamer（ユーザー）エンティティとグループの CRUD
- 認証・プロファイル以外の一切の横断的関心事を持たない

### 2. Onboarding（初期診断）
- `app/router/onboarding.py` → `app/services/onboarding/`
- バージョン管理付き質問票の提供
- ユーザー回答の保存・履歴取得
- Matching ドメインとは完全に独立

### 3. Matching（マッチング）
- `app/router/matching.py` → `app/services/matching/`
- Onboarding 回答 + 閲覧履歴 → プロファイルテキスト生成
- Algorithm 層の `VectorSearchRecommender` でベクトル類似検索
- Job 情報は gateway 経由で取得し、Matching 内で完結させる

### 4. Job（職業情報）
- `app/router/jobs.py` → `app/services/job/`
- 職業詳細・閲覧履歴・意味検索（ユーザー入力テキスト → Qdrant）
- Qdrant への職業データ同期（管理者用 `/admin/sync-vectordb`）
- マッチング（プロファイルベースの推薦）は担当しない

### 5. Chat（AI チャット）
- `app/router/chats.py` → `app/services/chat/`
- 職業担当者 AI との会話作成・メッセージ送受信
- OpenAI Chat Completions API でストリーミング応答
- 会話・メッセージの永続化（PostgreSQL）

---

## モジュール設計

### Gateway パターン

```python
# GatewayResult は常に {"success": bool, "message": list, "data": T} の形を返す
result = dreamer_gateway.get_dreamer(dreamer_id)
if not result["success"] or not result["data"]:
    raise HTTPException(...)
dreamer = result["data"][0]
```

すべての DB アクセスは Gateway を経由し、Service は直接 Prisma を呼び出さない。

### Prisma の同期実行

FastAPI は同期エンドポイント（`def`）で動作しており、Prisma Client は非同期 API しか持たない。
この差異を吸収するため `app/gateways/db/prisma_client.py` でデディケートスレッド上のイベントループを起動し、`asyncio.run_coroutine_threadsafe` で同期的に呼び出している。

```
FastAPI (sync)  →  run_prisma()  →  専用イベントループスレッド  →  Prisma (async)
```

### Algorithm 層の純粋性

`app/algorithm/` 配下のモジュールは **外部 I/O を持たない純粋計算** として設計されている。

- `VectorSearchRecommender`: Qdrant クライアントを保持するが、データ取得のロジックは Service 層が担う
- `RuleBasedProfileGenerator`: 入力 dict → プロファイルテキストの変換のみ
- `RecommendationProcessor`: 閲覧済みジョブのフィルタリングのみ

Gateway 呼び出し・HTTP 呼び出しを Algorithm 層に追加してはならない。

---

## リクエスト処理フロー

### マッチングリクエストの例

```
GET /api/v1/matching/recommend
        │
        ▼
app/router/matching.py
  └── matching_service.recommend(dreamer_id)
              │
              ├── dreamer_gateway.list_answer_history(dreamer_id)   → PostgreSQL
              │      └── dreamer_gateway.get_answer_question(id)    → PostgreSQL
              │      └── dreamer_gateway.get_answer_option(id)      → PostgreSQL
              │
              ├── job_gateway.get_history(dreamer_id)               → PostgreSQL
              │      └── job_gateway.get_job(job_id) × N           → PostgreSQL
              │
              ├── RuleBasedProfileGenerator.generate_profile(...)   → (純粋計算)
              │
              └── VectorSearchRecommender.search_jobs(profile)      → Qdrant
                         └── OpenAI.embeddings.create(profile)      → OpenAI API
```

### チャットメッセージ送信の例

```
POST /api/v1/chat/message/{conversation_id}
        │
        ▼
app/router/chats.py (StreamingResponse)
  └── conversation_service.create_ai_response_stream(...)
              │
              ├── chat_gateway.create_message(user_msg)             → PostgreSQL
              ├── chat_gateway.update_conversation(last_msg_at)     → PostgreSQL
              ├── get_job_data(job_id)                              → 自己 API
              ├── build_openai_messages(conversation_id, ...)       → PostgreSQL
              └── OpenAIClient.chat_stream(messages)                → OpenAI API (SSE)
```

---

## 依存関係

```
router
  └── service
        ├── gateway  ──── prisma_client ──── gen/prisma (自動生成)
        ├── algorithm.recommendation  ──── Qdrant
        └── chat.openai_client  ──── OpenAI API

設定: settings.py  ←── pydantic-settings  ←── .env.local
認証: app/lib/auth.py  (TODO: 現在はハードコードされたダミー UUID)
```

---

## 設計思想

1. **責務の明確な分離**: Router は HTTP のみ、Service はビジネスロジックのみ、Gateway は DB のみ担当する。
2. **Algorithm の純粋性**: アルゴリズム層は I/O を持たず、単体テストが容易な構造を目指す。
3. **Gateway Result の統一**: すべての DB アクセスは `{"success", "message", "data"}` 形式で返り、Service 層での一貫したエラーハンドリングを実現する。
4. **ドメイン間の独立性**: Onboarding と Matching は同一データを扱うが、サービスクラスを分離し直接依存しない設計とする。Matching が Onboarding のデータを必要とする場合は Gateway 経由でアクセスする。

---

## 既知の課題・TODO

| 項目 | 状況 |
|---|---|
| 認証・認可 | `app/lib/auth.py` がハードコードされたダミー UUID を返している。実装が必要。 |
| 本番環境の Qdrant | `docker/prod/docker-compose.yml` に Qdrant サービスが存在しない。追加が必要。 |
| 自動テスト | テストコードが存在しない。 |
| 型チェック | mypy / pyright が CI に組み込まれていない。 |
| Chat の自己 API 呼び出し | `app/services/chat/job_api.py` が `http://backend-app:8000` に HTTP リクエストしている。Gateway 経由に変更すべき。 |
