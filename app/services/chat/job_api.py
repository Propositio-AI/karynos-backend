import asyncio
import unicodedata

import requests
from fastapi import HTTPException


def normalize_job_id(job_id: str) -> str:
    return unicodedata.normalize("NFKC", str(job_id)).strip()


async def get_job_data(
    job_id: str, data_url: str = "http://backend-app:8000/api/v1/job"
):
    normalized_job_id = normalize_job_id(job_id)
    if not normalized_job_id:
        raise HTTPException(status_code=422, detail="job_id is required")

    try:
        response = await asyncio.to_thread(
            requests.get,
            f"{data_url}/detail/{normalized_job_id}",
            timeout=10,
        )
        response.raise_for_status()
    except requests.exceptions.Timeout as exc:
        raise HTTPException(
            status_code=504, detail="Job detail request timed out"
        ) from exc
    except requests.exceptions.HTTPError as exc:
        status_code = exc.response.status_code if exc.response is not None else 502
        if status_code == 404:
            detail = "Job not found"
        elif status_code == 422:
            detail = "Invalid job_id"
        else:
            detail = f"Failed to fetch job detail (status={status_code})"
        raise HTTPException(status_code=status_code, detail=detail) from exc
    except requests.exceptions.RequestException as exc:
        raise HTTPException(
            status_code=502, detail="Failed to fetch job detail"
        ) from exc

    return response.json()
