# Auth Service

[システム設計](https://www.notion.so/Karynos-backend-module-1b39a9038f388050816afe733aa3cdfc?source=copy_link#2109a9038f3880f694f2de2abb5ef125)

## 概要

Auth Serviceではkarynosにおいて認証・認可のサービスを提供します。

## 技術スタック

```
python==3.12

postgresql==17.5
```

## 環境構築

```
docker-compose build
```

## 実行方法

```
docker-compose up -d
```

## コンテナへの入り方

app
```
docker-compose exec app bash
```

db
```
docker-compose exec db bash // コンテナに入る
psql -U auth_service_admin -d auth // PostgreSQLに入る
```

## フォルダ構成

`*`がついているファイルは編集しないでください。

```
app/
├── api/
│   ├── v1/
│   │   ├── endpoints/
│   │   │   ├── mail_send.py      # /send関連エンドポイント
│   │   │   └── vertify.py        # /vertify関連エンドポイント
│   │   └── *api_router.py        # V1全体のルーター統括
│   └── *main_router.py           # バージョン統括ルーター（/api/v1）
│
├── core/
│   ├── *config.py                # 環境変数読み込み（pydantic）
│   ├── *db.py                    # DBセッション設定
│   ├── *init_db.py               # DB初期データの挿入
│
├── crud/
│   ├── Auth.py                   # AuthTable関連のCRUD操作
│   └── Refresh.py　　　　　       # RefreshTable関連のCRUD操作
│
├── models/
│   ├── *__init__.py               
│   ├── *AuthTable.py             # AuthTable 定義
│   ├── *base.py                  # SQLAlchemy 定義
│   └── *RefreshTable.py          # RefreshTable 定義
│
├── schemas/
│   ├── Auth.py                   # Pydanticモデル
│   └── Refresh.py
│
├── utils/
│   └── time.py                   # 時間関係
│
├── *tests/
│   └── db-data/                  # 開発用DBデータ
│
├── *main.py                      # アプリエントリーポイント
└── *__init__.py

```

### ファイル分割戦略

| フォルダパス | 分割単位 | 
|-------------|---------|
| `/api/v1/endpoints` | エンドポイントごと |
| `/crud` | テーブルごと |
| `/models` | テーブルごと |
| `/schemas` | テーブルごと |

### 
```
get_*	取得（1件またはリスト）
create_*	新規作成
update_*	更新
delete_*	削除
exists_*, is_*	真偽判定や存在チェックなど
```