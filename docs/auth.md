# 認証・認可設計

## 認証方式

Amazon Cognito ＋ JWT（RS256）を使用する。
クライアントは Cognito でサインインし、受け取った ID トークン（JWT）を
`Authorization: Bearer <token>` ヘッダーに付与してリクエストする。

---

## JWT 検証フロー

`app/lib/auth.py` がミドルウェア相当の依存関係として機能する。

```
1. Authorization: Bearer <jwt> を受け取る
2. JWT ヘッダーから kid を取得
3. Cognito JWKS エンドポイントから公開鍵を取得（lru_cache でキャッシュ）
   URL: https://cognito-idp.{region}.amazonaws.com/{pool_id}/.well-known/jwks.json
4. RS256 署名を検証
5. iss（Cognito User Pool エンドポイント）を検証
6. aud / client_id（COGNITO_CLIENT_ID）を検証
7. exp（有効期限）を検証
8. cognito:groups クレームからロールを判定
9. cognito_sub から DB の dreamer_id / mentor_id を解決
```

---

## JWT クレーム設計

| クレーム | 型 | 説明 |
|---|---|---|
| `sub` | `string` | Cognito が発行するユーザー識別子 |
| `cognito:groups` | `string[]` | ユーザーが属するグループ（`Dreamer` / `Mentor`） |
| `iss` | `string` | `https://cognito-idp.{region}.amazonaws.com/{pool_id}` |
| `aud` / `client_id` | `string` | Cognito アプリクライアント ID |
| `exp` | `number` | Unix タイムスタンプ（有効期限） |

### ロール判定

- `cognito:groups` に `"Mentor"` が含まれる → `Mentor`
- それ以外（`"Dreamer"` または グループなし） → `Dreamer`

---

## データスコープ（認可）

認可チェックはすべてサービス層（`app/services/`）で行う。

| ロール | アクセス可能なデータ |
|---|---|
| Dreamer | 自分自身の Dreamer レコード・閲覧履歴・回答・配布済み補助教材のみ |
| Mentor | 自分が担当するクラス・そのクラスに履修する生徒の基本情報と関心傾向・授業資料・生成教材のみ |

- Mentor が他のメンターのクラスにアクセスしようとすると `403 FORBIDDEN`
- Dreamer が自分以外の教材を取得しようとすると `403 FORBIDDEN`

### データスコープ実装箇所

```python
# MentorService._require_class — クラスの帰属確認
if str(cls.mentor_id) != mentor_id:
    raise HTTPException(status_code=403, detail="このクラスにはアクセスできません")

# DreamActionService.get_material_for_dreamer — 生徒スコープ確認
if str(mat.dreamer_id) != dreamer_id:
    raise HTTPException(status_code=403, detail="この教材にはアクセスできません")
```

---

## FastAPI 依存関係

| 関数 | 対象ロール | 返り値 |
|---|---|---|
| `get_current_user_id` | Dreamer のみ | `UUID`（dreamer_id） |
| `get_current_dreamer_sub` | Dreamer のみ | `str`（cognito_sub） |
| `get_current_mentor_sub` | Mentor のみ | `str`（cognito_sub） |
| `get_current_role` | Dreamer / Mentor | `"Dreamer"` / `"Mentor"` |

---

## モックモード（開発用）

`COGNITO_USER_POOL_ID` が未設定の場合、JWT 検証をスキップしてモック値を返す。

| 関数 | 返り値 |
|---|---|
| `get_current_user_id` | `UUID("00000000-0000-0000-0000-000000000001")` |
| `get_current_dreamer_sub` | `"mock-dreamer-sub"` |
| `get_current_mentor_sub` | `"mock-mentor-sub"` |
| `get_current_role` | `"Dreamer"` |

**Mentor モックの注意点**: `resolve_mentor_id("mock-mentor-sub")` は
`MentorService` が固定値 `"00000000-0000-0000-0000-000000000002"` を返す。
`make seed` で対応するシードデータを事前に投入すること。

---

## 未成年データの取り扱い方針

生徒（Dreamer）は未成年を含む。以下の方針を遵守する。

1. **最小権限**: Mentor は自クラスの生徒の基本情報（氏名）と関心傾向（いいねした職業カテゴリ）のみ参照できる。個人の全閲覧履歴は教員 API では返さない（集計値のみ）。
2. **生成教材の事前確認**: AI 生成教材は必ず DRAFT 状態で保存し、教員が確認・承認してから配布する（`REVIEWING` → `DISTRIBUTED` の状態遷移）。
3. **モデレーション**: 生成後に LLM によるモデレーションチェックを実施し、不適切コンテンツは DRAFT にすら保存しない。
4. **アクセスログ（TODO）**: 教員による生徒データアクセスをログに記録することが望ましい（未実装）。

---

## 環境変数

| 変数名 | 必須 | 説明 |
|---|---|---|
| `COGNITO_USER_POOL_ID` | 任意（未設定でモックモード） | 例: `ap-northeast-1_XXXXXXXX` |
| `COGNITO_CLIENT_ID` | 任意 | Cognito アプリクライアント ID |
| `AWS_REGION` | 任意（デフォルト: `ap-northeast-1`） | Cognito が存在するリージョン |
