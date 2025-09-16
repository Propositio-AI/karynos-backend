import json

def read_file(filepath: str):
    #TODO : エラー処理
    
    with open(filepath, "r", encoding="utf-8") as f:
        contents = f.read()

    return contents

def readJson(file_path: str):
    with open(file_path, "r") as f:
        dict_data = json.load(f)
    
    return dict_data