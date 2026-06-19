# API 仕様

すべてのエンドポイントは `/api/v1` プレフィックスを持つ。

## 統一エラーレスポンス

```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "クラスが見つかりません",
    "detail": null
  }
}
```

| HTTP | code |
|---|---|
| 400 | `BAD_REQUEST` |
| 401 | `UNAUTHORIZED` |
| 403 | `FORBIDDEN` |
| 404 | `NOT_FOUND` |
| 422 | `VALIDATION_ERROR` |
| 500 | `INTERNAL_SERVER_ERROR` |

---

## Mentor API

認可: `Authorization: Bearer <Mentor JWT>` が必要。

### プロフィール

| メソッド | パス | 説明 |
|---|---|---|
| `GET` | `/mentor/me` | 自分の Mentor プロフィールを取得 |

### クラス管理

| メソッド | パス | 説明 |
|---|---|---|
| `GET` | `/mentor/classes` | 担当クラス一覧 |
| `POST` | `/mentor/classes` | クラス作成 |
| `GET` | `/mentor/classes/{class_id}` | クラス取得 |
| `PUT` | `/mentor/classes/{class_id}` | クラス更新 |
| `DELETE` | `/mentor/classes/{class_id}` | クラス削除 |

**POST /mentor/classes リクエスト**
```json
{
  "name": "3年A組",
  "subject": "数学",
  "description": "説明",
  "academic_year": 2025
}
```

**ClassResponse**
```json
{
  "class_id": "uuid",
  "mentor_id": "uuid",
  "name": "3年A組",
  "subject": "数学",
  "description": null,
  "academic_year": 2025,
  "enrolled_count": 30,
  "material_count": 5,
  "created_at": "2025-01-01T00:00:00",
  "updated_at": "2025-01-01T00:00:00"
}
```

### 履修生徒管理

| メソッド | パス | 説明 |
|---|---|---|
| `GET` | `/mentor/classes/{class_id}/students` | 生徒一覧（`limit`, `offset`）|
| `GET` | `/mentor/classes/{class_id}/students/{dreamer_id}` | 生徒詳細（Dream Matching 傾向含む）|
| `POST` | `/mentor/classes/{class_id}/students` | 生徒追加 |
| `DELETE` | `/mentor/classes/{class_id}/students/{dreamer_id}` | 生徒削除 |

**GET /students/{dreamer_id} レスポンス**
```json
{
  "dreamer_id": "uuid",
  "name_family": "田中",
  "name_given": "太郎",
  "name": "田中 太郎",
  "enrolled_at": "2025-04-01T00:00:00",
  "interest_jobs": [
    {"job_id": 1, "job_name": "エンジニア", "good": true, "bad": false, "save": true}
  ],
  "top_categories": ["IT・通信", "製造"],
  "total_viewed": 15,
  "liked_count": 5
}
```

### 授業資料管理

| メソッド | パス | 説明 |
|---|---|---|
| `GET` | `/mentor/classes/{class_id}/materials` | 資料一覧（`limit`, `offset`）|
| `POST` | `/mentor/classes/{class_id}/materials` | 資料アップロード（multipart/form-data）|
| `GET` | `/mentor/classes/{class_id}/materials/{material_id}` | 資料取得 |
| `PUT` | `/mentor/classes/{class_id}/materials/{material_id}` | メタデータ更新（タイトル・科目・単元）|
| `DELETE` | `/mentor/classes/{class_id}/materials/{material_id}` | ソフトデリート |

**POST /materials フォームフィールド**

| フィールド | 型 | 必須 | 説明 |
|---|---|---|---|
| `file` | File | ✓ | PDF / DOCX / PPTX / TXT / MD（最大 20MB）|
| `title` | string | ✓ | 資料タイトル |
| `subject` | string | - | 科目 |
| `unit` | string | - | 単元 |
| `description` | string | - | 説明 |

### クラス集計

| メソッド | パス | 説明 |
|---|---|---|
| `GET` | `/mentor/classes/{class_id}/analytics` | クラス全体集計 |

**ClassAnalyticsResponse**
```json
{
  "class_id": "uuid",
  "total_students": 30,
  "top_job_categories": [
    {"category_name": "IT・通信", "count": 12}
  ],
  "generated_materials_count": 150,
  "distributed_materials_count": 120,
  "pending_review_count": 30
}
```

---

## Dream Action API (Mentor 向け)

認可: `Authorization: Bearer <Mentor JWT>` が必要。

### 補助教材生成

| メソッド | パス | 説明 |
|---|---|---|
| `POST` | `/mentor/classes/{class_id}/dream-action/generate` | 生成ジョブをトリガー（202 Accepted）|
| `GET` | `/mentor/classes/{class_id}/dream-action/jobs` | 生成ジョブ一覧 |
| `GET` | `/mentor/classes/{class_id}/dream-action/jobs/{job_id}` | ジョブ進捗取得 |

**POST /generate リクエスト**
```json
{
  "lesson_material_id": "uuid",
  "target_dreamer_ids": ["uuid", "uuid"],
  "force_regenerate": false
}
```
- `target_dreamer_ids` 省略時はクラス全員を対象にする
- `force_regenerate: true` で既存教材を再生成する（冪等キーを上書き）

**TriggerGenerationResponse**
```json
{
  "generation_job_id": "uuid",
  "status": "PENDING",
  "message": "補助教材の生成を開始しました"
}
```

**GenerationJobResponse**
```json
{
  "generation_job_id": "uuid",
  "lesson_material_id": "uuid",
  "class_id": "uuid",
  "status": "PROCESSING",
  "progress": 60,
  "total_dreamers": 30,
  "completed_dreamers": 18,
  "error_message": null,
  "started_at": "2025-06-01T10:00:00",
  "completed_at": null,
  "created_at": "2025-06-01T10:00:00",
  "updated_at": "2025-06-01T10:00:30"
}
```

**GenerationJob.status 値**

| 値 | 説明 |
|---|---|
| `PENDING` | 生成待ち |
| `PROCESSING` | 生成中 |
| `COMPLETED` | 完了 |
| `FAILED` | 失敗 |

### 補助教材管理・配布

| メソッド | パス | 説明 |
|---|---|---|
| `GET` | `/mentor/classes/{class_id}/dream-action/materials` | 生成教材一覧（`status`, `lesson_material_id`, `limit`, `offset`）|
| `GET` | `/mentor/classes/{class_id}/dream-action/materials/{id}` | 教材詳細（本文含む）|
| `POST` | `/mentor/classes/{class_id}/dream-action/distribute` | 選択した教材を配布 |
| `POST` | `/mentor/classes/{class_id}/dream-action/materials/{id}/regenerate` | 個別再生成 |

**POST /distribute リクエスト**
```json
{
  "generated_material_ids": ["uuid", "uuid"]
}
```

**DistributeMaterialResponse**
```json
{
  "distributed_count": 2,
  "message": "2 件の教材を配布しました"
}
```

**GeneratedMaterial.status 値**

| 値 | 説明 |
|---|---|
| `DRAFT` | 生成完了・教員未確認 |
| `REVIEWING` | 教員確認中（将来の拡張） |
| `DISTRIBUTED` | 配布済み（生徒が閲覧可能） |

---

## Dream Action API (Dreamer 向け)

認可: `Authorization: Bearer <Dreamer JWT>` が必要。配布済み（DISTRIBUTED）教材のみ取得可。

| メソッド | パス | 説明 |
|---|---|---|
| `GET` | `/dream-action/materials` | 自分の補助教材一覧（`limit`, `offset`）|
| `GET` | `/dream-action/materials/{id}` | 補助教材詳細（本文含む）|
| `PATCH` | `/dream-action/materials/{id}/read` | 既読にする |

**GeneratedMaterialSummary**
```json
{
  "generated_material_id": "uuid",
  "lesson_material_id": "uuid",
  "dreamer_id": "uuid",
  "job_id": 1,
  "job_name": "エンジニア",
  "title": "エンジニア を目指す 田中 太郎 さんへ（二次方程式の解法）",
  "status": "DISTRIBUTED",
  "is_read": false,
  "distributed_at": "2025-06-01T12:00:00",
  "created_at": "2025-06-01T10:00:00",
  "updated_at": "2025-06-01T12:00:00"
}
```

**GeneratedMaterialDetail** は上記に加えて `content` フィールド（Markdown 本文）を含む。

---

## 既存 API（Dream Matching）

認可: `Authorization: Bearer <Dreamer JWT>` が必要。

| メソッド | パス | 説明 |
|---|---|---|
| `GET` | `/matching/recommend` | 職業推薦（ベクトル検索）|
| `GET` | `/matching/recommend/debug` | デバッグ情報付き推薦 |
| `GET` | `/job/detail/{job_id}` | 職業詳細 |
| `GET` | `/job/history` | 閲覧履歴 |
| `GET` | `/job/search` | テキスト意味検索 |
| `POST` | `/job/history/{job_id}` | 閲覧履歴作成 |
| `PUT` | `/job/history/{history_id}` | good / bad / save 更新 |

---

## ページネーション

一覧 API は以下のクエリパラメータをサポートする。

| パラメータ | 型 | デフォルト | 説明 |
|---|---|---|---|
| `limit` | int (1-200) | 50 | 取得件数 |
| `offset` | int (≥0) | 0 | スキップ件数 |

レスポンス:
```json
{
  "items": [...],
  "total": 150
}
```
