# アーキテクチャ

## システム構成

```
                   ┌─────────────────────────────────────────┐
  クライアント      │             backend-app                  │
  (Next.js)  ──▶│          FastAPI / Uvicorn              │◀── :8000
                   │          (Python 3.12)                   │
                   └──────────┬──────────────────────────────┘
                              │
              ┌───────────────┼───────────────┬───────────────┐
              ▼               ▼               ▼               ▼
       ┌─────────────┐ ┌─────────────┐ ┌──────────────┐ ┌──────────┐
       │ PostgreSQL  │ │   Qdrant    │ │  OpenAI API  │ │  AWS     │
       │   17.5      │ │ (vector DB) │ │ gpt-4o       │ │ Cognito  │
       │ :5432       │ │ :6333       │ │ text-emb-3-s │ │ (JWT 認証)│
       └─────────────┘ └─────────────┘ └──────────────┘ └──────────┘
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

アプリケーションは 7 つのドメインに分割されている。

### 1. Dreamer（ユーザー管理）
- `app/router/dreamers.py` → `app/services/dreamer/`
- Dreamer（ユーザー）エンティティとグループの CRUD

### 2. Onboarding（初期診断）
- `app/router/onboarding.py` → `app/services/onboarding/`
- バージョン管理付き質問票の提供と回答の保存

### 3. Matching（Dream Matching）
- `app/router/matching.py` → `app/services/matching/`
- Onboarding 回答 + 閲覧履歴 → プロファイルテキスト生成
- Algorithm 層の `VectorSearchRecommender` でベクトル類似検索

### 4. Job（職業情報）
- `app/router/jobs.py` → `app/services/job/`
- 職業詳細・閲覧履歴・テキスト意味検索・Qdrant 同期

### 5. Chat（AI チャット）
- `app/router/chats.py` → `app/services/chat/`
- 職業担当者 AI との会話・OpenAI Streaming 応答

### 6. Mentor（教員管理）
- `app/router/mentor.py` → `app/services/mentor/`
- クラス・履修生徒・授業資料の管理（CRUD）
- クラス単位の集計（関心分野・教材配布状況）
- Dream Action トリガー・生成ジョブ管理・教材配布

### 7. Dream Action（補助教材生成・配布）
- Mentor 向け: `app/router/mentor.py` (prefix `/mentor/classes/{id}/dream-action/`)
- Dreamer 向け: `app/router/dream_action.py` (prefix `/dream-action/`)
- `app/services/dream_action/service.py`
- 授業資料 + 生徒の仮の夢 → LLM → 補助教材 生成パイプライン
- `BackgroundTasks` による非同期処理
- `GenerationJob` テーブルで進捗管理
- モデレーションチェック → 教員確認 → 配布 の状態遷移

---

## 認証・認可

### 認証方式

Amazon Cognito + JWT（RS256）。詳細は [`docs/auth.md`](auth.md) を参照。

```
クライアント → Authorization: Bearer <JWT>
                    ↓
         app/lib/auth.py (FastAPI 依存関係)
              ├── JWKS から公開鍵を取得（lru_cache でキャッシュ）
              ├── RS256 署名検証
              ├── iss / aud / exp 検証
              ├── cognito:groups → Role 判定（Dreamer / Mentor）
              └── cognito_sub → DB の dreamer_id / mentor_id に解決
```

### モックモード

`COGNITO_USER_POOL_ID` が未設定の場合、モック認証が有効になる。
- Dreamer: 固定 UUID `00000000-0000-0000-0000-000000000001`
- Mentor: cognito_sub `mock-mentor-sub` → `00000000-0000-0000-0000-000000000002`

---

## Dream Action パイプライン

```
Mentor: POST /mentor/classes/{class_id}/dream-action/generate
            │
            ▼
    DreamActionService.trigger_generation()
            ├── クラス帰属・資料帰属を確認
            ├── GenerationJob を PENDING で作成
            └── BackgroundTasks に _run_generation_job を登録
                        │
                        ▼ (非同期実行)
            _run_generation_job()
                ├── GenerationJob → PROCESSING
                ├── 履修生徒を取得（または指定 dreamer_ids）
                └── 各生徒 (_generate_for_dreamer):
                        ├── 冪等キー確認（force_regenerate でスキップ可）
                        ├── 生徒の仮の夢（liked job）を取得
                        ├── プロンプトテンプレート差し込み（prompts/dream_action/）
                        ├── OpenAI gpt-4o で教材生成
                        ├── モデレーションチェック（不合格は保存しない）
                        └── GeneratedMaterial を DRAFT で保存

Mentor: POST /mentor/classes/{class_id}/dream-action/distribute
            └── GeneratedMaterial → DISTRIBUTED（配布済み）

Dreamer: GET /dream-action/materials
            └── 自分宛ての DISTRIBUTED 教材のみ閲覧可
```

### プロンプト管理

LLM プロンプトはコードから分離し `app/prompts/dream_action/` で管理する。

| テンプレート | 変数 | 用途 |
|---|---|---|
| `generate_material.txt` | `student_name`, `job_name`, `job_description`, `subject`, `unit`, `material_title`, `lesson_content` | 補助教材生成 |
| `moderation_check.txt` | `content` | 適切性チェック（JSON 出力） |

---

## 統一エラーレスポンス形式

全エンドポイントのエラーレスポンスは以下の形式で統一される。

```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "クラスが見つかりません",
    "detail": null
  }
}
```

| HTTP ステータス | code |
|---|---|
| 400 | `BAD_REQUEST` |
| 401 | `UNAUTHORIZED` |
| 403 | `FORBIDDEN` |
| 404 | `NOT_FOUND` |
| 409 | `CONFLICT` |
| 413 | `PAYLOAD_TOO_LARGE` |
| 422 | `VALIDATION_ERROR` |
| 500 | `INTERNAL_SERVER_ERROR` |

---

## モジュール設計

### Gateway パターン

```python
# GatewayResult は常に {"success": bool, "message": list, "data": T} の形を返す
result = mentor_gateway.get_class(class_id)
if not result["success"] or not result["data"]:
    raise HTTPException(...)
cls = result["data"][0]
```

### Prisma の同期実行

FastAPI の同期エンドポイントと Prisma の非同期 API を橋渡しするため、
`app/gateways/db/prisma_client.py` でデディケートスレッド上のイベントループを起動し、
`asyncio.run_coroutine_threadsafe` で同期的に呼び出している。

```
FastAPI (sync)  →  run_prisma()  →  専用イベントループスレッド  →  Prisma (async)
```

---

## 設計思想

1. **責務の明確な分離**: Router は HTTP のみ、Service はビジネスロジックのみ、Gateway は DB のみ担当する。
2. **プロンプトのコード分離**: LLM プロンプトはコードに直書きせず `app/prompts/` で管理する。
3. **教員が最終判断者**: AI 生成教材は必ず DRAFT 状態で保存し、教員が確認・配布するまで生徒に見えない。
4. **未成年データの最小権限**: Mentor が参照できる生徒情報は教育目的に必要な範囲（基本情報 + 関心傾向）に限定する。
5. **Gateway Result の統一**: すべての DB アクセスは `{"success", "message", "data"}` 形式で返す。
6. **冪等な生成**: `idempotency_key = "{material_id}:{dreamer_id}"` で重複生成を防ぐ。

---

## 既知の課題・TODO

| 項目 | 状況 |
|---|---|
| 本番環境の Qdrant | `docker/prod/docker-compose.yml` に Qdrant サービスが存在しない。追加が必要。 |
| Chat の自己 API 呼び出し | `app/services/chat/job_api.py` が `http://backend-app:8000` に HTTP リクエストしている。Gateway 経由に変更すべき。 |
| Alembic マイグレーション | `alembic.ini` はあるが `migrations/` が未作成。現在は `db/init.sql` で初期化。 |
| アクセスログ | 教員による生徒データアクセスのログ記録は未実装。 |
