from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ── Mentor ────────────────────────────────────────────────────────────

class MentorResponse(BaseModel):
    mentor_id: UUID
    cognito_sub: str
    name_family: str
    name_given: str
    email: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MentorCreateRequest(BaseModel):
    cognito_sub: str = Field(..., description="Cognito ユーザーサブ")
    name_family: str = Field(..., description="苗字")
    name_given: str = Field(..., description="名前")
    email: str = Field(..., description="メールアドレス")


# ── Class ─────────────────────────────────────────────────────────────

class ClassCreateRequest(BaseModel):
    name: str = Field(..., description="クラス名")
    subject: str | None = Field(None, description="科目")
    description: str | None = Field(None, description="説明")
    academic_year: int | None = Field(None, description="年度（例: 2025）")


class ClassUpdateRequest(BaseModel):
    name: str | None = Field(None, description="クラス名")
    subject: str | None = Field(None, description="科目")
    description: str | None = Field(None, description="説明")
    academic_year: int | None = Field(None, description="年度")


class ClassSummary(BaseModel):
    class_id: UUID
    name: str
    subject: str | None
    description: str | None
    academic_year: int | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ClassResponse(ClassSummary):
    mentor_id: UUID
    enrolled_count: int = Field(0, description="履修生徒数")
    material_count: int = Field(0, description="授業資料数")


class ClassListResponse(BaseModel):
    items: list[ClassResponse]
    total: int


# ── Enrollment / Student ──────────────────────────────────────────────

class EnrollmentCreateRequest(BaseModel):
    dreamer_ids: list[UUID] = Field(..., description="追加する生徒 ID リスト")


class EnrollmentResponse(BaseModel):
    enrollment_id: UUID
    dreamer_id: UUID
    enrolled_at: datetime

    model_config = ConfigDict(from_attributes=True)


class JobInterestSummary(BaseModel):
    job_id: int
    job_name: str
    good: bool
    bad: bool
    save: bool


class StudentSummary(BaseModel):
    dreamer_id: UUID
    name_family: str
    name_given: str
    name: str
    enrolled_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StudentDetail(StudentSummary):
    interest_jobs: list[JobInterestSummary] = Field(
        default_factory=list, description="Dream Matching の興味傾向（liked/saved/bad）"
    )
    top_categories: list[str] = Field(
        default_factory=list, description="関心の高い職種カテゴリ"
    )
    total_viewed: int = Field(0, description="閲覧済み職業数")
    liked_count: int = Field(0, description="いいね数")


class StudentListResponse(BaseModel):
    items: list[StudentSummary]
    total: int


# ── LessonMaterial ────────────────────────────────────────────────────

class LessonMaterialResponse(BaseModel):
    material_id: UUID
    class_id: UUID
    mentor_id: UUID
    title: str
    subject: str | None
    unit: str | None
    description: str | None
    file_name: str
    file_size: int
    mime_type: str
    is_deleted: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LessonMaterialUpdateRequest(BaseModel):
    title: str | None = Field(None, description="タイトル")
    subject: str | None = Field(None, description="科目")
    unit: str | None = Field(None, description="単元")
    description: str | None = Field(None, description="説明")


class LessonMaterialListResponse(BaseModel):
    items: list[LessonMaterialResponse]
    total: int


# ── Class Analytics ───────────────────────────────────────────────────

class CategoryDistribution(BaseModel):
    category_name: str
    count: int


class ClassAnalyticsResponse(BaseModel):
    class_id: UUID
    total_students: int
    top_job_categories: list[CategoryDistribution] = Field(
        default_factory=list, description="人気職種カテゴリ分布"
    )
    generated_materials_count: int = Field(0, description="生成済み教材数")
    distributed_materials_count: int = Field(0, description="配布済み教材数")
    pending_review_count: int = Field(0, description="教員確認待ち教材数")
