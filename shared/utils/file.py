def read_file(filepath: str):
    #TODO : エラー処理
    
    with open(filepath, "r", encoding="utf-8") as f:
        contents = f.read()

    return contents