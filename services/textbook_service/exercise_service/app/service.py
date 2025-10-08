import json

from shared.lib.gRPC.client import gRPC_Client
from shared.utils import twice_backslash, readText, createPromptTemplate, model_to_prompt_structure
from shared.types import BaseFig, AnswerSchema

from pydantic import BaseModel, Field
from typing import List, Optional

import os

LLM_MODEL = os.getenv("LLM_MODEL", "local")

# パス定義
QUESTON_PROMPT_PATH = "./prompts/question_prompt.txt"
STYLE_PROMPT_PATH = "./shared/prompts/style_prompt.txt"
USER_TEMPLATE_PATH = "./shared/prompts/section_user_template.txt"

# プロンプトの読み込み
QUESTION_PROMPT = readText(QUESTON_PROMPT_PATH)
STYLE_PROMPT = readText(STYLE_PROMPT_PATH)
USER_TEMPLATE = readText(USER_TEMPLATE_PATH)

class Question(BaseModel):
    purpose: str = Field(..., description="問題を出題した意図/この問題の目的。スタイル要件に従って生成してください")
    question: str = Field(..., description="問題文。スタイル要件に従って生成してください")
    fig: BaseFig

    class Config:
        description = "問題"
        extra = "forbid" 

class QuestionsSchema(BaseModel):
    questions: List[Question]

    class Config:
        description = "問題一覧"
        extra = "forbid" 

class QuestionParts(BaseModel):
    question: str
    purpose: str
    fig_urls: List[str]

class AnswerParts(BaseModel):
    answer: str
    explanation: str
    fig_urls: List[str]

class ExerciseParts(BaseModel):
    question: QuestionParts
    answer: AnswerParts


# 問題生成
def generate_question(persona: str, title: str, message: str, textbook: str) -> List[Question]:
    # gRPCクライアントの定義
    llm_client = gRPC_Client("LLM")

    inputs = createPromptTemplate(
        QUESTION_PROMPT.format(schema = model_to_prompt_structure(QuestionsSchema), style = STYLE_PROMPT),
        USER_TEMPLATE.format(title = title, message = message, textbook = textbook, persona = persona)
    )

    # 問題の生成
    netSuccess, netResponse, netError = llm_client.call("StructInvoke", {
        "input": inputs,
        "json_schema": QuestionsSchema.model_json_schema(),
        "llm_model": LLM_MODEL
    })
    if netSuccess:
        serverSuccess, serverRes, serverError = netResponse
        
        if serverSuccess:
            return QuestionsSchema(**serverRes).questions
        
    else: raise netError

def generate_answer(persona: str, question: str) -> AnswerSchema: 
    # gRPCクライアントの定義
    solve_client = gRPC_Client("Solve")

    # 回答の生成
    netSuccess, netResponse, netError = solve_client.call("solveMath", {
        "question": question
    })
    if netSuccess:
        serverSuccess, serverRes, serverError = netResponse

        if serverSuccess:
            return AnswerSchema(**serverRes)
    else: raise netError


def generate_fig(persona:str, message:str) -> dict:
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


def generate_exercise(persona: str, title: str, message: str, textbook: str) -> dict:
    # 問題の作成
    questions = generate_question(persona, title, message, textbook)

    exercises = []
    for question in questions:
        # 問題図表の生成
        question_fig_urls = []
        if question.fig.is_need:
            question_fig_urls = generate_fig(persona, question.fig.message)

        # 回答の生成
        answer: AnswerSchema = generate_answer(persona, question.question)

        # 解答図表の生成
        answer_fig_urls = []
        if answer.fig.is_need:
            answer_fig_urls = generate_fig(persona, answer.fig.message)
        
        exercises.append(
            ExerciseParts(
                question = QuestionParts(
                    question = question.question,
                    purpose = question.purpose,
                    fig_urls = question_fig_urls
                ),
                answer = AnswerParts(
                    answer = answer.answer,
                    explanation = answer.explanation,
                    fig_urls = answer_fig_urls,
                )
            ).model_dump()
        )

    return exercises