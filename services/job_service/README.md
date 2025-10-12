# User Service

[システム設計](https://www.notion.so/Karynos-backend-module-1b39a9038f388050816afe733aa3cdfc?source=copy_link#2109a9038f388027b50cd137a959e89e)

## 概要

User serviceではKarynosにおいてユーザー管理のサービスを提供します。

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
│   │   │   └── user.py           # /user関連エンドポイント
│   │   └── *api_router.py        # V1全体のルーター統括
│   └── **main_router.py          # バージョン統括ルーター（/api/v1）
│
├── core/
│   ├── *config.py                # 環境変数読み込み（pydantic）
│   ├── **db.py                   # DBセッション設定
│   └── *init_db.py               # DB初期データの挿入
│
├── crud/
│   ├── User.py                   # UserTable関連のCRUD操作
│   └── UserType.py　　　　　      # UserTypeTable関連のCRUD操作
│
├── models/             
│   ├── *UserTable.py             # UserTable 定義
│   ├── **base.py                 # SQLAlchemy 定義
│   └── *UserTypeTable.py         # UserTypeTable 定義
│
├── schemas/
│   ├── Auth.py                   # Pydanticモデル
│   └── Refresh.py
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