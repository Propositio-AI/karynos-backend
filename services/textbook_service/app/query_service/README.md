# Query Service

[システム設計](https://www.notion.so/Karynos-backend-module-1b39a9038f388050816afe733aa3cdfc?source=copy_link#2119a9038f3880f6b72aee29c19fa59b)

## 概要

QueryServiceではKarynosにおいてユーザーからのクエリーの管理サービスを提供します。

## 技術スタック

```
python==3.12

postgresql==17.5
```

## コンテナのビルド

```
docker compose build
```

## コンテナの起動

```
docker compose --env-file .env_dev up -d
```

## コンテナ内への入り方

app
```
docker-compose exec app bash
```

db
```
docker-compose exec user-db bash // コンテナに入る
psql -U karynos_admin -d user // PostgreSQLへログイン
```

## フォルダ構成

`*`がついているファイルは編集しないでください。

```
app/
├── api/
│   ├── v1/
│   │   ├── endpoints/
│   │   │   └── query.py           # /archive関連エンドポイント
│   │   │   └── infer.py           # /archive/infer関連エンドポイント
│   │   └── *api_router.py        # V1全体のルーター統括
│   └── **main_router.py          # バージョン統括ルーター（/api/v1）
│
├── core/
│   ├── *config.py                # 環境変数読み込み（pydantic）
│   ├── **db.py                   # DBセッション設定
│   └── *init_db.py               # DB初期データの挿入
│
├── crud/
│   └── Query.py                  # QueryTable関連のCRUD操作
│
├── models/             
│   ├── *QueryTable.py            # QueryTable 定義
│   └── **base.py                 # SQLAlchemy 定義
│
├── schemas/                      # Pydanticモデル
│   └── QuerySchema.py                   
│
├── utils/
│   └── time.py                   # 時間関係
│
├── tests/
│   └── **db-data/                # 開発用DBデータ
│
├── *.env                         # 本番用環境変数
├── *.env_dev                     # 開発用環境変数
|
├── **.gitignore                     
|
├── *docker-compose.yml                            
├── **Dockerfile                            
|
├── *requirements.txt                            
|
├── *README.md                            
|
├── **main.py                     # アプリエントリーポイント
└── **__init__.py

```