from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


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
    groups: list[DreamerGroupSummary] = Field(
        default_factory=list, description="所属グループ"
    )

    model_config = ConfigDict(from_attributes=True)


class NewDreamerGroupRequest(BaseModel):
    name: str = Field(..., description="グループ名")
    description: str | None = Field(None, description="グループ説明")
    dreamers: list[UUID] = Field(default_factory=list, description="初期所属dreamer")


class NewDreamerGroupResponse(BaseModel):
    group_id: UUID = Field(..., description="グループID")

    model_config = ConfigDict(from_attributes=True)


class DreamerInGroup(BaseModel):
    name: str = Field(..., description="dreamer名")
    dreamer_id: UUID = Field(..., description="dreamer ID")


class DreamerGroupResponse(BaseModel):
    name: str = Field(..., description="グループ名")
    description: str | None = Field(None, description="グループ説明")
    dreamers: list[DreamerInGroup] = Field(
        default_factory=list, description="所属dreamer"
    )

    model_config = ConfigDict(from_attributes=True)


class UpdateDreamerGroupRequest(BaseModel):
    name: str = Field(None, description="グループ名")
    description: str = Field(None, description="グループ説明")


class DreamerToGroupRequest(BaseModel):
    dreamers: list[UUID] = Field(..., description="更新対象dreamer ID")


class DreamerToGroupResponse(BaseModel):
    dreamers: list[UUID] = Field(..., description="更新後dreamer ID")

    model_config = ConfigDict(from_attributes=True)
