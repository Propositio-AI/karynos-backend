# 閲覧履歴API実装ガイド

## 概要
閲覧履歴を返すAPIを実装しました。ユーザーが閲覧した職業の履歴情報を取得できます。

## 実装内容

### 1. スキーマ定義（[schema.py](services/job_service/app/schema.py)）

#### ViewingHistoryItem
単一の閲覧履歴アイテムを表します。

```python
class ViewingHistoryItem(BaseModel):
    history_id: UUID                    # 履歴ID
    job_id: int                         # 職業ID
    job_name: str                       # 職業名
    job_imgs: List[str]                # 職業の画像リスト
    good: bool                          # いいねフラグ
    bad: bool                           # バッドフラグ
    save: bool                          # 保存フラグ
    created_at: str                     # 閲覧日時（ISO 8601形式）
```

#### ViewingHistoryResponse
閲覧履歴一覧のレスポンスを表します。

```python
class ViewingHistoryResponse(BaseModel):
    total_count: int                    # 総閲覧数
    items: List[ViewingHistoryItem]    # 閲覧履歴アイテムリスト
    created_at: str                     # レスポンス生成時刻（ISO 8601形式）
```

### 2. APIエンドポイント（[route/api/v1.py](services/job_service/app/route/api/v1.py)）

#### GET /api/v1/job/history

ユーザーの閲覧履歴を取得するエンドポイントです。

**リクエスト:**
- `dreamer_id`: UUID（自動取得 - 認証から）
- `limit`: int（オプション、デフォルト: 50） - 取得する件数
- `offset`: int（オプション、デフォルト: 0） - オフセット

**レスポンス:**
```json
{
    "total_count": 25,
    "items": [
        {
            "history_id": "uuid-string",
            "job_id": 1,
            "job_name": "プログラマー",
            "job_imgs": ["url1", "url2"],
            "good": true,
            "bad": false,
            "save": false,
            "created_at": "2026-02-22T10:30:45.123456"
        },
        {
            "history_id": "uuid-string",
            "job_id": 2,
            "job_name": "デザイナー",
            "job_imgs": ["url1"],
            "good": false,
            "bad": false,
            "save": true,
            "created_at": "2026-02-22T09:15:30.654321"
        }
    ],
    "created_at": "2026-02-22T10:35:00.123456"
}
```

**特徴:**
- 認証ユーザーの履歴のみ取得
- 新しい順にソート（created_at降順）
- ページネーション対応（limit/offset）
- ジョブ情報（名前、画像）を自動取得して含める
- エラーハンドリング完備

## 使用方法

### cURLでのテスト例

```bash
# 基本的な使用法
curl -X GET "http://localhost:8000/api/v1/job/history" \
  -H "Authorization: Bearer YOUR_TOKEN"

# ページネーション付き
curl -X GET "http://localhost:8000/api/v1/job/history?limit=10&offset=0" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 最新の5件を取得
curl -X GET "http://localhost:8000/api/v1/job/history?limit=5&offset=0" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 技術仕様

### データベースクエリ
- `HistoryTable`から`dreamer_id`に基づいてフィルタリング
- 各履歴に対応する`JobsTable`から職業情報を取得
- `created_at`で降順ソート（新しい順）

### エラーハンドリング
- 404: ユーザーが見つからない
- 500: データベースクエリエラー
- 個別の履歴アイテム処理エラーはログ出力し、スキップ

### パフォーマンス
- ページネーション実装（デフォルトlimit=50）
- 不要なデータベースクエリを最小化
- 異常データもスキップして処理を継続

## 関連するモデル

### HistoryTable
- `history_id`: UUID（主キー）
- `job_id`: INTEGER（外部キー）
- `dreamer_id`: UUID
- `good`: BOOLEAN
- `bad`: BOOLEAN
- `save`: BOOLEAN
- `created_at`: DateTime

### JobsTable
- `job_id`: INTEGER（主キー）
- `name`: TEXT
- `imgs`: 関連テーブルから取得

## 実装ファイル修正履歴

1. **schema.py**: ViewingHistoryItem, ViewingHistoryResponseクラスを追加
2. **route/api/v1.py**: get_viewing_historyエンドポイントを追加、インポート更新

---

実装日: 2026-02-22
