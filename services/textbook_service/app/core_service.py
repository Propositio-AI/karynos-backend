import os

from typing import List

from shared.lib.gRPC import gRPC_Client
from shared.utils import createPromptTemplate, readText, model_to_prompt_structure

from schema import (
    Element,
    Page,
    ElementParts,
    ExerciseRootParts
)

from element.service import generate_text
from exercise.service import generate_exercise

LLM_MODEL = os.getenv("LLM_MODEL", "local")

# パス定義
PAGE_PROMPT_PATH = "./prompts/page.txt"
PLAN_PROMPT_PATH = "./prompts/plan_prompt.txt"

# プロンプト読み込み
PAGE_PROMPT = readText(PAGE_PROMPT_PATH)
PLAN_PROMPT = readText(PLAN_PROMPT_PATH)

def generate_textbook(persona: str, structures: List[Element], elements: list = []):
    # 各要素を作成
    for element in structures[len(elements):]:
        parts = generate_element(persona, element, elements)

        elements.append(parts.model_dump())
        
        yield elements

def generate_structure(persona: str, query: str) -> List[Element]:    
    # ページの構成を推論
    netSuccess, netResponse, netError = gRPC_Client("LLM").call("StructInvoke", {
        "input": createPromptTemplate(
            PAGE_PROMPT.format(schema = model_to_prompt_structure(Page)),
            f"# テーマ: 「{query}」\n\n # 生徒情報\n {persona}"
        ),
        "json_schema": Page.model_json_schema(),
        "llm_model": "openai"
    })
    if netSuccess:
        serverSuccess, serverRes, serverError = netResponse
        
        if serverSuccess:
            page = Page(**serverRes)
        
    else: raise netError


    structures = page.page

    return [structure.model_dump() for structure in structures]


def generate_element(persona: str, element: Element, textbook: List):
    parts = None

    if element.element in ["Definition", "Theorem", "Formula", "Column", "Text", "Summary"]:
        match element.element:
            case "Definition":
                theme = "定義"
            case "Theorem":
                theme = "定理"
            case "Formula":
                theme = "公式"
            case "Column":
                theme = "コラム"
            case "Text":
                theme = "構成要素と構成要素のつなぎ"
            case "Summary":
                theme = "まとめ"
        netSuccess, netResponse, netError = generate_text(
            theme = theme,
            persona = persona,
            title = element.title,
            message = element.message,
            textbook = textbook
        )
        if netSuccess:
            serverSuccess, serverRes, serverError = netResponse
            
            if serverSuccess:
                parts = ElementParts(
                    type = element.element,
                    **serverRes
                )
            
        else: raise netError

    elif element.element == "Section":
        parts = ElementParts(
            type = "Section",
            title = element.title
        )

    elif element.element == "Exercise":

        netSuccess, netResponse, netError = generate_exercise(
            persona = persona,
            title = element.title,
            message = element.message,
            textbook = textbook
        )
        if netSuccess:
            serverSuccess, serverRes, serverError = netResponse

            if serverSuccess:
                parts = ExerciseRootParts(exercises=serverRes)
            
        else: raise netError


    print(parts, flush=True)
    
    return parts

def generate_plan(persona: str, query: str):
    llm_client = gRPC_Client("LLM")

    inputs = createPromptTemplate(
        PLAN_PROMPT,
        f"# クエリー：「{query}」\n\n # 生徒情報\n{persona}"
    )


    for netSuccess, netRes, netError in llm_client.call_server_stream("GeneralInvoke", {
        "input": inputs,
        "llm_model": LLM_MODEL
    }):
        if netSuccess:
            serverSuccess, serverResponse, serverError = netRes
            
            if serverSuccess:
                yield serverResponse
        
        else: raise netError
