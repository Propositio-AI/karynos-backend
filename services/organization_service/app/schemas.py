from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from enum import Enum


class OrganizationType(str, Enum):
    SCHOOL_ELEMENTARY = "SCHOOL_ELEMENTARY"
    SCHOOL_JUNIOR = "SCHOOL_JUNIOR"
    SCHOOL_HIGH = "SCHOOL_HIGH"
    COMPANY = "COMPANY"
    OTHER = "OTHER"

class NewOrganizationRequest(BaseModel):
    organization_name: str = Field(..., description="組織名")
    display_name: str = Field(..., description="表示用名称")
    organization_type: OrganizationType = Field(..., description="団体種別")


class NewOrganizationResponse(BaseModel):
    organization_id: int = Field(..., description="組織ID")
    organization_name: str = Field(..., description="組織名")
    display_name: str = Field(..., description="表示用略称")
    organization_type: OrganizationType = Field(..., description="団体種別")
    created_at: datetime = Field(..., description="組織作成日時")

    model_config = ConfigDict(from_attributes=True)

class OrganizationNameResponse(BaseModel):
    organization_name: str = Field(..., description="組織名")

    model_config = ConfigDict(from_attributes=True)

class OrganizationListItem(BaseModel):
    organization_name: str = Field(..., description="組織名")
    organization_id: int = Field(..., description="組織ID")
    display_name: str = Field(..., description="表示用略称")

    model_config = ConfigDict(from_attributes=True)

class OrganizationListResponse(BaseModel):
    organizations: List[OrganizationListItem] = Field(..., description="登録済みの組織一覧")

class OrganizationResponse(BaseModel):
    organization_id: int = Field(..., description="組織ID")
    organization_name: str = Field(..., description="組織名")
    display_name: str = Field(..., description="表示用名称")
    organization_type: OrganizationType = Field(..., description="団体種別")
    created_at: datetime = Field(..., description="作成日時")
    updated_at: datetime = Field(..., description="更新日時")

    model_config = ConfigDict(from_attributes=True)

class UpdateOrganizationRequest(BaseModel):
    organization_name: str = Field(..., description="組織名")
    display_name: str = Field(..., description="表示用名称")
    organization_type: OrganizationType = Field(..., description="団体種別")

class UpdateOrganizationResponse(BaseModel):
    organization_id: int = Field(..., description="組織ID")
    organization_name: str = Field(..., description="組織名")
    display_name: str = Field(..., description="表示用名称")
    organization_type: OrganizationType = Field(..., description="団体種別")

    model_config = ConfigDict(from_attributes=True)
