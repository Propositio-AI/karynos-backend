# Karynos Backend — 運用マニュアル

職業診断・マッチング・AI チャットを提供する FastAPI バックエンド。
本書は **AWS 本番環境（EC2 + Docker Compose）の運用手順書**である。
アプリの設計・開発手順は `docs/` 配下を参照。

> ⚠️ **このリポジトリは公開（public）です。** アカウント ID・インスタンス ID・
> Elastic IP・シークレット値などの具体値はここに記載しない。実値はチーム内の
> 非公開運用メモ／AWS コンソールを参照すること。

---

## 0. 運用の基本ルール（厳守）

- AWS 操作は **Agent Toolkit for AWS (MCP)** 経由で行い、**プロファイルは `team-project`**、
  **リージョンは東京 `ap-northeast-1`** を使用する。
- EC2 へは **SSM Session Manager** で接続する（SSH ポート 22 は開けていない）。
- シークレットは **SSM Parameter Store（SecureString）** で管理し、リポジトリにコミットしない。
- 破壊的操作（DB クリーン等）は影響範囲を確認してから実行する。

---

## 1. 本番アーキテクチャ

```
                  ┌─────────────────────────────┐
   ユーザー ──────▶│ AWS Amplify Hosting          │  karynos.com / www
   (ブラウザ)       │ (Next.js 15 SSR / WEB_COMPUTE)│  (Route53 + ACM, develop)
                  └──────────────┬──────────────┘
                                 │ ブラウザから直接 HTTPS
                                 │ (api.karynos.com)
                                 ▼
                  ┌─────────────────────────────┐
                  │ EC2 (t3.medium, ap-northeast-1) + Elastic IP
                  │  Caddy (TLS終端 / 自動Let's Encrypt, SSE対応)
                  │    └─ reverse proxy ─▶ backend-app:8000
                  │  Docker Compose (docker/prod):
                  │    ├─ backend-app (FastAPI/uvicorn, 127.0.0.1:8000)
                  │    ├─ postgres 17.5   (named volume: pgdata)
                  │    └─ qdrant          (named volume: qdrant-data)
                  └─────────────────────────────┘
```

- フロント（Amplify）とバック（EC2）は別系統。ブラウザは `https://api.karynos.com` を直接呼ぶ
  （SSE チャットが Amplify SSR のバッファリングで壊れるのを回避）。
- 公開アクセスは Caddy（80/443）経由のみ。`backend-app` は `127.0.0.1:8000` のみバインド。

### リソース早見表（実 ID は非公開メモ参照）

| 種別 | 識別子 |
|---|---|
| EC2 インスタンス | Name タグ `karynos-backend`（t3.medium / Amazon Linux 2023 / gp3 50GB） |
| Elastic IP | `api.karynos.com` が指す固定 IP |
| セキュリティグループ | `karynos-backend-sg`（inbound 80/443 のみ） |
| IAM ロール / プロファイル | `karynos-backend-ec2-role` / `karynos-backend-ec2-profile` |
| SSM パラメータ | `/karynos/prod/*` |
| Route53 ホストゾーン | `karynos.com` |
| Amplify アプリ | `karynos-web`（WEB_COMPUTE、デプロイ対象ブランチ `develop`） |
| デプロイ先（EC2 上） | `/home/ec2-user/karynos-backend` |

---

## 2. 日常運用

EC2 上の作業は **SSM Run Command** か **SSM Session Manager** で実行する。
以下のシェル例は EC2 内での実行を想定（`PROJECT=/home/ec2-user/karynos-backend`）。

> compose 実行は必ず prod を指定する：
> `docker compose --env-file $PROJECT/.env -f $PROJECT/docker/prod/docker-compose.yml ...`
> （`make` ターゲットは **dev compose 固定** なので本番では使わない。後述）

### 2.1 EC2 の起動 / 停止（コスト管理）

MCP（`team-project`）から：

```bash
# 起動（同一 Elastic IP で復帰。コンテナは restart:unless-stopped で自動起動）
aws ec2 start-instances --instance-ids <INSTANCE_ID>

# 停止（コスト節約。データ/EIP/TLS証明書は保持される）
aws ec2 stop-instances --instance-ids <INSTANCE_ID>
```

- インスタンス ID は Name タグから取得：
  `aws ec2 describe-instances --filters Name=tag:Name,Values=karynos-backend --query "Reservations[].Instances[].InstanceId"`
- **起動後 2〜3 分**で全コンテナが healthy になる（postgres → backend-app の順）。
- ⚠️ **停止中は `karynos.com` の画面は表示できるが、API・ログイン・チャットは動かない**
  （バックエンドが落ちているため）。デモ・公開時は必ず起動しておく。

### 2.2 EC2 への接続

```bash
aws ssm start-session --target <INSTANCE_ID>      # 対話シェル
# あるいは SSM Run Command（非対話・自動化向け）
```

### 2.3 稼働確認

```bash
# 公開エンドポイント（ローカル PC から）
curl -s -o /dev/null -w "%{http_code}\n" https://api.karynos.com/openapi.json   # 200 を期待

# コンテナ状態（EC2 内）
docker compose --env-file $PROJECT/.env -f $PROJECT/docker/prod/docker-compose.yml ps
```

期待状態：`caddy` / `backend-app` / `karynos-db (healthy)` / `karynos-qdrant (healthy)` が Up。

### 2.4 ログ確認

```bash
docker compose --env-file $PROJECT/.env -f $PROJECT/docker/prod/docker-compose.yml logs --tail=200 backend-app
docker compose --env-file $PROJECT/.env -f $PROJECT/docker/prod/docker-compose.yml logs --tail=100 caddy   # TLS 取得状況など
```

---

## 3. デプロイ / 更新

レジストリは使わず、**EC2 上で git pull → ビルド → 起動**する。

```bash
cd $PROJECT
git pull origin <branch>     # 現状の本番反映ブランチ（インフラ構成は feature/infra-setup 系）

# .env を SSM から再生成（3章参照）してから：
cd $PROJECT/docker/prod
docker compose --env-file $PROJECT/.env -f docker-compose.yml up -d --build
```

- アプリイメージ（`karynos/be-app`）は `docker/prod/Dockerfile` から `--build` で生成される。
  Prisma クエリエンジンはビルド時にイメージへ焼き込まれる（実行時ネットワーク不要）。
- コードのみの変更ならレイヤキャッシュにより依存の再インストールは走らない。

---

## 4. シークレット / 環境変数（SSM Parameter Store）

本番の環境変数は **SSM Parameter Store `/karynos/prod/*`** に格納（DB 認証情報・
`OPENAI_API_KEY` 等は SecureString）。EC2 のインスタンスロールに読み取り権限を付与済み。

### 4.1 `.env` の生成（EC2 内）

```bash
aws ssm get-parameters-by-path --region ap-northeast-1 \
  --path /karynos/prod --recursive --with-decryption \
  --query "Parameters[].[Name,Value]" --output text \
  | while read -r name value; do echo "${name##*/}=$value"; done > $PROJECT/.env
chmod 600 $PROJECT/.env
```

### 4.2 値の更新（例：OpenAI キー差し替え）

```bash
aws ssm put-parameter --region ap-northeast-1 --name /karynos/prod/OPENAI_API_KEY \
  --type SecureString --overwrite --value "sk-...新しいキー..."
```

> 機密値はチャット履歴等に残さないよう、各自のターミナル／コンソールで実行する。
> 更新後は `.env` を再生成し、`docker compose ... up -d`（必要に応じ `run`）で反映する。

### 4.3 主なパラメータ

`APP_NAME` / `CORS_ORIGINS`(`https://karynos.com`) / `API_DOMAIN`(`api.karynos.com`) /
`POSTGRES_USER|PASSWORD|DB` / `DB_USER|PASS|HOST(karynos-db)|PORT|NAME` / `DATABASE_URL` /
`OPENAI_API_KEY` / `CSV_IMPORT_CONFIG_JSON`(`/app/db/import/table_sources.json`)。
詳細は [docs/environment-variables.md](docs/environment-variables.md)。

---

## 5. データ運用（職業 DB / ベクトル DB）

職業データを更新したら、**DB 再構築 → CSV 取り込み → Qdrant 再ベクトル化**を行う。

> ⚠️ Makefile の `make db-clean / db-import / sync-vectordb-rebuild` は **dev compose 固定**
> （`docker/dev` + `.env.local` + `db-data` バインドマウント）。**本番には効かない。**
> 本番では postgres データが **名前付きボリューム `pgdata`** のため、以下の prod 手順を使う。

### 5.1 DB 全クリーン再構築 + マスタ取り込み

⚠️ **既存の DB データ（ユーザー・会話を含む）が全削除される。** 影響を確認してから実行。

```bash
cd $PROJECT/docker/prod
ENVF=$PROJECT/.env

docker compose --env-file $ENVF -f docker-compose.yml down
docker volume rm prod_pgdata          # postgres データを破棄（init.sql 再適用のため）
docker compose --env-file $ENVF -f docker-compose.yml up -d   # init.sql でスキーマ再作成
# 更新 CSV（Google Drive）取り込み。run は DB healthy を待ってから走る
docker compose --env-file $ENVF -f docker-compose.yml \
  run --rm backend-app python /app/db/import/import_from_gdrive.py
```

- `prod_pgdata` の `prod_` は compose プロジェクト名（compose ファイルが `docker/prod/` 配下のため）。
  実名は `docker volume ls` で確認できる。
- `table_sources.json` が参照する Google Drive ファイルを差し替えると（URL/ID は不変）、
  取り込み内容が更新される。

### 5.2 Qdrant 全再ベクトル化

```bash
cd $PROJECT/docker/prod
docker compose --env-file $PROJECT/.env -f docker-compose.yml \
  run --rm backend-app sh -c "PYTHONPATH=/app python /app/scripts/sync-job-vectordb.py --rebuild"
```

- `--rebuild` は Qdrant コレクションを **delete→create で作り直してから全件 upsert** するため、
  古いポイントは残らない。OpenAI Embedding API（`text-embedding-3-small`）を使用。

### 5.3 完了確認

```bash
ENVF=$PROJECT/.env
# jobs 件数（PostgreSQL）
docker compose --env-file $ENVF -f $PROJECT/docker/prod/docker-compose.yml \
  exec -T karynos-db psql -U karynos -d karynos -tAc "SELECT count(*) FROM jobs;"

# Qdrant ポイント数（REST API を backend-app から叩く）
docker compose --env-file $ENVF -f $PROJECT/docker/prod/docker-compose.yml \
  run --rm backend-app python -c \
  "import urllib.request,json;print(json.load(urllib.request.urlopen('http://qdrant:6333/collections/job_vector_db'))['result']['points_count'])"
```

`jobs 件数 == Qdrant ポイント数`（例：883 / 883）になっていれば成功。

> SSM Run Command 経由で上記をスクリプト送信する場合、**シングルクォートや `..`・
> `127.0.0.1` を含む文字列がプロキシで除去・遮断される**ことがある。Python は
> ヒアドキュメントでファイル化して実行し、パスは絶対パスを使うと安全（7 章参照）。

---

## 6. ドメイン / TLS

- **バックエンド**：Caddy が `api.karynos.com` の TLS を **自動取得・自動更新**（Let's Encrypt）。
  証明書は名前付きボリューム `caddy-data` に永続化され、EC2 停止→起動でも再利用される。
  SSE 対応のため Caddy はバッファリング無効（`flush_interval -1`）。
- **フロント**：Amplify が `karynos.com` / `www.karynos.com` を配信（ACM 証明書、Route53）。
  DNS は apex を A(ALIAS)、www を CNAME で Amplify の CloudFront に向けている。

---

## 7. トラブルシュート / ハマりどころ

| 症状 | 原因 / 対処 |
|---|---|
| 起動スクリプトが `set: Illegal option -` で落ちる | `scripts/*.sh` の CRLF 改行。prod Dockerfile で LF 正規化済み。Windows でファイルを足す時は LF に注意 |
| `docker compose build` が `requires buildx 0.17.0 or later` | AL2023 同梱 buildx が古い。`docker-buildx` プラグイン（0.17+）を `/usr/local/lib/docker/cli-plugins/` に導入 |
| import が無言でスキップ | `CSV_IMPORT_CONFIG_JSON` 未設定（コード既定パスが実体と不一致）。SSM で `/app/db/import/table_sources.json` を設定する |
| データを更新したのに反映されない | `CSV_IMPORT_SKIP_IF_TABLE_HAS_DATA=true` のため既存データありだとスキップ。5.1 の DB クリーンを先に実行 |
| Qdrant 件数が古い数のまま | `--rebuild` 無しの upsert では古いポイントが残る。`--rebuild` を使う |
| SSE チャットが途中で切れる | Caddy のバッファリング設定（`flush_interval -1`）を確認 |
| SSM Run Command が「認証エラー」/構文エラー | コマンド文字列の `../`・`http://127.0.0.1`・シングルクォートが除去/遮断される。絶対パス・ヒアドキュメントで回避 |
| カスタムドメインが CloudFront 競合で FAILED | 同一 CNAME を別ディストリビューションが保持。旧ディストリビューションのエイリアスを外す |

---

## 8. コスト管理メモ

- 主な固定費：EBS(gp3 50GB)・Elastic IP(パブリック IPv4)・Route53 ホストゾーン・Amplify ホスティング。
  これらは **EC2 停止中も発生**する（数百円〜/月規模）。
- 変動費：**EC2 t3.medium の稼働時間**が最大要因。常時稼働とデモ時のみ起動で大きく変わる
  （概算は別途レポート参照）。
- **OpenAI API は AWS とは別請求**（チャット＝gpt-4o、ベクトル化＝text-embedding-3-small）。
  883 件の再ベクトル化自体は極小（数円規模）。
- コスト節約の基本運用：**デモ・確認時のみ EC2 起動、終わったら停止**。

---

## 9. アプリ概要（参考）

| 機能 | 接頭辞 | 概要 |
|---|---|---|
| 初期診断 (Onboarding) | `/api/v1/onboarding` | 質問票への回答収集・保存 |
| マッチング (Matching) | `/api/v1/matching` | プロファイル生成 + Qdrant 類似検索 |
| 職業情報 (Job) | `/api/v1/job` | 職業詳細・意味検索・閲覧履歴・Qdrant 同期 |
| AI チャット (Chat) | `/api/v1/chat` | OpenAI Streaming による会話 |
| Dreamer 管理 | `/api/v1/dreamer` | ユーザー / グループ CRUD・テストログイン |

**技術スタック**：FastAPI + Uvicorn / Python 3.12 / Prisma(prisma-py) / PostgreSQL 17.5 /
Qdrant / OpenAI(gpt-4o, text-embedding-3-small) / Docker Compose。

> 認証は MVP ではモック（ダミー UUID）。フロントは「名前＋学年」テストログイン運用
> （Cognito 不使用）。バックエンドはトークンを検証しない既知ギャップ。

---

## 10. 開発環境（ローカル）

ローカル開発は dev compose ＋ Makefile を使う（本番とは別系統）。

```bash
cp .env.example .env.local   # OPENAI_API_KEY を設定
make build-base              # 初回 / pyproject.toml 変更時
make up                      # 起動 → Prisma 生成 → CSV 取込 → Qdrant 同期
# http://localhost:8000/docs で Swagger UI
```

よく使う dev コマンド：`make down` / `make logs` / `make shell-app` / `make shell-db` /
`make prisma` / `make db-clean` / `make qdrant-clean` / `make sync-vectordb-rebuild`。

---

## 11. ドキュメント一覧

| ドキュメント | 内容 |
|---|---|
| [docs/architecture.md](docs/architecture.md) | システム構成・レイヤ設計・リクエストフロー |
| [docs/database.md](docs/database.md) | テーブル一覧・リレーション・DDL・運用 |
| [docs/development.md](docs/development.md) | 開発環境構築・Lint・CI/CD |
| [docs/environment-variables.md](docs/environment-variables.md) | 環境変数一覧・必須/任意・利用箇所 |
| [docs/directory-structure.md](docs/directory-structure.md) | 各ディレクトリの責務・依存関係 |

### Push 前チェック（CI: `develop`/`main`）

- [ ] Black 通過 — `uvx black --check .`
- [ ] Ruff 通過 — `uvx ruff check .`
- [ ] エンドポイント変更時は `PYTHONPATH=. python openapi.py` で `openapi.json` 更新
- [ ] `db/init.sql` と Prisma スキーマの整合
