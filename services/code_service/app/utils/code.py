import re

def clean_code_block(text):
    text = text.strip()
    if text.startswith("```python"):
        text = text[len("```python"):].strip()
    elif text.startswith("```"):
        text = text[len("```"):].strip()
    if text.endswith("```"):
        text = text[:-3].strip()
    return text

def replace_and_with_reduce(code):
    pattern = r'sp\.And\(([^)]+)\)'
    replacement=r'sp.reduce_inequalities([\1)'
    return re.sub(pattern,replacement,code)

def preprocess_code(code:str):
    code = clean_code_block(code)
    code = replace_and_with_reduce(code)

    return code