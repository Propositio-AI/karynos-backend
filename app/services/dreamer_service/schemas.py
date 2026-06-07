from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from uuid import UUID


class NewDreamerRequest(BaseModel):
    organization_id: int = Field(..., description="団体ID")
    name_family: str = Field(..., description="苗字")
    name_given: str = Field(..., description="名前")


class NewDreamerResponse(BaseModel):
    dreamer_id: UUID = Field(..., description="dreamer ID")

    model_config = ConfigDict(from_attributes=True)


class UpdateDreamerRequest(BaseModel):
    organization_id: int = Field(None, description="団体ID")
    name_family: str = Field(None, description="苗字")
    name_given: str = Field(None, description="名前")


class DreamerGroupSummary(BaseModel):
    name: str = Field(..., description="グループ名")
    group_id: UUID = Field(..., description="グループID")


class DreamerResponse(BaseModel):
    login_id: str = Field(..., description="ログイン用ID")
    organization_id: int = Field(..., description="団体ID")
    name_family: str = Field(..., description="苗字")
    name_given: str = Field(..., description="名前")
    groups: List[DreamerGroupSummary] = Field(default_factory=list, description="所属グループ")

    model_config = ConfigDict(from_attributes=True)


class NewDreamerGroupRequest(BaseModel):
    name: str = Field(..., description="グループ名")
    description: Optional[str] = Field(None, description="グループ説明")
    dreamers: List[UUID] = Field(default_factory=list, description="初期所属dreamer")


class NewDreamerGroupResponse(BaseModel):
    group_id: UUID = Field(..., description="グループID")

    model_config = ConfigDict(from_attributes=True)


class DreamerInGroup(BaseModel):
    name: str = Field(..., description="dreamer名")
    dreamer_id: UUID = Field(..., description="dreamer ID")


class DreamerGroupResponse(BaseModel):
    name: str = Field(..., description="グループ名")
    description: Optional[str] = Field(None, description="グループ説明")
    dreamers: List[DreamerInGroup] = Field(default_factory=list, description="所属dreamer")

    model_config = ConfigDict(from_attributes=True)


class UpdateDreamerGroupRequest(BaseModel):
    name: str = Field(None, description="グループ名")
    description: str = Field(None, description="グループ説明")


class DreamerToGroupRequest(BaseModel):
    dreamers: List[UUID] = Field(..., description="更新対象dreamer ID")


class DreamerToGroupResponse(BaseModel):
    dreamers: List[UUID] = Field(..., description="更新後dreamer ID")

    model_config = ConfigDict(from_attributes=True)


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
    options: List[InitQuestionOptionResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class GetInitQuestionsResponse(BaseModel):
    questions: List[InitQuestionResponse]
    version: int
    total_questions: int

    model_config = ConfigDict(from_attributes=True)


class SubmitInitAnswerRequest(BaseModel):
    question_id: UUID
    option_id: UUID
    question_version: int


class SubmitInitAnswersRequest(BaseModel):
    answers: List[SubmitInitAnswerRequest]


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
    answers: List[InitAnswerResponse]

    model_config = ConfigDict(from_attributes=True)


class UserInitialAnswerHistoryResponse(BaseModel):
    answer_id: UUID
    question_id: UUID
    question_text: str
    option_id: UUID
    option_text: str
    question_version: int
    answered_at: str

    model_config = ConfigDict(from_attributes=True)
