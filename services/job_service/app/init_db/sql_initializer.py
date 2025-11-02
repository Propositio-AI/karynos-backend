import os
import datetime
import uuid  # UUID生成のため
from sqlalchemy.inspection import inspect  # モデル定義の読み取り
from sqlalchemy.types import Integer, BigInteger, UUID  # 型判定のため
from sqlalchemy.dialects import postgresql  # PostgreSQLのUUID型判定のため

class SqlInitializer:
    """
    SQLAlchemyのモデルクラスを受け取り、追加されたデータを
    INSERT文のSQLファイルとしてエクスポートするクラス。

    機能:
    - Unique制約を考慮し、重複データはスルーします。
    - add_data時に、指定がなければIntegerのPKを連番で、
      nullable=FalseのUUIDを自動生成します。
    - add_dataは追加された辞書データ、または重複した既存データを返します。
    """

    def __init__(self, model_class):
        """
        初期化時にモデルクラスを受け取ります。
        Unique制約、連番カラム、自動UUIDカラムを特定します。
        """
        self.model_class = model_class
        self.table_name = model_class.__tablename__
        self.data_to_insert = []
        
        self.unique_columns = set()
        
        # デフォルト自動設定カラムの特定
        self.serial_col_name = None  # 連番(Integer PK)カラム名
        self.serial_counter = 1      # 連番カウンター
        self.uuid_cols = set()       # 自動生成するUUIDカラム名
        
        print(f"[{self.table_name}] Initializerをセットアップ中...")
        
        try:
            mapper = inspect(model_class)
            for col in mapper.columns:
                # 1. Unique制約
                if col.unique:
                    self.unique_columns.add(col.name)
                
                # 2. 連番カラムの特定 (Integer型かつPrimary Key)
                if col.primary_key and isinstance(col.type, (Integer, BigInteger)):
                    self.serial_col_name = col.name
                    print(f"  -> 連番(Serial)カラムを検出: {self.serial_col_name}")

                # 3. 自動UUIDカラムの特定 (UUID型かつ NOT NULL)
                if isinstance(col.type, (UUID, postgresql.UUID)) and not col.nullable:
                    self.uuid_cols.add(col.name)
                    print(f"  -> 自動UUIDカラムを検出: {col.name}")

        except Exception as e:
            print(f"Warning: {self.table_name} のカラム解析に失敗しました: {e}")

        if self.unique_columns:
            print(f"  -> Unique制約カラムを検出: {self.unique_columns}")
        
        print(f"[{self.table_name}] セットアップ完了。")

    def _format_sql_value(self, value):
        """
        Pythonの値をSQLの値の文字列にフォーマットします。
        """
        if value is None:
            return "NULL"
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, bool):
            return "TRUE" if value else "FALSE"
        elif isinstance(value, uuid.UUID):
            # UUID型を文字列に変換
            return f"'{str(value)}'"
        elif isinstance(value, (datetime.datetime, datetime.date)):
            # ISO 8601形式の文字列に変換
            return f"'{value.isoformat()}'"
        elif isinstance(value, str):
            # SQLインジェクションを防ぐため、シングルクォートをエスケープ
            escaped_value = value.replace("'", "''")
            return f"'{escaped_value}'"
        else:
            # その他の型も文字列としてエスケープ処理
            escaped_value = str(value).replace("'", "''")
            return f"'{escaped_value}'"

    def _is_duplicate(self, new_data: dict) -> dict | None:
        """
        Unique制約カラムにおいて重複がないかチェックします。
        重複する場合は、*重複の原因となった既存のデータ*を返します。
        重複しない場合は None を返します。
        """
        if not self.unique_columns:
            return None  # チェック対象がない
            
        for col_name in self.unique_columns:
            # 新しいデータに、チェック対象のカラムが含まれているか
            if col_name in new_data:
                new_value = new_data[col_name]
                
                # None (NULL) は重複チェックの対象外
                if new_value is None:
                    continue

                # 既存データ(self.data_to_insert)をスキャン
                for existing_data in self.data_to_insert:
                    if existing_data.get(col_name) == new_value:
                        # 重複を発見
                        print(f"[{self.table_name}] 重複データ検出 (カラム: {col_name}, 値: '{new_value}')。")
                        return existing_data  # 重複した既存データを返す
        
        # 重複なし
        return None

    def add_data(self, **kwargs) -> dict | None:
        """
        データを1行追加し、処理後の辞書を返します。
        
        - 正常に追加された場合は、*追加されたデータ*を返します。
        - Unique制約に違反する場合、*重複した既存のデータ*を返します。
        """
        data_to_add = kwargs.copy()
        
        # --- 1. デフォルト値の自動設定 ---
        
        # 1a. 連番(Serial)カラムの処理
        if self.serial_col_name:
            if self.serial_col_name in data_to_add:
                # もしIDが手動で指定されたら、カウンターを更新
                # (次に自動採番されるIDが、手動指定のIDより大きくなるように)
                self.serial_counter = max(
                    self.serial_counter, 
                    data_to_add[self.serial_col_name] + 1
                )
            else:
                # IDが指定されなければ、カウンターから採番
                data_to_add[self.serial_col_name] = self.serial_counter
                # ※カウンターのインクリメントは、重複チェック通過後に行う
        
        # 1b. 自動UUIDカラムの処理
        for col_name in self.uuid_cols:
            if col_name not in data_to_add:
                # UUIDが指定されなければ、自動生成
                data_to_add[col_name] = uuid.uuid4()
        
        # --- 2. 重複チェック ---
        
        # _is_duplicate は重複した既存データを返す (なければ None)
        conflicting_data = self._is_duplicate(data_to_add)
        
        if conflicting_data:
            # 重複した場合
            print(f"[{self.table_name}] 追加をスキップ。重複した既存データを返します。")
            return conflicting_data  # 重複した既存データを返す
        
        # --- 3. 重複がなかったので、データを確定・追加 ---
        
        # 連番カラムが *自動採番された* (手動指定でなかった) 場合のみ、カウンターをインクリメント
        if self.serial_col_name and (self.serial_col_name not in kwargs):
             self.serial_counter += 1

        self.data_to_insert.append(data_to_add)
        
        # 正常に追加されたデータを返す
        return data_to_add

    def add_many(self, data_list: list[dict]) -> list[dict]:
        """
        挿入するデータを辞書のリストでまとめて追加します。
        正常に追加されたデータのリストを返します。
        (重複したデータは返り値のリストに含まれません)
        """
        added_items = []
        for data_item in data_list:
            # add_data の返り値 (正常追加データ or 重複データ) を受け取る
            added_item_or_conflict = self.add_data(**data_item)
            
            # 返り値が None ではなく、かつ、重複データでもない
            # (＝self.data_to_insert に実際に追加されたオブジェクトそのもの) かをチェック
            if added_item_or_conflict is not None and \
               added_item_or_conflict in self.data_to_insert:
                 # 正常に追加されたものだけをリストに追加
                 added_items.append(added_item_or_conflict)
                 
        return added_items

    def export_to_sql(self, output_dir: str = ".") -> str:
        """
        蓄積されたデータを元に INSERT 文を作成し、
        {テーブル名}_init.sql という名前でファイルに保存します。

        Args:
            output_dir (str, optional): 出力先のディレクトリ。デフォルトはカレントディレクトリ。

        Returns:
            str: 保存されたファイルのフルパス (データがない場合は None)
        """
        if not self.data_to_insert:
            print(f"Warning: {self.table_name} に挿入するデータがありません。SQLファイルは作成されません。")
            return None

        sql_statements = []

        for data_dict in self.data_to_insert:
            if not data_dict:
                continue

            # カラム名をダブルクォートで囲む（予約語対策）
            columns = [f'"{key}"' for key in data_dict.keys()]
            values = [self._format_sql_value(val) for val in data_dict.values()]

            columns_str = ", ".join(columns)
            values_str = ", ".join(values)

            sql = f"INSERT INTO {self.table_name} ({columns_str}) VALUES ({values_str});"
            sql_statements.append(sql)

        # ファイル名の決定と保存
        filename = f"{self.table_name}_init.sql"
        file_path = os.path.join(output_dir, filename)

        # ディレクトリが存在しない場合は作成
        os.makedirs(output_dir, exist_ok=True)

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("\n".join(sql_statements))
                f.write("\n") # 最後に改行を追加
            
            print(f"SQLファイルが正常にエクスポートされました: {file_path}")
            return file_path
        
        except IOError as e:
            print(f"ファイルの書き込みに失敗しました: {e}")
            return None