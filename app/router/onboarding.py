from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.lib.auth import get_current_user_id
from app.services.onboarding.schemas import (
    GetInitQuestionsResponse,
    InitAnswerHistoryItem,
    InitAnswersSubmitResponse,
    SubmitInitAnswersRequest,
)
from app.services.onboarding.service import onboarding_service

router = APIRouter()


@router.get("/questions", response_model=GetInitQuestionsResponse)
async def get_questions(version: int = 1):
    try:
        return onboarding_service.get_questions(version)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/answers", response_model=InitAnswersSubmitResponse)
async def submit_answers(
    request: SubmitInitAnswersRequest,
    dreamer_id: UUID = Depends(get_current_user_id),
):
    try:
        return onboarding_service.submit_answers(request, dreamer_id)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/answers/history", response_model=list[InitAnswerHistoryItem])
async def get_answer_history(
    dreamer_id: UUID = Depends(get_current_user_id),
):
    try:
        return onboarding_service.get_answer_history(dreamer_id)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
