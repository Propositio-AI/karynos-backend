from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.lib.auth import get_current_user_id
from app.services.dream_action.schemas import (
    GeneratedMaterialDetail,
    GeneratedMaterialListResponse,
)
from app.services.dream_action.service import dream_action_service

router = APIRouter()


@router.get(
    "/materials",
    response_model=GeneratedMaterialListResponse,
    tags=["Dream Action - Dreamer"],
)
async def list_my_materials(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    dreamer_id: UUID = Depends(get_current_user_id),
):
    return dream_action_service.list_materials_for_dreamer(
        str(dreamer_id), limit=limit, offset=offset
    )


@router.get(
    "/materials/{generated_material_id}",
    response_model=GeneratedMaterialDetail,
    tags=["Dream Action - Dreamer"],
)
async def get_my_material(
    generated_material_id: UUID,
    dreamer_id: UUID = Depends(get_current_user_id),
):
    return dream_action_service.get_material_for_dreamer(
        str(dreamer_id), str(generated_material_id)
    )


@router.patch(
    "/materials/{generated_material_id}/read",
    tags=["Dream Action - Dreamer"],
)
async def mark_material_as_read(
    generated_material_id: UUID,
    dreamer_id: UUID = Depends(get_current_user_id),
):
    return dream_action_service.mark_as_read(str(dreamer_id), str(generated_material_id))
