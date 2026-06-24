from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class InitQuestionOptionResponse(BaseModel):
    option_id: UUID
    option_text: str
    option_order: int

    model_config = ConfigDict(from_attributes=True)


class InitQuestionResponse(BaseModel):
    question_id: UUID
    category: str
    question_text: str
    question_order: int
    version: int
    options: list[InitQuestionOptionResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class GetInitQuestionsResponse(BaseModel):
    questions: list[InitQuestionResponse]
    version: int
    total_questions: int

    model_config = ConfigDict(from_attributes=True)


class SubmitInitAnswerRequest(BaseModel):
    question_id: UUID
    option_id: UUID
    question_version: int


class SubmitInitAnswersRequest(BaseModel):
    answers: list[SubmitInitAnswerRequest]


class InitAnswerResponse(BaseModel):
    answer_id: UUID
    dreamer_id: UUID
    question_id: UUID
    option_id: UUID
    question_version: int
    answered_at: str

    model_config = ConfigDict(from_attributes=True)


class InitAnswersSubmitResponse(BaseModel):
    total_saved: int
    answers: list[InitAnswerResponse]

    model_config = ConfigDict(from_attributes=True)


class InitAnswerHistoryItem(BaseModel):
    answer_id: UUID
    question_id: UUID
    question_text: str
    option_id: UUID
    option_text: str
    question_version: int
    answered_at: str

    model_config = ConfigDict(from_attributes=True)
