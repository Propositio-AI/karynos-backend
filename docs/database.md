# データベース

## 概要

- RDBMS: PostgreSQL 17.5
- スキーマ定義: `db/init.sql`（唯一の正）
- ORM: Prisma Client Python (`app/gen/prisma/`)
- UUID 生成: PostgreSQL の `gen_random_uuid()`（標準 UUID v4）、および自作 `uuid_generate_v7()` 関数
- `alembic.ini` が存在するが `migrations/` ディレクトリは存在しない。Alembic によるマイグレーション管理は現時点で未使用。

---

## テーブル一覧

| テーブル名 | 主な用途 |
|---|---|
| `industries` | 業種マスター |
| `job_categories` | 職種カテゴリマスター |
| `skills` | スキルマスター |
| `certifications` | 資格マスター |
| `companies` | 企業マスター |
| `talents` | 才能・特性マスター |
| `interests` | 興味・関心マスター |
| `jobs` | 職業エンティティ |
| `job_images` | 職業に紐づく画像 URL |
| `job_feedbacks` | 職業の詳細フィードバック（1 job : 1 feedback） |
| `feedback_skill` | job_feedback と skills の中間テーブル |
| `feedback_certification` | job_feedback と certifications の中間テーブル |
| `feedback_company` | job_feedback と companies の中間テーブル |
| `feedback_talent` | job_feedback と talents の中間テーブル |
| `feedback_interest` | job_feedback と interests の中間テーブル |
| `histories` | ユーザーの職業閲覧履歴（good / bad / save フラグ付き） |
| `dreamers` | ユーザー（Dreamer）エンティティ |
| `dreamer_groups` | Dreamer のグループ |
| `dreamer_group_members` | Dreamer とグループの中間テーブル |
| `init_questions` | 初期診断の質問（バージョン管理・有効フラグ付き） |
| `init_question_options` | 初期診断質問の選択肢 |
| `user_initial_answers` | ユーザーの診断回答 |
| `conversations` | AI チャットの会話セッション |
| `messages` | 会話内のメッセージ（user / assistant / system） |
| `conversation_participants` | 会話の参加者 |

---

## テーブル詳細・リレーション

### 職業ドメイン

```
industries (1)──< jobs (1)──< job_images
                      │
                      └──< job_feedbacks (1)──< feedback_skill ──> skills
                                          ├──< feedback_certification ──> certifications
                                          ├──< feedback_company ──> companies
                                          ├──< feedback_talent ──> talents
                                          └──< feedback_interest ──> interests
```

`jobs.industry_id` は `ON DELETE RESTRICT`（業種削除禁止）。
`job_feedbacks` は `jobs` に対して `ON DELETE CASCADE`（現 DDL では RESTRICT） — **要確認**。

#### jobs

| カラム | 型 | 制約 | 説明 |
|---|---|---|---|
| `job_id` | SERIAL | PK | |
| `industry_id` | INTEGER | FK → industries | |
| `category_id` | INTEGER | FK → job_categories, NULL 許容 | |
| `name` | TEXT | NOT NULL | |
| `description` | TEXT | | |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT NOW(), trigger 更新 | |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | |

#### job_feedbacks

1 つの `jobs` に対して最大 1 件（設計上の想定）。実装上は `find_many` で全件取得し `[0]` を参照している。

| カラム | 型 | 制約 | 説明 |
|---|---|---|---|
| `feedback_id` | UUID | PK, DEFAULT gen_random_uuid() | |
| `job_id` | INTEGER | FK → jobs | |
| `salary` | INTEGER | salary > 0 | |
| `level` | INTEGER | 1–5 | |
| `end_time` | TIME | | 就業終了時刻 |
| `holiday` | INTEGER | ≥ 0 | 年間休日数 |
| `overtime_hours` | INTEGER | ≥ 0 | 月平均残業時間 |
| `age` | INTEGER | ≥ 0 | 平均年齢 |
| `tenure_years` | INTEGER | ≥ 0 | 平均勤続年数 |
| `marriage_age` | INTEGER | ≥ 0 | 平均結婚年齢 |
| `gender_ratio` | REAL | ≥ 0 | 男性比率 (%) |
| `romance_rate` | REAL | ≥ 0 | 社内恋愛率 (%) |
| `work_life_balance` | REAL | ≥ 0 | |
| `rarity` | REAL | ≥ 0 | 希少性スコア |
| `uniform` | BOOLEAN | | 制服有無 |
| `focus_on_education` | BOOLEAN | | 学歴重視フラグ |
| `focus_on_achievements` | BOOLEAN | | 実績重視フラグ |
| 各種 TEXT カラム | TEXT | | 説明文・特性テキスト |

### ユーザードメイン

```
dreamers (1)──< dreamer_group_members >──< dreamer_groups
          │
          └──< histories ──> jobs
          │
          └──< user_initial_answers ──> init_questions
                                   ──> init_question_options
```

#### dreamers

| カラム | 型 | 制約 | 説明 |
|---|---|---|---|
| `dreamer_id` | UUID | PK, DEFAULT gen_random_uuid() | |
| `organization_id` | INTEGER | NULL 許容 | 所属組織 |
| `login_id` | TEXT | NOT NULL | ランダム文字列 (`app/utils/security.py`) |
| `name_family` | TEXT | NOT NULL | 苗字 |
| `name_given` | TEXT | NOT NULL | 名前 |
| `last_login_at` | TIMESTAMP | NULL 許容 | |

#### histories（閲覧履歴）

| カラム | 型 | 制約 | 説明 |
|---|---|---|---|
| `history_id` | UUID | PK | |
| `job_id` | INTEGER | FK → jobs ON DELETE CASCADE | |
| `dreamer_id` | UUID | NOT NULL（FK 制約なし） | |
| `good` | BOOLEAN | DEFAULT FALSE | いいね |
| `bad` | BOOLEAN | DEFAULT FALSE | 興味なし |
| `save` | BOOLEAN | DEFAULT FALSE | 保存 |

> `dreamer_id` は外部キー制約なし（DDL より）。

### 初期診断ドメイン

```
init_questions (1)──< init_question_options
init_questions (1)──< user_initial_answers ──> init_question_options
                                          ──> dreamers
```

#### init_questions

| カラム | 型 | 説明 |
|---|---|---|
| `version` | INTEGER | 質問票バージョン（複数バージョン共存可） |
| `category` | TEXT | 質問カテゴリ |
| `question_order` | INTEGER | 表示順 |
| `is_active` | BOOLEAN | 有効フラグ（無効化で非表示） |

#### user_initial_answers

| カラム | 型 | 説明 |
|---|---|---|
| `question_version` | INTEGER | 回答時のバージョンを記録（後から変えられても追跡可能） |

### チャットドメイン

```
conversations (1)──< messages
              (1)──< conversation_participants
```

#### conversations

| カラム | 型 | 説明 |
|---|---|---|
| `owner_id` | UUID | 会話オーナー（外部キー制約なし） |
| `job_id` | TEXT | 紐づく職業 ID |
| `job_name` | TEXT | 会話作成時点の職業名（冗長カラム） |
| `assistant_name` | TEXT | AI キャラクター名 |
| `assistant_gender` | TEXT | AI キャラクター性別（現在 "unisex" 固定） |
| `share_type` | share_type | ENUM: PRIVATE / PUBLIC |

#### messages

| カラム | 型 | 説明 |
|---|---|---|
| `role` | role_type | ENUM: user / assistant / system |
| `sender_id` | UUID | ユーザーまたは固定 AI UUID |

---

## インデックス

```sql
-- init_questions
CREATE INDEX idx_init_questions_version_active ON init_questions(version, is_active);
CREATE INDEX idx_init_questions_category ON init_questions(category);

-- init_question_options
CREATE INDEX idx_init_question_options_question_id ON init_question_options(question_id);

-- user_initial_answers
CREATE INDEX idx_user_initial_answers_dreamer_id ON user_initial_answers(dreamer_id);
CREATE INDEX idx_user_initial_answers_question_version ON user_initial_answers(question_version);
```

その他テーブルにはアプリケーション用インデックスが未定義。`dreamer_id` や `job_id` への検索が多いため、将来的に追加を検討すること。

---

## トリガー

`update_timestamp()` 関数により、以下のテーブルの `updated_at` が `BEFORE UPDATE` で自動更新される。

- `jobs`, `job_feedbacks`
- `dreamers`, `dreamer_groups`
- `init_questions`, `user_initial_answers`
- `messages`, `conversations`

---

## ENUM 型

| 型名 | 値 |
|---|---|
| `share_type` | `PRIVATE`, `PUBLIC` |
| `role_type` | `user`, `assistant`, `system` |

---

## データ投入・マスターデータ

マスターデータ（職業・スキル・資格など）は Google Drive 上の CSV から投入する。

```bash
make db-import
# → db/import/import_from_gdrive.py が db/import/table_sources.json を読み込み
#   各テーブルに upsert（既存データがある場合はスキップ）
```

`table_sources.json` の `truncate: false` によりデータが既存の場合は挿入をスキップする。

---

## スキーマ変更手順

Alembic マイグレーション機能は現在未使用。スキーマ変更は以下の手順で行う。

1. `db/init.sql` を編集する
2. Prisma スキーマ（`app/gen/prisma/schema.prisma`）を同期して編集する
3. `make prisma` で Prisma クライアントを再生成する
4. 開発環境でリセットする場合は `make db-clean` でデータを削除して再起動する

> **注意**: `db/init.sql` は初回コンテナ起動時に `docker-entrypoint-initdb.d` 経由で実行される。既存 DB がある場合は再実行されない。本番環境でのスキーマ変更手順は要検討。
