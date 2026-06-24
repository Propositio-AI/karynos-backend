# Karynos Backend

職業診断・マッチング・AIチャットを提供する FastAPI バックエンドサービス。

## 主な機能

| 機能 | エンドポイント接頭辞 | 概要 |
|---|---|---|
| **初期診断 (Onboarding)** | `/api/v1/onboarding` | バージョン付き質問票へのユーザー回答を収集・保存 |
| **マッチング (Matching)** | `/api/v1/matching` | 回答と閲覧履歴からプロファイルを生成し Qdrant でベクトル類似検索 |
| **職業情報 (Job)** | `/api/v1/job` | 職業詳細・意味検索・閲覧履歴管理・Qdrant 同期 |
| **AI チャット (Chat)** | `/api/v1/chat` | 職業担当者 AI とのリアルタイム会話（OpenAI Streaming） |
| **Dreamer 管理** | `/api/v1/dreamer` | ユーザー (Dreamer) とグループの CRUD |

詳細な API 仕様は `docs/api.md` を参照（生成方法は後述）。

## 技術スタック

| カテゴリ | 採用技術 |
|---|---|
| Web フレームワーク | FastAPI + Uvicorn |
| 言語 | Python 3.12 |
| ORM | Prisma (prisma-py) |
| DB | PostgreSQL 17.5 |
| ベクトル DB | Qdrant |
| AI | OpenAI API (gpt-4o / text-embedding-3-small) |
| コンテナ | Docker / Docker Compose |
| Lint / Format | Ruff / Black |

## セットアップ

### 前提条件

- Docker Desktop がインストールされていること
- `OPENAI_API_KEY` を取得済みであること

### 手順

```bash
# 1. 環境変数ファイルを作成
cp .env.example .env.local
vi .env.local        # OPENAI_API_KEY を設定する

# 2. ベースイメージをビルド（初回 / pyproject.toml 変更時のみ）
make build-base

# 3. アプリイメージをビルド
make build
```

## 起動方法

```bash
make up
```

`make up` は以下を順番に実行する。

1. コンテナ起動（PostgreSQL + Qdrant + backend-app）
2. Prisma クライアント再生成
3. Google Drive からマスターデータをインポート
4. 職業データを Qdrant へ同期

起動後 `http://localhost:8000/docs` で Swagger UI を確認できる。

### よく使うコマンド

```bash
make down                    # コンテナ停止
make logs                    # backend-app のログを tail
make shell-app               # backend-app コンテナに入る
make shell-db                # PostgreSQL に psql で接続
make prisma                  # schema.prisma 変更後にクライアント再生成
make db-clean                # DB データ完全削除（コンテナ再起動）
make qdrant-clean            # Qdrant データ削除（コンテナ再起動）
make sync-vectordb-rebuild   # Qdrant に全件再構築
```

## ディレクトリ構成（簡易版）

```
karynos-backend/
├── app/
│   ├── main.py               # FastAPI アプリ・ルーター登録
│   ├── router/               # HTTP エンドポイント定義
│   ├── services/             # ビジネスロジック（5 ドメイン）
│   ├── gateways/             # DB アクセス層（Prisma ラッパー）
│   ├── algorithm/            # ベクトル検索・プロファイル生成（純粋計算）
│   ├── lib/                  # 認証など共通ユーティリティ
│   └── gen/prisma/           # Prisma 自動生成コード（編集禁止）
├── db/
│   ├── init.sql              # DDL・テーブル定義（スキーマの唯一の正）
│   └── import/               # Google Drive からのマスターデータインポート
├── docker/
│   ├── base/Dockerfile       # ベースイメージ（pip + Prisma CLI）
│   ├── dev/docker-compose.yml
│   └── prod/docker-compose.yml
├── scripts/                  # 起動・Prisma バイナリ取得・Qdrant 同期スクリプト
├── .env.example              # 環境変数テンプレート
├── pyproject.toml            # 依存パッケージ・ツール設定
└── Makefile                  # 全作業の入口
```

詳細は [docs/directory-structure.md](docs/directory-structure.md) を参照。

## ドキュメント一覧

| ドキュメント | 内容 |
|---|---|
| [docs/architecture.md](docs/architecture.md) | システム構成・レイヤ設計・リクエストフロー |
| [docs/database.md](docs/database.md) | テーブル一覧・リレーション・DDL・運用 |
| [docs/development.md](docs/development.md) | 開発環境構築・Lint・CI/CD・デプロイ |
| [docs/environment-variables.md](docs/environment-variables.md) | 環境変数一覧・必須/任意・利用箇所 |
| [docs/directory-structure.md](docs/directory-structure.md) | 各ディレクトリの責務・依存関係 |
| docs/api.md | API 仕様（下記コマンドで生成） |

### API ドキュメントの生成

```bash
# openapi.json を最新化（エンドポイント変更時は必ず実行）
PYTHONPATH=. python openapi.py

# Markdown に変換
npx openapi-markdown openapi.json > docs/api.md
```

## Push 前チェックリスト

CI (`develop` / `main` ブランチへの push・PR) で自動実行されるもの：

- [ ] **Black フォーマットチェック通過** — `uvx black --check .`
- [ ] **Ruff lint チェック通過** — `uvx ruff check .`

ローカルで確認すること：

- [ ] **Docker build 成功** — `make build-base && make build`
- [ ] **openapi.json 更新済み** — エンドポイント変更時は `PYTHONPATH=. python openapi.py` を実行
- [ ] **db/init.sql と Prisma スキーマが整合している** — テーブル追加・変更時に確認

> 自動テスト・型チェック (mypy / pyright) は現時点で CI に含まれていない。

## ライセンス

TODO: ライセンスを設定すること。
