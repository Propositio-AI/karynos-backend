
from pydantic import BaseModel
from typing import List, Literal, Optional

PageElement = Literal[
    "Section",
    "Definition",
    "Theorem",
    "Formula",
    "Exercise",
    "Column",
    "Text",
    "Summary"
]

class Element(BaseModel):
    element: PageElement
    title: str
    reason: str
    message: str

    class Config:
        description = "構成要素"
        extra = "forbid" 

class Page(BaseModel):
    page: List[Element]

    class Config:
        description = "教科書ページ"
        extra = "forbid" 

class ElementParts(BaseModel):
    type: str
    title: Optional[str] = None
    text: Optional[str] = None
    fig_urls: Optional[List[str]] = None

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

class ExerciseRootParts(BaseModel):
    type: str = "Exercise"
    exercises: List[ExerciseParts]