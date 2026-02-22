# 職業検索API実装ガイド

## 概要
職業を自由度高く検索できるAPIを実装しました。ベクトル類似度検索を活用して、様々な属性から職業を検索できます。

## 実装内容

### 1. スキーマ定義（[schema.py](services/job_service/app/schema.py)）

#### JobSearchResult
単一の検索結果アイテムを表します。

```python
class JobSearchResult(BaseModel):
    job_id: int                         # 職業ID
    name: str                           # 職業名
    description: str                    # 職業説明
    imgs: List[str]                    # 職業の画像リスト
    personality_traits: str             # 求められる性格特性
    appeal_points: str                 # アピールポイント
    growth_opportunities: str           # 成長機会
    similarity_score: float             # 検索クエリとの類似度スコア（0-100）
```

#### JobSearchResponse
検索結果一覧のレスポンスを表します。

```python
class JobSearchResponse(BaseModel):
    query: str                          # 検索クエリ
    total_count: int                    # マッチした職業数
    items: List[JobSearchResult]       # 検索結果リスト
    created_at: str                     # レスポンス生成時刻（ISO 8601形式）
```

### 2. APIエンドポイント（[route/api/v1.py](services/job_service/app/route/api/v1.py)）

#### GET /api/v1/job/search

職業を自由度高く検索するエンドポイントです。

**リクエストパラメータ:**
- `q` (string, 必須): 検索クエリ（日本語対応）
- `limit` (int, オプション, デフォルト: 20): 取得する件数（1-100）
- `offset` (int, オプション, デフォルト: 0): オフセット

**レスポンス例:**
```json
{
    "query": "人と関わる仕事",
    "total_count": 45,
    "items": [
        {
            "job_id": 1,
            "name": "営業職",
            "description": "商品やサービスを顧客に販売する職業...",
            "imgs": ["url1", "url2"],
            "personality_traits": "コミュニケーション能力、積極性、説得力",
            "appeal_points": "人間関係の構築、成功時の達成感",
            "growth_opportunities": "マネジメント職への昇進、専門性の深化",
            "similarity_score": 92.5
        },
        {
            "job_id": 5,
            "name": "営養士",
            "description": "栄養に関する指導と管理を行う職業...",
            "imgs": ["url1"],
            "personality_traits": "思いやり、教育心、専門知識への執着",
            "appeal_points": "人の健康に貢献できる",
            "growth_opportunities": "スポーツ栄養、食品開発分野への転職",
            "similarity_score": 87.3
        }
    ],
    "created_at": "2026-02-22T10:40:00.123456"
}
```

## 検索の仕組み

### ベクトル類似度検索の活用
このAPIはChroma DBのベクトル類似度検索を使用しています：

1. ユーザーの検索クエリをベクトルに変換
2. 職業データベース内のすべての職業情報（名前、説明、性格特性、アピールポイントなど）と比較
3. コサイン類似度に基づいてマッチ度（0-100スコア）を計算
4. スコアが高い順に結果を返却

### 検索可能な属性
以下の属性から、文脈を理解した検索が可能です：

- **職業名**: 「プログラマー」「看護師」など
- **得意なこと**: 「人と関わる」「創造的」「分析的」など
- **性格特性**: 「コミュニケーション能力」「責任感」など
- **アピールポイント**: 「安定性」「やりがい」「成長機会」など
- **職業説明**: 「毎日違う」「チームで働く」など
- **複合的なクエリ**: 「安定して稼げて人と関わる仕事」

## 使用例

### cURLでのテスト

```bash
# 1. 基本的な検索
curl -X GET "http://localhost:8000/api/v1/job/search?q=人と関わる仕事" \
  -H "Accept: application/json"

# 2. ページネーション付き
curl -X GET "http://localhost:8000/api/v1/job/search?q=創造性が必要&limit=10&offset=0" \
  -H "Accept: application/json"

# 3. 複合的なクエリ
curl -X GET "http://localhost:8000/api/v1/job/search?q=安定して稼げて人間関係が良い&limit=15" \
  -H "Accept: application/json"

# 4. 職業名での直接検索
curl -X GET "http://localhost:8000/api/v1/job/search?q=エンジニア&limit=20" \
  -H "Accept: application/json"
```

### JavaScriptでの使用例

```javascript
// 基本的な検索
async function searchJobs(query) {
    const response = await fetch(
        `/api/v1/job/search?q=${encodeURIComponent(query)}&limit=20`
    );
    const data = await response.json();
    console.log(data.items);
}

// 使用例
searchJobs("人と関わる仕事");
searchJobs("在宅勤務できる");
searchJobs("高年収");
```

## 検索クエリの例

| クエリ | 想定される結果 |
|--------|-------------|
| `人と関わる仕事` | 営業職、カウンセラー、教師、営養士など |
| `創造的な仕事` | デザイナー、イラストレーター、建築家など |
| `安定している` | 公務員、銀行員、教員など |
| `高年収` | 医師、弁護士、エンジニア上級職など |
| `在宅勤務` | プログラマー、ライター、デザイナーなど |
| `体を動かす` | スポーツインストラクター、建設作業員など |
| `専門性が必要` | 医師、弁護士、エンジニアなど |
| `やりがいがある` | 看護師、社会福祉士、ジャーナリストなど |

## エラーハンドリング

| ステータスコード | エラー | 説明 |
|-----------------|-------|------|
| 400 | 検索クエリが空 | qパラメータが指定されていない |
| 500 | ベクトルDBエラー | Chroma DBが初期化されていない |
| 500 | 検索処理エラー | その他のエラー |

## 技術仕様

### ベクトル埋め込みモデル
- **モデル名**: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
- **言語対応**: 多言語（日本語含む）
- **次元数**: 384次元
- **類似度メトリクス**: コサイン距離

### データベースへのアクセス
- `JobsTable`から職業情報を取得
- `VectorSearchRecommender`を使用したベクトル検索

### パフォーマンス
- ベクトル検索はメモリ効率的で、大規模データセットに対応
- ページネーション実装により、クライアント側の負荷を軽減
- 検索結果キャッシング（オプション）による高速化可能

## 注意事項

### 前提条件
- Chroma DBが初期化されている必要があります
- 職業データが`/admin/sync-chromadb`エンドポイントで同期されている必要があります

### 推奨される使用方法
1. 初回は`limit=20`で検索
2. 結果数が多い場合はページネーション（offset）で次ページを取得
3. 類似度スコア80以上の結果をハイライト表示するなど、UXを工夫

## 実装ファイル修正履歴

1. **schema.py**: JobSearchResult, JobSearchResponseクラスを追加
2. **route/api/v1.py**: search_jobsエンドポイントを追加、インポート更新

---

実装日: 2026-02-22
