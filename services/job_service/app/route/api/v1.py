from fastapi import APIRouter, status
from typing import List
from uuid import UUID

from schema import RecommendResponse, JobDetailResponse


# /api/v1/job
router = APIRouter()


@router.get("/detail/{job_id}", response_model=JobDetailResponse)
async def get_job(job_id: int):
    """job情報の取得"""
   
    pass

@router.put("/good/{history_id}", status_code=status.HTTP_200_OK)
async def put_good(history_id: UUID):
    """ジョブに対する「いいね」登録（履歴の更新）"""

    pass

@router.put("/bad/{history_id}", status_code=status.HTTP_200_OK)
async def put_bad(history_id: UUID):
    """ジョブに対する「バッド」登録（履歴の更新）"""

    pass

@router.put("/save/{history_id}", status_code=status.HTTP_200_OK)
async def put_save(history_id: UUID):
    """ジョブに対する「保存」登録（履歴の更新）"""

    pass

@router.get("/recommend/{dreamer_id}", response_model=List[RecommendResponse])
async def get_recommendations(dreamer_id: UUID):
    """Dreamerにおすすめの職業をレスポンス"""
    # 例: おすすめ職業のリストを返す処理

    pass
