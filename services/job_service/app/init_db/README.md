# SQL Initializer (Seeder)

`SqlInitializer` は、SQLAlchemyのモデル定義を利用して、データベースに接続せずに初期データ（シードデータ）用の `INSERT` 文を生成するためのPythonクラスです。

`{テーブル名}_init.sql` という形式で、SQLファイルをエクスポートします。

## 🚀 主な機能

* **DB接続不要**: データベースに接続せず、Pythonスクリプトのみで `INSERT` 文を生成します。
* **重複データの自動スキップ**: モデルに定義された `unique=True` 制約を読み取り、重複するデータを自動でスキップ（スルー）します。
* **データ追加時の返り値**: `add_data` メソッドは、正常に追加されたデータ（辞書）を返します。重複した場合は、**重複の原因となった既存のデータ（辞書）**を返します。
* **連番IDの自動採番**: `Integer` 型の主キー（例: `id`）が指定されない場合、`1`, `2`, `3`... と自動で連番を振ります。
* **UUIDの自動生成**: `UUID` 型かつ `nullable=False` のカラムが指定されない場合、`uuid.uuid4()` で自動生成します。
* **型サポート**: `string`, `int`, `float`, `bool`, `datetime`, `UUID` 型のSQLフォーマットに自動で対応します。

---

## 📖 使い方 (例)

`SqlInitializer` クラスをプロジェクトに保存（例: `sql_initializer.py`）した後、以下のようにモデルを読み込ませて使用します。

`run_seeder.py` として保存し、`SqlInitializer` と同じディレクトリで実行する想定です。

```python
import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
# (PostgreSQLのUUID型を使う例。標準のUUIDでも可)
from sqlalchemy.dialects.postgresql import UUID as pgUUID 

# ----------------------------------------------------
# 1. SqlInitializer クラスをインポート
# (別ファイル 'sql_initializer.py' から読み込む場合)
# from sql_initializer import SqlInitializer 
# ----------------------------------------------------

# (※ここに SqlInitializer クラス本体が定義されていると仮定します)

# --- 2. SQLAlchemyのモデルを定義 ---
Base = declarative_base()

class User(Base):
    """
    テスト用のUserモデル
    - id: 連番PK
    - user_uuid: 自動UUID (NOT NULL)
    - username: Unique
    """
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True) 
    user_uuid = Column(pgUUID(as_uuid=True), nullable=False) 
    username = Column(String(50), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow) # DB側で設定

class Product(Base):
    """
    テスト用のProductモデル
    - id: 連番PK
    - product_code: Unique
    """
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    product_code = Column(String(20), unique=True, nullable=False)
    name = Column(String(100))
    price = Column(Integer)


# --- 3. SqlInitializer のインスタンスを作成 ---
print("--- Initializerセットアップ ---")
user_initializer = SqlInitializer(User)
product_initializer = SqlInitializer(Product)


# --- 4. データを追加 (add_data) ---
print("\n--- ユーザーデータ追加 ---")

# 1件目 (正常に追加)
# id と user_uuid は自動設定される
res1 = user_initializer.add_data(username='alice')
print(f"Response 1 (追加): {res1}")

# 2件目 (正常に追加)
res2 = user_initializer.add_data(username='bob')
print(f"Response 2 (追加): {res2}")

# 3件目 (username='alice' が重複)
# res1 と同じ内容が返される
res3 = user_initializer.add_data(username='alice')
print(f"Response 3 (重複): {res3}") 

# 4件目 (IDを手動指定)
# user_uuid は自動設定される
res4 = user_initializer.add_data(id=10, username='charlie')
print(f"Response 4 (追加): {res4}")

# 5件目 (IDは自動設定)
# カウンターが 11 (res4の次) になっているので id=11 となる
res5 = user_initializer.add_data(username='david')
print(f"Response 5 (追加): {res5}")


# --- 5. データをまとめて追加 (add_many) ---
print("\n--- 商品データ追加 ---")
products_data = [
    {"product_code": "A-001", "name": "Laptop", "price": 150000},
    {"product_code": "A-002", "name": "Mouse", "price": 3500},
    {"product_code": "A-001", "name": "Duplicate Laptop", "price": 99999}, # 重複
]
added_products = product_initializer.add_many(products_data)
print(f"実際に追加された商品データ: {len(added_products)} 件")


# --- 6. SQLファイルとしてエクスポート ---
print("\n--- SQLエクスポート ---")
# 'sql_seed_output' というディレクトリに保存する例
output_directory = "sql_seed_output"

user_sql_file = user_initializer.export_to_sql(output_directory)
product_sql_file = product_initializer.export_to_sql(output_directory)

print(f"Users SQL: {user_sql_file}")
print(f"Products SQL: {product_sql_file}")
```
## 実行結果
```bash
--- Initializerセットアップ ---
[users] Initializerをセットアップ中...
  -> 連番(Serial)カラムを検出: id
  -> 自動UUIDカラムを検出: user_uuid
  -> Unique制約カラムを検出: {'username'}
[users] セットアップ完了。
[products] Initializerをセットアップ中...
  -> 連番(Serial)カラムを検出: id
  -> Unique制約カラムを検出: {'product_code'}
[products] セットアップ完了。

--- ユーザーデータ追加 ---
Response 1 (追加): {'username': 'alice', 'id': 1, 'user_uuid': UUID('...')}
Response 2 (追加): {'username': 'bob', 'id': 2, 'user_uuid': UUID('...')}
[users] 重複データ検出 (カラム: username, 値: 'alice')。
[users] 追加をスキップ。重複した既存データを返します。
Response 3 (重複): {'username': 'alice', 'id': 1, 'user_uuid': UUID('...')}
Response 4 (追加): {'id': 10, 'username': 'charlie', 'user_uuid': UUID('...')}
Response 5 (追加): {'username': 'david', 'id': 11, 'user_uuid': UUID('...')}

--- 商品データ追加 ---
[products] 重複データ検出 (カラム: product_code, 値: 'A-001')。
[products] 追加をスキップ。重複した既存データを返します。
実際に追加された商品データ: 2 件

--- SQLエクスポート ---
SQLファイルが正常にエクスポートされました: sql_seed_output/users_init.sql
SQLファイルが正常にエクスポートされました: sql_seed_output/products_init.sql
Users SQL: sql_seed_output/users_init.sql
Products SQL: sql_seed_output/products_init.sql
```