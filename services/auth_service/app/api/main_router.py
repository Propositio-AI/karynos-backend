from fastapi import APIRouter
from api.v1.api_router import router as api_router

router = APIRouter()
router.include_router(api_router, prefix="/auth", tags=["Auth API"])