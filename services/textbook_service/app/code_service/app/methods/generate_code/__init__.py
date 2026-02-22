from shared.lib.gRPC import gRPC_Client
from shared.utils import readText, createPromptTemplate

import os
from pydantic import BaseModel, Field

LLM_MODEL = os.getenv("LLM_MODEL", "local")

# パス定義
CODE_PROMPT_PATH = "./methods/generate_code/prompts/code_prompt.txt"
USER_TEMPLATE_PATH = "./methods/generate_code/prompts/user_template.txt"

def _read_text_or_raise(path: str) -> str:
    response = readText(path)
    if response["success"]:
        return response["data"]
    raise RuntimeError("\n".join(response["message"]))

# プロンプトの読み込み
CODE_PROMPT = _read_text_or_raise(CODE_PROMPT_PATH)
USER_TEMPLATE = _read_text_or_raise(USER_TEMPLATE_PATH)

class CodeSchema(BaseModel):
    code: str = Field(..., description="ソースコード")

    class Config:
        extra = "forbid" 

def generate_code(request: str, query: str, code:str = "", error: str = "") -> str:
    llm_client = gRPC_Client("LLM")
    
    inputs = createPromptTemplate(
        CODE_PROMPT,
        USER_TEMPLATE.format(request = request, query = query, code = code, error = error)
    )

    code = ""

    for net_response in llm_client.call_server_stream("GeneralInvoke", {
        "input": inputs,
        "llm_model": LLM_MODEL
    }):
        if net_response["success"]:
            server_response = net_response["data"]
            if server_response["success"]:
                code += server_response["data"]
            else:
                raise RuntimeError("\n".join(server_response["message"]))
        else:
            raise RuntimeError("\n".join(net_response["message"]))

    return code