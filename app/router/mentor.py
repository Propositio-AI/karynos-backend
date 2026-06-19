from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, Query, UploadFile, status

from app.lib.auth import get_current_mentor_sub
from app.services.dream_action.schemas import (
    DistributeMaterialRequest,
    DistributeMaterialResponse,
    GeneratedMaterialDetail,
    GeneratedMaterialListResponse,
    GenerationJobListResponse,
    GenerationJobResponse,
    TriggerGenerationRequest,
    TriggerGenerationResponse,
)
from app.services.dream_action.service import dream_action_service
from app.services.mentor.schemas import (
    ClassAnalyticsResponse,
    ClassCreateRequest,
    ClassListResponse,
    ClassResponse,
    ClassUpdateRequest,
    EnrollmentCreateRequest,
    LessonMaterialListResponse,
    LessonMaterialResponse,
    LessonMaterialUpdateRequest,
    MentorResponse,
    StudentDetail,
    StudentListResponse,
)
from app.services.mentor.service import mentor_service

router = APIRouter()


# ── Mentor プロフィール ────────────────────────────────────────────────

@router.get("/me", response_model=MentorResponse, tags=["Mentor"])
async def get_my_profile(
    cognito_sub: str = Depends(get_current_mentor_sub),
):
    return mentor_service.get_mentor(cognito_sub)


# ── クラス管理 ─────────────────────────────────────────────────────────

@router.get("/classes", response_model=ClassListResponse, tags=["Mentor - Class"])
async def list_classes(
    cognito_sub: str = Depends(get_current_mentor_sub),
):
    mentor_id = mentor_service.resolve_mentor_id(cognito_sub)
    return mentor_service.list_classes(mentor_id)


@router.post(
    "/classes",
    response_model=ClassResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Mentor - Class"],
)
async def create_class(
    request: ClassCreateRequest,
    cognito_sub: str = Depends(get_current_mentor_sub),
):
    mentor_id = mentor_service.resolve_mentor_id(cognito_sub)
    return mentor_service.create_class(request, mentor_id)


@router.get("/classes/{class_id}", response_model=ClassResponse, tags=["Mentor - Class"])
async def get_class(
    class_id: UUID,
    cognito_sub: str = Depends(get_current_mentor_sub),
):
    mentor_id = mentor_service.resolve_mentor_id(cognito_sub)
    return mentor_service.get_class(str(class_id), mentor_id)


@router.put("/classes/{class_id}", response_model=ClassResponse, tags=["Mentor - Class"])
async def update_class(
    class_id: UUID,
    request: ClassUpdateRequest,
    cognito_sub: str = Depends(get_current_mentor_sub),
):
    mentor_id = mentor_service.resolve_mentor_id(cognito_sub)
    return mentor_service.update_class(str(class_id), request, mentor_id)


@router.delete("/classes/{class_id}", tags=["Mentor - Class"])
async def delete_class(
    class_id: UUID,
    cognito_sub: str = Depends(get_current_mentor_sub),
):
    mentor_id = mentor_service.resolve_mentor_id(cognito_sub)
    return mentor_service.delete_class(str(class_id), mentor_id)


# ── 履修生徒管理 ───────────────────────────────────────────────────────

@router.get(
    "/classes/{class_id}/students",
    response_model=StudentListResponse,
    tags=["Mentor - Student"],
)
async def list_students(
    class_id: UUID,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    cognito_sub: str = Depends(get_current_mentor_sub),
):
    mentor_id = mentor_service.resolve_mentor_id(cognito_sub)
    return mentor_service.list_students(str(class_id), mentor_id, limit, offset)


@router.get(
    "/classes/{class_id}/students/{dreamer_id}",
    response_model=StudentDetail,
    tags=["Mentor - Student"],
)
async def get_student_detail(
    class_id: UUID,
    dreamer_id: UUID,
    cognito_sub: str = Depends(get_current_mentor_sub),
):
    mentor_id = mentor_service.resolve_mentor_id(cognito_sub)
    return mentor_service.get_student_detail(str(class_id), str(dreamer_id), mentor_id)


@router.post(
    "/classes/{class_id}/students",
    status_code=status.HTTP_201_CREATED,
    tags=["Mentor - Student"],
)
async def add_students(
    class_id: UUID,
    request: EnrollmentCreateRequest,
    cognito_sub: str = Depends(get_current_mentor_sub),
):
    mentor_id = mentor_service.resolve_mentor_id(cognito_sub)
    return mentor_service.add_students(str(class_id), request, mentor_id)


@router.delete(
    "/classes/{class_id}/students/{dreamer_id}",
    tags=["Mentor - Student"],
)
async def remove_student(
    class_id: UUID,
    dreamer_id: UUID,
    cognito_sub: str = Depends(get_current_mentor_sub),
):
    mentor_id = mentor_service.resolve_mentor_id(cognito_sub)
    return mentor_service.remove_student(str(class_id), str(dreamer_id), mentor_id)


# ── 授業資料管理 ───────────────────────────────────────────────────────

@router.get(
    "/classes/{class_id}/materials",
    response_model=LessonMaterialListResponse,
    tags=["Mentor - Material"],
)
async def list_materials(
    class_id: UUID,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    cognito_sub: str = Depends(get_current_mentor_sub),
):
    mentor_id = mentor_service.resolve_mentor_id(cognito_sub)
    return mentor_service.list_materials(str(class_id), mentor_id, limit, offset)


@router.post(
    "/classes/{class_id}/materials",
    response_model=LessonMaterialResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Mentor - Material"],
)
async def upload_material(
    class_id: UUID,
    file: UploadFile = File(...),
    title: str = Form(...),
    subject: str | None = Form(None),
    unit: str | None = Form(None),
    description: str | None = Form(None),
    cognito_sub: str = Depends(get_current_mentor_sub),
):
    mentor_id = mentor_service.resolve_mentor_id(cognito_sub)
    return await mentor_service.upload_material(
        str(class_id), mentor_id, file, title, subject, unit, description
    )


@router.get(
    "/classes/{class_id}/materials/{material_id}",
    response_model=LessonMaterialResponse,
    tags=["Mentor - Material"],
)
async def get_material(
    class_id: UUID,
    material_id: UUID,
    cognito_sub: str = Depends(get_current_mentor_sub),
):
    mentor_id = mentor_service.resolve_mentor_id(cognito_sub)
    return mentor_service.get_material(str(class_id), str(material_id), mentor_id)


@router.put(
    "/classes/{class_id}/materials/{material_id}",
    response_model=LessonMaterialResponse,
    tags=["Mentor - Material"],
)
async def update_material(
    class_id: UUID,
    material_id: UUID,
    request: LessonMaterialUpdateRequest,
    cognito_sub: str = Depends(get_current_mentor_sub),
):
    mentor_id = mentor_service.resolve_mentor_id(cognito_sub)
    return mentor_service.update_material(
        str(class_id), str(material_id), request, mentor_id
    )


@router.delete(
    "/classes/{class_id}/materials/{material_id}",
    tags=["Mentor - Material"],
)
async def delete_material(
    class_id: UUID,
    material_id: UUID,
    cognito_sub: str = Depends(get_current_mentor_sub),
):
    mentor_id = mentor_service.resolve_mentor_id(cognito_sub)
    return mentor_service.delete_material(str(class_id), str(material_id), mentor_id)


# ── クラス集計 ─────────────────────────────────────────────────────────

@router.get(
    "/classes/{class_id}/analytics",
    response_model=ClassAnalyticsResponse,
    tags=["Mentor - Analytics"],
)
async def get_class_analytics(
    class_id: UUID,
    cognito_sub: str = Depends(get_current_mentor_sub),
):
    mentor_id = mentor_service.resolve_mentor_id(cognito_sub)
    return mentor_service.get_class_analytics(str(class_id), mentor_id)


# ── Dream Action (Mentor 向け) ─────────────────────────────────────────

@router.post(
    "/classes/{class_id}/dream-action/generate",
    response_model=TriggerGenerationResponse,
    status_code=status.HTTP_202_ACCEPTED,
    tags=["Mentor - Dream Action"],
)
async def trigger_generation(
    class_id: UUID,
    request: TriggerGenerationRequest,
    background_tasks: BackgroundTasks,
    cognito_sub: str = Depends(get_current_mentor_sub),
):
    mentor_id = mentor_service.resolve_mentor_id(cognito_sub)
    return dream_action_service.trigger_generation(
        str(class_id), request, mentor_id, background_tasks
    )


@router.get(
    "/classes/{class_id}/dream-action/jobs",
    response_model=GenerationJobListResponse,
    tags=["Mentor - Dream Action"],
)
async def list_generation_jobs(
    class_id: UUID,
    cognito_sub: str = Depends(get_current_mentor_sub),
):
    mentor_id = mentor_service.resolve_mentor_id(cognito_sub)
    return dream_action_service.list_generation_jobs(str(class_id), mentor_id)


@router.get(
    "/classes/{class_id}/dream-action/jobs/{generation_job_id}",
    response_model=GenerationJobResponse,
    tags=["Mentor - Dream Action"],
)
async def get_generation_job(
    class_id: UUID,
    generation_job_id: UUID,
    cognito_sub: str = Depends(get_current_mentor_sub),
):
    mentor_id = mentor_service.resolve_mentor_id(cognito_sub)
    return dream_action_service.get_generation_job(
        str(generation_job_id), str(class_id), mentor_id
    )


@router.get(
    "/classes/{class_id}/dream-action/materials",
    response_model=GeneratedMaterialListResponse,
    tags=["Mentor - Dream Action"],
)
async def list_generated_materials(
    class_id: UUID,
    lesson_material_id: UUID | None = Query(None),
    status_filter: str | None = Query(None, alias="status"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    cognito_sub: str = Depends(get_current_mentor_sub),
):
    mentor_id = mentor_service.resolve_mentor_id(cognito_sub)
    return dream_action_service.list_generated_materials(
        str(class_id),
        mentor_id,
        lesson_material_id=str(lesson_material_id) if lesson_material_id else None,
        status_filter=status_filter,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/classes/{class_id}/dream-action/materials/{generated_material_id}",
    response_model=GeneratedMaterialDetail,
    tags=["Mentor - Dream Action"],
)
async def get_generated_material(
    class_id: UUID,
    generated_material_id: UUID,
    cognito_sub: str = Depends(get_current_mentor_sub),
):
    mentor_id = mentor_service.resolve_mentor_id(cognito_sub)
    return dream_action_service.get_generated_material_detail(
        str(class_id), str(generated_material_id), mentor_id
    )


@router.post(
    "/classes/{class_id}/dream-action/distribute",
    response_model=DistributeMaterialResponse,
    tags=["Mentor - Dream Action"],
)
async def distribute_materials(
    class_id: UUID,
    request: DistributeMaterialRequest,
    cognito_sub: str = Depends(get_current_mentor_sub),
):
    mentor_id = mentor_service.resolve_mentor_id(cognito_sub)
    return dream_action_service.distribute_materials(str(class_id), request, mentor_id)


@router.post(
    "/classes/{class_id}/dream-action/materials/{generated_material_id}/regenerate",
    response_model=TriggerGenerationResponse,
    status_code=status.HTTP_202_ACCEPTED,
    tags=["Mentor - Dream Action"],
)
async def regenerate_material(
    class_id: UUID,
    generated_material_id: UUID,
    background_tasks: BackgroundTasks,
    cognito_sub: str = Depends(get_current_mentor_sub),
):
    mentor_id = mentor_service.resolve_mentor_id(cognito_sub)
    return dream_action_service.regenerate_material(
        str(class_id), str(generated_material_id), mentor_id, background_tasks
    )
