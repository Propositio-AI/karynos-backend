from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class GenerationJobResponse(BaseModel):
    generation_job_id: UUID
    lesson_material_id: UUID
    class_id: UUID
    status: str
    progress: int
    total_dreamers: int
    completed_dreamers: int
    error_message: str | None
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GenerationJobListResponse(BaseModel):
    items: list[GenerationJobResponse]
    total: int


class GeneratedMaterialSummary(BaseModel):
    generated_material_id: UUID
    lesson_material_id: UUID
    dreamer_id: UUID
    job_id: int | None
    job_name: str
    title: str | None
    status: str
    is_read: bool
    distributed_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GeneratedMaterialDetail(GeneratedMaterialSummary):
    content: str | None = Field(None, description="生成された補助教材本文")


class GeneratedMaterialListResponse(BaseModel):
    items: list[GeneratedMaterialSummary]
    total: int


class TriggerGenerationRequest(BaseModel):
    lesson_material_id: UUID = Field(..., description="対象授業資料 ID")
    target_dreamer_ids: list[UUID] | None = Field(
        None, description="対象生徒 ID リスト（省略時はクラス全員）"
    )
    force_regenerate: bool = Field(
        False, description="既存教材を無視して再生成するか"
    )


class TriggerGenerationResponse(BaseModel):
    generation_job_id: UUID
    status: str
    message: str


class DistributeMaterialRequest(BaseModel):
    generated_material_ids: list[UUID] = Field(..., description="配布する教材 ID リスト")


class DistributeMaterialResponse(BaseModel):
    distributed_count: int
    message: str


class ModerationResult(BaseModel):
    is_safe: bool
    reason: str = ""
