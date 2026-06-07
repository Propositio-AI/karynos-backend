import json
from datetime import datetime
from pathlib import Path
import sys

from fastapi import HTTPException

workspace_root = str(Path(__file__).resolve().parents[1])
if workspace_root not in sys.path:
    sys.path.insert(0, workspace_root)

from app.services.job_service.services.job_service import job_service


def main() -> int:
    try:
        result = job_service.sync_jobs_to_chromadb()
        payload = {
            "ok": True,
            "message": result.get("message", "sync completed"),
            "synced_count": int(result.get("synced_count", 0) or 0),
            "total_jobs": int(result.get("total_jobs", 0) or 0),
            "completed_at": result.get("completed_at", datetime.now().isoformat()),
        }
        print(json.dumps(payload, ensure_ascii=False))
        return 0
    except HTTPException as exc:
        payload = {
            "ok": False,
            "status_code": exc.status_code,
            "detail": exc.detail,
            "completed_at": datetime.now().isoformat(),
        }
        print(json.dumps(payload, ensure_ascii=False))
        return 1
    except Exception as exc:
        payload = {
            "ok": False,
            "status_code": 500,
            "detail": str(exc),
            "completed_at": datetime.now().isoformat(),
        }
        print(json.dumps(payload, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
