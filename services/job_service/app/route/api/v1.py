from fastapi import APIRouter, status
from typing import List
from uuid import UUID

from crud import jobs_crud, history_crud
from schema import RecommendResponse, JobDetailResponse

# /api/v1/job
router = APIRouter()

@router.get("/detail/{job_id}", response_model=JobDetailResponse)
async def _(job_id: int):
    """job情報の取得"""
    _, jobs, error = jobs_crud.read([
        ["job_id", "==", job_id]
    ])

    return JobDetailResponse.model_validate(jobs[0])

@router.put("/good/{history_id}", status_code=status.HTTP_200_OK)
async def _(history_id: UUID):
    """ジョブに対する「いいね」登録（履歴の更新）"""
    _, updated, error = history_crud.update(
        [["history_id", "==", history_id]],
        {"good": True}
    )
    return {"message": "いいね登録が完了しました"}

@router.put("/bad/{history_id}", status_code=status.HTTP_200_OK)
async def _(history_id: UUID):
    """ジョブに対する「バッド」登録（履歴の更新）"""
    _, updated, error = history_crud.update(
        [["history_id", "==", history_id]],
        {"bad": True}
    )
    return {"message": "バッド登録が完了しました"}

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
