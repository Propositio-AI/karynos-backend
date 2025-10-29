from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from typing import List, Optional

class NewMentorRequest(BaseModel):
    chief_mentor_id: Optional[UUID] = Field(None, description="チーフメンターのID") 
    # UUID7どうしたらよい
    organization_id: int = Field(..., description="団体ID")
    name_family: str = Field(..., description="苗字")
    name_given: str = Field(..., description="名前")
    access_group: Optional[UUID] = Field(None, description="アクセスグループのID")
    
class NewMentorResponse(BaseModel):
    mentor_id: UUID = Field(..., description="Mentor ID")

    model_config = ConfigDict(from_attributes=True)
    
class MentorGroupInfo(BaseModel):
    name: str = Field(..., description="グループ名")
    group_id: UUID = Field(..., description="グループID")
    
class MentorResponse(BaseModel):
    login_id: str = Field(..., description="ログイン用ID")
    chief_mentor_id: UUID = Field(None, description="チーフメンターのID") 
    organization_id: int = Field(..., description="団体ID")
    name_family: str = Field(..., description="苗字")
    name_given: str = Field(..., description="名前")
    access_group: UUID = Field(..., description="アクセスグループのID")
    group: List[MentorGroupInfo] = Field(
        default_factory=list,
        description="所属しているMentorグループの一覧"          
    )

    model_config = ConfigDict(from_attributes=True)

    
class UpdateMentorRequest(BaseModel):
    chief_mentor_id: UUID = Field(None, description="チーフメンターのID") 
    organization_id: int = Field(None, description="団体ID")
    name_family: str = Field(None, description="苗字")
    name_given: str = Field(None, description="名前")
    access_group: UUID = Field(None, description="アクセスグループのID")

class MentorRoleInfo(BaseModel):
    mentor_id: UUID = Field(..., description="Mentor ID")
    role: str = Field(..., description="役割")

class NewMentorGroupRequest(BaseModel):
    chief_mentor_id: UUID = Field(None, description="グループのチーフメンターのID") 
    name: str = Field(..., description="グループ名")
    description: str = Field(..., description="グループの説明")
    mentors: List[MentorRoleInfo] = Field(
        default_factory=list,
        description="初期グループメンバー(mentor_idとrole)"
    )
    
class NewMentorGroupResponse(BaseModel):
    group_id: UUID = Field(..., description="グループID")

    model_config = ConfigDict(from_attributes=True)
    
class MentorInGroup(BaseModel):
    name: str = Field(..., description="Mentor名")
    mentor_id: UUID = Field(..., description="Mentor ID")
    
class MentorGroupResponse(BaseModel):
    chief_mentor_id: UUID = Field(None, description="グループのチーフメンターのID") 
    name: str = Field(..., description="グループ名")
    description: str = Field(..., description="グループの説明")
    mentors: List[MentorInGroup] = Field(
        default_factory=list,
        description="グループに所属しているMentorの一覧"
    )

    model_config = ConfigDict(from_attributes=True)

class UpdateMentorGroupRequest(BaseModel):
    chief_mentor_id: UUID = Field(None, description="グループのチーフメンターのID") 
    name: str = Field(None, description="グループ名")
    description: str = Field(None, description="グループの説明")
    

class MentorToGroupRequest(BaseModel):
    mentors: List[MentorRoleInfo] = Field(..., description="更新したいmentorIDとroleのリスト")
    
class MentorToGroupResponse(BaseModel):
    mentors: List[MentorRoleInfo] = Field(...,description="グループに所属しているMentorの一覧とその役割")
    
    model_config = ConfigDict(from_attributes=True)