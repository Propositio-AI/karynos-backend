from shared.lib.gRPC import gRPC_Client
from shared.utils import readText, createPromptTemplate, model_to_prompt_structure
from shared.types import AnswerSchema

from pydantic import BaseModel, Field
from typing import List

import json
import os

LLM_MODEL = os.getenv("LLM_MODEL", "local")

# パス定義
POINT_PROMPT_PATH = "./prompts/point_prompt.txt"
CODE_PROMPT_PATH = "./prompts/code_prompt.txt"
EXPLANATION_PROMPT_PATH = "./prompts/explaination_prompt.txt"
STYLE_PROMPT_PATH = "./shared/prompts/style_prompt.txt"

def _read_text_or_raise(path: str) -> str:
    response = readText(path)
    if response["success"]:
        return response["data"]
    raise RuntimeError("\n".join(response["message"]))

# プロンプトの読み込み
POINT_PROMPT = _read_text_or_raise(POINT_PROMPT_PATH)
CODE_PROMPT = _read_text_or_raise(CODE_PROMPT_PATH)
EXPLANATION_PROMPT = _read_text_or_raise(EXPLANATION_PROMPT_PATH)
STYLE_PROMPT = _read_text_or_raise(STYLE_PROMPT_PATH)

class PointSchema(BaseModel):
    variables: List[str] = Field(..., description="変数とその説明")
    conditions: List[str] = Field(..., description="条件")
    assumptions: List[str] = Field(..., description="仮定")
    goal: List[str] = Field(..., description="問題が解くように求めていること")
    steps: List[str] = Field(..., description="推論手順")

    class Config:
        extra = "forbid" 

def create_point(question: str) -> PointSchema:
    # クライアントの定義
    llm_client = gRPC_Client("LLM")

    inputs = createPromptTemplate(
        POINT_PROMPT.format(schema = model_to_prompt_structure(PointSchema)),
        question
    )

    # 生成
    net_response = llm_client.call("StructInvoke", {
        "input": inputs,
        "json_schema": PointSchema.model_json_schema(),
        "llm_model": LLM_MODEL
    })
    if net_response["success"]:
        server_response = net_response["data"]
        if server_response["success"]:
            return PointSchema(**server_response["data"])
        raise RuntimeError("\n".join(server_response["message"]))
    raise RuntimeError("\n".join(net_response["message"]))


def generate_code(question: str, point: PointSchema) -> str:
    # gRPCクラインアントの定義
    code_client = gRPC_Client("Code")

    net_response = code_client.call("GenExecCode", {
        "request": CODE_PROMPT,
        "query": f"Question:{question}\n\nPoint:\n{json.dumps(point.model_dump())}",
    })
    if net_response["success"]:
        server_response = net_response["data"]
        if server_response["success"]:
            return server_response["data"]
        raise RuntimeError("\n".join(server_response["message"]))
    raise RuntimeError("\n".join(net_response["message"]))

def generate_explanation(question: str, code_result: str, point: PointSchema):
    # クライアントの定義
    llm_client = gRPC_Client("LLM")

    inputs = createPromptTemplate(
        EXPLANATION_PROMPT.format(schema = model_to_prompt_structure(AnswerSchema), style=STYLE_PROMPT),
        f"Question:{question}\n\nPoint:\n{json.dumps(point.model_dump())}\n\nPythonAnswer\n{code_result}"
    )

    # 生成
    net_response = llm_client.call("StructInvoke", {
        "input": inputs,
        "json_schema": AnswerSchema.model_json_schema(),
        "llm_model": LLM_MODEL
    })
    if net_response["success"]:
        server_response = net_response["data"]
        if server_response["success"]:
            return AnswerSchema(**server_response["data"])
        raise RuntimeError("\n".join(server_response["message"]))
    raise RuntimeError("\n".join(net_response["message"]))
    
def solve_question(question:str):
    # 問題構造化
    point: PointSchema = create_point(question)
    
    # コード生成
    code_result = generate_code(question, point)

    # 解説生成
    answer: AnswerSchema = generate_explanation(question, code_result, point)

    return answer.model_dump()