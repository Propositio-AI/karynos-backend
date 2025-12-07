from pydantic import BaseModel, Field, ConfigDict, field_validator
from uuid import UUID
from typing import List, Optional

class NewMentorRequest(BaseModel):
    chief_mentor_id: Optional[UUID] = Field(None, description="チーフメンターのID") 
    # UUID7どうしたらよい
    organization_id: int = Field(..., description="団体ID")
    name_family: str = Field(..., description="苗字")
    name_given: str = Field(..., description="名前")
    access_group: Optional[UUID] = Field(None, description="アクセスグループのID")
    
    @field_validator('chief_mentor_id', 'access_group', mode='before')
    @classmethod
    def empty_str_to_none(cls, v):
        if v == "" or v is None:
            return None
        return v
    
class NewMentorResponse(BaseModel):
    mentor_id: UUID = Field(..., description="Mentor ID")

    model_config = ConfigDict(from_attributes=True)
    
class MentorGroupInfo(BaseModel):
    name: str = Field(..., description="グループ名")
    group_id: UUID = Field(..., description="グループID")
    
class MentorResponse(BaseModel):
    login_id: str = Field(..., description="ログイン用ID")
    chief_mentor_id: Optional[UUID] = Field(None, description="チーフメンターのID") 
    organization_id: int = Field(..., description="団体ID")
    name_family: str = Field(..., description="苗字")
    name_given: str = Field(..., description="名前")
    access_group: Optional[UUID] = Field(None, description="アクセスグループのID")
    group: List[MentorGroupInfo] = Field(
        default_factory=list,
        description="所属しているMentorグループの一覧"          
    )

    model_config = ConfigDict(from_attributes=True)

    
class UpdateMentorRequest(BaseModel):
    chief_mentor_id: Optional[UUID] = Field(None, description="チーフメンターのID") 
    organization_id: int = Field(None, description="団体ID")
    name_family: str = Field(None, description="苗字")
    name_given: str = Field(None, description="名前")
    access_group: Optional[UUID] = Field(None, description="アクセスグループのID")
    
    @field_validator('chief_mentor_id', 'access_group', mode='before')
    @classmethod
    def empty_str_to_none(cls, v):
        if v == "" or v is None:
            return None
        return v

class MentorRoleInfo(BaseModel):
    mentor_id: UUID = Field(..., description="Mentor ID")
    role: str = Field(..., description="役割")

class NewMentorGroupRequest(BaseModel):
    chief_mentor_id: Optional[UUID] = Field(None, description="グループのチーフメンターのID") 
    name: str = Field(..., description="グループ名")
    description: str = Field(..., description="グループの説明")
    mentors: List[MentorRoleInfo] = Field(
        default_factory=list,
        description="初期グループメンバー(mentor_idとrole)"
    )
    
    @field_validator('chief_mentor_id', mode='before')
    @classmethod
    def empty_str_to_none(cls, v):
        if v == "" or v is None:
            return None
        return v
    
class NewMentorGroupResponse(BaseModel):
    group_id: UUID = Field(..., description="グループID")

    model_config = ConfigDict(from_attributes=True)
    
class MentorInGroup(BaseModel):
    name: str = Field(..., description="Mentor名")
    mentor_id: UUID = Field(..., description="Mentor ID")
    
class MentorGroupResponse(BaseModel):
    chief_mentor_id: Optional[UUID] = Field(None, description="グループのチーフメンターのID") 
    name: str = Field(..., description="グループ名")
    description: str = Field(..., description="グループの説明")
    mentors: List[MentorInGroup] = Field(
        default_factory=list,
        description="グループに所属しているMentorの一覧"
    )

    model_config = ConfigDict(from_attributes=True)

class UpdateMentorGroupRequest(BaseModel):
    chief_mentor_id: Optional[UUID] = Field(None, description="グループのチーフメンターのID") 
    name: str = Field(None, description="グループ名")
    description: str = Field(None, description="グループの説明")
    
    @field_validator('chief_mentor_id', mode='before')
    @classmethod
    def empty_str_to_none(cls, v):
        if v == "" or v is None:
            return None
        return v
    

class AddMentorToGroupRequest(BaseModel):
    mentors: List[MentorRoleInfo] = Field(..., description="追加したいmentorIDとroleのリスト")
    
class AddMentorToGroupResponse(BaseModel):
    mentors: List[MentorRoleInfo] = Field(..., description="追加されたMentorの一覧といその役割")
    
    model_config = ConfigDict(from_attributes=True)

class RemoveMentorFromGroupRequest(BaseModel):
    mentor_ids: List[UUID] = Field(..., description="削除したいmentorのIDリスト")

class RemoveMentorResponse(BaseModel):
    mentor_ids: List[UUID] = Field(..., description="削除されたmentorのIDリスト")
    
    model_config = ConfigDict(from_attributes=True)