import json

from shared.lib.gRPC.client import gRPC_Client
from shared.utils import readText, createPromptTemplate, model_to_prompt_structure
from shared.types import BaseElementGenerateSchema, BaseElementSchema

from typing import List

import os

LLM_MODEL = os.getenv("LLM_MODEL", "local")

# パス定義
ELEMENT_PROMPT_PATH = "./prompts/element_prompt.txt"
STYLE_PROMPT_PATH = "./shared/prompts/style_prompt.txt"
USER_TEMPLATE_PATH = "./shared/prompts/section_user_template.txt"

# プロンプトの読み込み
ELEMENT_PROMPT = readText(ELEMENT_PROMPT_PATH)
STYLE_PROMPT = readText(STYLE_PROMPT_PATH)
USER_TEMPLATE = readText(USER_TEMPLATE_PATH)

def generate_text(thema: str, persona: str, title: str, message: str, textbook: str) -> dict:
    # gRPCクライアント定義
    llm_client = gRPC_Client("LLM")

    inputs = createPromptTemplate(
        ELEMENT_PROMPT.format(thema = thema, schema = model_to_prompt_structure(BaseElementGenerateSchema), style = STYLE_PROMPT),
        USER_TEMPLATE.format(title = title, message = message, textbook = textbook, persona = persona)
    )

    # 生成
    netSuccess, netResponse, netError = llm_client.call("StructInvoke", {
        "input": inputs,
        "json_schema": BaseElementGenerateSchema.model_json_schema(),
        "llm_model": LLM_MODEL
    })
    if netSuccess:
        serverSuccess, serverRes, serverError = netResponse
        
        if serverSuccess:
            return serverRes
        
    else: raise netError

def generate_fig(persona: str, message: List[str]) -> dict:
    # gRPCクライアント定義
    vision_client = gRPC_Client("Vision")

    # 図表の生成
    netSuccess, netResponse, netError = vision_client.call("GenerateVision", {
        "persona": persona,
        "message": message,
    })
    if netSuccess:
        serverSuccess, serverRes, serverError = netResponse
        
        if serverSuccess:
            return serverRes["urls"]
        
    else: raise netError

def generate_element(thema:str, persona:str, title: str, message: str, textbook: str) -> dict:
    # 定義の文章生成
    generated_text = BaseElementGenerateSchema(**generate_text(
        thema = thema,
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