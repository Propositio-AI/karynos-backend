from fastapi import APIRouter, Depends, status
from typing import List
from uuid import UUID

from crud import  history_crud, jobs_crud
from schema import RecommendResponse, JobDetailResponse
from shared.lib.API.auth.main import get_current_user

# /api/v1/job
router = APIRouter()

@router.get("/detail/{job_id}", response_model=JobDetailResponse)
async def _(job_id: int):
    """job情報の取得"""

    _, jobs, error = jobs_crud.read([
        ["job_id", "==", job_id]
    ])


    job = jobs[0]

    payload = {
        "job_id": getattr(job, "job_id", 0),
        "name": getattr(job, "name", "") or "",
        "description": getattr(job, "description", "") or "",
        "imgs": getattr(job, "imgs", []) or [],
        "salary": int(getattr(job, "salary", 0) or 0),
        "level": int(getattr(job, "level", 0) or 0),
        "end_time": getattr(job, "end_time", "") or "",
        "holiday": int(getattr(job, "holiday", 0) or 0),
        "overtime_hours": int(getattr(job, "overtime_hours", 0) or 0),
        "age": int(getattr(job, "age", 0) or 0),
        "tenure_years": int(getattr(job, "tenure_years", 0) or 0),
        "marriage_age": int(getattr(job, "marriage_age", 0) or 0),
        "gender_ratio": float(getattr(job, "gender_ratio", 0.0) or 0.0),
        "romance_rate": float(getattr(job, "romance_rate", 0.0) or 0.0),
        "social_signification": getattr(job, "social_signification", "") or "",
        "personality_traits": getattr(job, "personality_traits", "") or "",
        "growth_opportunities": getattr(job, "growth_opportunities", "") or "",
        "wrong_image": getattr(job, "wrong_image", "") or "",
        "uniform": bool(getattr(job, "uniform", False) or False),
        "work_life_balance": float(getattr(job, "work_life_balance", 0.0) or 0.0),
        "future_outlook": getattr(job, "future_outlook", "") or "",
        "rarity": float(getattr(job, "rarity", 0.0) or 0.0),
        "scandal_history": getattr(job, "scandal_history", "") or "",
        "focus_on_education": bool(getattr(job, "focus_on_education", False) or False),
        "focus_on_achievements": bool(getattr(job, "focus_on_achievements", False) or False),
        "appeal_points": getattr(job, "appeal_points", "") or "",
        "daily_routine": getattr(job, "daily_routine", "") or "",
        "comments": getattr(job, "comments", "") or "",
        "skills": getattr(job, "skills", []) or [],
        "certifications": getattr(job, "certifications", []) or [],
        "companies": getattr(job, "companies", []) or [],
        "talents": getattr(job, "talents", []) or [],
        "interests": getattr(job, "interests", []) or [],
    }

    return JobDetailResponse.model_validate(payload)

@router.put("/good/{history_id}", status_code=status.HTTP_200_OK)
async def _(history_id: UUID):
    """ジョブに対する「いいね」登録（履歴の更新）"""
    _, updated, error = history_crud.update(
        [["history_id", "==", history_id]],
        {"good": True}
    )

    return status.HTTP_200_OK

@router.put("/bad/{history_id}", status_code=status.HTTP_200_OK)
async def _(history_id: UUID):
    """ジョブに対する「バッド」登録（履歴の更新）"""
    _, updated, error = history_crud.update(
        [["history_id", "==", history_id]],
        {"bad": True}
    )
    return status.HTTP_200_OK

@router.put("/save/{history_id}", status_code=status.HTTP_200_OK)
async def _(history_id: UUID):
    """ジョブに対する「保存」登録（履歴の更新）"""
    _, updated, error = history_crud.update(
        [["history_id", "==", history_id]],
        {"save": True}
    )
    return {"message": "保存登録が完了しました"}

@router.get("/recommend/{dreamer_id}", response_model=List[RecommendResponse])
async def _(dreamer_id: UUID):
    """Dreamerにおすすめの職業をレスポンス"""
   
    pass
