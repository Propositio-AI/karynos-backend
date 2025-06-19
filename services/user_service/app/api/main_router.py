from fastapi import APIRouter
from api.v1.api_router import router as api_router
from core.config import settings

router = APIRouter()
router.include_router(api_router, prefix=settings.PREFIX, tags=[settings.TAG])