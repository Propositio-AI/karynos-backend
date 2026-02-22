import os
import json

from shared.lib.gRPC import gRPC_Client

from shared.utils import readText, createPromptTemplate, model_to_prompt_structure
from schema import OutlineSchema, PointSchema
from TexCompiler import Compiler

compiler = Compiler()

LLM_MODEL = os.getenv("LLM_MODEL", "local")

# パス定義
OUTLINE_PROMPT_PATH = "./prompts/outline_prompt.txt"
POINT_PROMPT_PATH = "./prompts/point_prompt.txt"

def _read_text_or_raise(path: str) -> str:
    response = readText(path)
    if response["success"]:
        return response["data"]
    raise RuntimeError("\n".join(response["message"]))

# プロンプトの読み込み
OUTLINE_PROMPT = _read_text_or_raise(OUTLINE_PROMPT_PATH)
POINT_PROMPT = _read_text_or_raise(POINT_PROMPT_PATH)

# 図表概要の生成
def generate_outlint(persona: str, message: str) -> OutlineSchema:
    # gRPCクライアントの定義
    llm_client = gRPC_Client("LLM")

    inputs = createPromptTemplate(
        OUTLINE_PROMPT.format(schema = model_to_prompt_structure(OutlineSchema)),
        f"## メッセージ: {message} \n\n ## 生徒情報\n{persona}"
    )

    # 問題の生成
    net_response = llm_client.call("StructInvoke", {
        "input": inputs,
        "json_schema": OutlineSchema.model_json_schema(),
        "llm_model": LLM_MODEL
    })
    if net_response["success"]:
        server_response = net_response["data"]
        if server_response["success"]:
            return OutlineSchema(**server_response["data"])
        raise RuntimeError("\n".join(server_response["message"]))
    raise RuntimeError("\n".join(net_response["message"]))
    

# 図表設計の生成
def generate_point(outline: OutlineSchema) -> PointSchema:
    # gRPCクライアントの定義
    llm_client = gRPC_Client("LLM")

    inputs = createPromptTemplate(
        POINT_PROMPT.format(schema = model_to_prompt_structure(PointSchema)),
        json.dumps(outline.model_dump())
    )

    # 問題の生成
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
    

def generate_vision(persona: str, message: str) -> dict:
    # 図表概要の生成
    outline: OutlineSchema = generate_outlint(persona, message)

    # 図表設計書を生成
    point: PointSchema = generate_point(outline)
    
    tex_filename = compiler.convert(point)
    pdf_filename = compiler.tex_to_pdf(tex_filename)
    images = compiler.pdf_to_image(pdf_filename)

    # TODO 自動切り取り
    print(images)

    #TODO: S3に上げる処理

    return []
    # return images
