import json

from shared.lib.gRPC import gRPC_Client
from shared.utils import readText, createPromptTemplate, model_to_prompt_structure
from shared.types import BaseElementGenerateSchema, BaseElementSchema
from shared.lib.basicError import errorWrapper

from typing import List

import os

LLM_MODEL = os.getenv("LLM_MODEL", "local")

# パス定義
ELEMENT_PROMPT_PATH = "./element/prompts/element_prompt.txt"#elementなしかも
STYLE_PROMPT_PATH = "./shared/prompts/style_prompt.txt"
USER_TEMPLATE_PATH = "./shared/prompts/section_user_template.txt"

def _read_text_or_raise(path: str) -> str:
    response = readText(path)
    if response["success"]:
        return response["data"]
    raise RuntimeError("\n".join(response["message"]))

# プロンプトの読み込み
ELEMENT_PROMPT = _read_text_or_raise(ELEMENT_PROMPT_PATH)
STYLE_PROMPT = _read_text_or_raise(STYLE_PROMPT_PATH)
USER_TEMPLATE = _read_text_or_raise(USER_TEMPLATE_PATH)

@errorWrapper("Unclassified system exception")
def generate_text(theme: str, persona: str, title: str, message: str, textbook: str) -> dict:
    # gRPCクライアント定義
    llm_client = gRPC_Client("LLM")

    inputs = createPromptTemplate(
        ELEMENT_PROMPT.format(theme = theme, schema = model_to_prompt_structure(BaseElementGenerateSchema), style = STYLE_PROMPT),
        USER_TEMPLATE.format(title = title, message = message, textbook = textbook, persona = persona)
    )

    # 生成
    net_response = llm_client.call("StructInvoke", {
        "input": inputs,
        "json_schema": BaseElementGenerateSchema.model_json_schema(),
        "llm_model": LLM_MODEL
    })
    if net_response["success"]:
        server_response = net_response["data"]
        if server_response["success"]:
            return server_response["data"]
        raise RuntimeError("\n".join(server_response["message"]))
    raise RuntimeError("\n".join(net_response["message"]))

def generate_fig(persona: str, message: List[str]) -> dict:
    # gRPCクライアント定義
    vision_client = gRPC_Client("Vision")

    # 図表の生成
    net_response = vision_client.call("GenerateVision", {
        "persona": persona,
        "message": message,
    })
    if net_response["success"]:
        server_response = net_response["data"]
        if server_response["success"]:
            return server_response["data"]["urls"]
        raise RuntimeError("\n".join(server_response["message"]))
    raise RuntimeError("\n".join(net_response["message"]))

def generate_element(theme:str, persona:str, title: str, message: str, textbook: str) -> dict:
    # 定義の文章生成
    generated_text = BaseElementGenerateSchema(**generate_text(
        theme = theme,
        persona = persona,
        title = title,
        message = message,
        textbook = textbook
    ))

    # 図表の生成
    urls = []
    if(generated_text.fig.is_need): 
        urls = generate_fig(
            persona = persona,
            message = generated_text.fig.message
        )

    element = BaseElementSchema(
        title = generated_text.title,
        text = generated_text.text, 
        fig_urls = urls
    )

    return element.model_dump()