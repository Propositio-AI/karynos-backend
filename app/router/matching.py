from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.lib.auth import get_current_user_id
from app.services.matching.schemas import MatchingDebugResponse, MatchingResponse
from app.services.matching.service import matching_service

router = APIRouter()


@router.get("/recommend", response_model=MatchingResponse)
def recommend(dreamer_id: UUID = Depends(get_current_user_id)):
    try:
        return matching_service.recommend(dreamer_id)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/recommend/debug", response_model=MatchingDebugResponse)
def recommend_debug(dreamer_id: UUID = Depends(get_current_user_id)):
    try:
        return matching_service.recommend_debug(dreamer_id)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
