from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from typing import List, Optional

# Dreamer Schemas
class NewDreamerRequest(BaseModel):
    organization_id: int = Field(..., description = "団体ID")
    name_family: str = Field(..., description = "苗字")
    name_given: str = Field(..., description = "名前")

class NewDreamerResponse(BaseModel):
    dreamer_id: UUID = Field(..., description = "dreamer ID")
    
    model_config = ConfigDict(from_attributes=True)

class UpdateDreamerRequest(BaseModel):
    organization_id: int = Field(None, description = "団体ID")
    name_family: str = Field(None, description = "苗字")
    name_given: str = Field(None, description = "名前")

class DreamerGroupSummary(BaseModel): #サブモデル
    name: str = Field(..., description = "グループ名")
    group_id: UUID = Field(..., description = "グループID")

class DreamerResponse(BaseModel):
    login_id: str = Field(..., description = "ログイン用ID")
    organization_id: int = Field(..., description = "団体ID")
    name_family: str = Field(..., description = "苗字")
    name_given: str = Field(..., description = "名前")
    groups: List[DreamerGroupSummary] = Field(
        default_factory = list,
        description = "所属しているdreamerのグループ概要リスト"
    )

    model_config = ConfigDict(from_attributes=True)

    
#Dreamer Group Schemas
class NewDreamerGroupRequest(BaseModel):
    name: str = Field(..., description = "グループ名")
    description: Optional[str] = Field(None, description = "グループの説明")
    dreamers: List[UUID] = Field(
        default_factory = list,
        description = "初期所属のdreamerのIDリスト")

class NewDreamerGroupResponse(BaseModel):
    group_id: UUID =Field(..., description = "グループID")

    model_config = ConfigDict(from_attributes=True)


class DreamerInGroup(BaseModel): #サブモデル
    name: str = Field(..., description = "dreamer名")
    dreamer_id: UUID = Field(..., description = "dreamer ID")

class DreamerGroupResponse(BaseModel):
    name: str = Field(..., description = "グループ名")
    description: Optional[str] = Field(None, description = "グループの説明")
    dreamers: List[DreamerInGroup] = Field(
        default_factory = list,
        description = "所属しているdreamerの一覧"
        )

    model_config = ConfigDict(from_attributes=True)

class UpdateDreamerGroupRequest(BaseModel):
    name: str = Field(None, description = "グループ名")
    description: str = Field(None, description = "グループの説明")

#Dreamer to Group
class DreamerToGroupRequest(BaseModel):
    dreamers: List[UUID] = Field(..., description = "更新したいdreamer IDのリスト")
    
class DreamerToGroupResponse(BaseModel):
    dreamers: List[UUID] = Field(..., description = "更新後のdreamer IDのリスト")

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# 初期診断質問関連 Schemas
# ============================================================================

class InitQuestionOptionResponse(BaseModel):
    """質問の選択肢"""
    option_id: UUID = Field(..., description="選択肢ID")
    option_text: str = Field(..., description="選択肢の文言")
    option_order: int = Field(..., description="表示順")
    
    model_config = ConfigDict(from_attributes=True)


class InitQuestionResponse(BaseModel):
    """質問情報（選択肢を含む）"""
    question_id: UUID = Field(..., description="質問ID")
    category: str = Field(..., description="カテゴリ")
    question_text: str = Field(..., description="質問文")
    question_order: int = Field(..., description="表示順")
    version: int = Field(..., description="質問バージョン")
    options: List[InitQuestionOptionResponse] = Field(
        default_factory=list,
        description="選択肢リスト"
    )
    
    model_config = ConfigDict(from_attributes=True)


class GetInitQuestionsResponse(BaseModel):
    """全質問の取得レスポンス"""
    questions: List[InitQuestionResponse] = Field(..., description="質問リスト")
    version: int = Field(..., description="質問セットのバージョン")
    total_questions: int = Field(..., description="質問数")
    
    model_config = ConfigDict(from_attributes=True)


class SubmitInitAnswerRequest(BaseModel):
    """ユーザーの初期診断回答を保存するリクエスト"""
    question_id: UUID = Field(..., description="質問ID")
    option_id: UUID = Field(..., description="選択した選択肢ID")
    question_version: int = Field(..., description="質問バージョン")


class SubmitInitAnswersRequest(BaseModel):
    """複数の回答をまとめて送信"""
    answers: List[SubmitInitAnswerRequest] = Field(..., description="回答リスト")


class InitAnswerResponse(BaseModel):
    """回答の保存確認レスポンス"""
    answer_id: UUID = Field(..., description="回答ID")
    dreamer_id: UUID = Field(..., description="dreamer ID")
    question_id: UUID = Field(..., description="質問ID")
    option_id: UUID = Field(..., description="選択肢ID")
    question_version: int = Field(..., description="質問バージョン")
    answered_at: str = Field(..., description="回答日時")
    
    model_config = ConfigDict(from_attributes=True)


class InitAnswersSubmitResponse(BaseModel):
    """複数回答の保存確認レスポンス"""
    total_saved: int = Field(..., description="保存された回答数")
    answers: List[InitAnswerResponse] = Field(..., description="保存された回答詳細")
    
    model_config = ConfigDict(from_attributes=True)


class UserInitialAnswerHistoryResponse(BaseModel):
    """ユーザーの回答履歴"""
    answer_id: UUID = Field(..., description="回答ID")
    question_id: UUID = Field(..., description="質問ID")
    question_text: str = Field(..., description="質問文")
    option_id: UUID = Field(..., description="選択肢ID")
    option_text: str = Field(..., description="選択した選択肢のテキスト")
    question_version: int = Field(..., description="質問バージョン")
    answered_at: str = Field(..., description="回答日時")
    
    model_config = ConfigDict(from_attributes=True)