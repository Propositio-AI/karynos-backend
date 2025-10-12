from shared.lib.gRPC import gRPC_Client
from shared.utils import readText, createPromptTemplate

import os
from pydantic import BaseModel, Field

LLM_MODEL = os.getenv("LLM_MODEL", "local")

# パス定義
CODE_PROMPT_PATH = "./methods/generate_code/prompts/code_prompt.txt"
USER_TEMPLATE_PATH = "./methods/generate_code/prompts/user_template.txt"

# プロンプトの読み込み
CODE_PROMPT = readText(CODE_PROMPT_PATH)
USER_TEMPLATE = readText(USER_TEMPLATE_PATH)

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

    for netSuccess, netResponse, netError in llm_client.call_server_stream("GeneralInvoke", {
        "input": inputs,
        "llm_model": LLM_MODEL
    }):
        if netSuccess:
            serverSuccess, serverRes, serverError = netResponse
            
            if serverSuccess:
                code += serverRes
        else: raise netError

    return code