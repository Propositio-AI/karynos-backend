import json
import random

# 名前を生成する関数
def generate_name(name_type=["japanese_surnames", "japanese_unisex_names"], data_file='services/names.json'):
    try:
        # JSONデータを読み込む
        with open(data_file, 'r', encoding='utf-8') as f:
            names_data = json.load(f)
        
        result_names = []

        for key in name_type:
            if key not in names_data:
                return f"エラー: '{key}' はデータファイルに存在しません"
            result_names.append(random.choice(names_data[key]))
            
        return f"{' '.join(result_names)}"

    except FileNotFoundError:
        return "エラー: データファイルが見つかりません"
    except Exception as e:
        return f"エラーが発生しました: {e}"
    
# AIキャラクターを作成する
# 今後の拡張案(llnを通して国籍や年齢層も指定可能にする等)
def crate_ai_character(assistant_gender: str):
    assistant_name = generate_name(name_type=["japanese_surnames", f"japanese_{assistant_gender}_names"])
    return {"assistant_name": assistant_name, "assistant_gender": assistant_gender}