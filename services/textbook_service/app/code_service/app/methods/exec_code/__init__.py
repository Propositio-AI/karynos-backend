import traceback

from utils import preprocess_code

def exec_code(code: str):
    code = preprocess_code(code)
    
    exec_globals = {}
    try:
        exec(code, exec_globals)

        result = exec_globals.get("results", None)
        if result is None:
            return False, "変数名resultsが存在していません。"
        
        return True, result 
    except Exception as e:
        return False, traceback.format_exc()