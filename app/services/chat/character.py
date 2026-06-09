import json
import random
from pathlib import Path


def generate_name(name_type=None, data_file=None):
    if name_type is None:
        name_type = ["japanese_surnames", "japanese_unisex_names"]
    if data_file is None:
        data_file = Path(__file__).resolve().parent / "names.json"

    try:
        with open(data_file, encoding="utf-8") as file:
            names_data = json.load(file)

        result_names = []
        for key in name_type:
            if key not in names_data:
                return f"エラー: '{key}' はデータファイルに存在しません"
            result_names.append(random.choice(names_data[key]))
        return " ".join(result_names)
    except Exception as exc:
        return f"エラーが発生しました: {exc}"
