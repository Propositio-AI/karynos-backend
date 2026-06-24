from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.lib.auth import get_current_user_id
from app.services.job.schema import (
    JobDetailResponse,
    JobSearchResponse,
    ViewingHistoryResponse,
)
from app.services.job.service import job_service

router = APIRouter()


@router.get("/detail/{job_id}", response_model=JobDetailResponse)
async def get_job_detail(job_id: int):
    return job_service.get_job_detail(job_id)


@router.get("/history", response_model=ViewingHistoryResponse)
async def get_viewing_history(
    dreamer_id: UUID = Depends(get_current_user_id),
    limit: int = 50,
    offset: int = 0,
):
    return job_service.get_viewing_history(dreamer_id, limit, offset)


@router.get("/search", response_model=JobSearchResponse)
async def search_jobs(q: str, limit: int = 20, offset: int = 0):
    return job_service.search_jobs(q, limit, offset)


@router.put("/good/{history_id}", status_code=status.HTTP_200_OK)
async def mark_good(history_id: UUID):
    return job_service.mark_history(history_id, {"good": True})


@router.put("/bad/{history_id}", status_code=status.HTTP_200_OK)
async def mark_bad(history_id: UUID):
    return job_service.mark_history(history_id, {"bad": True})


@router.put("/save/{history_id}", status_code=status.HTTP_200_OK)
async def mark_save(history_id: UUID):
    job_service.mark_history(history_id, {"save": True})
    return {"message": "保存登録が完了しました"}


@router.post("/admin/sync-vectordb", status_code=status.HTTP_200_OK)
async def sync_jobs_to_vectordb():
    return job_service.sync_jobs_to_vectordb(rebuild=False)


@router.post("/admin/sync-vectordb/rebuild", status_code=status.HTTP_200_OK)
async def rebuild_vectordb():
    return job_service.sync_jobs_to_vectordb(rebuild=True)
